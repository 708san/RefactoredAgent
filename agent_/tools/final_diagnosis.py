from langchain.schema import HumanMessage

from ..llm.prompt_templates import FINAL_PROMPT
from ..models import DiagnosisOutput


def _format_tentative(tentative):
    if not tentative or not hasattr(tentative, "ans"):
        return "No tentative diagnoses"
    return "\n".join([f"{x.rank}. {x.disease_name} - {x.description}" for x in tentative.ans])


def _format_reflection(reflection):
    if not reflection or not hasattr(reflection, "ans"):
        return "No reflection"
    return "\n".join([f"{x.disease_name}: Correct={x.Correctness}" for x in reflection.ans])


def create_final_diagnosis(state):
    llm = state.get("llm")
    if not llm:
        return None, None

    prompt = FINAL_PROMPT.format(
        present_hpo=", ".join(state.get("hpoDict", {}).values()),
        absent_hpo=", ".join(state.get("absentHpoDict", {}).values()),
        onset=state.get("onset", "Unknown"),
        sex=state.get("sex", "Unknown"),
        tentative=_format_tentative(state.get("tentativeDiagnosis")),
        reflection=_format_reflection(state.get("reflection")),
    )
    messages = [HumanMessage(content=prompt)]
    result = llm.get_structured_llm(DiagnosisOutput).invoke(messages)
    return result, prompt
