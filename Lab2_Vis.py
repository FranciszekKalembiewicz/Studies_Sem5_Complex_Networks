import networkx as nx
import random
import matplotlib.pyplot as plt
from pyvis.network import Network
import pandas as pd

# wczytanie z pliku graphml
# G = nx.read_graphml("lotniska_male.graphml")

# wczytanie z incydencji
A = pd.read_csv("lotniska_male_macierz_sasiedstwa.csv", index_col=0)

G = nx.from_pandas_adjacency(A)

print(f"Oryginalny graf: {G.number_of_nodes()} węzłów, {G.number_of_edges()} krawędzi")


# zapsiuje mniejszy graf z wiekoszego
def zmniejszenie_grafu(G, n_nodes):
    nodes_list = list(G.nodes())

    if len(nodes_list) >= n_nodes:
        nodes_sample = random.sample(nodes_list, n_nodes)
    else:
        nodes_sample = nodes_list  #

    G_small = G.subgraph(nodes_sample).copy()

    print(f"Nowy graf: {G_small.number_of_nodes()} węzłów, {G_small.number_of_edges()} krawędzi")

    nx.write_graphml(G_small, "lotniska_male.graphml")


# tworze macierze

def macierze_tworzenie(G):
    macierz_sasiedstwa = nx.to_pandas_adjacency(G, dtype=int)
    macierz_sasiedstwa.to_csv("lotniska_male_macierz_sasiedstwa.csv")

    macierz_incydencji = nx.incidence_matrix(G, oriented=False).todense()
    edges = [f"{u}-{v}" for u, v in G.edges()]
    macierz_incydencji_df = pd.DataFrame(macierz_incydencji, index=G.nodes(), columns=edges)
    macierz_incydencji_df.to_csv("lotniska_male_macierz_incydencji.csv")


# vizualizacje
def viz_nx(G):
    plt.figure(figsize=(10, 8))

    pos = nx.spring_layout(G, seed=42, k=5)

    nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=800,
        node_color="skyblue",
        edge_color="gray",
        width=1.2,
        font_size=10,
        font_color="black",
        alpha=0.9,
    )

    plt.title("Wizualizacja grafu (ładny układ)", fontsize=14)
    plt.axis("off")
    plt.show()


def viz_pyvis(G):
    net = Network(
        height="800px",
        width="100%",
        bgcolor="#ffffff",
        font_color="black",
        directed=True
    )

    for node in G.nodes():
        net.add_node(node)

    for u, v in G.edges():
        net.add_edge(u, v, color="gray")

    net.toggle_physics(True)

    net.write_html("podgraf.html", open_browser=True)


viz_nx(G)