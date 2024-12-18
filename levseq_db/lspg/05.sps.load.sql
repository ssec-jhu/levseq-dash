/*
   03.sps.load.sql
*/


/* function get_file_load_status */
drop function if exists v1.get_file_load_status(int,varchar,varchar);

create or replace function v1.get_file_load_status(
    in _uid int,
    in _upload_dir varchar(256),
	in _filenames varchar ) 
returns table ( filename  varchar(64),
                task      varchar(32),
                status    varchar(32) )
language plpgsql
as $body$

declare
    u varchar(256) = rtrim(_upload_dir,'/') || '/';   -- ensure trailing separator
    i smallint = 1;
    f varchar(64) = '';
	filespec varchar(320);
	s varchar(10);
	fileinfo varchar(128) = null;
	pkey_log int;
	pkey_result int = null;
	load_status varchar(512) = 'none';

begin

    -- split the list of filenames
    f = trim( both ' ' from split_part(_filenames, ',', i) );
    while f != '' loop
        raise notice 'i: %, f: %', i, f;

		-- check whether the file exists in the specified upload directory
		filespec = u || f;
        fileinfo = pg_stat_file(filespec, true);  -- (requires su permission)
		s = case when fileinfo is not null then 'completed' else 'failed' end;

THIS WON'T WORKL
        -- log the result
        insert into v1.load_log( uid, task, status, details)
        select _uid, t1.pkey, t2.pkey, filespec
          from v1.load_tasks t1
    cross join v1.load_states t2
         where t1.task = 'upload'
		   and t2.status = s
     returning pkey into pkey_log;

        -- track the pkey of the first logged row
        if pkey_result is null then pkey_result = pkey_log; end if;

	 raise notice 'pkey_log: %  pkey_result: %', pkey_log, pkey_result;

        -- iterate
        i = i + 1;
        f = trim( both ' ' from split_part(_filenames, ',', i) );
    end loop;
***/

    -- return upload status for each file
    return query
    select regexp_replace( t0.details, '.*/', '')::varchar, t2.task::varchar, t3.status::varchar
      from v1.load_log t0
      join v1.users t1 on t1.pkey = t0.uid
      join v1.load_tasks t2 on t2.pkey = t0.task
      join v1.load_states t3 on t3.pkey = t0.status
	 where t0.pkey >= pkey_result
	   and t0.uid = _uid
	   and t2.task = 'upload'
  order by t0.pkey asc;

end;

$body$;
/*** test
truncate table v1.load_log;
select * from v1.get_file_load_status(
  2,
  '/mnt/Data/ssec-devuser/uploads',
  'flatten_ep_processed_xy_cas.csv,ligand_bound.cif,ligand_bound.pdb, nosuch.file'
);

select * from v1.get_file_load_status(
  1,
  '/mnt/Data/ssec-devuser/uploads',
  'flatten_ep_processed_xy_cas.csv,ligand_bound.cif,ligand_bound.pdb'
);


select * from v1.load_log;
select t0.pkey, t1.username, dt, t2.task, t3.status, t0.details
  from v1.load_log t0
  join v1.users t1 on t1.pkey = t0.uid
  join v1.load_tasks t2 on t2.pkey = t0.task
  join v1.load_states t3 on t3.pkey = t0.status
 order by pkey asc;
***/


/* procedure load_csv_file */
drop procedure if exists v1.load_csv_file(int,varchar);

create or replace procedure v1.load_csv_file( in _uid int, in _filespec varchar(320) ) 
language plpgsql
as $body$

declare
    fileinfo varchar(128) = pg_stat_file(_filespec, true);  -- (requires su permission)
    execsql varchar(360) =
			'copy _rawcsv from '
            || quote_literal(_filespec)
            || ' with (format csv, header match)';

begin
	--raise notice 'Value: %', fileinfo;
    --raise notice 'Value: %', execsql;

	if fileinfo is null
    then
	
        -- load log: file upload failed
	    insert into v1.load_log( uid, task, status, details)
        select _uid, t1.pkey, t2.pkey, _filespec
          from v1.load_tasks t1
          join v1.load_states t2 on t2.status = 'failed'
         where t1.task = 'upload';

		 return;

    end if;

    /* at this point we have a file to load */
	
    -- load log: file upload completed
    insert into v1.load_log( uid, task, status, details)
    select _uid, t1.pkey, t2.pkey, _filespec
      from v1.load_tasks t1
      join v1.load_states t2 on t2.status = 'completed'
     where t1.task = 'upload';

	/* load csv into a temporary table */
    create temporary table _rawcsv
    (
      "id"                        varchar(32)      not null,
      barcode_plate               integer          not null,
      cas_number                  varchar(12)      not null,
      plate                       varchar(32)      not null,
      well                        varchar(4)       not null,
      alignment_count             double precision not null,
      nucleotide_mutation         varchar(512)     null,
      amino_acid_substitutions    varchar(64)      null,
      alignment_probability       double precision null ,
      average_mutation_frequency  double precision null,
      p_value                     double precision null,
      p_adj_value                 double precision null,
      nt_sequence                 varchar(1024)    null,
      aa_sequence                 varchar(512)     null,
      x_coordinate                double precision null,
      y_coordinate                double precision null,
      fitness_value               double precision null                
    );
	
    execute execsql;

    /* clean up */
    drop table _rawcsv;

    -- load log: file upload completed; the regex replaces everything before the
	--  rightmost forward slash with an empty string, which leaves only the filename
	insert into v1.load_log( uid, task, status, details)
	select _uid, t1.pkey, t2.pkey,
	       regexp_replace( _filespec, '.*/', '')
      from v1.load_tasks t1
	  join v1.load_states t2 on t2.status = 'completed'
	 where t1.task = 'load';


end;

$body$;
/*** test
select pg_stat_file('/mnt/Data/ssec-devuser/uploads/flatten_ep_processed_xy_cas.csv', true);

truncate table v1.load_log;
call v1.load_csv_file(2, '/mnt/Data/ssec-devuser/uploads/flatten_ep_processed_xy_cas.csv');


select * from v1.load_log;
select t0.pkey, t1.username, dt, t2.task, t3.status, t0.details
  from v1.load_log t0
  join v1.users t1 on t1.pkey = t0.uid
  join v1.load_tasks t2 on t2.pkey = t0.task
  join v1.load_states t3 on t3.pkey = t0.status
 order by pkey asc;
  
***/
