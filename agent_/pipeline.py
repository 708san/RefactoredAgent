import datetime
import os
import traceback

from langgraph.graph import StateGraph

from .llm.azure_llm_instance import get_llm_instance
from .utils.logger import log_node_result

from .config import AgentRuntimeConfig
from .graph_spec import GRAPH_EDGES, route_after_reflection
from .nodes import NODE_FUNCTIONS
from .state_types import State


class RefactoredRareDiseaseDiagnosisPipeline:
    def __init__(self, model_name: str = "gpt-4o", enable_log: bool = False, log_filename: str = None, config: AgentRuntimeConfig = None):
        self.config = config or AgentRuntimeConfig.from_env()
        self.enable_log = enable_log
        self.log_filename = log_filename
        self.logfile_path = self._resolve_logfile_path() if enable_log else None
        self.llm = get_llm_instance(model_name)
        self.graph = self._build_graph()
        if self.enable_log:
            self._write_graph_ascii_to_log()

    def _resolve_logfile_path(self) -> str:
        log_dir = os.path.join(os.getcwd(), "log")
        os.makedirs(log_dir, exist_ok=True)
        if self.log_filename:
            return os.path.join(log_dir, self.log_filename)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(log_dir, f"agent_refactored_{timestamp}.log")

    def _write_graph_ascii_to_log(self):
        try:
            ascii_graph = self.graph.get_graph().draw_ascii()
        except Exception as e:
            ascii_graph = f"[Failed to draw graph: {e}]"
        with open(self.logfile_path, "w", encoding="utf-8") as f:
            f.write("=== Refactored Agent Flow Graph ===\n")
            f.write(ascii_graph)
            f.write("\n\n")

    def _log(self, node_name: str, payload):
        if self.enable_log and self.logfile_path:
            log_node_result(self.logfile_path, node_name, payload)

    def _append_trace(self, state: State, event: str, node: str, detail: str = ""):
        trace = state.get("nodeTrace", [])
        trace.append(
            {
                "time": datetime.datetime.now().isoformat(),
                "event": event,
                "node": node,
                "detail": detail,
            }
        )
        state["nodeTrace"] = trace

    def _append_error(self, state: State, node: str, err: Exception):
        errors = state.get("nodeErrors", [])
        errors.append(
            {
                "time": datetime.datetime.now().isoformat(),
                "node": node,
                "error_type": type(err).__name__,
                "message": str(err),
            }
        )
        state["nodeErrors"] = errors

    def _fallback_for(self, node: str, state: State):
        fallback = {
            "begin_flow": {"depth": int(state.get("depth", 0)) + 1, "tentativeDiagnosis": None, "reflection": None},
            "pcf": {"pubCaseFinder": []},
            "normalize_pcf": {},
            "gestalt": {"GestaltMatcher": []},
            "normalize_gestalt": {},
            "create_hpo_dict": {"hpoDict": {}},
            "create_absent_hpo_dict": {"absentHpoDict": {}},
            "create_zero_shot": {"zeroShotResult": None},
            "normalize_zero_shot": {},
            "hpo_web_search": {"webresources": state.get("webresources", [])},
            "disease_search_with_hpo": {},
            "create_diagnosis": {},
            "normalize_tentative_diagnosis": {"tentativeDiagnosis": state.get("tentativeDiagnosis")},
            "disease_search": {"memory": state.get("memory", [])},
            "reflection": {"reflection": None},
            "final_diagnosis": {"finalDiagnosis": state.get("tentativeDiagnosis")},
            "normalize_final_diagnosis": {"finalDiagnosis": state.get("finalDiagnosis")},
        }
        return fallback.get(node, {})

    def _wrap_node(self, node_name: str, node_func):
        def wrapped(state: State):
            self._append_trace(state, "start", node_name)
            try:
                result = node_func(state)
                self._append_trace(state, "end", node_name)
                self._log(node_name, result)
                if isinstance(result, dict) and "result" in result:
                    return result["result"]
                return result
            except Exception as e:
                self._append_trace(state, "error", node_name, f"{type(e).__name__}: {e}")
                self._append_error(state, node_name, e)
                self._log(node_name, {"error": str(e), "traceback": traceback.format_exc(limit=8)})
                return self._fallback_for(node_name, state)

        return wrapped

    def _build_graph(self):
        graph_builder = StateGraph(State)
        for node_name, node_func in NODE_FUNCTIONS.items():
            graph_builder.add_node(node_name, self._wrap_node(node_name, node_func))

        for src, dst in GRAPH_EDGES:
            graph_builder.add_edge(src, dst)

        graph_builder.add_conditional_edges(
            "reflection",
            route_after_reflection,
            path_map={
                "to_beginning": "begin_flow",
                "to_final": "final_diagnosis",
            },
        )
        return graph_builder.compile()

    def _build_initial_state(
        self,
        hpo_list,
        image_path=None,
        absent_hpo_list=None,
        onset=None,
        sex=None,
        patient_id=None,
    ) -> State:
        return {
            "depth": 0,
            "maxDepth": self.config.max_reflection_depth,
            "clinicalText": None,
            "hpoList": hpo_list,
            "absentHpoList": absent_hpo_list or [],
            "imagePath": image_path,
            "pubCaseFinder": [],
            "GestaltMatcher": [],
            "hpoDict": {},
            "absentHpoDict": {},
            "webresources": [],
            "memory": [],
            "zeroShotResult": None,
            "tentativeDiagnosis": None,
            "reflection": None,
            "finalDiagnosis": None,
            "onset": onset if onset else "Unknown",
            "sex": sex if sex else "Unknown",
            "patient_id": patient_id if patient_id else "unknown",
            "llm": self.llm,
            "diseaseSearchTimeoutSec": self.config.disease_search_timeout_sec,
            "reflectionTimeoutSec": self.config.reflection_timeout_sec,
            "nodeTrace": [],
            "nodeErrors": [],
        }

    def run(
        self,
        hpo_list,
        image_path=None,
        verbose=False,
        absent_hpo_list=None,
        onset=None,
        sex=None,
        patient_id=None,
    ):
        initial_state = self._build_initial_state(
            hpo_list=hpo_list,
            image_path=image_path,
            absent_hpo_list=absent_hpo_list,
            onset=onset,
            sex=sex,
            patient_id=patient_id,
        )

        result = self.graph.invoke(initial_state)
        if verbose:
            self.pretty_print(result)
        return result

    def pretty_print(self, result):
        reflection = result.get("reflection")
        final_diag = result.get("finalDiagnosis")

        print("=== reflection ===")
        if reflection and hasattr(reflection, "ans"):
            for i, ans in enumerate(reflection.ans, 1):
                print(f"{i}. {getattr(ans, 'disease_name', '')} -> {getattr(ans, 'Correctness', False)}")
        else:
            print("No reflection result")

        print("=== final diagnosis ===")
        if final_diag and hasattr(final_diag, "ans"):
            for i, ans in enumerate(final_diag.ans, 1):
                print(f"{i}. {getattr(ans, 'disease_name', '')}")
        else:
            print("No final diagnosis")
