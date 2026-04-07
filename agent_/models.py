from typing import Dict, List, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Field


class PCFResult(TypedDict):
    omim_disease_name_en: str
    description: str
    score: Optional[float]
    omim_id: str


class InformationItem(TypedDict):
    title: str
    url: str
    content: str
    disease_name: str


class WebResource(TypedDict):
    title: str
    url: str
    snippet: str


class ZeroShotFormat(BaseModel):
    disease_name: str
    rank: int
    OMIM_id: Optional[str] = None


class ZeroShotOutput(BaseModel):
    ans: List[ZeroShotFormat] = Field(default_factory=list)


class DiagnosisFormat(BaseModel):
    disease_name: str
    OMIM_id: Optional[str] = None
    description: str
    rank: int


class DiagnosisOutput(BaseModel):
    ans: List[DiagnosisFormat] = Field(default_factory=list)
    reference: Optional[str] = None


class ReflectionFormat(BaseModel):
    disease_name: str
    Correctness: bool
    PatientSummary: str
    DiagnosisAnalysis: str
    references: List[str] = Field(default_factory=list)


class ReflectionOutput(BaseModel):
    ans: List[ReflectionFormat] = Field(default_factory=list)


class GestaltMatcherFormat(BaseModel):
    subject_id: str
    syndrome_name: str
    omim_id: str
    image_id: str
    score: float


class OMIMEntry(BaseModel):
    OMIM_id: str
    disease_name: str
    synonym: Optional[str] = None
    definition: Optional[str] = None
    phenotype: Optional[List[str]] = None


class PhenotypeSearchFormat(BaseModel):
    disease_info: OMIMEntry
    similarity_score: float


def as_simple_hpo_dict(hpo_list: List[str]) -> Dict[str, str]:
    return {hpo: hpo for hpo in hpo_list if hpo}
