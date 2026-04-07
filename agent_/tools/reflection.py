from langchain.schema import HumanMessage

from ..llm.prompt_templates import REFLECTION_PROMPT
from ..models import ReflectionFormat


def _format_evidence(memory, disease_name: str) -> str:
    if not memory:
        return "No evidence"
    lines = []
    for item in memory:
        if item.get("disease_name") == disease_name:
            lines.append(f"- {item.get('title', '')}: {item.get('content', '')}")
    return "\n".join(lines) if lines else "No disease-specific evidence"


def create_reflection(state, diagnosis_to_judge):
    llm = state.get("llm")
    if not llm:
        return None, None

    disease_name = diagnosis_to_judge.disease_name
    prompt = REFLECTION_PROMPT.format(
        present_hpo=", ".join(state.get("hpoDict", {}).values()),
        absent_hpo=", ".join(state.get("absentHpoDict", {}).values()),
        onset=state.get("onset", "Unknown"),
        sex=state.get("sex", "Unknown"),
        diagnosis=f"{disease_name} (rank={diagnosis_to_judge.rank})\n{diagnosis_to_judge.description}",
        evidence=_format_evidence(state.get("memory", []), disease_name),
    )

    messages = [HumanMessage(content=prompt)]
    result = llm.get_structured_llm(ReflectionFormat).invoke(messages)
    return result, prompt
