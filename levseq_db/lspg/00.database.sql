/*
   00.database.sql

   Notes:
    Connect to database "postgres" to execute this script in pgadmin4.

    Execute each statement separately (not as a batch).
*/

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
