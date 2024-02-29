"""Implements a dummy classifier that simply takes in the list of available drug names (from our database)
and tries to find any matches from the input text. If a match is found, it returns the matched drug name.

As preprocessing, we first lowercame the input text, we remove non-alphanumeric characters, and then we split the
text into words. We then compare each word with the list of drug names and return the first match.

Example:
    The purpose of this trial is to assess the efficacy, safety, tolerability, biologic activity, and pharmacokinetics of sacituzumab...
    -> ["salituzumab"]
"""

import re
from typing import List

from drug_discoverer.classifier.base import BaseClassifier
from drug_discoverer.drug_db import DrugDB


class DummyClassifier(BaseClassifier):
    def classify_single(self, text: str) -> List[str]:
        """Classify the input text and return the matched drug names.
        Only unique drug names are returned.
        """
        if self.to_lower:
            text = text.lower()
        if self.remove_punctuation:
            text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
        # also replace multiple new lines with one space
        text = re.sub(r"\n+", " ", text)
        text = re.sub(r"\n", " ", text)
        text = re.sub(r" +", " ", text).strip()
        words = text.split()
        output = []
        for word in words:
            if word in self.drug_names:
                output.append(self.drug_names[word])
        return list(set(output))
