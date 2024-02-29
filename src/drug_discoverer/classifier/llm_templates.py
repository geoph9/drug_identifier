DrugDiscoveryOneShotTemplate = """Given a brief summary of a clinical trial, find which drugs are mentioned in the summary.

Clinical Trial Summary: ```This is a multicenter, Phase 3 randomized, placebo-controlled study designed to evaluate adalimumab in children 4 to 17 years old with polyarticular juvenile idiopathic arthritis (JIA) who are either methotrexate (MTX) treated or non-MTX treated.```
Drug names: ["adalimumab", "methotrexate"].

Summary: ```{summary}```
Drug names: 
"""

DrugDiscoveryZeroShotTemplate = """Given a brief summary of a clinical trial, find which drugs are mentioned in the summary.

Clinical Trial Summary: ```{summary}```
Drug names: 
"""

def get_template(template_name: str) -> str:
    if template_name in ["1shot", "one-shot", "DrugDiscoveryOneShotTemplate"]:
        return DrugDiscoveryOneShotTemplate
    elif template_name in ["0shot", "zero-shot", "DrugDiscoveryZeroShotTemplate"]:
        return DrugDiscoveryZeroShotTemplate
    raise ValueError(f"Invalid template name: {template_name}. Expected one of: '1shot', '0shot'.")