from prefect import Flow, Parameter, task
from prefect_sf_parsing.parsers import parse_candidate, parse_tabulator, parse_ballot, parse_contest, parse_precinct
from prefect_sf_parsing.downloaders import poll_modified_date, get_and_extract
from prefect_sf_parsing.loaders import create_database, wipe_database, load_data
from prefect_sf_parsing.models import Tabulator, Ballot, Mark, Contest, Precinct, Candidate

CVR_LOCATION = "https://www.sfelections.org/results/20191105/data/20191125/CVR_Export_20191125163446.zip"
CACHE_LOCATION = "./cache.pickle"
DB_LOCATION = "sqlite:///parsed_data/votes.sqlite"

with Flow("ETL voter data") as flow:
    cvr_location = Parameter("cvr_location")
    db_conn_string = Parameter("db_conn_string")
    last_modified_date = poll_modified_date(cvr_location)
    extracted = get_and_extract(cvr_location, last_modified_date)

    ballot_dict = parse_ballot(extracted['CvrExport'])
    model_dict = {
        Mark: ballot_dict['Mark'],
        Ballot: ballot_dict['Ballot'],
        Tabulator: parse_tabulator(extracted['TabulatorManifest']),
        Contest: parse_contest(extracted['ContestManifest']),
        Candidate: parse_candidate(extracted['CandidateManifest']),
        Precinct: parse_precinct(extracted['PrecinctPortionManifest'])
    }
    model_tuples = [(db_conn_string, ) + x for x in model_dict.items()]

    db = create_database(db_conn_string)
    db.set_upstream(extracted)

    wipe_database = wipe_database(db_conn_string)
    wipe_database.set_upstream(db)

    initial_data_loaded = load_data.map(model_tuples)
    initial_data_loaded.set_upstream(wipe_database)