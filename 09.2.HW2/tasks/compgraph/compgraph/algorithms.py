from . import Graph, operations
import typing as tp


def word_count_graph(input_stream_name: str, text_column: str = 'text', count_column: str = 'count',
                     file: bool = False, parser: tp.Callable[[str], operations.TRow] | None = None) -> Graph:
    """Constructs graph which counts words in text_column of all rows passed"""
    read_graph = (
        Graph.graph_from_iter(input_stream_name)
        if not file
        else Graph.graph_from_file(input_stream_name, parser=parser)
    )
    return  read_graph.map(operations.FilterPunctuation(text_column)) \
        .map(operations.LowerCase(text_column)) \
        .map(operations.Split(text_column)) \
        .sort([text_column]) \
        .reduce(operations.Count(count_column), [text_column]) \
        .sort([count_column, text_column])


def inverted_index_graph(input_stream_name: str, doc_column: str = 'doc_id', text_column: str = 'text',
                         result_column: str = 'tf_idf',
                         file: bool = False, parser: tp.Callable[[str], operations.TRow] | None = None) -> Graph:
    """Constructs graph which calculates td-idf for every word/document pair"""
    read_graph = (
        Graph.graph_from_iter(input_stream_name)
        if not file
        else Graph.graph_from_file(input_stream_name, parser=parser)
    )
    graph = read_graph.map(operations.FilterPunctuation(text_column)) \
        .map(operations.LowerCase(text_column)) \
        .map(operations.Split(text_column)) \
        .sort([doc_column])
    graph2 = graph.reduce(operations.TermFrequency(text_column), [doc_column])
    graph3 = graph.map(operations.Project([doc_column, text_column])) \
        .sort([doc_column, text_column]) \
        .reduce(operations.FirstReducer(), [text_column, doc_column])\
        .sort([text_column])\
        .reduce(operations.Count('count_of_docs'),[text_column])
    graph4 =  graph.map(operations.Project([doc_column])) \
        .sort([doc_column]) \
        .reduce(operations.FirstReducer(), [text_column, doc_column])\
        .reduce(operations.Count('docs_at_all'),[]) # todo: поменять на вымышленные
    graph5 = graph2.sort([text_column, doc_column]).join(operations.LeftJoiner(), graph3, [text_column])
    graph6 = graph5.join(operations.InnerJoiner(), graph4, []) \
        .map(operations.Divide("docs_at_all", "count_of_docs")) \
        .map(operations.Log("divide", "idf")) \
        .map(operations.Product(['idf', "tf"], result_column)) \
        .map(operations.Project([doc_column, text_column, result_column]))\
        .sort([text_column, result_column])\
        .reduce(operations.TopN(result_column, 3), [text_column])

    return graph6


def pmi_graph(input_stream_name: str, doc_column: str = 'doc_id', text_column: str = 'text',
              result_column: str = 'pmi',
              file: bool = False, parser: tp.Callable[[str], operations.TRow] | None = None) -> Graph:
    """Constructs graph which gives for every document the top 10 words ranked by pointwise mutual information"""
    def row_filter(row: operations.TRow) -> bool:
        if row["count_of_words"]>= 2 and len(row[text_column]) >= 4:
            return True
        else:
            return False

    read_graph = (
        Graph.graph_from_iter(input_stream_name)
        if not file
        else Graph.graph_from_file(input_stream_name, parser=parser)
    )
    graph0 = read_graph.map(operations.FilterPunctuation(text_column)) \
        .map(operations.LowerCase(text_column)) \
        .map(operations.Split(text_column))

    graph = graph0.sort([doc_column, text_column])\
        .reduce(operations.Count("count_of_words"), [doc_column, text_column]) \
        .map(operations.Filter(row_filter))

    graph1 = graph.sort([doc_column, text_column]) \
        .reduce(operations.Sum("count_of_words"),[doc_column])
    graph2 = graph.sort([doc_column, text_column]) \
        .reduce(operations.Sum("count_of_words"),[text_column])

    graph3 = graph.join(operations.LeftJoiner("_cur","_all_in_line"), graph1, [doc_column])
    graph4 = graph3.join(operations.LeftJoiner(), graph2, [text_column])
    graph5 = graph.reduce(operations.Sum("count_of_words"), [])
    graph6 = graph4.join(operations.LeftJoiner("_in_text", "_total"), graph5,[]) \
        .map(operations.Divide("count_of_words_cur","count_of_words_all_in_line", "res_1" )) \
        .map(operations.Divide("count_of_words_in_text","count_of_words_total", "res_2" )) \
        .map(operations.Divide("res_1","res_2")) \
        .map(operations.Log("divide", result_column))  \
        .map(operations.Project([doc_column, text_column, result_column])) \
        .sort([result_column])  \
        .reduce(operations.TopN(result_column, 10), [])
    graph7 = graph0.reduce(operations.FirstReducer(), [text_column, doc_column]) \
        .map(operations.Enumerate('enum')) \
        .sort([doc_column, text_column]) \
        .reduce(operations.FirstReducer(), [text_column, doc_column])
    graph8 = graph6.sort([doc_column, text_column])\
            .join(operations.LeftJoiner(), graph7, [doc_column, text_column]) \
            .sort(["enum"]) \
            .map(operations.Project([doc_column, text_column, result_column]))

    return graph8
def yandex_maps_graph(input_stream_name_time: str, input_stream_name_length: str,
                      enter_time_column: str = 'enter_time', leave_time_column: str = 'leave_time',
                      edge_id_column: str = 'edge_id', start_coord_column: str = 'start', end_coord_column: str = 'end',
                      weekday_result_column: str = 'weekday', hour_result_column: str = 'hour',
                      speed_result_column: str = 'speed') -> Graph:
    """Constructs graph which measures average speed in km/h depending on the weekday and hour"""
    graph = Graph.graph_from_iter(input_stream_name_time) \
        .map(operations.MakeDateTime(enter_time_column, "date_time_enter")) \
        .map(operations.MakeDateTime(leave_time_column, "date_time_leave"))
    edges = Graph.graph_from_iter(input_stream_name_length)
    graph1 = graph.join(operations.InnerJoiner(), edges, [edge_id_column]) \
        .map(operations.Distance(start_coord_column, end_coord_column, "distance"))\
        .map(operations.Speed("date_time_enter", "date_time_leave" , "distance", "speed_temp")) \
        .map(operations.SplitTimeByWeekAndHour("date_time_enter", hour_result_column, weekday_result_column)) \
        .map(operations.Project([hour_result_column, weekday_result_column, "speed_temp"])) \
        .sort([hour_result_column, weekday_result_column]) \
        .reduce(operations.Medium("speed_temp",speed_result_column), [hour_result_column, weekday_result_column])
    return graph1
