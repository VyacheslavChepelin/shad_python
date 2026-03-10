# CompGraph

A lightweight computational graph framework for building and executing data processing pipelines with map, reduce, join, and sort operations.

## Getting Started

### Prerequisites

- Python 3.13+

## Quick Example

```python
from compgraph import Graph, operations as ops

# Create a graph that reads from a file
graph = Graph.graph_from_file(
    'data.txt',
    parser=lambda line: {'word': line.strip()}
)

# Build processing pipeline
graph = (graph
    .map(ops.Filter(lambda row: len(row['word']) > 3))
    .reduce(ops.Count(), ['word'])
    .sort(['count'])
)

# Execute the graph
result = graph.run()
for row in result:
    print(row)
```

## Running Tests

```bash
pytest compgraph
```
## Run examples

Usual pyton running code. You can use your favorite Python Interpreter to run code. 

You can find examples in examples folder.

## Built With

- Pure Python (no external dependencies)

## License

"SLAVACHEPELIN IS THE BEST PROGRAMMER NOMINATION" ITMO CT 3239 MIT

# Operations

## Operations with graph

- **`graph_from_iter(name)`** - Create graph from iterator
- **`graph_from_file(filename, parser)`** - Create graph from file
- **`map(mapper)`** - Apply transformation to each row
- **`reduce(reducer, keys)`** - Aggregate data by keys
- **`sort(keys)`** - Sort rows by specified keys
- **`join(joiner, join_graph, keys)`** - Join with another graph
- **`run(**kwargs)`** - Execute the graph with input data

## Mappers
- **DummyMapper** - Yield exactly the row passed
- **FilterPunctuation(column: str)** - Left only non-punctuation symbols in specified column
- **LowerCase(column: str)** - Replace column value with value in lower case
- **Split(column: str, separator: str | None = None)** - Split row on multiple rows by separator
- **Product(columns: Sequence[str], result_column: str = 'product')** - Calculates product of multiple columns
- **Divide(column_1: str, column_2: str, result_column: str = 'divide')** - Calculates division of two columns
- **Log(column: str, result_column: str = 'log')** - Calculates natural logarithm of column
- **Enumerate(result_column: str = 'log')** - Add enumeration (sequential number) to each row
- **MakeDateTime(column: str, result_column: str = 'log')** - Parse string to datetime object
- **SplitTimeByWeekAndHour(start_time: str, hour_result: str, week_result: str)** - Extract hour and week from datetime
- **Distance(start: str, end: str, result: str)** - Calculates distance between two values
- **Speed(start: str, end: str, dist: str, result: str)** - Calculates speed (distance ÷ time difference)
- **Filter(condition: Callable[[TRow], bool])** - Remove records that don't satisfy condition

## Reducers
- **FirstReducer** - Yield only first row from each group
- **TopN(column: str, n: int)** - Calculate top N by value in column
- **TermFrequency(column: str)** - Calculate frequency of values in column
- **Count()** - Count records by key
- **Sum(column: str)** - Sum values aggregated by key
- **Medium(column: str, result_column: str)** - Calculate mean (average) of values aggregated by key

## Joiners
- **InnerJoiner** - Join with inner strategy (only matching keys)
- **OuterJoiner** - Join with outer strategy (all rows, nulls for missing)
- **LeftJoiner** - Join with left strategy (all left rows, matching right)
- **RightJoiner** - Join with right strategy (all right rows, matching left)



