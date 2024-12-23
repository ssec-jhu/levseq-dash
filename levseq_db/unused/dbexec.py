#
# dbexec.py --- UNUSED IF WE'RE GOING THROUGH A WEBSERVICE!!!!!
#
# Notes:
#  This module implements data transfers between this web application and a postgres database
#   server running on the same machine.
#
#  We assume this application is running under user credentials that are also authenticated
#   on the postgres server, so that no password is needed in the database connection string.
#

import psycopg
from psycopg import sql as scm  # "SQL composition utility module"
from psycopg import abc  # typedef Params for cursor.execute()
import typing
import global_vars as gv


# handy type aliases
type Rowset = list[tuple]
type Scalar = typing.Union[int, float, str]
type Arglist = typing.Union[abc.Params, None]


# build a postgres SQL command
def _buildSqlCmd(execCmd: str, verb: str, args: Arglist) -> scm.Composed:

    # build the format string for the SQL command builder; this may be overkill, but doing it
    #  this way takes care of string formatting details (and should prevent SQL injection, too)
    fmt = f"{execCmd} {gv.schema}.{{}}("

    if args is not None:
        # build a comma-separated string of '%s' strings (one per argument)
        aPct = len(args) * ["%s"]
        fmt += ",".join(aPct)

    fmt += ");"

    # compose the SQL command
    return scm.SQL(fmt).format(scm.Identifier(verb), args)


# execute a postgres SQL stored procedure
def _fnExecuteNonQuery(cur: psycopg.Cursor, verb: str, args: Arglist) -> None:
    cmd = _buildSqlCmd("call", verb, args)
    cur.execute(cmd, args)  # execute and wait for completion
    return None


# execute a postgres SQL function and return a rowset (result set)
def _fnExecuteQuery(cur: psycopg.Cursor, verb: str, args: Arglist) -> Rowset:
    cmd = _buildSqlCmd("select * from", verb, args)
    cur.execute(cmd, args)  # execute and wait for a result set
    return cur.fetchall()  # return the result set rows as python tuples


# execute a postgres SQL function and return the first value in the first column of the result set
def _fnExecuteScalar(cur: psycopg.Cursor, verb: str, args: Arglist) -> Scalar:
    cmd = _buildSqlCmd("select * from", verb, args)
    cur.execute(cmd, args)
    return cur.fetchone()[0]  # type:ignore


# execute SQL on the postgres server and bind result sets to python tuples
#
# Examples:
#  Call with no arguments:   rows = dbexec.Query( 'countries' )
#  Call with 1 argument:     rows = dbexec.Query( 'population_data', ['Turkey'] )
#  Call with 3 arguments:    rows = dbexec.Query( 'population_data_3', ['France', 'Italy', 'Oz'] )
#  Call with no result set:  dbexec.NonQuery( 'save_uploaded_files', 'bc123.csv', 'abc123.pdb' )
#  Call for scalar result:   rval = dbexec.QueryScalar( 'get_upload_status', 'abc123.csv' )
#
# fmt:off
def _doQuery(fn: typing.Callable, verb: str, args: Arglist) -> Rowset | Scalar | None:
# fmt:on
    # open a database connection; we don't bother with connection pooling for
    #  this lightweight, low-usage application
    with psycopg.connect(gv.pgcs) as cn:

        # open a postgres/psycopg "cursor" to perform database operations
        #  (for more info: https://www.psycopg.org/psycopg3/docs/advanced/cursors.html)
        with cn.cursor() as cur:

            # execute and wait for the operation to complete
            rval = fn(cur, verb, args)

            # be nice and release whatever resources the cursor is using
            cur.close()

    return rval


# execute a postgres SQL stored procedure that does not return a rowset (result set)
def NonQuery(verb: str, args: Arglist = None) -> None:
    _doQuery(_fnExecuteNonQuery, verb, args)
    return


# execute a postgres SQL function that returns a rowset (result set)
def Query(verb: str, args: Arglist = None) -> Rowset:
    return _doQuery(_fnExecuteQuery, verb, args) # type:ignore


# execute a postgres SQL function that returns a scalar (number or string)
def QueryScalar(verb: str, args: Arglist = None) -> Scalar:
    return _doQuery(_fnExecuteScalar, verb, args) # type:ignore


# return a string that represents a row (tuple) from a result set
def RowToString(row: tuple, sep: str = " ") -> str:

    # Each row in the rowset is a python tuple.  Here we do a join on the string
    #  representation of each item in a row tuple, using the specified separator.
    #
    # This ugly code could be avoided by letting the database server "stringify" the
    #  rows, but there may be applications where the underlying typed data is needed
    #  for computation.
    #
    return sep.join(tuple(str(c) for c in row))


def RowToDropdownOption(row: tuple, sep: str = " ") -> dict:

    # value: the first item
    # label: the remaining items concatenated into a string
    return {"value": row[0], "label": RowToString(row[1:], sep)}
