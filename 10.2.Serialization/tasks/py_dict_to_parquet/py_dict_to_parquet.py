from collections import defaultdict

import pyarrow as pa
import pyarrow.parquet as pq


ValueType = int | list[int] | str | dict[str, str]




def save_rows_to_parquet(rows: list[dict[str, ValueType]], output_filepath: str) -> None:
    """
    Save rows to parquet file.

    :param rows: list of rows containing data.
    :param output_filepath: local filepath for the resulting parquet file.
    :return: None.
    """
    keys = set(key for row in rows for key in row.keys())
    types = dict()
    values = defaultdict(list)
    is_required = defaultdict(lambda: True)
    for row in rows:
        for key in keys:
            if key not in row.keys():
                is_required[key] = False
                values[key].append(None)
            else:
                values[key].append(row[key])
                temp_type = pa.string()
                match type(row[key]).__name__:
                    case "int":
                        temp_type = pa.int64()
                    case "list":
                        temp_type = pa.list_(pa.int64())
                    case "dict":
                        temp_type = pa.map_(pa.string(), pa.string())
                    case "str":
                        temp_type = pa.string()
                if key in types.keys():
                    if types[key] != temp_type:
                        raise TypeError(f"Field {key} has different types")
                types[key] = temp_type

    order_list = []
    for row in rows:
        for key in row.keys():
            if key not in order_list:
                order_list.append(key)

    schema = pa.schema([pa.field(key, types[key], nullable = not is_required[key] ) for key in order_list])
    table = pa.Table.from_arrays([values[key] for key in order_list], schema=schema)
    pq.write_table(table, output_filepath)


