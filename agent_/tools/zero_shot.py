from langchain.schema import HumanMessage

from ..llm.prompt_templates import ZERO_SHOT_PROMPT
from ..models import ZeroShotOutput


def create_zero_shot(state):
    hpo_dict = state.get("hpoDict", {})
    if not hpo_dict:
        return None, None

    llm = state.get("llm")
    if not llm:
        return None, None

    prompt = ZERO_SHOT_PROMPT.format(
        present_hpo=", ".join(hpo_dict.values()),
        absent_hpo=", ".join(state.get("absentHpoDict", {}).values()),
        onset=state.get("onset", "Unknown"),
        sex=state.get("sex", "Unknown"),
    )
    messages = [HumanMessage(content=prompt)]
    result = llm.get_structured_llm(ZeroShotOutput).invoke(messages)
    return result, prompt
