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
#   suitable for other kinds of data consumers, including Plotly Dash components like
#   DataTable (https://dash.plotly.com/datatable/reference) and HTML elements.

import re
import pydantic
import dbexec
import fsexec
import global_vars as g


# It would be possible to serialize result sets as json in postgres using json_agg(),
#  jsonb_build_object(), and so on, but it's probably more efficient (and certainly
#  much less painful) to let postgres/psycopg deliver python data structures (list,
#  tuple, etc.) and jsonize them here.
#
# FastAPI uses the pydantic BaseModel class to implement json serialization:
class QueryParams(pydantic.BaseModel):
    verb: str
    params: list[dbexec.Scalar]


class QueryResultSet(pydantic.BaseModel):
    columns: list[str]
    rows: list[tuple]


class QueryScalar(pydantic.BaseModel):
    details: dbexec.Scalar


# handy type aliases
type QueryResponse = QueryResultSet | QueryScalar | None


#
# GET requests
#
# Request data from the postgres SQL implementation and from this webservice instance.
#  If this operation succeeds, we must be connected end to end.
#
# FWIW, the FastAPI remote development client does this request by default when it
#  connects to this webservice.
def GetImplementationInfo() -> QueryResponse:

    c, r = dbexec.Query("get_pginfo", [g.ws_id])
    return QueryResultSet(columns=c, rows=r)


#
# POST requests
#
def PostDatabaseQuery(args: QueryParams) -> QueryResponse:

    # extract the verb prefix:
    #  ^     start at the beginning of the string
    #  \w+?  one or more alphanumeric characters, non-greedy capture
    #  _     followed by underscore
    m = re.match(r"^(\w+?)_", args.verb)

    if m != None:

        # dispatch according to the prefix
        match m[1]:
            case "get":
                c, r = dbexec.Query(args.verb, [param for param in args.params])
                return QueryResultSet(columns=c, rows=r)

            case "do" | "save":
                return dbexec.NonQuery(args.verb, [param for param in args.params])

            case "is" | "peek":
                rval = dbexec.QueryScalar(args.verb, [param for param in args.params])
                return QueryScalar(details=rval)

            case "load":
                rval = fsexec.LoadFile(args.params)
                return QueryScalar(details=rval)

            case "unload":
                fsexec.UnloadFile(args.params)
                return None

            case _:
                pass

    # at this point the prefix is invalid
    raise ValueError(f"invalid query '{args.verb}'")
