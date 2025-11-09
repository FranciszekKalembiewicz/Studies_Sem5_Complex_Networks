import networkx as nx

G = nx.read_graphml("lotniska_male.graphml")
rzad = G.number_of_nodes()
rozmiar = G.number_of_edges()
sredni_stopien = 2 * rozmiar / rzad
gestosc = nx.density(G)

# Użyj grafu nieskierowanego
G_undirected = G.to_undirected()
#tylko jesli spojny
if nx.is_connected(G_undirected):
    srednica = nx.diameter(G_undirected)
    srednia_dl_sciezki = nx.average_shortest_path_length(G_undirected)
else:
    largest_cc = max(nx.connected_components(G_undirected), key=len)
    Gcc = G_undirected.subgraph(largest_cc)
    srednica = nx.diameter(Gcc)
    srednia_dl_sciezki = nx.average_shortest_path_length(Gcc)

print(f"Rząd (liczba węzłów): {rzad}")
print(f"Rozmiar (liczba krawędzi): {rozmiar}")
print(f"Średni stopień ⟨k⟩ = {sredni_stopien:.2f}")
print(f"Gęstość grafu: {gestosc:.4f}")
print(f"Średnica grafu: {srednica}")
print(f"Średnia długość ścieżki: {srednia_dl_sciezki:.4f}")