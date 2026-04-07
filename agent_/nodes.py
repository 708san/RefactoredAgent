import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed
from typing import Callable, Dict

from .models import ReflectionOutput
from .tools.diagnosis import create_diagnosis
from .tools.disease_normalize import (
    disease_normalize_for_diagnosis,
    normalize_gestalt_results,
    normalize_pcf_results,
    normalize_zeroshot_results,
)
from .tools.disease_search import disease_search_for_diagnosis
from .tools.embedding_search import embedding_search_with_hpo
from .tools.final_diagnosis import create_final_diagnosis
from .tools.gestalt_matcher import call_gestalt_matcher_api
from .tools.hpo_web_research import search_hpo_terms
from .tools.make_hpo_dict import make_hpo_dict
from .tools.pcf_api import call_pcf
from .tools.reflection import create_reflection
from .tools.zero_shot import create_zero_shot

from .state_types import State


def begin_flow_node(state: State) -> Dict:
    depth = int(state.get("depth", 0)) + 1
    return {"depth": depth, "tentativeDiagnosis": None, "reflection": None}


def pcf_node(state: State) -> Dict:
    hpo_list = state.get("hpoList", [])
    if not hpo_list:
        return {"pubCaseFinder": []}
    depth = int(state.get("depth", 0))
    return {"pubCaseFinder": call_pcf(hpo_list)}


def normalize_pcf_node(state: State) -> Dict:
    normalized_results = normalize_pcf_results(state)
    return {"pubCaseFinder": normalized_results} if normalized_results else {}


def gestalt_matcher_node(state: State) -> Dict:
    image_path = state.get("imagePath")
    if not image_path:
        return {"GestaltMatcher": []}

    depth = int(state.get("depth", 0))
    raw_results = call_gestalt_matcher_api(image_path, depth)
    normalized = []
    for res in raw_results:
        normalized.append(
            {
                "subject_id": res.get("subject_id", ""),
                "syndrome_name": res.get("syndrome_name", ""),
                "omim_id": res.get("omim_id", ""),
                "image_id": res.get("image_id", ""),
                "score": res.get("score"),
            }
        )
    return {"GestaltMatcher": normalized}


def normalize_gestalt_node(state: State) -> Dict:
    normalized_results = normalize_gestalt_results(state)
    return {"GestaltMatcher": normalized_results} if normalized_results else {}


def create_hpo_dict_node(state: State) -> Dict:
    return {"hpoDict": make_hpo_dict(state.get("hpoList", []))}


def create_absent_hpo_dict_node(state: State) -> Dict:
    return {"absentHpoDict": make_hpo_dict(state.get("absentHpoList", []))}


def create_zero_shot_node(state: State) -> Dict:
    if state.get("zeroShotResult") is not None:
        return {"zeroShotResult": state["zeroShotResult"]}

    hpo_dict = state.get("hpoDict", {})
    if not hpo_dict:
        return {"zeroShotResult": None}

    result, prompt = create_zero_shot(state)
    if result:
        return {"zeroShotResult": result, "prompt": prompt}
    return {"zeroShotResult": None}


def normalize_zero_shot_node(state: State) -> Dict:
    normalized_result = normalize_zeroshot_results(state)
    return {"zeroShotResult": normalized_result} if normalized_result else {}


def hpo_web_search_node(state: State) -> Dict:
    webresources = search_hpo_terms(state)
    merged = state.get("webresources", []) + webresources
    return {"webresources": merged}


def disease_search_with_hpo_node(state: State) -> Dict:
    search_results = embedding_search_with_hpo(state)
    return {"phenotypeSearchResult": search_results} if search_results else {}


def create_diagnosis_node(state: State) -> Dict:
    result, prompt = create_diagnosis(state)
    if result:
        return {"tentativeDiagnosis": result, "prompt": prompt}
    return {}


def normalize_tentative_diagnosis_node(state: State) -> Dict:
    tentative = state.get("tentativeDiagnosis")
    if tentative is None:
        return {"tentativeDiagnosis": None}
    return {"tentativeDiagnosis": disease_normalize_for_diagnosis(tentative)}


def disease_search_node(state: State) -> Dict:
    return disease_search_for_diagnosis(state)


def _empty_reflection_output():
    return ReflectionOutput(ans=[])


def reflection_node(state: State) -> Dict:
    tentative = state.get("tentativeDiagnosis")
    hpo_dict = state.get("hpoDict")
    if not tentative or not hpo_dict or not hasattr(tentative, "ans"):
        return {"reflection": _empty_reflection_output()}

    targets = tentative.ans
    if not targets:
        return {"reflection": _empty_reflection_output()}

    timeout_sec = int(state.get("reflectionTimeoutSec", os.getenv("AGENT_REFLECTION_TIMEOUT_SECONDS", "180")))
    max_workers = min(len(targets), 10)
    if max_workers <= 0:
        return {"reflection": _empty_reflection_output()}

    reflection_results = []
    prompts = []

    def task(diagnosis_to_judge):
        result, prompt = create_reflection(state, diagnosis_to_judge)
        return result, prompt

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_target = {executor.submit(task, t): t for t in targets}
        futures = list(future_to_target.keys())
        try:
            for future in as_completed(future_to_target, timeout=timeout_sec):
                try:
                    result, prompt = future.result()
                    if result:
                        reflection_results.append(result)
                        prompts.append(prompt)
                except Exception:
                    continue
        except TimeoutError:
            pass
        finally:
            for future in futures:
                if not future.done():
                    future.cancel()

    if not reflection_results:
        return {"reflection": _empty_reflection_output()}

    return {"reflection": ReflectionOutput(ans=reflection_results), "prompt": prompts}


def final_diagnosis_node(state: State) -> Dict:
    final_diagnosis, prompt = create_final_diagnosis(state)
    return {"finalDiagnosis": final_diagnosis, "prompt": prompt}


def normalize_final_diagnosis_node(state: State) -> Dict:
    final_diagnosis = state.get("finalDiagnosis")
    if final_diagnosis is None:
        return {"finalDiagnosis": None}
    return {"finalDiagnosis": disease_normalize_for_diagnosis(final_diagnosis)}


NODE_FUNCTIONS: Dict[str, Callable[[State], Dict]] = {
    "begin_flow": begin_flow_node,
    "pcf": pcf_node,
    "normalize_pcf": normalize_pcf_node,
    "gestalt": gestalt_matcher_node,
    "normalize_gestalt": normalize_gestalt_node,
    "create_hpo_dict": create_hpo_dict_node,
    "create_absent_hpo_dict": create_absent_hpo_dict_node,
    "create_zero_shot": create_zero_shot_node,
    "normalize_zero_shot": normalize_zero_shot_node,
    "hpo_web_search": hpo_web_search_node,
    "disease_search_with_hpo": disease_search_with_hpo_node,
    "create_diagnosis": create_diagnosis_node,
    "normalize_tentative_diagnosis": normalize_tentative_diagnosis_node,
    "disease_search": disease_search_node,
    "reflection": reflection_node,
    "final_diagnosis": final_diagnosis_node,
    "normalize_final_diagnosis": normalize_final_diagnosis_node,
}
