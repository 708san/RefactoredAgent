import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AgentRuntimeConfig:
    max_reflection_depth: int = 1
    reflection_timeout_sec: int = 180
    disease_search_timeout_sec: int = 300

    @classmethod
    def from_env(cls) -> "AgentRuntimeConfig":
        return cls(
            max_reflection_depth=int(os.getenv("AGENT_MAX_REFLECTION_DEPTH", "1")),
            reflection_timeout_sec=int(os.getenv("AGENT_REFLECTION_TIMEOUT_SECONDS", "180")),
            disease_search_timeout_sec=int(os.getenv("AGENT_DISEASE_SEARCH_TIMEOUT_SECONDS", "300")),
        )
