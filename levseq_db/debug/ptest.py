import pandas as pd
import json


# jr = Jrows()
# jr.cols = ["col_1", "col_2"]
# jr.rows = [(3, "a"), (2, "b"), (1, "c"), (0, "d")]
# print(str(jr.__dict__))
# print(jr.toJson())
# exit()

# cols: list[str]
cols = ["col_1", "col_2"]
# rows: list[tuple]
rows = [(3, """a"b"""), (2, "b"), (1, "c"), (0, "d")]

# serialize as json
jrows = json.dumps(rows)
jcols = json.dumps(cols)
print(f"type(jrows)={type(jrows)} jrows={jrows}")
print(f"type(jcols)={type(jcols)} jcols={jcols}")

# build more json
### jpkg = f'{{ "columns": {jcols},\n  "rows": {jrows}\n}}'
jpkg = f'{{ "columns": {jcols},' + "\n" + f'   "rows": {jrows}}}'
print(jpkg)

pkg = json.loads(jpkg)
print(f"type(pkg): {type(pkg)}")
print(pkg)


# deserialize as python
cols = json.loads(jcols)
print(f"type(cols): {type(cols)}  cols: {cols}")
rows = json.loads(jrows)
print(f"type(rows): {type(rows)}  rows: {rows}")


# df = pd.DataFrame.from_records(rows, columns=cols)
df = pd.DataFrame.from_records(pkg["rows"], columns=pkg["columns"])
print(df)


#   col_1 col_2
# 0      3     a
# 1      2     b
# 2      1     c
# 3      0     d
