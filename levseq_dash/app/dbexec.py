#
# dbexec.py
#
# Notes:
#  This module implements data transfers between this web application and a postgres database
#   server running on the same machine.
#
#  We assume this application is running under user credentials that are also authenticated
#   on the postgres server.  No password needs to be specified in the database connection
#   string.

import psycopg
from psycopg import sql as scm  # "SQL composition utility module"
from psycopg import abc         # typedef Params for cursor.execute()
import typing
import global_strings as gs





def doNoFetch():
    return

def doFetch( verb : str, args : abc.Params = None ) -> typing.Any :

    # open a database connection; we don't bother with connection pooling for
    #  this very lightweight, low-usage application
    with psycopg.connect( gs.pgcs ) as cn:

        # open a postgres/psycopg "cursor" to perform database operations
        #  (for more info: https://www.psycopg.org/psycopg3/docs/advanced/cursors.html)
        with cn.cursor() as cur:

            # build the format string for the SQL command builder
            fmt = f"select * from {gs.schema}.{{}}("

            if args is not None :
                # build a list of '%s' strings (one per argument)
                aPct = []
                aPct += len(args) * ["%s"]

                # build a comma-separated string
                fmt += ','.join(aPct)

            fmt += ");"

            # the postgres function name starts with "fetch_"
            fnid = f"fetch_{verb}"

            # compose the SQL command
            cmd = scm.SQL(fmt).format(scm.Identifier(fnid), args)

            # execute and wait for a result set
            cur.execute( cmd, args )

            # get result set rows as Python tuples
            tuples = cur.fetchall()

            # be nice and release whatever resources the cursor is using
            cur.close()
    
    return tuples

def doInsert():
    return

def doUpdate():
    return


# pandas can read a csv file directly, but we're going to pull the data from a postgres table
# df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')       

# get tuples from a postgres table



