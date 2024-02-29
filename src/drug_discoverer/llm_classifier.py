from typing import Optional, List

import torch
from transformers import pipeline, AutoTokenizer
from loguru import logger

from drug_discoverer.templates import DrugDiscoveryTemplate
from drug_discoverer.utils import get_clinical_trials_summaries


class Prompter:
    """Prompter for drug discovery tasks.
    It takes in a huggingface model name (e.g. "tiiuae/falcon-7b-instruct") and a prompting template.
    It provides a method to generate prompts for drug discovery tasks. The templates assist the
    LLM in finding/classifying Drug Entities from the input summaries. The summaries are taken from
    clinicaltrials.gov and we only care about certain ids.
    """
    def __init__(self, model: str, template: Optional[str] = DrugDiscoveryTemplate):
        self.model = model
        if model is None:
            self.model = "tiiuae/falcon-7b-instruct"
            logger.info(f"No model provided, using default model {self.model}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model)
        self.template = template
        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )

    def identify_drugs(self, entries: List[str], max_length: int = 50) -> str:
        prompt = self.template.format(
            molecule=entries[0],
        )
        return self.pipe(prompt, max_length=max_length)[0]["generated_text"]
