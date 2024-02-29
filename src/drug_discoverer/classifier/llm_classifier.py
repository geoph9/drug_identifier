"""Defines the LLMClassifier class that uses prompting through LangChain to
identify drug names in a given text.
"""
import ast
from typing import List

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from loguru import logger

from drug_discoverer.classifier.base import BaseClassifier
from drug_discoverer.drug_db import DrugDB
from drug_discoverer.classifier import llm_templates


class LLMClassifier(BaseClassifier):
    """This class uses an LLM (GPT-based model from OpenAI) to identify drug names in a given text.
    The pipeline (for a single clinical trial summary) is as follows:
    - Create a prompt using the template.
    - Use the LLM to generate text based on the prompt. E.g. A simple prompt could be
      "You are given the following clinical trial summary: {summary}. Please identify the drug names that appear in it."
    - Extract the drug names from the generated text.
    - Lowercase the drug names and try to find them in the database (using the `lname` column).
    - Return the preferred names of the matched drug names.
    - The output json will have a also contain a list of the non-matched drug names.
    """
    def __init__(
        self,
        drug_db: DrugDB,
        model: str,
        template: str,
        lower_case: bool = True,
        save_unmatched_drugs: bool = False,
        *args,
        **kwargs,
    ):
        super().__init__(drug_db, lower_case, remove_punctuation=False, save_unmatched_drugs=save_unmatched_drugs)
        self.model = ChatOpenAI(model=model)
        self.template = llm_templates.get_template(template)

    def classify_single(self, text: str) -> List[str]:
        """Classify the input text and return the matched drug names.
        Only unique drug names are returned.
        """
        prompt = ChatPromptTemplate.from_template(self.template)
        chain = prompt | self.model
        predictions = chain.invoke({"summary": text})
        try:
            drug_names = list(set(ast.literal_eval(predictions.content.strip())))
        except Exception as e:
            logger.warning(f"Failed to find drugs on text: {text}\nLLM output was: {predictions} (Error={e})")
            drug_names = []
        if self.to_lower:
            drug_names = [name.lower() for name in drug_names]
        return drug_names
