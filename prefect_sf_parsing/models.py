from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Float,
    Boolean,
    ForeignKey,
    PickleType,
    ForeignKeyConstraint,
    Enum,
)
from sqlalchemy.orm import relationship, Session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()


class Candidate(Base):
    __tablename__ = "candidate"

    # Id: identifier of the candidate (internal machine id)
    id = Column(Integer, primary_key=True, nullable=False)
    # Description: name of the candidate.
    name = Column(String, nullable=False)
    # ContestId: identifier of the contest this choice belongs to.
    contest_id = Column(String, ForeignKey("contest.id"), nullable=False)
    # Type: candidate type. Regular, Writein, NoPreference , QualifiedWriteIn
    candidate_type = Enum("Regular", "Writein", "NoPreference", "QualifiedWriteIn")

    contest = relationship("Contest", backref="candidates")


class Contest(Base):
    __tablename__ = "contest"

    # Id: identifier of the contest (internal machine id).
    id = Column(Integer, primary_key=True, nullable=False)
    # Description: name of the contest.
    description = Column(String, nullable=False)
    # External Id: external identifier (optional).
    external_id = Column(String, nullable=True)
    # VoteFor: the number of votes allowed/number of positions to be elected.
    num_positions = Column(Integer, nullable=False)
    # NumOfRanks: the number of rankings allowed to be made
    num_ranks = Column(Integer, nullable=False)


class Tabulator(Base):
    __tablename__ = "tabulator"

    # Id: identifier of the tabulator, we will use tabulator number here.
    id = Column(Integer, primary_key=True, nullable=False)
    # Description: name of the tabulator
    description = Column(String, nullable=False)
    # ExternalId: the external string identifier(optional).
    external_id = Column(String, nullable=True)
    # ThresholdMin: minimum threshold for voting box scanned on this tabulator
    threshold_min = Column(Integer, nullable=False)
    # ThresholdMax: maximum threshold for voting box scanned on this tabulator
    threshold_max = Column(Integer, nullable=False)
    # WriteinThresholdMin: minimum threshold for write-in area scanned on this tabulator
    write_in_threshold_min = Column(Integer, nullable=False)
    # WriteinThresholdMax: maximum threshold for write-in area scanned on this tabulator
    write_in_threshold_max = Column(Integer, nullable=False)


class Batch(Base):
    __tablename__ = "batch"

    batch_id = Column(Integer, nullable=False, primary_key=True)
    # TabulatorId: the tabulator id, same as the one used in the manifest
    tabulator_id = Column(
        Integer, ForeignKey("tabulator.id"), nullable=False, primary_key=True
    )


class Precinct(Base):
    __tablename__ = "precinct"
    # Id: identifier of the precinct portion (internal machine id)
    id = Column(Integer, nullable=False, primary_key=True)
    # Description: name of the precinct portion•
    description = Column(String, nullable=False)
    # External Id: external identifier(optional)
    external_id = Column(String, nullable=True)


class Ballot(Base):
    __tablename__ = "ballot"
    __table_args__ = (
        ForeignKeyConstraint(
            ["batch_id", "tabulator_id"],
            ["batch.batch_id", "batch.tabulator_id"],
            onupdate="CASCADE",
            ondelete="SET NULL",
        ),
    )

    # TabulatorId: the tabulator id, same as the one used in the manifest
    tabulator_id = Column(Integer, nullable=False, primary_key=True)
    # BatchId: the batch id, unique for a given tabulator id.
    batch_id = Column(Integer, nullable=False, primary_key=True)
    # RecordId: the CVR id within the batch.
    batch_record_id = Column(Integer, nullable=False, primary_key=True)
    # PrecinctId: The ID of the precinct the ballot is coming from
    precinct_id = Column(Integer, ForeignKey("precinct.id"), nullable=False)


class Mark(Base):
    __tablename__ = "mark"
    __table_args__ = (
        ForeignKeyConstraint(
            ["batch_id", "tabulator_id", "batch_record_id"],
            ["ballot.batch_id", "ballot.tabulator_id", "ballot.batch_record_id"],
            onupdate="CASCADE",
            ondelete="SET NULL",
        ),
    )
    # TabulatorId: the tabulator id, same as the one used in the manifest
    tabulator_id = Column(Integer, nullable=False, primary_key=True)
    # BatchId: the batch id, unique for a given tabulator id.
    batch_id = Column(Integer, nullable=False, primary_key=True)
    # RecordId: the CVR id within the batch.
    batch_record_id = Column(Integer, nullable=False, primary_key=True)
    # CandidateId: indicates the candidate the mark is for
    candidate_id = Column(
        Integer, ForeignKey("candidate.id"), nullable=False, primary_key=True
    )
    # ContestId: indicates the contest the mark is for
    contest_id = Column(
        Integer, ForeignKey("contest.id"), nullable=False, primary_key=True
    )
    # PartyId: indicates party affiliation.
    party_id = Column(Integer, nullable=True)
    # Rank: indicates rank; will be 1 by default, will only contain values higher than 1 if ranked choice voting is used
    rank = Column(Integer, nullable=False, primary_key=True)
    # IsAmbiguous: a Boolean value indicating whether mark is ambiguous.
    is_ambiguous = Column(Boolean, nullable=False)
    # IsVote: a Boolean value indicating whether the mark produced a vote.
    is_vote = Column(Boolean, nullable=False)

    contest = relationship("Contest", backref="marks")
    candidate = relationship("Candidate", backref="marks")
