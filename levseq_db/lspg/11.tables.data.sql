/*
   11.tables.data.sql
*/

/* ensure that the SQL schema exists */
create schema if not exists "v1" authorization "ssec-devuser";


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
-- drop table if exists v1.experiments
create table if not exists v1.experiments
(
  pkey               int          not null generated always as identity,
  dt_load            timestamptz  not null,
  experiment_name    varchar(128) not null,
  assay              varchar(128) not null,
  mutagenesis_method int          not null,
  dt_experiment      timestamptz  null
);

alter table if exists v1.experiments owner to "ssec-devuser";

drop index if exists v1.pk_experiments;

create unique index pk_experiments
          on v1.experiments
       using btree
             (pkey asc)
        with (deduplicate_items=True)
  tablespace pg_default;

/*** test
truncate table v1.experiments;
alter sequence v1.experiments_pkey_seq restart with 1;

insert into v1.experiments( experiment ) values ('experiment 1');
insert into v1.experiments( experiment ) values ('experiment 2');
***/


/* table v1.data_files */
-- drop table if exists v1.data_files
create table if not exists v1.data_files
(
  pkey int                 not null generated always as identity,
  experiment  int          not null constraint fk_data_files_experiments
                                    references v1.experiments(pkey),
  filespec    varchar(64)  not null,
  dt_upload   timestamptz  not null default current_timestamp,
  upload_by   smallint     not null constraint fk_data_files_users
                                    references v1.users(pkey),
  filesize    int          null
);

alter table if exists v1.data_files owner to "ssec-devuser";

drop index if exists v1.pk_data_files;

create unique index pk_data_files
          on v1.data_files
       using btree
             (pkey asc)
        with (deduplicate_items=True)
  tablespace pg_default;

create index Ix_data_files_experiment
          on v1.data_files
       using btree
             (experiment asc)
        with (deduplicate_items=True)
  tablespace pg_default;


/*** test
truncate table v1.data_files;
alter sequence v1.data_files_pkey_seq restart with 1;

select * from v1.data_files order by pkey;
***/
