import datetime
import email.utils as eut
import json
import tempfile
import zipfile
from datetime import timedelta
from pathlib import Path
from typing import Dict

import requests
from prefect import task
from prefect.engine.cache_validators import partial_inputs_only


@task
def poll_modified_date(location: str) -> datetime.datetime:
    """Get the last modified date of a location.

    Arguments:
        location {str} -- Web address for the file.

    Returns:
        datetime.datetime -- Last modified date as returned by the HTTP header.
    """
    r = requests.head(location)
    modified_string = r.headers.get('Last-Modified')
    return datetime.datetime(*eut.parsedate(modified_string)[:6])


@task(cache_for=timedelta(days=365), cache_validator=partial_inputs_only(['last_modified_date']))
def get_and_extract(location: str, last_modified_date: datetime.datetime) -> Dict[str, Dict]:
    temp_file = tempfile.NamedTemporaryFile(delete=True)
    data = requests.get(location)
    temp_file.write(data.content)
    temp_dir = tempfile.TemporaryDirectory()
    with zipfile.ZipFile(temp_file) as zip_ref:
        zip_ref.extractall(temp_dir.name)
    contents = list(Path(temp_dir.name).iterdir())
    output_dict = {}
    for path in contents:
        with open(path) as json_file:
            data = json.load(json_file)
        name = path.with_suffix('').name
        output_dict[name] = data
    return output_dict
