from compgraph.algorithms import word_count_graph
import json

def main() -> None:
    input_filepath = input("Input file path: ")
    output_filepath = input("Output file path: ")
    graph = word_count_graph(input_stream_name=input_filepath,
            text_column='text', count_column='count', file = True, parser = json.loads)

    result = graph.run()
    # pyrefly: ignore  # no-matching-overload
    with open(output_filepath, "w") as out:
        for row in result:
            print(row, file=out)


if __name__ == "__main__":
    main()
