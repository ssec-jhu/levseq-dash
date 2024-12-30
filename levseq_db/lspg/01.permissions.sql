/*
   00.permissions.sql

   Notes:
    Connect to database "postgres" to execute this script in pgadmin4.
*/


/* postgres permissions for the LevSeq dedicated login

   - We default the login name to: lsdb
   - Permission to select/insert/update/delete must be granted
      on individual tables
   - File uploads require use of the postgres copy command, about which
      the postgres documentation says:

        COPY naming a file or command is only allowed to database superusers
        or users who are granted one of the roles pg_read_server_files,
        pg_write_server_files, or pg_execute_server_program, since it allows
        reading or writing any file or running a program that the server has
        privileges to access.

        (See https://www.postgresql.org/docs/current/sql-copy.html)
*/
grant pg_read_server_files to lsdb;
grant execute on function pg_stat_file(text,boolean) to lsdb;

/* 10.tables.admin.sql */
grant select,insert,update,delete on v1.usergroups to lsdb;
grant select,insert,update,delete on v1.users to lsdb;

/* 11.tables.ref.sql */
grant select on v1.mutagenesis_methods to lsdb;
grant select on v1.assays to lsdb;
grant select,insert,update on v1.cas to lsdb;

/* 12.tables.data.sql */
grant select,insert,update,delete on v1.experiments to lsdb;
grant select,insert,update,delete on v1.experiment_cas to lsdb;

/* 13.tables.load.sql */
grant select,insert,update,delete on v1.experiments_pending to lsdb;

/* 23.sps.load.sql */
grant update on sequence v1.experiments_pkey_seq to lsdb;
