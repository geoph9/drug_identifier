"""Command-line interface."""
import sys

import click
from loguru import logger

from drug_discoverer.drug_db import DrugDB
from drug_discoverer.classifier.dummy_classifier import DummyClassifier
from drug_discoverer.utils import get_env_variables


logger.add(sys.stderr, level="INFO")

@click.command()
@click.version_option()
@click.option(
    "--nctids-file",
    "-n",
    type=click.Path(exists=True),
    required=True,
    help="Path to a file containing the NCTIDs.",
)
@click.option(
    "--output-json",
    "-o",
    type=click.Path(),
    required=True,
    help="Path to the output json file.",
)
@click.option(
    "--clf-type",
    "-c",
    type=click.Choice(["llm", "dummy"]),
    default="llm",
    help="Type of classifier to use. Options: 'llm', 'dummy'. Default: 'llm'",
)
def main(nctids_file: str, output_json: str, clf_type: str = "llm") -> None:
    """Drug Discoverer. Steps:
    1. Connect to the database and get the list of drug names.
    2. Create a Classifier instance with the drug db as input.
    3. Load the file under --nctids-file and get the NCTIDs.
    4. Use <classifier_obj>.classify to load the bried summaries of each NCTID, classify
       them, convert them to their preferred name, and save the results to a json.
    5. Save the results in json format.
    6. (Not done by this script) Evaluate the results.

    Arguments:
    ----------
    nctids_file : str
        Path to a file containing the NCTIDs.
    output_json : str
        Path to the output json file.
    clf_type: str
        Type of classifier to use. Options: "llm", "dummy". Default: "llm"
    """
    
    db_uri = "postgresql://{DB_USERNAME}:{DB_PWD}@localhost:5432/{DB_NAME}"
    try:
        env_vars = get_env_variables()  # this will throw an error if the env vars are not set.
    except KeyError as ke:
        raise click.ClickException(f"Expected to find the environment variable: {ke}")
    db_uri = db_uri.format(**env_vars)
    logger.info("Initializing DrugDB...")
    drug_db = DrugDB(db_uri)
    if clf_type == "llm":
        raise NotImplementedError("LLM classifier is not implemented yet.")
    elif clf_type == "dummy":
        classifier = DummyClassifier(drug_db)
    else:
        raise ValueError(f"Invalid clf_type: {clf_type}")
    nctids = [line.strip() for line in open(nctids_file, "r").readlines()]
    classifier.classify(nctids, output_json)


if __name__ == "__main__":
    """Run the main function.

    Example:
    --------
    $ python -m drug_discoverer --nctids-file /path/to/nctids.txt --output-json /path/to/output.json
    """
    main(prog_name="drug_discoverer")  # pragma: no cover
