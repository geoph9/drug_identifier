"""Use spaCy to classify the input text and return the matched drug names.
Here, we will use Kormilitzin's et al. `en_core_med7_lg` model to classify the input text.
We only care about the entities that are of type `DRUG`. We will return the preferred names of the matched drug names.

NOTE: We assume that you have followed the instructions in https://github.com/kormilitzin/med7
to install the `en_core_med7_lg` model:
`pip install https://huggingface.co/kormilitzin/en_core_med7_trf/resolve/main/en_core_med7_trf-any-py3-none-any.whl`
"""

import spacy

from drug_discoverer.classifier.base import BaseClassifier
from drug_discoverer.drug_db import DrugDB


class SpacyClassifier(BaseClassifier):
    def __init__(
        self,
        drug_db: DrugDB,
        lower_case: bool = True,
        save_unmatched_drugs: bool = False,
        *args,
        **kwargs,
    ):
        super().__init__(
            drug_db,
            lower_case,
            remove_punctuation=False,
            save_unmatched_drugs=save_unmatched_drugs
        )
        self.nlp = spacy.load("en_core_med7_trf")

    def classify_single(self, text: str):
        """Classify the input text and return the matched drug names.
        Only unique drug names are returned.
        """
        doc = self.nlp(text)
        drug_names = list(set([ent.text.lower() for ent in doc.ents if ent.label_ == "DRUG"]))
        return drug_names