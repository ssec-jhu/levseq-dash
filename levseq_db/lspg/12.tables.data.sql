/*
   12.tables.data.sql
*/

/* table v1.experiment_cas */
-- drop table if exists v1.experiment_cas cascade
create table if not exists v1.experiment_cas
(
  pkexp     int      not null constraint fk_experiment_cas_pkexp
                              references v1.experiments(pkey),
  pkcas     int      not null constraint fk_experiment_cas_pkcas
                              references v1.cas(pkey),
  substrate boolean  not null default false,
  product   boolean  not null default false,
  n         smallint not null default 0
);

create index ix_experiment_cas_exp
          on v1.experiment_cas
       using btree (pkexp asc)
        with (deduplicate_items=True)
  tablespace pg_default;

create index ix_experiment_cas_cas
          on v1.experiment_cas
       using btree (pkcas asc)
        with (deduplicate_items=True)
  tablespace pg_default;



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
-- drop table if exists v1.experiments cascade;
create table if not exists v1.experiments
(
  pkey                int          not null generated always as identity primary key,
  uid                 int          not null constraint fk_experiments_uid
                                            references v1.users(pkey),
  experiment_name     text         not null,
  assay               smallint     not null constraint fk_experiments_assay
                                            references v1.assays(pkey),
  mutagenesis_method  smallint     not null constraint fk_experiments_mutagenesis_method
                                            references v1.mutagenesis_methods(pkey),
  dt_experiment       timestamptz  not null,
  dt_load             timestamptz  not null default now()
);
/*** test
truncate table v1.experiments;
alter sequence v1.experiments_pkey_seq restart with 1;

insert into v1.experiments( dt_load, experiment_name, assay, mutagenesis_method )
     values (now(), 'experiment 1', 1, 1 );
select * from v1.experiments;
***/

/* table v1.experiments_pending

   Note:
    This table records experiment metadata for the brief interval between the
     initial call to v1.init_load() and the subsequent call to v1.load_file().

    During this interval, the LevSeq webservice uploads the data file(s)
     associated with the experiment.
	 
    A row in this table persists until one of the following events occurs:
     - experiment data is successfully loaded
	 - a new row in the table is created for the same LevSeq user
	 - a new row in the table is created for any LevSeq user at least 24 hours later
*/
-- drop table if exists v1.experiments_pending;
create table if not exists v1.experiments_pending
(
  eid                 int          not null primary key,
  uid                 int          not null constraint fk_experiments_pending_uid
                                            references v1.users(pkey),
  experiment_name     text         not null,
  assay               smallint     not null constraint fk_experiments_assay
                                            references v1.assays(pkey),
  mutagenesis_method  smallint     not null constraint fk_experiments_mutagenesis_method
                                            references v1.mutagenesis_methods(pkey),
  dt_experiment       timestamptz  not null,
  cas_substrate       text         not null,
  cas_product         text         not null
);

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

