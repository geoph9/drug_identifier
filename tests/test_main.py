"""Test cases for the __main__ module."""
import os

import pytest
from click.testing import CliRunner

from drug_discoverer import __main__


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


def test_main_succeeds_with_dummy_classifier(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    test_data_path = "tests/data/nctids.txt"
    output_json = "tests/data/output.json"
    result = runner.invoke(
        __main__.main,
        ["--nctids-file", test_data_path, "--output-json", output_json, "--clf-type", "dummy"]
    )
    assert os.path.isfile(output_json), f"Expected to find the output file {output_json} but it was not found."
    # delete the output file
    os.remove(output_json)
    assert result.exit_code == 0
