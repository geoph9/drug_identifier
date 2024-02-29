"""Test cases for the drug_db module (src/drug_discoverer/drug_db)."""

import os

import pytest

from drug_discoverer.drug_db import DrugDB
from drug_discoverer.utils import get_env_variables


@pytest.fixture
def drug_db() -> DrugDB:
    """Fixture for the DrugDB class."""
    db_uri = "postgresql://{DB_USERNAME}:{DB_PWD}@localhost:5432/{DB_NAME}"
    env_vars = get_env_variables()
    db_uri = db_uri.format(**env_vars)
    return DrugDB(db_uri)


def test_drug_db_get_drug_names_works(drug_db: DrugDB) -> None:
    """It returns a list of drug names."""
    result = drug_db.get_all_names()
    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(name, str) for name in result)