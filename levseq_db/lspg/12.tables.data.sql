/*
   12.tables.data.sql
*/

/* table v1.experiments

   Note:
    This table's primary key uniquely identifies a set of metadata (experiment name, etc.) entered
     interactively through the LevSeq web application.  There is no way to trace the origin of any
     data in the database, to detect data-entry errors in the identification of a given set of
     experimental data, or to verify that the interactively-entered metadata actually corresponds
     to the data with which it is associated.

    Modifying and replacing uploaded experimental data is NOT supported.  The only way to change
     data in the database is to delete all data associated with a given primary key -- in which
     case a new primary key is assigned even if the "changed" data pertains to the same experiment.
*/
-- drop table if exists v1.experiments cascade
create table if not exists v1.experiments
(
  pkey                int          not null generated always as identity primary key,
  dt_load             timestamptz  not null,
  experiment_name     text         not null,
  assay               smallint     not null,
  mutagenesis_method  smallint     not null,
  dt_experiment       timestamptz  null
);
grant select,insert,update,delete on v1.experiments to lsdb;
/*** test
truncate table v1.experiments;
alter sequence v1.experiments_pkey_seq restart with 1;

insert into v1.experiments( dt_load, experiment_name, assay, mutagenesis_method )
     values (now(), 'experiment 1', 1, 1 );
select * from v1.experiments;
***/

/* table v1.data_files */
-- drop table if exists v1.data_files
create table if not exists v1.data_files
(
  pkey       int          not null generated always as identity primary key,
  gid        int          not null constraint fk_data_files_group
                                   references v1.usergroups(pkey),
  eid        int          not null constraint fk_data_files_experiment
                                   references v1.experiments(pkey),
  filespec   text         not null,
  dt_upload  timestamptz  not null default current_timestamp,
  uid        smallint     not null constraint fk_data_files_users
                                   references v1.users(pkey),
  filesize   int          null
);

create unique index ix_data_files_gid_eid_filespec
                 on v1.data_files
              using btree (gid asc, eid asc, filespec asc)
               with (deduplicate_items=True)
         tablespace pg_default;
grant select,insert,update,delete on v1.data_files to lsdb;
/*** test
truncate table v1.data_files;
alter sequence v1.data_files_pkey_seq restart with 1;

select * from v1.users
select * from v1.usergroups
select * from v1.experiments
insert into v1.data_files( gid, eid, filespec, uid )
     values (2, 1, '/mnt/Data/ssec-devuser/uploads/G00002/E00001/tiny.csv', 1);
	 
select * from v1.data_files order by pkey;
delete from v1.data_files where pkey >= 1;
***/

