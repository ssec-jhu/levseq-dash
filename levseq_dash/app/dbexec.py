#
# dbexec.py
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
from psycopg import abc         # typedef Params for cursor.execute()
import typing
import global_strings as gs


# handy type aliases
type Rowset = list[tuple]

# execute a postgres SQL stored procedure
def _fnExecuteNonQuery( cur: psycopg.Cursor, cmd: scm.Composed, args: abc.Params ) -> None:
            
    cur.execute( cmd, args )    # execute and wait for completion
    return None

# Execute a postgres SQL function and return a rowset (result set)
#
# Examples:
#  Call with no arguments:   rows = dbexec.Query( "countries" )
#  Call with 1 argument:     rows = dbexec.Query( "population_data", ["Turkey"] )
#  Call with 3 arguments:    rows = dbexec.Query( "population_data_3", ["France", "Italy", "Oz"] )
#  Call with no result set:  dbexec.NonQuery( "user_list" )
#
def _fnExecuteQuery( cur: psycopg.Cursor, cmd: scm.Composed, args: abc.Params ) -> Rowset:
            
    cur.execute( cmd, args )    # execute and wait for a result set
    return cur.fetchall()       # return the result set rows as python tuples

# execute SQL on the postgres server and bind result sets to python tuples
def _doQuery( fn: typing.Callable, verb: str, args: abc.Params ) -> Rowset | None :

    # open a database connection; we don't bother with connection pooling for
    #  this lightweight, low-usage application
    with psycopg.connect( gs.pgcs ) as cn:

        # open a postgres/psycopg "cursor" to perform database operations
        #  (for more info: https://www.psycopg.org/psycopg3/docs/advanced/cursors.html)
        with cn.cursor() as cur:

            # build the format string for the SQL command builder; this may be overkill, but doing it
            #  this way takes care of string formatting details (and should prevent SQL injection, too)
            fmt = f"select * from {gs.schema}.{{}}("

            if args is not None :
                # build a comma-separated string of '%s' strings (one per argument)
                aPct = len(args) * ["%s"]
                fmt += ','.join(aPct)

            fmt += ");"

            # the postgres function name starts with "fetch_"
            fnid = f"fetch_{verb}"

            # compose the SQL command
            cmd = scm.SQL(fmt).format(scm.Identifier(fnid), args)

            # execute and wait for the operation to complete
            rval = fn( cur, cmd, args )

            # be nice and release whatever resources the cursor is using
            cur.close()

    return rval

# execute a postgres SQL stored procedure that does not return a rowset (result set)
def NonQuery( verb: str, args: abc.Params = None ) -> None :
    return _doQuery( _fnExecuteNonQuery, verb, args )

# execute a postgres SQL function that returns a rowset (result set)
def Query( verb: str, args: abc.Params = None ) -> Rowset :
    return _doQuery( _fnExecuteQuery, verb, args )

# return a string that represents a row (tuple) from a result set
def RowToString( row: tuple, sep: str = ' ' ) -> str :

    # Each row in the rowset is a python tuple.  Here we do a join on the string
    #  representation of each item in a row tuple, using the specified separator.
    #
    # This ugly code could be avoided by letting the database server "stringify" the
    #  rows, but there may be applications where the underlying typed data is needed
    #  for computation.
    #
    return sep.join( tuple(str(c) for c in row) )
