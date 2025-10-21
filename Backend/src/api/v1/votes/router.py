# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Dict

from fastapi import APIRouter, HTTPException

from src.api.schemas import parties
from src.api.v1.votes.schemas import VoteMatrix, Disagreements
from src.logging import logger

DATA_DIR: Path = Path(__file__).parent.parent.parent.parent.parent / "data"
with open(DATA_DIR / "matrix.json", "r") as f:
    MATRIX_DATA = VoteMatrix.model_validate_json(f.read())

DISAGREEMENTS_CACHE: Dict[str, Disagreements] = {}
for cache_file in (DATA_DIR / "party_disagreements").iterdir():
    if cache_file.suffix != ".json":
        continue
    with open(cache_file, "rb") as f:
        data = f.read()
        for enc in ("utf-8", "latin-1", "cp1252"):
            try:
                text = data.decode(enc)
                break
            except UnicodeDecodeError:
                continue
        DISAGREEMENTS_CACHE[cache_file.stem] = Disagreements.model_validate_json(text)


router = APIRouter()


@router.get("/matrix", response_model=VoteMatrix)
def get_vote_matrix() -> VoteMatrix:
    logger.info("chats - get_vote_matrix")
    return MATRIX_DATA


@router.get("/disagreements", response_model=Disagreements)
def get_disagreements(party_a: str, party_b: str) -> Disagreements:
    logger.info(f"chats - get_disagreements ({party_a}, {party_b})")
    try:
        party_a = parties[list(map(lambda s: s.lower(), parties)).index(party_a.lower())]
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid party name: {party_a}")
    try:
        party_b = parties[list(map(lambda s: s.lower(), parties)).index(party_b.lower())]
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid party name: {party_b}")

    party_a, party_b = tuple(sorted([party_a, party_b]))

    cache_key = f"disagreements_{party_a}_{party_b}"
    if cache_key not in DISAGREEMENTS_CACHE:
        raise HTTPException(
            status_code=404,
            detail=f"No disagreements found for party pair {party_a} and {party_b}",
        )

    return DISAGREEMENTS_CACHE[cache_key]
