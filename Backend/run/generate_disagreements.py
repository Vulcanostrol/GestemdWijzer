import asyncio
import itertools
from pathlib import Path
from time import sleep
from typing import Tuple

import pandas as pd
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai.chat_models import ChatOpenAI
from tqdm.asyncio import tqdm
from openai import RateLimitError

from src.api.schemas import parties
from src.api.v1.votes.schemas import PartyPairDisagreements, Disagreements, PartyPairDisagreementsData

load_dotenv(".env.local")

DATA_DIR: Path = Path(__file__).parent.parent / "data"


async def get_disagreements(pair: Tuple[str, str]) -> PartyPairDisagreements:
    party_a, party_b = tuple(sorted(pair))  # Guarantee alphabetic order

    cache_file = DATA_DIR / f"party_disagreements/disagreements_{party_a}_{party_b}.json"
    if cache_file.exists():
        with open(cache_file, "r") as f:
            return PartyPairDisagreements(
                party_a=party_a,
                party_b=party_b,
                disagreements=Disagreements.model_validate_json(f.read()),
            )

    df = pd.read_json(DATA_DIR / "votes.json")
    df = df[["title", party_a, party_b]]
    df = df[df[party_a] != df[party_b]]

    titles_list_str = "\n".join("- " + df["title"].str.strip())

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Jouw taak is om de lijst van Tweede Kamer moties te lezen en te categoriseren in vijf categorieën.\n"
         "De lijst van moties is een lijst van moties waar twee partijen van mening verschillen. Dit is dus al een gefilterde lijst.\n"
         "De categorieën die jij maakt geeft inzicht in de onderwerpen waar de twee partijen van mening verschillen. De gebruiker is alleen geïnteresseerd in de vijf belangrijkste categorieën.\n"
         "De partijen zijn: {party_a} en {party_b}\n"
         "\n"
         "Schrijf de explanation een beetje in de vorm: 'X en Y verschillen op het gebied van ... vooral op ...'"),
        ("user", "{motion_titles}")
    ])
    llm = ChatOpenAI(model="gpt-4o", temperature=0).with_structured_output(Disagreements)
    chain = prompt | llm
    retries = 3
    while retries > 0:
        try:
            result: Disagreements = await chain.ainvoke(dict(motion_titles=titles_list_str, party_a=party_a, party_b=party_b))
            with open(cache_file, "w") as f:
                f.write(result.model_dump_json())
            return PartyPairDisagreements(
                party_a=party_a,
                party_b=party_b,
                disagreements=result,
            )
        except RateLimitError:
            print(f"Rate limit exceeded, retrying in 10 seconds (retries left: {retries})")
            retries -= 1
            sleep(10)
    raise Exception("Failed to get disagreements")


async def main() -> PartyPairDisagreementsData:
    party_pairs = list(itertools.combinations(parties, 2))

    disagreements: PartyPairDisagreementsData = PartyPairDisagreementsData(data=[])
    coroutines = [get_disagreements(pair) for pair in party_pairs]
    results = await tqdm.gather(*coroutines, desc="Generating disagreements")
    for party_pair_disagreements in results:
        disagreements.data.append(party_pair_disagreements)

    with open(DATA_DIR / "disagreements.json", "w") as f:
        f.write(disagreements.model_dump_json())

    return disagreements


if __name__ == "__main__":
    asyncio.run(main())
