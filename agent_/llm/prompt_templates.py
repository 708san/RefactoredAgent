ZERO_SHOT_PROMPT = """
You are a clinical geneticist.
Given patient phenotype information, output the top 5 likely diagnoses.

Present HPO terms: {present_hpo}
Absent HPO terms: {absent_hpo}
Onset: {onset}
Sex: {sex}
"""


DIAGNOSIS_PROMPT = """
You are a rare disease diagnostician.
Synthesize candidate diseases from multiple sources and rank top 5.

Present HPO: {present_hpo}
Absent HPO: {absent_hpo}
Onset: {onset}
Sex: {sex}

PubCaseFinder:
{pcf_results}

Zero-shot:
{zeroshot_results}

GestaltMatcher:
{gestalt_results}

Phenotype search:
{phenotype_results}

Web resources:
{web_results}
"""


REFLECTION_PROMPT = """
You are reviewing a tentative diagnosis.
Judge correctness for this patient and explain briefly.

Present HPO: {present_hpo}
Absent HPO: {absent_hpo}
Onset: {onset}
Sex: {sex}

Diagnosis under review:
{diagnosis}

Evidence:
{evidence}
"""


FINAL_PROMPT = """
You are generating final ranked diagnoses.
Use tentative diagnoses and reflection outputs.

Present HPO: {present_hpo}
Absent HPO: {absent_hpo}
Onset: {onset}
Sex: {sex}

Tentative diagnoses:
{tentative}

Reflection results:
{reflection}
"""
