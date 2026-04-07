from typing import Dict, List, Optional
from typing_extensions import TypedDict

from .llm.llm_wrapper import AzureOpenAIWrapper
from .models import (
    DiagnosisOutput,
    GestaltMatcherFormat,
    InformationItem,
    PCFResult,
    PhenotypeSearchFormat,
    ReflectionOutput,
    WebResource,
    ZeroShotOutput,
)


class NodeTrace(TypedDict):
    time: str
    event: str
    node: str
    detail: str


class NodeError(TypedDict):
    time: str
    node: str
    error_type: str
    message: str


class State(TypedDict, total=False):
    depth: int
    maxDepth: int
    imagePath: Optional[str]
    clinicalText: Optional[str]
    hpoList: List[str]
    hpoDict: Dict[str, str]
    absentHpoList: List[str]
    absentHpoDict: Dict[str, str]
    pubCaseFinder: List[PCFResult]
    GestaltMatcher: List[GestaltMatcherFormat]
    phenotypeSearchResult: List[PhenotypeSearchFormat]
    webresources: List[WebResource]
    memory: List[InformationItem]
    zeroShotResult: Optional[ZeroShotOutput]
    tentativeDiagnosis: Optional[DiagnosisOutput]
    reflection: Optional[ReflectionOutput]
    finalDiagnosis: Optional[DiagnosisOutput]
    onset: Optional[str]
    sex: Optional[str]
    patient_id: Optional[str]
    llm: Optional[AzureOpenAIWrapper]
    diseaseSearchTimeoutSec: int
    reflectionTimeoutSec: int
    nodeTrace: List[NodeTrace]
    nodeErrors: List[NodeError]
