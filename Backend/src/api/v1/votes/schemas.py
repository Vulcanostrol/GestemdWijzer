# -*- coding: utf-8 -*-
from typing import List

from pydantic import BaseModel, Field


class PartyVoteMapping(BaseModel):
    DENK: float
    PvdD: float
    SP: float
    GroenLinks_PvdA: float = Field(alias="GroenLinks-PvdA")
    Volt: float
    D66: float
    ChristenUnie: float
    NSC: float
    CDA: float
    SGP: float
    VVD: float
    BBB: float
    JA21: float
    PVV: float
    FVD: float


class VoteMatrix(BaseModel):
    DENK: PartyVoteMapping
    PvdD: PartyVoteMapping
    SP: PartyVoteMapping
    GroenLinks_PvdA: PartyVoteMapping = Field(alias="GroenLinks-PvdA")
    Volt: PartyVoteMapping
    D66: PartyVoteMapping
    ChristenUnie: PartyVoteMapping
    NSC: PartyVoteMapping
    CDA: PartyVoteMapping
    SGP: PartyVoteMapping
    VVD: PartyVoteMapping
    BBB: PartyVoteMapping
    JA21: PartyVoteMapping
    PVV: PartyVoteMapping
    FVD: PartyVoteMapping


class Disagreement(BaseModel):
    subject: str = Field(description="Het onderwerp waarin de partijen verschillen zijn.")
    explanation: str = Field(description="Een korte uitleg met een toelichting wat voor soort moties er verschillend wordt gestemd.")


class Disagreements(BaseModel):
    subjects: List[Disagreement] = Field(description="De lijst van onderwerpen.")


class PartyPairDisagreements(BaseModel):
    party_a: str
    party_b: str
    disagreements: Disagreements


class PartyPairDisagreementsData(BaseModel):
    data: List[PartyPairDisagreements]
