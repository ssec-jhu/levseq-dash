/*
   00.database.sql

   Notes:
    Connect to database "postgres" to execute this script in pgadmin4.

    Execute each statement separately (not as a batch).
*/

/* create the LevSeq database*/
-- drop database if exists "LevSeq";
 create database "LevSeq"
            with owner = "ssec-devuser"
        encoding = 'UTF8'
 locale_provider = 'libc'
      tablespace = pg_default
connection limit = -1
     is_template = False;

comment on database "LevSeq"
                 is 'LevSeq data';

/* ensure that the SQL schema exists */
create schema if not exists v1 authorization "ssec-devuser";


/* tables and indexes

    index names are formatted as:

        {tablename}_{columnname(s)}_{suffix}

    where the suffix is one of the following:

        pkey for a Primary Key constraint
        key for a Unique constraint
        excl for an Exclusion constraint
        idx for any other kind of index
        fkey for a Foreign key
        check for a Check constraint
*/
select tablename, indexname, indexdef
  from pg_indexes
 where schemaname = 'v1'
 order by tablename, indexname;
