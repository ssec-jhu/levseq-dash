#
# wsexec.py
#
# Notes:
#  This webservice returns three differently-formatted responses, depending on the kind
#   of query:
#
#    query type    verb           response
#    NonQuery      do_*           (none)
#    QueryScalar   is_* | peek_*  scalar
#    Query         get_*          column names (list[str]), rows (list[tuple])
#
#  For Query requests, the remote consumer of rowsets returned through this webservice
#   is intended to be a pandas DataFrame, which has a simple initializer:
#
#       rows = [(3, 'a'), (2, 'b'), (1, 'c'), (0, 'd')]
#       cols = ['col_1', 'col_2']
#       df = pandas.DataFrame.from_records( rows, columns=cols )
#       print( df )
#
#               col_1 col_2
#            0      3     a
#            1      2     b
#            2      1     c
#            3      0     d
#
#   (https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.from_records.html)
#
#  The same rowset tuple (column names, rows) can be zipped into python Dict instances
#   suitable for other kinds of data consumers, including Plotly Dash components (e.g.,
#   DataTable) and HTML elements.

import typing
import re
import pydantic
import dbexec
import globals as g


# It would be possible to implement the jsonization of result sets in postgres using json_agg,
#  jsonb_build_object, and so on, but it's probably more efficient (and certainly much less
#  painful) to refrain from serializing result sets as json except to ship them from this
#  webservice to a remote client.
#
# FastAPI uses the pydantic BaseModel class to implement json serialization:
class ResultSet(pydantic.BaseModel):
    columns: list[str]
    rows: list[tuple]


#
# GET requests
#
# Request data from the postgres SQL implementation and from this webservice instance.
#  If this operation succeeds, we must be connected end to end.
#
# FWIW, the FastAPI remote development client does this request at initialization.
def GetImplementationInfo() -> ResultSet:
    c, r = dbexec.Query("get_pgid", [g.ID])
    return ResultSet(columns=c, rows=r)


#
# POST requests
#
# The verb prefix determines the way the database query executes.

# TODO: tighten up the type annotation


def PostDatabaseQuery(verb: str, *args) -> typing.Any:
    prefix = re.match(r"^\w+", verb)
    match prefix:
        case "get":
            c, r = dbexec.Query(verb, [arg for arg in args])
            return ResultSet(columns=c, rows=r)

        case "do":
            return "Tuesday"

        case "is" | "peek":
            return "Wednesday"

        case _:
            return "Invalid day number"  # TODO: HOW TO THROW THIS ERROR
