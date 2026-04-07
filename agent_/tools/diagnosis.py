from langchain.schema import HumanMessage

from ..llm.prompt_templates import DIAGNOSIS_PROMPT
from ..models import DiagnosisOutput


def _fmt_pcf(pcf_results):
    if not pcf_results:
        return "No PCF results"
    return "\n".join(
        [
            f"{i + 1}. {x.get('omim_disease_name_en', '')} (score={x.get('score', '')})"
            for i, x in enumerate(pcf_results)
        ]
    )


def _fmt_zeroshot(output):
    if not output or not hasattr(output, "ans"):
        return "No zero-shot results"
    return "\n".join([f"{i + 1}. {x.disease_name}" for i, x in enumerate(output.ans)])


def _fmt_gestalt(results):
    if not results:
        return "No gestalt results"
    return "\n".join([f"{i + 1}. {x.get('syndrome_name', '')}" for i, x in enumerate(results)])


def _fmt_phenotype(results):
    if not results:
        return "No phenotype-search results"
    return "\n".join([f"{i + 1}. {x.disease_info.disease_name}" for i, x in enumerate(results)])


def _fmt_web(results):
    if not results:
        return "No web results"
    return "\n".join([f"- {x.get('title', '')}" for x in results])

# 
def create_diagnosis(state):
    llm = state.get("llm")
    if not llm:
        return None, None

    prompt = DIAGNOSIS_PROMPT.format(
        present_hpo=", ".join(state.get("hpoDict", {}).values()),
        absent_hpo=", ".join(state.get("absentHpoDict", {}).values()),
        onset=state.get("onset", "Unknown"),
        sex=state.get("sex", "Unknown"),
        pcf_results=_fmt_pcf(state.get("pubCaseFinder", [])),
        zeroshot_results=_fmt_zeroshot(state.get("zeroShotResult")),
        gestalt_results=_fmt_gestalt(state.get("GestaltMatcher", [])),
        phenotype_results=_fmt_phenotype(state.get("phenotypeSearchResult", [])),
        web_results=_fmt_web(state.get("webresources", [])),
    )
    messages = [HumanMessage(content=prompt)]
    result = llm.get_structured_llm(DiagnosisOutput).invoke(messages)
    return result, prompt
