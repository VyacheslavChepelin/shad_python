import enum

class Status(enum.Enum):
    NEW = 0
    EXTRACTED = 1
    FINISHED = 2

def dfs(v: str,graph: dict[str, set[str]], visited: dict[str, bool], topologic: list[str] )->None:
    visited[v] = True
    for u in graph[v]:
        if not visited[u]:
            dfs(u, graph, visited, topologic)
    topologic.append(v)

def extract_alphabet(
        graph: dict[str, set[str]]
        ) -> list[str]:
    """
    Extract alphabet from graph
    :param graph: graph with partial order
    :return: alphabet
    """
    used = {key: False for key in graph.keys()}
    top_sort = []
    for v in graph.keys():
        if not used[v]:
           dfs(v, graph, used, top_sort)
    top_sort.reverse()
    return top_sort


def build_graph(
        words: list[str]
        ) -> dict[str, set[str]]:
    """
    Build graph from ordered words. Graph should contain all letters from words
    :param words: ordered words
    :return: graph
    """
    letters = {letter for word in words for letter in word}
    dct = {letter: set() for letter in letters}
    for ind in range(len(words) - 1):
        for char1, char2 in zip(words[ind], words[ind + 1]):
            if char1 != char2:
                dct[char1].add(char2)
                break

    return dct
#########################
# Don't change this code
#########################

def get_alphabet(
        words: list[str]
        ) -> list[str]:
    """
    Extract alphabet from sorted words
    :param words: sorted words
    :return: alphabet
    """
    graph = build_graph(words)
    return extract_alphabet(graph)

#########################
