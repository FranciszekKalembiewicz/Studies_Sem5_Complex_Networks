import pandas as pd
import itertools
from collections import Counter
import networkx as nx

INPUT = "imdb_top_1000.csv"
OUT_EDGELIST = "actors_edgelist.csv"
OUT_GML = "actors_graph.gml"

STAR_COLS = ["Star1", "Star2", "Star3", "Star4"]
USECOLS = ["Series_Title"] + STAR_COLS

def build_actor_pairs(df):
    pair_weights = Counter()
    for _, row in df.iterrows():
        actors = []
        for c in STAR_COLS:
            if c in row and not pd.isna(row[c]):
                name = str(row[c]).strip()
                if name:
                    actors.append(name)

        actors = list(dict.fromkeys(actors))
        for a, b in itertools.combinations(sorted(actors), 2):
            pair_weights[(a, b)] += 1
    return pair_weights

def main():
    df = pd.read_csv(INPUT, usecols=USECOLS, encoding='utf-8')
    pair_weights = build_actor_pairs(df)

    with open(OUT_EDGELIST, "w", encoding="utf-8") as f:
        f.write("actor1,actor2,weight\n")
        for (a, b), w in pair_weights.items():
            f.write(f"\"{a}\",\"{b}\",{w}\n")

    G = nx.Graph()
    for (a, b), w in pair_weights.items():
        G.add_edge(a, b, weight=w)

    nx.write_gml(G, OUT_GML)

if __name__ == "__main__":
    main()