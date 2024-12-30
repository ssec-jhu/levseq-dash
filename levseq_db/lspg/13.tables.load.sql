/*
   12.tables.load.sql
*/

/* table v1.experiments_pending

   Note:
    This table records experiment metadata for the brief interval between the
     initial call to v1.init_load() and the subsequent call to
	 v1.load_experiment_data().

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
/*** test
select * from v1.experiments_pending;
delete from v1.experiments_pending where eid = 2;
***/

