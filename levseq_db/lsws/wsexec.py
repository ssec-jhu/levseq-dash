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
import fastapi
import pydantic
import dbexec
import globals as g

import psycopg  ### TODO: MOVE THIS TO dbexec.py


# It would be possible to serialize result sets as json in postgres using json_agg(),
#  jsonb_build_object(), and so on, but it's probably more efficient (and certainly
#  much less painful) to jsonize them only to ship them from this webservice to a
#  remote client.
#
# FastAPI uses the pydantic BaseModel class to implement json serialization:
class QueryRowset(pydantic.BaseModel):
    columns: list[str]
    rows: list[tuple]


class QueryScalar(pydantic.BaseModel):
    result: dbexec.Scalar


class QueryParams(pydantic.BaseModel):
    verb: str
    params: list[dbexec.Scalar]


# handy type aliases
type QueryResponse = QueryRowset | QueryScalar | None


#
# GET requests
#
# Request data from the postgres SQL implementation and from this webservice instance.
#  If this operation succeeds, we must be connected end to end.
#
# FWIW, the FastAPI remote development client does this request at initialization.
def GetImplementationInfo() -> QueryResponse:
    c, r = dbexec.Query("get_pgid", [g.ID])
    return QueryRowset(columns=c, rows=r)


#
# POST requests
#
# The verb prefix determines the way the database query executes.
def _invalidVerbException(verb: str) -> None:
    raise fastapi.HTTPException(status_code=404, detail=f"invalid query '{verb}'")


# Reflect the postgres exception message
def _postgresException(msg: str) -> None:
    raise fastapi.HTTPException(status_code=422, detail=msg)


## TODO: HANDLE "BAD REQUEST" ERRORS FROM POSTGRES
def PostDatabaseQuery(args: QueryParams) -> QueryResponse:

    # extract the verb prefix:
    #  \w+?  one or more alphanumeric characters, non-greedy capture
    #  _     followed by underscore
    m = re.match(r"^(\w+?)_", args.verb)
    if m == None:
        return _invalidVerbException(args.verb)

    try:
        # dispatch according to the prefix
        match m[1]:
            case "get":
                c, r = dbexec.Query(args.verb, [param for param in args.params])
                return QueryRowset(columns=c, rows=r)

            case "do":
                return dbexec.NonQuery(args.verb, [param for param in args.params])

            case "is" | "peek":
                rval = dbexec.QueryScalar(args.verb, [param for param in args.params])
                return QueryScalar(result=rval)

            case _:
                return _invalidVerbException(args.verb)

    ### TODO: repackage this so the postgres-specific stuff is in dbexec.py
    except Exception as ex:
        if isinstance(ex, psycopg.Error):
            _postgresException(str(ex))
        else:
            raise
