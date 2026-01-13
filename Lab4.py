import pandas as pd
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from networkx.algorithms.bipartite.matrix import biadjacency_matrix
from networkx.algorithms import bipartite

INPUT = "imdb_top_1000.csv"

df = pd.read_csv(INPUT)
actors_cols = ["Star1", "Star2", "Star3", "Star4"]

edges = []
for _, row in df.iterrows():
    film = row["Series_Title"]
    for col in actors_cols:
        actor = row[col]
        if pd.notna(actor):
            edges.append((actor, film))

edges_df = pd.DataFrame(edges, columns=["actor", "film"])

top_n_actors = 10
actor_counts = edges_df['actor'].value_counts()
top_actors = actor_counts.head(top_n_actors).index.tolist()

edges_df = edges_df[edges_df['actor'].isin(top_actors)].copy()
edges_df.to_csv("Lab4_edge_list.csv", index=False)

films = edges_df['film'].unique().tolist()

B = nx.Graph()
B.add_nodes_from(top_actors, bipartite="actors")
B.add_nodes_from(films, bipartite="films")
B.add_edges_from(edges_df.itertuples(index=False, name=None))

A = biadjacency_matrix(B, row_order=top_actors, column_order=films)
A_df = pd.DataFrame(A.toarray(), index=top_actors, columns=films)
A_df.to_csv("Lab4_biadjacency_matrix.csv")

adj_df = pd.DataFrame(nx.to_numpy_array(B, nodelist=B.nodes()), index=B.nodes(), columns=B.nodes())
adj_df.to_csv("Lab4_adjacency_matrix.csv")
nx.to_numpy_array(B, nodelist=B.nodes())

pos = {}

for i, a in enumerate(top_actors):
    pos[a] = (0, i)

for j, f in enumerate(films):
    pos[f] = (1, j)

color_map = ['skyblue' if n in top_actors else 'salmon' for n in B.nodes()]

plt.figure(figsize=(12, 14))
nx.draw(B, pos, with_labels=False, node_size=50, node_color=color_map, width=0.5, alpha=0.9)
plt.title(f"Graf dwudzielny: Top {top_n_actors} aktorów i ich filmy", fontsize=16)
plt.axis("off")
plt.show()

plt.figure(figsize=(14, 10))
pos2 = nx.bipartite_layout(B, top_actors)

nx.draw(
    B,
    pos2,
    with_labels=False,
    node_size=60,
    node_color=color_map,
    width=0.4,
    alpha=0.9
)

plt.title(f"Graf dwudzielny (layout bipartite): Top {top_n_actors} aktorów i ich filmy", fontsize=16)
plt.axis("off")
plt.tight_layout()
plt.show()

plt.figure(figsize=(10, 6))
plt.imshow(A.toarray(), aspect='auto', interpolation='nearest')
plt.colorbar(label='1 = występ')
plt.yticks(ticks=np.arange(len(top_actors)), labels=top_actors, fontsize=8)
plt.xticks(ticks=np.arange(len(films)), labels=films, fontsize=8, rotation=90)
plt.title(f"Heatmapa macierzy dwudzielnej (Top {len(top_actors)} aktorów × {len(films)} filmów)")
plt.tight_layout()
plt.show()