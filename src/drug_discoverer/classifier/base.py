"""Implementation of the base classifier class. This class should be inherited by all other classifiers.
It provides a common interface for all classifiers. List of abstract methods:
- classify
- save_to_json
"""

import json
import os
import re
from abc import ABC
from abc import abstractmethod
from typing import List

from loguru import logger
from tqdm import tqdm

from drug_discoverer.drug_db import DrugDB
from drug_discoverer.utils import get_clinical_trials_summaries


class BaseClassifier(ABC):
    def __init__(
        self,
        drug_db: DrugDB,
        lower_case: bool = True,
        remove_punctuation: bool = True,
        save_unmatched_drugs: bool = False,
    ):
        # Keep a dictionary mapping from the original (provided) name to the processed one (i.e. the one
        # after lowercasing and removing punctuation).
        self.drug_db = drug_db
        drug_names = self.drug_db.get_all_names(only_lowercase=lower_case)
        self.drug_names = {name: name for name in drug_names}
        # convert to string instead of Column[...]
        self.drug_names = {str(name): str(name) for name in drug_names}
        self.to_lower = lower_case
        self.remove_punctuation = remove_punctuation
        self.save_unmatched_drugs = save_unmatched_drugs
        if remove_punctuation:
            self.drug_names = {
                re.sub(r" +", " ", re.sub(r"[^a-zA-Z0-9\s]", " ", name)): name
                for name in self.drug_names
            }

    @abstractmethod
    def classify_single(self, text: str) -> List[str]:
        """Classify the input text and return the matched drug names.
        Only unique drug names are returned.
        """
        pass

    def _to_preferred_name(self, clf_output: List[str]) -> List[str]:
        """Convert the classifier output to preferred drug names. Assumes
        that self.drug_db is a valid DrugDB instance.
        """
        return [
            self.drug_db.get_preferred_name(name, is_lower=self.to_lower)
            for name in clf_output
        ]

    def classify(self, nctids: List[str], output_filename: str) -> None:
        """Classify the input text and return the matched drug names.
        Only unique drug names are returned.
        """
        nctid_to_summary: dict = get_clinical_trials_summaries(nctids)
        nctid_to_drugs_found = {}
        for nctid, summary in tqdm(
            nctid_to_summary.items(), desc="Classifying summaries"
        ):
            labels = self.classify_single(summary)
            nctid_to_drugs_found[nctid] = (summary, self._to_preferred_name(labels))
        self.save_to_json(output_filename, nctid_to_drugs_found)

    def save_to_json(self, output_filename: str, nctid_to_drugs_found: dict) -> None:
        """Save the results to a json file."""
        os.makedirs(os.path.dirname(output_filename), exist_ok=True)
        if self.save_unmatched_drugs:
            for nctid, (summary, drugs) in nctid_to_drugs_found.items():
                # TODO: Inneficent double parsing, but it's ok for now
                unmatched_drugs = [
                    drug.replace("<UNMATCHED> ", "")
                    for drug in drugs
                    if "<UNMATCHED> " in drug
                ]
                nctid_to_drugs_found[nctid] = {
                    "summary": summary,
                    "matched": [drug for drug in drugs if "<UNMATCHED>" not in drug],
                    "unmatched": unmatched_drugs,
                }
        else:
            for nctid, (summary, drugs) in nctid_to_drugs_found.items():
                matched_drugs = [drug for drug in drugs if "<UNMATCHED>" not in drug]
                # Make sure there is the same pattern regardless of self.save_unmatched_drugs
                nctid_to_drugs_found[nctid] = {
                    "summary": summary,
                    "matched": matched_drugs
                }
        with open(output_filename, "w") as f:
            json.dump(nctid_to_drugs_found, f, indent=4)
        logger.info(f"Saved the results to: {output_filename}")
