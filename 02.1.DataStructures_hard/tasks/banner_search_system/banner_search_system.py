from collections import defaultdict
import heapq

def normalize(
        text: str
        ) -> str:
    """
    Removes punctuation and digits and convert to lower case
    :param text: text to normalize
    :return: normalized query
    """
    answer = ""
    for char in text:
        if char.isalpha() or char.isspace():
            answer += char
    answer = answer.lower()
    return answer


def get_words(
        query: str
        ) -> list[str]:
    """
    Split by words and leave only words with letters greater than 3
    :param query: query to split
    :return: filtered and split query by words
    """
    return [word for word in query.split() if len(word) > 3]

def build_index(
        banners: list[str]
        ) -> dict[str, list[int]]:
    """
    Create index from words to banners ids with preserving order and without repetitions
    :param banners: list of banners for indexation
    :return: mapping from word to banners ids
    """
    dct = defaultdict(list)
    for ind in range(len(banners)):
        tags = get_words(normalize(banners[ind]))
        for word in {tag for tag in tags}:
            dct[word].append(ind)
    return dct


def get_banner_indices_by_query(
        query: str,
        index: dict[str, list[int]]
        ) -> list[int]:
    """
    Extract banners indices from index, if all words from query contains in indexed banner
    :param query: query to find banners
    :param index: index to search banners
    :return: list of indices of suitable banners
    """
    tags = get_words(normalize(query))
    if not tags:
        return []
    lists = []
    for tag in tags:
        lists.append(index[tag])


    heap = []
    pointers = [0] * len(lists)
    for pos in range(len(lists)):
        if len(lists[pos]) != 0:
            heapq.heappush(heap, (lists[pos][0], pos))

    answer = []
    while len(heap) >= len(lists):
        if heapq.nsmallest(1, heap)[0][0] == heapq.nlargest(1, heap)[0][0]:
            answer.append(heapq.heappop(heap)[0])
            while heap:
                heapq.heappop(heap)
            for pos in range(len(lists)):
                pointers[pos] += 1
                if pointers[pos] < len(lists[pos]):
                    ind = pointers[pos]
                    heapq.heappush(heap, (lists[pos][ind], pos))
        else:
            val, pos = heapq.heappop(heap)
            pointers[pos] += 1
            if pointers[pos] < len(lists[pos]):
                ind = pointers[pos]
                heapq.heappush(heap, (lists[pos][ind], pos))
    return answer


#########################
# Don't change this code
#########################

def get_banners(
        query: str,
        index: dict[str, list[int]],
        banners: list[str]
        ) -> list[str]:
    """
    Extract banners matched to queries
    :param query: query to match
    :param index: word-banner_ids index
    :param banners: list of banners
    :return: list of matched banners
    """
    indices = get_banner_indices_by_query(query, index)
    return [banners[i] for i in indices]

#########################
