/*
   23.sps.load.sql

   Notes:
    We leave the uploaded CSV, PDB, and CIF files intact in the filesystem.
     There's no good reason to complicate things since their contents will not
     be used in relational operations (they're just blobs), and performance
     (i.e., delivering them on demand) is best this way.
	 
	 See: https://www.cybertec-postgresql.com/en/binary-data-performance-in-postgresql/)
*/


/* function v1.upload_experiment_file */
drop function if exists v1.save_experiment_file(int,int,text,text);

create or replace function v1.load_experiment_file
( in _filespec text,   -- (see lsws fsexec.py)
  in _uid int,
  in _eid int,
  in _filename text,
  in _filedata text )
returns int
language plpgsql
as $body$

declare
    gid      smallint;
    fidprev  int;
	exp_name text;
	dirpath  text;
    filespec text;
	sqlcmd   text;

begin

    -- avoid duplicating the file for the current experiment
	select t0.pkey into fidprev
      from v1.experiment_files t0
     where t0.eid = _eid and t0.filename = _filename;

    if fidprev is not null
    then
        select t0.experiment_name into exp_name
          from v1.experiments t0
         where t0.pkey = _eid;

        raise exception 'Duplicate filename %s for experiment %s', _filename, exp_name;
		return 0;
    end if;
	  
    -- get the upload directory for the user's group
	select t0.pkey, t0.upload_dir into gid, dirpath
	  from v1.usergroups t0
	  join v1.users t1 on t1.gid = t0.pkey
     where t1.pkey = _uid;

    -- insert the current system login and group ID into the directory path
    dirpath = format( dirpath, current_user, right('0000'||gid::text,5) );
	if right(dirpath,1) != '/' then dirpath = dirpath || '/'; end if;

    -- append the filename
	filespec = dirpath || _filename;

	-- create a temporary table that contains the file data
    create temporary table _fc
	( filedata text not null );
	
	insert into _fc(filedata) values(_filedata);

    -- file contents are assumed to be non-binary (or is it genderfluid?)
    sqlcmd = format('copy (select filedata from _fc) to ''%s'' with( encoding ''UTF8'')',
                    filespec);
	raise notice 'sqlcmd: -->%<--', sqlcmd;
    execute sqlcmd;
	
raise notice 'filespec: %', filespec;

    return 0;
end;
$body$;
/*** test
select v1.upload_experiment_file( 1, 1, 'tiny.csv',
'id,barcode_plate,cas_number,plate,well,alignment_count,nucleotide_mutation,amino_acid_substitutions,alignment_probability,average_mutation_frequency,p_value,p_adj_value,nt_sequence,aa_sequence,x_coordinate,y_coordinate,fitness_value
20241201-SSM-P1-A1,1,395683-37-1,20241201-SSM-P1,A1,2,G175A_C176A,#LOW#,0.5,0.5,0.009709951,0.9321553,ATGACTCCCTCGGACATCTCGGGGTATGATTATGGGCGTGTCGAGAAGTCACCCATCACGGACCTTGAGTTTGACCTTCTGAAGAAGACTGTCATGTTAGGTGAAGAGGACGTAATGTACTTGAAAAAGGCGGCTGACGTTCTGAAAGATCAAGTTGATGAGATCCTTGACCTGAAGGGTGGTTGGGCAGCATCAAATGAGCATTTGATTTATTACGGTTCCAATCCGGATACAGGAGCGCCTATTAAAGAATACCTGGAACGTGTACGCGCTCGCATTGGAGCCTGGGTTCTGGACACTACCTGCCGCGACTATAACCGTGAATGGTTAGACTACCAGTACGAAGTTGGGCTTCGTCATCACCGTTCAAAGAAAGGGGTCACAGACGGAGTACGCACCGTGCCCAATACCCCACTTCGTTATCTTATCGCAGGTATCTATCCTATCACCGCCACTATCAAGCCATTTTTAGCTAAGAAAGGTGGCTCTCCGGAGGACATCGAAGGGATGTACAACGCTTGGCTCAAGTCTGTAGTTCTACAAGTTGCCATCTGGTCACACCCTTATACTAAGGAGAATGACCGG,MTPSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLKGGWAASNEHLIYYGSNPDTGAPIKEYLERVRARIGAWVLDTTCRDYNREWLDYQYEVGLRHHRSKKGVTDGVRTVPNTPLRYLIAGIYPITATIKPFLAKKGGSPEDIEGMYNAWLKSVVLQVAIWSHPYTKENDR,-0.12535994,-0.14982244,1496.4556
20241201-SSM-P1-A2,1,395683-37-1,20241201-SSM-P1,A2,64,#PARENT#,#PARENT#,1,,,,ATGACTCCCTCGGACATCTCGGGGTATGATTATGGGCGTGTCGAGAAGTCACCCATCACGGACCTTGAGTTTGACCTTCTGAAGAAGACTGTCATGTTAGGTGAAGAGGACGTAATGTACTTGAAAAAGGCGGCTGACGTTCTGAAAGATCAAGTTGATGAGATCCTTGACCTGGCGGGTGGTTGGGCAGCATCAAATGAGCATTTGATTTATTACGGTTCCAATCCGGATACAGGAGCGCCTATTAAAGAATACCTGGAACGTGTACGCGCTCGCATTGGAGCCTGGGTTCTGGACACTACCTGCCGCGACTATAACCGTGAATGGTTAGACTACCAGTACGAAGTTGGGCTTCGTCATCACCGTTCAAAGAAAGGGGTCACAGACGGAGTACGCACCGTGCCCAATACCCCACTTCGTTATCTTATCGCAGGTATCTATCCTATCACCGCCACTATCAAGCCATTTTTAGCTAAGAAAGGTGGCTCTCCGGAGGACATCGAAGGGATGTACAACGCTTGGCTCAAGTCTGTAGTTCTACAAGTTGCCATCTGGTCACACCCTTATACTAAGGAGAATGACCGG,MTPSDISGYDYGRVEKSPITDLEFDLLKKTVMLGEEDVMYLKKAADVLKDQVDEILDLAGGWAASNEHLIYYGSNPDTGAPIKEYLERVRARIGAWVLDTTCRDYNREWLDYQYEVGLRHHRSKKGVTDGVRTVPNTPLRYLIAGIYPITATIKPFLAKKGGSPEDIEGMYNAWLKSVVLQVAIWSHPYTKENDR,0.038451646,0.02593873,273777.8326');
***/    


select encode('abcde', 'base64')
select decode('YWJjZGU=', 'base64')::text

select * from v1.upload_base64_file( 1, 1, '/mnt/Data/lsdb/uploads', )
COPY { table_name [ ( column_name [, ...] ) ] | ( query ) }
    TO { 'filename' | PROGRAM 'command' | STDOUT }
    [ [ WITH ] ( option [, ...] ) ]

where option can be one of:

    FORMAT format_name
    FREEZE [ boolean ]
    DELIMITER 'delimiter_character'
    NULL 'null_string'
    DEFAULT 'default_string'
    HEADER [ boolean | MATCH ]
    QUOTE 'quote_character'
    ESCAPE 'escape_character'
    FORCE_QUOTE { ( column_name [, ...] ) | * }
    FORCE_NOT_NULL { ( column_name [, ...] ) | * }
    FORCE_NULL { ( column_name [, ...] ) | * }
    ON_ERROR error_action
    ENCODING 'encoding_name'
    LOG_VERBOSITY verbosity






/* function v1.get_upload_directory */
create or replace function v1.get_upload_directory( in _cas varchar(16) )
returns smallint
language plpgsql
as $body$

declare
    ccc int;
    is_valid smallint;	

begin

    -- validate syntax: there must be
	if not regexp_like(_cas, '\d{2,7}-\d\d-\d') then return 0; end if;

    -- validate checksum (https://en.wikipedia.org/wiki/CAS_Registry_Number)
	create temporary table _casx
	( ordinal smallint not null generated always as identity (minvalue 0),
      digit   smallint not null );

    insert into _casx(digit)
    select cast(digit[1] as smallint)
      from regexp_matches( reverse(_cas), '\d', 'g' ) as digit;

    select sum(ordinal*digit) % 10 from _casx into ccc;
    select digit-ccc from _casx where ordinal = 0 into is_valid;
	is_valid = 1 - abs(sign(is_valid));

    drop table _casx;

	return is_valid;

end;


/* function is_valid_cas */
drop function if exists v1.is_valid_cas(varchar);

create or replace function v1.is_valid_cas( in _cas varchar(16) )
returns smallint
language plpgsql
as $body$

declare
    ccc int;
    is_valid smallint;	

begin

    -- validate syntax: there must be
	if not regexp_like(_cas, '\d{2,7}-\d\d-\d') then return 0; end if;

    -- validate checksum (https://en.wikipedia.org/wiki/CAS_Registry_Number)
	create temporary table _casx
	( ordinal smallint not null generated always as identity (minvalue 0),
      digit   smallint not null );

    insert into _casx(digit)
    select cast(digit[1] as smallint)
      from regexp_matches( reverse(_cas), '\d', 'g' ) as digit;

    select sum(ordinal*digit) % 10 from _casx into ccc;
    select digit-ccc from _casx where ordinal = 0 into is_valid;
	is_valid = 1 - abs(sign(is_valid));

    drop table _casx;

	return is_valid;

end;

$body$;
/*** test
select v1.is_valid_cas( '7732-18-5'::varchar );    -- ok: water
select v1.is_valid_cas( '64-17-5'::varchar);       -- ok: ethanol
select v1.is_valid_cas( '439-14-5'::varchar);      -- ok: diazepam
select v1.is_valid_cas( '99685-96-8'::varchar);    -- ok: buckminsterfullerene

select v1.is_valid_cas( '345905-97-7'::varchar );  -- ok:
select v1.is_valid_cas( '3459O5-97-7'::varchar );  -- fail: O, not zero
select v1.is_valid_cas( '345905-97-6'::varchar );  -- fail: checksum
***/


/* function init_load

   Notes:
    This function returns a
*/
drop function if exists v1.init_load(int,timestamptz,varchar,varchar,varchar,int,timestamptz);

create or replace function v1.init_load(
    in _uid                int,
	in _experiment_name    varchar(128) = '',
    in _dt                 timestamptz = now(),
    in _cas_substrate      varchar(128) = '',  -- comma-separated list of CAS numbers
    in _cas_product        varchar(128) = '',  -- comma-separated list of CAS numbers
    in _assay              varchar(128) = '',
    in _mutagenesis_method int = 0,
    in _dt_experiment      timestamptz = null,
	in _csvfile            bytea,
	in _pdbfile            bytea = null,
	in _ciffile            bytea = null
)
returns table ( pkey      int,
                esn       char(6),
                task      varchar(32),
                status    varchar(32),
                details   varchar(128)
              )
language plpgsql
as $body$

declare
    ok bool = True;
    eid int = -1;
	msg varchar(128) = '';
    i smallint;
    s varchar(128);

begin

    -- verify that the user has specified an experiment name
	if( trim(_experiment_name) = '') is not false
	then
	    details = 'You must specify an experiment name.';
	    ok = False;
	end if;

    if ok
	then
        -- split the list of substrate CAS numbers
        i = 1;
        s = trim( both ' ' from split_part(_cas_substrate, ',', i) );

    raise notice 'i: %, s: -->%<--', i, s;

        while s != ''
		loop
            -- verify that we have a valid CAS number
            if not v1.is_valid_cas(s)
		    then
			    details = format('Invalid CAS number: %s', s);
				ok = false;
			end if;
		end loop;		    

        -- iterate
        i = i + 1;
        s = trim( both ' ' from split_part(_cas_substrate, ',', i) );
    end loop;

end;

$body$;
/*** test
select * from v1.init_load( 1, now(),
	'7732-18-5'::varchar,
    '7732-18-5,345905-97-7'::varchar,
	'some assay name'::varchar,
	1, now() );
***/

	
    in _uid int,
    in _dt timestamptz,
    in _cas_substrate varchar(130),   -- comma-separated list of up to 10 CAS numbers
    in _cas_product varchar(130),     -- comma-separated list of up to 10 CAS numbers
    in _assay varchar(128),
    in _mutagenesis_method smallint,
    in _dt_experiment timestamptz
)





		
 




check whether the file exists in the specified upload directory
		filespec = u || f;
        fileinfo = pg_stat_file(filespec, true);  -- (requires su permission)
		s = case when fileinfo is not null then 'completed' else 'failed' end;

		-- conditionally log the result ("upsert)"
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

		-- conditionally log the result ("upsert)"
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



/* procedure do_nothing */
drop procedure if exists v1.do_nothing( int );

create or replace procedure v1.do_nothing(in _uid int )
language plpgsql
as $body$
begin
    raise notice '% nothing', _uid;
end;
$body$;
/*** test
call v1.do_nothing( 12345 );
***/


/* procedure load_csv_file */
drop procedure if exists v1.load_csv_file(int,varchar);

create or replace procedure v1.load_csv_file( in _uid int, in _expt int, in _filespec varchar(320) ) 
language plpgsql
as $body$

declare
    fileinfo varchar(128) = pg_stat_file(_filespec, true);  -- (requires su permission)
    execsql varchar(360) = 'copy _rawcsv from '
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




