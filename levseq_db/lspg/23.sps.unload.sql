/*
   23.sps.unload.sql
*/


/* procedure v1.unload_experiment

   Notes:
    This procedure does NOT delete uploaded files associated with
     the specified experiment.
*/
-- drop procedure if exists v1.unload_experiment(int,int);
create or replace procedure v1.unload_experiment
( in _uid int,
  in _eid int )
language plpgsql
as $body$
begin

    -- delete the specified experiment in v1.experiments as well as
    --  all rows with foreign key references to v1.experiments(pkey)
    delete from v1.experiments cascade
     where pkey = _eid;
	 
    -- remove pending references to the specified experiment
    delete from v1.experiments_pending
     where eid = _eid
       and uid = _uid;

end;
$body$;
/*** test
select * from v1.fitness;              -- v1.experiment_cas, v1.variants
select * from v1.mutations;            -- v1.variants
select * from v1.variants;             -- v1.plates v1.experiments
select * from v1.parent_sequences;     -- v1.plates v1.experiments
select * from v1.reference_sequences;  -- ok to leave as is
select * from v1.cas;                  -- ok to leave as is
select * from v1.experiment_cas;       -- v1.experiments;
select * from v1.plates;               -- v1.experiments;
select * from v1.experiments;
select * from v1.experiments_pending;


call v1.unload_experiment( 5, 25 );

insert into v1.experiments_pending(eid,uid,dt_load,experiment_name,assay,mutagenesis_method,dt_experiment,cas_substrate,cas_product)
values(28,5,now(),'expt1',8,2,'2024-12-26','345905-97-7','395683-37-1')

expt2
99685-96-8
7732-18-5


select * from v1.experiments;
select * from v1.get_experiment_row_counts(25);


"v1.fitness"	1903
"v1.mutations"	1732
"v1.variants"	960
"v1.parent_sequences"	10
"v1.experiment_cas"	2
"v1.plates"	4
"v1.experiments"	1
"v1.experiments_pending"	0
***/


/* procedure v1.unload_file UNUSED */
/*****************************
drop procedure if exists v1.unload_file(int,int,text);

--create or replace procedure v1.unload_file
( in _uid int,
  in _eid int,
  in _filespec text )
language plpgsql
as $body$

declare
    grp      int;
    grpname  text;
    expname  text;
	nRows    int;     -- TODO: CHOP WHEN DEBUGGED

begin
    -- get the LevSeq user's group ID and name
    select t1.pkey, t1.groupname into grp, grpname
      from v1.users t0
	  join v1.usergroups t1 on t1.pkey = t0.gid
     where t0.pkey = _uid;

    -- get the specified experiment name
    select t0.experiment_name into expname
      from v1.experiments t0
     where t0.pkey = _eid;

    -- conditionally delete data loaded from the file
	if right(_filespec,4) = '.csv'
	then
	    call v1.unload_experiment_data( _eid );
	end if;

    /* remove the record of the specified file from the database,
        regardless of whether or not the file actually exists */
	delete from v1.data_files
     where eid = _eid
	   and gid = grp
	   and filespec = _filespec;

    -- TODO: CHOP WHEN DEBUGGED
    get diagnostics nRows = row_count;
    raise notice '% row(s) deleted', nRows;
	   
end;
$body$;
*********************/
/*** test
select * from v1.users;
select * from v1.data_files;
call v1.unload_file( 5, 1, '/mnt/Data/lsdb/uploads/G00002/E00001/tiny.csv' );
***/

