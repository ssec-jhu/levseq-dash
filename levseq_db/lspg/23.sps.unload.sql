/*
   23.sps.unload.sql
*/


/* function v1.get_unload_dirpath */
drop function if exists v1.get_unload_dirpath(int,int);

create or replace function v1.get_unload_dirpath
( in _uid int,
  in _eid int )
returns text
language plpgsql
as $body$

declare
    grp      int;
	dirpath  text;
	grpname  text;

begin

    -- get the LevSeq user's group ID
	select t0.gid into grp
	  from v1.users t0
     where t0.pkey = _uid;

    /* build the file specification by injecting the current database
	    user name into the directory path */	    
	select format(t0.upload_dir, current_user), t0.groupname
      into dirpath, grpname
      from v1.usergroups t0
     where t0.pkey = grp;

	-- limit the character set
    dirpath = regexp_replace( dirpath, '[^A-Za-z0-9_\-\/]', '_', 'g' );
	
    -- append group and experiment subdirectories
    dirpath = dirpath
              || 'G' || right('0000'||grp, 5) || '/'
              || 'E' || right('0000'||_eid, 5) || '/';

    -- return the slash-terminated directory path
    return dirpath;

end;
$body$;
/*** test
select v1.get_unload_dirpath( 5, 1 );
***/

/* procedure v1.unload_experiment */
drop procedure if exists v1.unload_experiment(int,int);

create or replace procedure v1.unload_experiment
( in _uid int,
  in _eid int )
language plpgsql
as $body$

declare

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
select * from v1.experiments;
select * from v1.experiment_cas;
call v1.unload_experiment( 5, 1 );
***/




/* procedure v1.unload_file UNUSED */
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
/*** test
select * from v1.users;
select * from v1.data_files;
call v1.unload_file( 5, 1, '/mnt/Data/lsdb/uploads/G00002/E00001/tiny.csv' );
***/

