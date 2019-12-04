import pandas as pd
from prefect import task
from typing import Dict
@task
def parse_candidate(candidate_data_dict: Dict) -> pd.DataFrame:
    """Parse the Candidate data.

    Arguments:
        candidate_data_location {str} -- Location of the downloaded candidate JSON.

    Returns:
        pd.DataFrame -- A DataFrame that fits the Candidate model.
    """
    candidate_mapping = {
        "Description": "name",
        "Id": "id",
        "ExternalId": "external_id",
        "ContestId": "contest_id",
        "Type": "candidate_type",
    }
    candidate_df = pd.DataFrame.from_records(
        pd.DataFrame.from_dict(candidate_data_dict)["List"]
    ).rename(columns=candidate_mapping)
    return candidate_df.to_dict(orient="records")



@task
def parse_precinct(precinct_data_dict: Dict) -> pd.DataFrame:
    """Parse the Precinct data.

    Arguments:
        precinct_data_dict {str} -- Location of the downloaded precinct JSON.

    Returns:
        pd.DataFrame -- A DataFrame that fits the Precinct model.
    """
    precinct_mapping = {
        "Description": "description",
        "Id": "id",
        "ExternalId": "external_id"
    }
    precinct_df = pd.DataFrame.from_records(
        pd.DataFrame.from_dict(precinct_data_dict)["List"]
    ).rename(columns=precinct_mapping)
    return precinct_df.to_dict(orient="records")



@task
def parse_contest(contest_data_dict: str) -> pd.DataFrame:
    """Parse the Contest data.

    Arguments:
        contest_data_dict {str} -- Location of the downloaded contest JSON.

    Returns:
        pd.DataFrame -- A DataFrame that fits the Contest model.
    """
    contest_mapping = {
        "Description": "description",
        "Id": "id",
        "ExternalId": "external_id",
        "VoteFor": "num_positions",
        "NumOfRanks": "num_ranks",
    }
    contest_df = pd.DataFrame.from_records(pd.DataFrame.from_dict(contest_data_dict)[
        "List"]).rename(columns=contest_mapping)
    return contest_df.to_dict(orient="records")


@task
def parse_tabulator(tablulator_data_dict: str) -> pd.DataFrame:
    """Parse the Tabulator data.

    Arguments:
        tabulator_data_dict {str} -- Location of the downloaded tabulator JSON.

    Returns:
        pd.DataFrame -- A DataFrame that fits the Tabulator model.
    """
    tabulator_mapping = {
        "Description": "description",
        "Id": "id",
        "ExternalId": "external_id",
        "ThresholdMin": "threshold_min",
        "ThresholdMax": "threshold_max",
        "WriteThresholdMin": "write_in_threshold_min",
        "WriteThresholdMax": "write_in_threshold_max",
    }
    tabulator_df = pd.DataFrame.from_records(
        pd.DataFrame.from_dict(tablulator_data_dict)["List"]
    ).rename(columns=tabulator_mapping)
    return tabulator_df.to_dict(orient="records")


@task
def parse_ballot(ballot_data_dict: str) -> pd.DataFrame:
    """Parse the Ballot data.

    Arguments:
        ballot_data_dict {str} -- Location of the downloaded ballot JSON.

    Returns:
        pd.DataFrame -- A DataFrame that fits the Ballot model.
    """
    ballot_df_mapping = {
        "TabulatorId": "tabulator_id",
        "BatchId": "batch_id",
        "RecordId": "batch_record_id",
    }
    ballot_df_with_marks = pd.DataFrame.from_records(
        pd.DataFrame.from_dict(ballot_data_dict)["Sessions"]
    )
    ballot_df_with_marks["Contests"] = ballot_df_with_marks["Original"].map(
        lambda x: x["Contests"]
    )
    ballot_df_with_marks["precinct_id"] = ballot_df_with_marks["Original"].map(
        lambda x: x["PrecinctPortionId"])
    ballot_df = ballot_df_with_marks[["TabulatorId", "BatchId", "RecordId", "precinct_id"]].rename(
        columns=ballot_df_mapping
    )
    contest_df = (
        ballot_df_with_marks.explode("Contests")
        .reset_index()
        .assign(contest_id=lambda x: x.Contests[0]["Id"])
    )
    contest_df["Marks"] = contest_df["Contests"].map(lambda x: x["Marks"])
    contest_df["contest_id"] = contest_df["Contests"].map(lambda x: x["Id"])
    contest_df = contest_df.explode("Marks")
    contest_df = contest_df[contest_df["Marks"].map(lambda x: type(x)) == dict]
    contest_df["candidate_id"] = contest_df["Marks"].map(
        lambda x: x["CandidateId"])
    contest_df["rank"] = contest_df["Marks"].map(lambda x: x["Rank"])
    contest_df["is_ambiguous"] = contest_df["Marks"].map(
        lambda x: x["IsAmbiguous"])
    contest_df["is_vote"] = contest_df["Marks"].map(lambda x: x["IsVote"])
    contest_df["party_id"] = (
        contest_df["Marks"].map(lambda x: x.get("PartyId")).astype("Int32")
    )
    mark_df = contest_df.rename(columns=ballot_df_mapping).loc[
        :,
        [
            "tabulator_id",
            "batch_id",
            "batch_record_id",
            "contest_id",
            "candidate_id",
            "party_id",
            "rank",
            "is_ambiguous",
            "is_vote",
        ],
    ]
    mark_df = mark_df[
        -mark_df.duplicated(
            [
                "tabulator_id",
                "batch_id",
                "batch_record_id",
                "candidate_id",
                "contest_id",
                "rank",
            ]
        )
    ]
    return {'Ballot': ballot_df.to_dict(orient="Records"), 'Mark': mark_df.to_dict(orient="Records")}
