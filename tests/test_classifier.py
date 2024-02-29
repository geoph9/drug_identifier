"""Test cases for the classifier module (src/drug_discoverer/classifier).
This module contains the following classes:
- LLMClassifier
- BaseClassifier
- SpacyClassifier
- DummyClassifier
"""

import os

import pytest

from drug_discoverer.classifier.base import BaseClassifier
from drug_discoverer.classifier.spacy_classifier import SpacyClassifier
from drug_discoverer.classifier.llm_classifier import LLMClassifier
from drug_discoverer.classifier.dummy_classifier import DummyClassifier
from drug_discoverer.drug_db import DrugDB
from drug_discoverer.utils import get_env_variables


@pytest.fixture
def drug_db() -> DrugDB:
    """Fixture for the DrugDB class."""
    db_uri = "postgresql://{DB_USERNAME}:{DB_PWD}@localhost:5432/{DB_NAME}"
    env_vars = get_env_variables()
    db_uri = db_uri.format(**env_vars)
    return DrugDB(db_uri)

def test_base_classifier_classify_single_raises_not_implemented_error(drug_db: DrugDB) -> None:
    """It raises a NotImplementedError."""
    clf = BaseClassifier(drug_db)
    with pytest.raises(NotImplementedError):
        clf.classify_single("dummy text")

def test_spacy_classifier_classify_single_works(drug_db: DrugDB) -> None:
    """It returns a list of drug names."""
    clf = SpacyClassifier(drug_db)
    text = "The patient was given a dose of aspirin."
    result = clf.classify_single(text)
    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(name, str) for name in result)

def test_dummy_classifier_classify_single_works(drug_db: DrugDB) -> None:
    """It returns a list of drug names."""
    clf = DummyClassifier(drug_db)
    text = "The patient was given a dose of aspirin."
    result = clf.classify_single(text)
    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(name, str) for name in result)
