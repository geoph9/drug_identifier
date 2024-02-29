# Drug Discoverer

[![License](https://img.shields.io/pypi/l/drug_discoverer)][license]

[![Codecov](https://codecov.io/gh/geoph9/drug_discoverer/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[read the docs]: https://drug_discoverer.readthedocs.io/
[tests]: https://github.com/geoph9/drug_identifier/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/geoph9/drug_identifier
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## TL;DR

_Drug Discoverer_ is a Python library for identifying drugs in clinical trial summaries. Example usage from the command line:

```bash
python -m drug_discoverer --nctids-file data/nctids.txt \
                          --output-file data/llm_1shot_predictions.json \
                          --clf-type llm \
                          --llm-template 1shot
```

The above command will read the NCTIDs from the file `data/nctids.txt`, get their brief summaries from clinicaltrials.gov,
and then use ChatGPT (through LangChain) to classify which drugs are mentioned in each summary. The results will be saved
in json format in the file `test_outputs.json`.

## Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Evaluation](#evaluation)
- [Contributing](#contributing)
- [License](#license)
- [Issues](#issues)
- [Credits](#credits)

## Features

- Given a list of NCTIDs, search clinicaltrials.gov to get a list of summaries of the trials.
- Given a list of drugs, search the DrugCentral database to get a list of synonyms for the drugs.
- For each clinical trial summary, identify the drug names that appear in the summary.
- Option 1: Use a dummy classifier to predict whether a drug is mentioned in the summary. This is
  purely for demonstrational purposes and it just searches for words that appear both in the synonyms
  table of the database and in the clinical trial summary.
- Option 2: Use prompt engineering to ask an LLM model to predict whether a drug is mentioned in the
  summary. LangChain is used for this purpose, along with ChatGPT.
- Option 3: Use a purely NLP solution to predict whether a drug is mentioned in the summary. This is done with the help of spaCy's medical NER model.

NOTE: For the LLM prompting case, you need to have a valid openai API key (requires credits).

Evaluating the results of the predictions is impossible since we don't have ground truth labels. However,
due to the small size of the given NCTIDs, we can manually check the results and see if they make sense.

## Requirements

Make sure `psql` exists as a command. If so, then make sure that you have created a new user
with the right permissions to create a database and fill it from a text dump. Then do the following:

```bash
cd /path/to/my/my/dir

# 1. Download postgres dump and unzip
wget https://unmtid-shinyapps.net/download/drugcentral.dump.11012023.sql.gz
gunzip drugcentral.dump.11012023.sql.gz

# 2. Create a PostgreSQL database
sudo -u postgres createdb your_database_name

# 3. Validate that the user '<user>>' has the right privileges
# Replace 'your_database_name' with the actual database name you created
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE your_database_name TO <user>;"

# 4. Load the text dump file 'drugcentral.dump.11012023.sql'
# Replace 'your_database_name' with the actual database name you created
sudo -u <user> psql -d your_database_name -a -f drugcentral.dump.11012023.sql
```

We only care about the `synonyms` table of the `public` schema. Here is a preview of how that looks
after being loaded to a pandas dataframe (for demonstration purposes only; you don't need to install pandas to use this library):

```python
>>> import pandas as pd
... from sqlalchemy import create_engine
>>> DATABASE_URI = 'postgresql://<user>:<passwd>@localhost/llmdrugs'
>>> engine = create_engine(DATABASE_URI, echo=True)  # Set echo to True for debugging
>>> query = f"SELECT * FROM public.synonyms;"
... df = pd.read_sql_query(query, engine)
>>> df.head()
   syn_id      id                        name  preferred_name  parent_id                       lname
0   23310  5391                 sacituzumab             NaN        NaN                 sacituzumab
1   23311  5391       sacituzumab govitecan             1.0        NaN       sacituzumab govitecan
2   23312  5391  sacituzumab govitecan-hziy             NaN        NaN  sacituzumab govitecan-hziy
3   23313  5391                    trodelvy             NaN        NaN                    trodelvy
4   23314  5391                    IMMU-132             NaN        NaN                    immu-132
```

`syn_id` is the primary key of the table, while `id` is the identifier of the drug. For example, `id=5391` is the identifier of the drug `sacituzumab` which also appears under the name `sacituzumab govitecan` and `sacituzumab govitecan-hziy`, among others. The `name` column contains the names of the drugs, while the `lname` column contains the lower case version of the names. The `preferred_name` column is a boolean column that indicates whether the name is the preferred name for the drug. Finally, the `parent_id` column is the identifier of the parent drug, if any.

In our scenario, we will not use the `parent_id` information. Instead we will only use the preferred names of each drug (i.e. the name for which `preferred_name=1`), and the `lname` column. We will use the `lname` column to search for drugs, and the `preferred_name` column to display the preferred name of the drug.

## Installation

You can install _Drug Discoverer_ via poetry. To do so, you first need to clone this repository and
follow the instructions below:

```bash
# [Optional] Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Clone the repository and install the dependencies
git clone git@github.com:geoph9/drug_identifier.git
cd drug_identifier

# [Optional (if planning to use as a library)] Choose the python binary for poetry
# poetry env use ../.venv/bin/python
poetry install
```

### Using SpaCy

You will additionally need to download the medical NER model `en_core_med7_trf` from spaCy. To do so, run the following command:

```bash
poetry run pip install https://huggingface.co/kormilitzin/en_core_med7_trf/resolve/main/en_core_med7_trf-any-py3-none-any.whl
```

This is because the aforementioned model is more than 1GB in size and there is no point in downloading it by default,
since the LLM functionality is the main thing we are interested in.

## Usage

Before using this library, make sure you have a `.env` file containing the following environment variables:

```bash
OPENAI_API_KEY=<your_openai_api_key>
DB_USERNAME=<your_db_username>
DB_PWD=<your_db_password>
DB_NAME=<your_db_name>
```

To see a list of all available options, run:

```bash
> poetry run python -m drug_discoverer --help

Usage: drug_discoverer [OPTIONS]

  Drug Discoverer. Steps: 
    1. Connect to the database and get the list of drug names. 
    2. Create a Classifier instance with the drug db as input.
    3. Load the file under --nctids-file and get the NCTIDs.
    4. Use <classifier_obj>.classify to load the bried summaries of each NCTID,
       classify    them, convert them to their preferred name, and save the results
       to a json.
    5. Save the results in json format.
    6. (Not done by this script) Evaluate the results.

Options:
  --version                       Show the version and exit.
  -n, --nctids-file PATH          Path to a file containing the NCTIDs.
                                  [required]
  -o, --output-json PATH          Path to the output json file.  [required]
  -c, --clf-type [llm|spacy|dummy]
                                  Type of classifier to use. Options: 'llm',
                                  'spacy', 'dummy'. Default: 'llm'
  -k, --keep-unmatched-drugs      Keep the unmatched drugs in the output json.
                                  A drug is considered unmatched if it is not
                                  found in the drug db.
  -t, --llm-template [1shot|0shot|one-shot|zero-shot]
                                  The template to use for the LLM classifier.
                                  Default: 1shot. Options: '1shot', '0shot', 
                                  'one-shot', 'zero-shot'.Only used if
                                  --clf-type is 'llm'
  --help                          Show this message and exit.
```

If you want to keep the information about the drugs found by the LLM that did not have a match in the database,
then you may also pass the `--keep-unmatched-drugs` (or just `-k`) flag. The unmatched drugs will be saved in the
same file as the matched ones and will be under the `"unmatched"` key of each NCTID.

Example output json:

```json
{
  "NCT00000102": {
    "summary": "...",
    "matched": [
      "sacituzumab",
      "trodelvy",
      "immu-132"
    ],
    "unmatched": [
      "SC902",
    ]
  },
  ...
}
```

## Evaluation

The evaluation of the results is not done by this script since there are no ground truth labels for the
given clinical trials. If there were, we could use the F1 score to evaluate the results in a more quantitative way. Instead, the user should manually check the results and see if they make sense. 
The user should also check the unmatched drugs and see if they are actually drugs or model hallucinations.

Currently the data directory contains the following files:
```
data
├── nctids.txt
├── spacy_predictions.json
├── spacy_matchedonly_predictions.json
├── dummy_predictions.json
├── llm_1shot_predictions.json
└── llm_0shot_predictions.json
```

### Purely NLP Solution

The `spacy_predictions.json` file contains the results of the purely NLP solution. The `spacy_matchedonly_predictions.json`
file contains the results of the purely NLP solution, but only for the drugs that were matched in the database. Here is a sample of the former file:

```json
{
  "NCT00037648": {
      "summary": "The purpose of this study is to determine the safety of anakinra in patients with Polyarticular-Course Juvenile Rheumatoid Arthritis, a form of rheumatoid arthritis affecting children.",
      "matched": [
          "anakinra"
      ],
      "unmatched": []
  },
  "NCT00048542": {
      "summary": "This is a multicenter, Phase 3 randomized, placebo-controlled study designed to evaluate adalimumab in children 4 to 17 years old with polyarticular juvenile idiopathic arthritis (JIA) who are either methotrexate (MTX) treated or non-MTX treated.",
      "matched": [
          "adalimumab",
          "methotrexate"
      ],
      "unmatched": [
          "mtx"
      ]
  },
  "NCT00071487": {
      "summary": "The purpose of this study is to evaluate the safety and efficacy of 3 different doses of belimumab, administered in addition to standard therapy, in patients with active SLE disease.",
      "matched": [
          "belimumab"
      ],
      "unmatched": []
  },
  ...
}
```

### LLM Classifier

The `llm_1shot_predictions.json` file contains the results of the LLM classifier using the 1shot template. The `llm_0shot_predictions.json` file contains the results of the LLM classifier using the 0shot template. Here is a sample of the zero-shot predictions:

```json
{
    "NCT00037648": {
        "summary": "The purpose of this study is to determine the safety of anakinra in patients with Polyarticular-Course Juvenile Rheumatoid Arthritis, a form of rheumatoid arthritis affecting children.",
        "matched": [],
        "unmatched": []
    },
    "NCT00048542": {
        "summary": "This is a multicenter, Phase 3 randomized, placebo-controlled study designed to evaluate adalimumab in children 4 to 17 years old with polyarticular juvenile idiopathic arthritis (JIA) who are either methotrexate (MTX) treated or non-MTX treated.",
        "matched": [],
        "unmatched": []
    },
  ...
}
```
 As you can see, there are no matched drugs in the above example and that pattern persists for the whole set of inputs. This is because the 0shot template is not suitable for this kind of data. The 1shot template is more suitable for this kind of data, and it is the one that should be used. Here is a sample of the 1shot predictions:

```json
{
    "NCT00037648": {
        "summary": "The purpose of this study is to determine the safety of anakinra in patients with Polyarticular-Course Juvenile Rheumatoid Arthritis, a form of rheumatoid arthritis affecting children.",
        "matched": [
            "anakinra"
        ],
        "unmatched": []
    },
    "NCT00048542": {
        "summary": "This is a multicenter, Phase 3 randomized, placebo-controlled study designed to evaluate adalimumab in children 4 to 17 years old with polyarticular juvenile idiopathic arthritis (JIA) who are either methotrexate (MTX) treated or non-MTX treated.",
        "matched": [
            "adalimumab",
            "methotrexate"
        ],
        "unmatched": []
    },
    "NCT00071487": {
        "summary": "The purpose of this study is to evaluate the safety and efficacy of 3 different doses of belimumab, administered in addition to standard therapy, in patients with active SLE disease.",
        "matched": [
            "belimumab"
        ],
        "unmatched": []
    },
  ...
}
```

Here, the results are much more accurate. The LLM model is able to predict the drugs mentioned in the summaries with high accuracy. Further tuning the prompt and providing more data to the model will likely improve the results even further.

### Dummy Classifier

The `dummy_predictions.json` file contains the results of the dummy classifier. Here is a sample of the predictions:

```json
{
    "NCT00037648": {
        "summary": "The purpose of this study is to determine the safety of anakinra in patients with Polyarticular-Course Juvenile Rheumatoid Arthritis, a form of rheumatoid arthritis affecting children.",
        "matched": [
            "anakinra"
        ]
    },
    "NCT00048542": {
        "summary": "This is a multicenter, Phase 3 randomized, placebo-controlled study designed to evaluate adalimumab in children 4 to 17 years old with polyarticular juvenile idiopathic arthritis (JIA) who are either methotrexate (MTX) treated or non-MTX treated.",
        "matched": [
            "methotrexate",
            "adalimumab"
        ]
    },
    "NCT00071487": {
        "summary": "The purpose of this study is to evaluate the safety and efficacy of 3 different doses of belimumab, administered in addition to standard therapy, in patients with active SLE disease.",
        "matched": [
            "belimumab"
        ]
    },
  ...
}
```

Considering that the dummy classifier is the baseline, the results are not bad. However, the LLM classifier is more accurate and should be used instead since it is able to generalize better to unseen data. LLMs with big context windows will also be able to accept a list of available drugs and predict whether each one is mentioned in the summary in any form.


## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [MIT license][license],
_Drug Discoverer_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

This project was generated from [@cjolowicz]'s [Hypermodern Python Cookiecutter] template.

[@cjolowicz]: https://github.com/cjolowicz
[pypi]: https://pypi.org/
[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python
[file an issue]: https://github.com/geoph9/drug_discoverer/issues
[pip]: https://pip.pypa.io/

<!-- github-only -->

[license]: https://github.com/geoph9/drug_identifier/blob/master/LICENSE
[contributor guide]: https://github.com/geoph9/drug_identifier/blob/master/CONTRIBUTING.md
[command-line reference]: https://drug_discoverer.readthedocs.io/en/latest/usage.html
