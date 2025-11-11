import os, random
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
from pyvis.network import Network

EDGE_LIST_CSV = "actors_edgelist.csv"
GRAPH_GML = "actors_graph.gml"
OUTPUT_GML_SMALL = "actors_graph_small.gml"
OUTPUT_ADJ_CSV = "actors_adjacency.csv"
OUTPUT_INC_CSV = "actors_incidence.csv"
PYVIS_HTML = "actors_pyvis.html"
N_NODES = 200

def load_graph():
    if os.path.exists(GRAPH_GML):
        G = nx.read_gml(GRAPH_GML)
        return G.to_undirected() if G.is_directed() else G
    if os.path.exists(EDGE_LIST_CSV):
        df = pd.read_csv(EDGE_LIST_CSV)
        cols = [c.lower() for c in df.columns]
        a1 = df.columns[cols.index("actor1")] if "actor1" in cols else df.columns[0]
        a2 = df.columns[cols.index("actor2")] if "actor2" in cols else df.columns[1]
        wcol = None
        if "weight" in cols: wcol = df.columns[cols.index("weight")]
        elif len(df.columns) > 2: wcol = df.columns[2]
        G = nx.Graph()
        if wcol is None:
            for _, r in df.iterrows(): G.add_edge(str(r[a1]), str(r[a2]), weight=1.0)
        else:
            for _, r in df.iterrows(): G.add_edge(str(r[a1]), str(r[a2]), weight=float(r[wcol]))
        return G
    raise FileNotFoundError("Brak actors_graph.gml i actors_edgelist.csv")

def reduce_by_degree(G, n):
    if G.number_of_nodes() <= n: return G.copy()
    nodes_sorted = sorted(G.degree(), key=lambda x: x[1], reverse=True)
    top = [node for node,_ in nodes_sorted[:n]]
    Gs = G.subgraph(top).copy()
    nx.write_gml(Gs, OUTPUT_GML_SMALL)
    print(f"Zapisano {OUTPUT_GML_SMALL}: {Gs.number_of_nodes()} węzłów, {Gs.number_of_edges()} krawędzi")
    return Gs

def save_matrices(G):
    nx.to_pandas_adjacency(G, dtype=int, weight=None).to_csv(OUTPUT_ADJ_CSV)
    inc = nx.incidence_matrix(G, oriented=False).todense()
    pd.DataFrame(inc, index=G.nodes(), columns=[f"{u}-{v}" for u,v in G.edges()]).to_csv(OUTPUT_INC_CSV)
    print(f"Zapisano macierze: {OUTPUT_ADJ_CSV}, {OUTPUT_INC_CSV}")

def viz_nx(G, figsize=(14,10), use_kamada=False):
    plt.figure(figsize=figsize)
    n = G.number_of_nodes()
    # skalowanie parametrów zależnie od rozmiaru grafu
    if n <= 50:
        node_base = 500
        font_size = 10
        k = 0.7
        iterations = 300
    elif n <= 200:
        node_base = 250
        font_size = 8
        k = 0.5
        iterations = 400
    else:
        node_base = 120
        font_size = 6
        k = 0.35
        iterations = 600

    if use_kamada:
        pos = nx.kamada_kawai_layout(G)
    else:
        pos = nx.spring_layout(G, seed=42, k=k, iterations=iterations)

    deg = dict(G.degree())
    node_sizes = [node_base + deg[nn] * (node_base // 2) for nn in G.nodes()]

    weights = nx.get_edge_attributes(G, "weight")
    if weights:
        max_w = max(weights.values())
        widths = [0.6 + 2.0 * (weights.get((u, v), weights.get((v, u), 1.0)) / max_w) for u, v in G.edges()]
    else:
        widths = 0.8

    nx.draw_networkx_edges(G, pos, alpha=0.5, width=widths)
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color="skyblue", edgecolors="k", linewidths=0.3)
    # rysujemy etykiety osobno z tłem bbox, i lekko skalujemy pozycję etykiety od węzła aby nie nachodziły
    labels = {n: str(n) for n in G.nodes()}
    offset_pos = {}
    for n, (x, y) in pos.items():
        offset_pos[n] = (x + 0.01, y + 0.01)  # lekki offset etykiety

    nx.draw_networkx_labels(G, offset_pos, labels, font_size=font_size,
                            bbox=dict(facecolor="white", edgecolor="none", alpha=0.8, boxstyle="round,pad=0.1"))

    plt.title("Wizualizacja grafu (NetworkX)")
    plt.axis("off")
    plt.tight_layout()
    plt.show()


def viz_pyvis(G, height="800px", width="100%", physics=True):
    net = Network(height=height, width=width, directed=False)
    # dodajemy węzły i krawędzie
    for n in G.nodes():
        net.add_node(n, label=str(n), title=f"deg:{G.degree(n)}", value=G.degree(n))
    for u, v, d in G.edges(data=True):
        net.add_edge(u, v, value=d.get("weight", 1.0), title=f"w:{d.get('weight',1.0)}")

    if physics:
        # silniejsze odpychanie i krótsze sprężyny - zwykle rozsuwa węzły
        net.barnes_hut(gravity=-80000, central_gravity=0.01, spring_length=150, spring_strength=0.01, damping=0.09)
        net.set_options("""
        var options = {
          "physics": {
            "enabled": true,
            "barnesHut": {
              "gravitationalConstant": -20000,
              "centralGravity": 0.01,
              "springLength": 150,
              "springConstant": 0.005,
              "damping": 0.09,
              "avoidOverlap": 1
            }
          }
        }
        """)
    else:
        net.toggle_physics(False)

    net.show(PYVIS_HTML)
    print(f"Zapisano interaktywną wizualizację: {PYVIS_HTML}")

def main():
    G = load_graph()
    print(f"Oryginał: {G.number_of_nodes()} węzłów, {G.number_of_edges()} krawędzi")
    G_small = reduce_by_degree(G, N_NODES)
    save_matrices(G_small)
    viz_nx(G_small)
    viz_pyvis(G_small)

if __name__ == "__main__":
    main()
