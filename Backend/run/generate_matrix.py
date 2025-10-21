from pathlib import Path

import pandas as pd

from src.api.schemas import parties
from src.api.v1.votes.schemas import VoteMatrix

DATA_DIR: Path = Path(__file__).parent.parent / "data"


def calculate_similarity(party1_votes, party2_votes):
    valid_mask = ~(party1_votes.isna() | party2_votes.isna())
    if valid_mask.sum() == 0:
        return 0.0
    agreements = (party1_votes[valid_mask] == party2_votes[valid_mask]).sum()
    total_comparisons = valid_mask.sum()
    return (agreements / total_comparisons) * 100


def main() -> VoteMatrix:
    df = pd.read_json('data/dataset.json')
    df = pd.json_normalize(df['motions']).set_index('id')
    df['title'] = df['title'].str.replace('\nMotie\n:\n', '')
    df['title'] = df['title'].str.replace('\nMotie (gewijzigd/nader)\n:\n', '')
    df = df.dropna()

    df = df.explode('votes')
    vote_data = pd.json_normalize(df['votes'])
    df = pd.concat([df[['did', 'url', 'title']].reset_index(), vote_data], axis=1)
    df = df.pivot_table(
        index=['id', 'did', 'url', 'title'],
        columns='party',
        values='vote',
        aggfunc='first'
    ).reset_index()
    df.columns.name = None
    df = df.set_index('id')

    df.to_json("data/votes.json")
    df = df[parties]

    similarity_matrix = pd.DataFrame(index=parties, columns=parties, dtype=float)

    for party1 in parties:
        for party2 in parties:
            if party1 == party2:
                similarity_matrix.loc[party1, party2] = 100.0
            else:
                similarity = calculate_similarity(df[party1], df[party2])
                similarity_matrix.loc[party1, party2] = similarity

    similarity_matrix = similarity_matrix.round(1)

    similarity_matrix.to_json("data/matrix.json")
    return VoteMatrix.model_validate(similarity_matrix.to_dict())


if __name__ == "__main__":
    main()
