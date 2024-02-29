# Drug Discoverer

[![PyPI](https://img.shields.io/pypi/v/drug_discoverer.svg)][pypi_]
[![Status](https://img.shields.io/pypi/status/drug_discoverer.svg)][status]
[![Python Version](https://img.shields.io/pypi/pyversions/drug_discoverer)][python version]
[![License](https://img.shields.io/pypi/l/drug_discoverer)][license]

[![Read the documentation at https://drug_discoverer.readthedocs.io/](https://img.shields.io/readthedocs/drug_discoverer/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/geoph9/drug_discoverer/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/geoph9/drug_discoverer/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi_]: https://pypi.org/project/drug_discoverer/
[status]: https://pypi.org/project/drug_discoverer/
[python version]: https://pypi.org/project/drug_discoverer
[read the docs]: https://drug_discoverer.readthedocs.io/
[tests]: https://github.com/geoph9/drug_discoverer/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/geoph9/drug_discoverer
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Features

- TODO

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
after being loaded to a pandas dataframe:
```python
>>> import pandas as pd
... from sqlalchemy import create_engine
>>> DATABASE_URI = 'postgresql://<user>:<passwd>@localhost/llmdrugs'
>>> engine = create_engine(DATABASE_URI, echo=True)  # Set echo to True for debugging
>>> query = f"SELECT * FROM public.synonyms;"
... df = pd.read_sql_query(query, engine)
>>> df.head()
   syn_id      id                        name  preferred_name  parent_id                       lname
0   23310  5391.0                 sacituzumab             NaN        NaN                 sacituzumab
1   23311  5391.0       sacituzumab govitecan             1.0        NaN       sacituzumab govitecan
2   23312  5391.0  sacituzumab govitecan-hziy             NaN        NaN  sacituzumab govitecan-hziy
3   23313  5391.0                    trodelvy             NaN        NaN                    trodelvy
4   23314  5391.0                    IMMU-132             NaN        NaN                    immu-132
```

`syn_id` is the primary key of the table, while `id` is the identifier of the drug. For example, `id=5391` is the identifier of the drug `sacituzumab` which also appears under the name `sacituzumab govitecan` and `sacituzumab govitecan-hziy`, among others. The `name` column contains the names of the drugs, while the `lname` column contains the lower case version of the names. The `preferred_name` column is a boolean column that indicates whether the name is the preferred name for the drug. Finally, the `parent_id` column is the identifier of the parent drug, if any.

In our scenario, we will not use the `parent_id` information. Instead we will only use the preferred names of each drug (i.e. the name for which `preferred_name=1`), and the `lname` column. We will use the `lname` column to search for drugs, and the `preferred_name` column to display the preferred name of the drug.

## Installation

You can install _Drug Discoverer_ via poetry. To do so, you first need to clone this repository and 
follow the instructions below:

```bash
git clone <TODO>
cd drug_discoverer
poetry install
```

## Usage

Please see the [Command-line Reference] for details.

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

[license]: https://github.com/geoph9/drug_discoverer/blob/main/LICENSE
[contributor guide]: https://github.com/geoph9/drug_discoverer/blob/main/CONTRIBUTING.md
[command-line reference]: https://drug_discoverer.readthedocs.io/en/latest/usage.html
