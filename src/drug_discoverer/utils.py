import os
from math import log
from pathlib import Path
from typing import Dict
from typing import List
from typing import Union

import requests
from dotenv import load_dotenv
from loguru import logger
from tqdm import tqdm


current_dir = os.path.dirname(os.path.abspath(__file__))


def get_logger_file(log_filename: str) -> str:
    logfile = Path(current_dir).parent.parent / "logs"
    logfile.mkdir(exist_ok=True)
    logfile = logfile / f"{log_filename}.log"
    logfile.touch(exist_ok=True)
    return str(logfile)


logger.remove(0)
logger.add(
    get_logger_file(__name__),
    level="DEBUG",
    colorize=False,
    backtrace=True,
    diagnose=True,
)


def get_clinical_trials_summaries(nctids: Union[str, List[str]]) -> Dict[str, str]:
    """Get the brief summaries of clinical trials from clinicaltrials.gov for the given NCTIDs.

    Arguments:
    ----------
    nctids : Union[str, List[str]]
        Either a string representing the path to a file containing NCTIDs or a list of NCTIDs.

    Returns:
    --------
    Dict[str, str]
        A dictionary where the keys are the NCTIDs and the values are the brief summaries of the clinical trials.
    """
    if isinstance(nctids, str):
        assert os.path.isfile(
            nctids
        ), f"Expected to find a file containing list of NCTIDs under: {nctids}"
        with open(nctids) as f:
            nctids = f.readlines()

    base_url = "https://clinicaltrials.gov/api/v2/studies?query.term=AREA[NCTId]{NCTId}&fields=BriefSummary"
    summaries = {}
    for nctid in tqdm(nctids, desc="Getting summaries from clinicaltrials.gov"):
        nctid = nctid.strip()
        url = base_url.format(NCTId=nctid)
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()["studies"]
        logger.debug(f"For NCTID: {nctid}, found:\n\t{data}")
        assert len(data) == 1, f"Expected to find 1 study for NCTID: {nctid}"
        summaries[nctid] = data[0]["protocolSection"]["descriptionModule"][
            "briefSummary"
        ]
    return summaries


def get_env_variables() -> Dict[str, str]:
    """Get the environment variables."""
    load_dotenv()
    return {
        "DB_USERNAME": os.environ["DB_USERNAME"],
        "DB_PWD": os.environ["DB_PWD"],
        "DB_NAME": os.environ["DB_NAME"],
    }
