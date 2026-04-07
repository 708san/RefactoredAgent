import os
from typing import Any, Dict

from langchain_openai import AzureChatOpenAI

 # Azure OpenAIのLLMインスタンスを管理するラッパークラス
class AzureOpenAIWrapper:
    def __init__(self, model_name, azure_endpoint, api_key, deployment_name, api_version):
        self.model_name = model_name
        self.azure_endpoint = azure_endpoint
        self.api_key = api_key
        self.deployment_name = deployment_name
        self.api_version = api_version

        self.default_max_tokens = 8192 if model_name == "gpt-4o" else 12000
        self.request_timeout = float(os.getenv("AGENT_LLM_TIMEOUT_SECONDS", "90"))
        self.max_retries = int(os.getenv("AGENT_LLM_MAX_RETRIES", "2"))
        self.llm = self._create_llm(self.default_max_tokens)
        """
        指定されたトークン数でAzureChatOpenAIインスタンスを生成する。
        モデルがgpt-4oかそれ以外（o1系など）かでパラメータ構成を切り替える。
        """
    def _create_llm(self, max_completion_tokens: int) -> AzureChatOpenAI:
        llm_params: Dict[str, Any] = {
            "azure_endpoint": self.azure_endpoint,
            "api_key": self.api_key,
            "deployment_name": self.deployment_name,
            "api_version": self.api_version,
            "request_timeout": self.request_timeout,
            "max_retries": self.max_retries,
        }

        if self.model_name == "gpt-4o":
            llm_params["temperature"] = 0.0
            llm_params["max_tokens"] = max_completion_tokens
        else:
            llm_params["model_kwargs"] = {
                "extra_body": {
                    "max_completion_tokens": max_completion_tokens,
                    "verbosity": "medium",
                    "reasoning_effort": "none",
                }
            }

        return AzureChatOpenAI(**llm_params)

    def get_temp_llm_with_max_tokens(self, max_completion_tokens: int) -> AzureChatOpenAI:
        return self._create_llm(max_completion_tokens)

    def get_structured_llm(self, output_schema):
        return self.llm.with_structured_output(output_schema)

    def generate(self, prompt: str):
        return self.llm.invoke(prompt)
