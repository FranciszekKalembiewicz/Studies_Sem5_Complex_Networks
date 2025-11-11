import networkx as nx
import os

# Plik grafu przyciętego z zadania 2
GRAPH_SMALL_GML = "actors_graph_small.gml"


def load_graph(filename=GRAPH_SMALL_GML):
    if os.path.exists(filename):
        G = nx.read_gml(filename)
        # upewnij się, że graf jest nieskierowany
        return G.to_undirected() if G.is_directed() else G
    raise FileNotFoundError(f"Brak pliku {filename}")


def compute_network_properties(G):
    rzad = G.number_of_nodes()
    rozmiar = G.number_of_edges()
    sredni_stopien = 2 * rozmiar / rzad if rzad > 0 else 0
    gestosc = nx.density(G)

    # Największa spójna składowa dla niespójnych grafów
    if nx.is_connected(G):
        Gcc = G
    else:
        largest_cc = max(nx.connected_components(G), key=len)
        Gcc = G.subgraph(largest_cc)

    srednica = nx.diameter(Gcc) if rzad > 1 else 0
    srednia_dl_sciezki = nx.average_shortest_path_length(Gcc) if rzad > 1 else 0
    wspolczynnik_klastrowania = nx.average_clustering(G)

    return {
        "rząd": rzad,
        "rozmiar": rozmiar,
        "średni_stopień": sredni_stopien,
        "gęstość": gestosc,
        "średnica": srednica,
        "średnia_długość_ścieżki": srednia_dl_sciezki,
        "współczynnik_klastrowania": wspolczynnik_klastrowania
    }


def main():
    G = load_graph()
    props = compute_network_properties(G)
    print("Własności sieci:")
    for k, v in props.items():
        if isinstance(v, float):
            print(f"{k}: {v:.4f}")
        else:
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()
