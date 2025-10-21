# -*- coding: utf-8 -*-
import json
import traceback
from pathlib import Path
from typing import List, Union, Optional
from urllib.parse import urlparse, parse_qs

import asyncio

import aiohttp
import pandas
from bs4 import BeautifulSoup
from bs4.element import Tag
from pydantic import BaseModel
from tqdm.asyncio import tqdm
from io import StringIO

from src.config import settings

BASE_URL = "https://www.tweedekamer.nl/kamerstukken/moties"

def motions_page(page: int) -> str:
    return f"{BASE_URL}?fld_prl_kamerstuk=Moties&fld_tk_categorie=Kamerstukken&fromdate=22/11/2023&qry=*&srt=date%3Adesc%3Adate&sta=1&todate=29/10/2025&page={page}"


class ParliamentMotionLocator(BaseModel):
    id: str
    did: str
    url: str


class PartyVote(BaseModel):
    party: str
    seats: int
    vote: str


class ParliamentMotion(BaseModel):
    id: str
    did: str
    url: str
    title: str
    votes: List[PartyVote]


class NoTableFound(Exception):
    pass


async def fetch(session, url):
    async with session.get(url, headers={"User-Agent": settings.USER_AGENT}) as response:
        response.raise_for_status()
        return await response.text()


class ParliamentMotionDataset(BaseModel):
    motions: List[Union[ParliamentMotionLocator, ParliamentMotion]]


def parse_card_as_motion_locator(card: Tag) -> ParliamentMotionLocator:
    """
    This function parses a card element from the parliament website and returns a ParliamentMotionLocator object.
    """
    motion_locator = card.find("a", class_="h-link-inverse")
    motion_url = f"{BASE_URL}{motion_locator['href']}".replace("/kamerstukken/moties/kamerstukken/moties", "/kamerstukken/moties")
    params = parse_qs(urlparse(motion_url).query)

    return ParliamentMotionLocator(
        id=params.get("id", [""])[0],
        did=params.get("did", [""])[0],
        url=motion_url
    )


async def scrape_for_motions(session: aiohttp.ClientSession, url: str) -> ParliamentMotionDataset:
    """
    This function scrapes the parliament website and creates a dataset needed for the application.
    """
    html_content = await fetch(session, url)
    soup = BeautifulSoup(html_content, "html.parser")

    card_elements = soup.find_all("div", class_="m-card")
    motions = [parse_card_as_motion_locator(card) for card in card_elements]

    return ParliamentMotionDataset(motions=motions)


async def fill_motion(session, motion: ParliamentMotionLocator) -> ParliamentMotion:
    """
    This function fills a motion with the votes and title of the motion.
    """
    html_content = await fetch(session, motion.url)
    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table")
    if table is None:
        raise NoTableFound()
    df = pandas.read_html(StringIO(str(table)))[0]

    columns = ["Fracties", "Zetels", "Voor/Tegen"]
    df = df[columns]

    def safe_mode(x):
        # This function is how you know I made this without AI: AI could never write code as awful as this.
        if len(x.mode()) > 0:
            result = x.mode().iloc[0]
        else:
            result = x.iloc[0]
        if isinstance(result, float):
            return ""
        elif result:
            return result
        else:
            return ""

    # Group by party and aggregate
    grouped_df = df.groupby('Fracties').agg({
        'Zetels': 'sum',
        'Voor/Tegen': safe_mode,
    }).reset_index()

    votes: List[PartyVote] = []

    for _, row in grouped_df.iterrows():
        votes.append(PartyVote(
            party=row['Fracties'],
            seats=int(row['Zetels']),
            vote=row['Voor/Tegen']
        ))

    return ParliamentMotion(
        id=motion.id,
        did=motion.did,
        url=motion.url,
        title=soup.find("h1").get_text(),
        votes=votes,
    )


async def try_fill_motion(session, motion: ParliamentMotionLocator) -> Optional[ParliamentMotion]:
    if not isinstance(motion, ParliamentMotionLocator):
        return None
    try:
        return await fill_motion(session, motion)
    except NoTableFound:
        return None
    except Exception:
        print(f"Error filling motion {motion.id} ({motion.url})")
        traceback.print_exc()
        return None


async def main() -> ParliamentMotionDataset:
    """
    This command scrapes the parliament website and creates a dataset needed for the application.
    """
    async with aiohttp.ClientSession() as session:
        dataset_file = Path(__file__).parent.parent / "data/dataset.json"
        if dataset_file.exists():
            dataset = ParliamentMotionDataset.model_validate_json(dataset_file.read_text())
        else:
            coroutines = [scrape_for_motions(session, motions_page(page)) for page in range(334)]
            datasets = await tqdm.gather(*coroutines, desc="Scraping pages for motions")
            motions = []
            for d in datasets:
                motions += d.motions
            dataset = ParliamentMotionDataset(motions=motions)
            with open(dataset_file, "w") as file:
                json.dump(dataset.model_dump(), file)

        coroutines = [try_fill_motion(session, motion) for motion in dataset.motions]
        results: List[Optional[ParliamentMotion]] = await tqdm.gather(*coroutines)

        successes = 0
        for k, result in enumerate(results):
            if result is not None:
                successes += 1
                dataset.motions[k] = result

        print(f"Success: {successes}/{len(results)} ({successes / len(results) * 100:.1f}%)")

        with open(dataset_file, "w") as file:
            json.dump(dataset.model_dump(), file)

    return dataset


if __name__ == "__main__":
    asyncio.run(main())
