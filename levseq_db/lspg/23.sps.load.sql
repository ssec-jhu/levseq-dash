/*
   23.sps.load.sql

   Notes:
    We leave the uploaded CSV, PDB, and CIF files intact in the filesystem.
     There's no good reason to load them as blobs into the database since
     their contents will not be used in relational operations.

     In addition, performance (i.e., delivering them on demand) should be
     better if we keep the files in the filesystem:

     See: https://www.cybertec-postgresql.com/en/binary-data-performance-in-postgresql/)
*/


/* function v1.get_load_dirpath */
drop function if exists v1.get_load_dirpath(int,int,text);

create or replace function v1.get_load_dirpath
( in _uid int,
  in _eid int,
  in _filename text )
returns text
language plpgsql
as $body$

declare
    grp      int;
	dirpath  text;
	filepath text;
	grpname  text;
	expname  text;

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

    -- verify that the group/experiment/filename tuple is unique
	filepath = dirpath || _filename;
    if exists (select *
                 from v1.data_files t0
                where t0.filespec = filepath)
    then
        -- the specified file has already been uploaded
        select t0.experiment_name into expname
          from v1.experiments t0
         where t0.pkey = _eid;
		  
        raise exception 'Duplicate filename % for group=%, experiment=%', _filename, grpname, expname;

    end if;

	-- conditionally verify that the group/experiment/extension tuple is unique
	if right(_filename,4) = '.csv'
	then
        if exists (select *
                     from v1.data_files t0
                    where t0.gid = grp
                      and t0.eid = _eid
                      and right(filespec,4) = '.csv')
        then
            -- the specified file has already been uploaded
            select t0.experiment_name into expname
              from v1.experiments t0
             where t0.pkey = _eid;
		  
            raise exception 'Experiment data in % has already been loaded for group=%, experiment=%',
		                    _filename, grpname, expname;
        end if;
    end if;

    -- return the slash-terminated directory path
    return dirpath;

end;
$body$;
/*** test
select v1.get_load_dirpath( 5, 1, 'tiny.csv' );
***/

/* function is_valid_cas */
drop function if exists v1.is_valid_cas(text);

create or replace function v1.is_valid_cas( in _cas text )
returns smallint
language plpgsql
as $body$

declare
    ccc int;
    is_valid smallint;	

begin

    -- validate CAS syntax
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

/* procedure v1.load_experiment_data

   The call to copy ... from requires either superuser or
    pg_read_server_files permission.
*/
drop procedure if exists v1.load_experiment_data(text);

create or replace procedure v1.load_experiment_data( in _filespec text )
language plpgsql
as $body$

declare
    execsql  text = 'copy _rawcsv from '
                    || quote_literal(_filespec)
                    || ' with (format csv, header match)';

begin
    /* load csv into a temporary table */
    create temporary table _rawcsv
    ( "id"                        text             not null,
      barcode_plate               integer          not null,
      cas_number                  text             not null,
      plate                       text             not null,
      well                        text             not null,
      alignment_count             smallint         not null,
      nucleotide_mutation         text             null,
      amino_acid_substitutions    text             null,
      alignment_probability       double precision null,
      average_mutation_frequency  double precision null,
      p_value                     double precision null,
      p_adj_value                 double precision null,
      nt_sequence                 text             null,
      aa_sequence                 text             null,
      x_coordinate                double precision null,
      y_coordinate                double precision null,
      fitness_value               double precision null );

    execute execsql;

    -- TODO: spread the data to the tables


    -- TODO: zap the temporary table
    drop table _rawcsv;

end;
$body$;
/*** test
***/

/* function v1.load_file

   The call to pg_stat_file requires either superuser or
    pg_read_server_files permission.
*/
drop function if exists v1.load_file(int,int,text);

create or replace function v1.load_file
( in _uid int,
  in _eid int,
  in _filespec text )
returns int
language plpgsql
as $body$

declare
    cb_file  int;
    grp      int;
    grpname  text;
    expname  text;
	filename text;
	m        text[];

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

    -- ensure that the specified file exists and is not empty
    select "size" into cb_file from pg_stat_file(_filespec, true);
    if coalesce(cb_file, 0) = 0
    then
        m = regexp_split_to_array( _filespec, '/');
        filename = m[cardinality(m)];
        raise exception 'File % missing or empty (group=%, experiment=%)',
                        filename, grpname, expname;
    end if;

    -- conditionally extract data from the uploaded file
    if right(_filespec,4) = '.csv'
	then
	    call v1.load_experiment_data( _filespec );
        end if;

        -- record successful upload
        insert into v1.data_files( gid, eid, filespec, dt_upload, uid, filesize )
            values ( grp, _eid, _filespec, now(), _uid, cb_file );

    -- return the number of bytes in the file
    return cb_file;

end;
$body$;
/*** test
drop table _rawcsv;
select v1.load_file( 1, 1, '/mnt/Data/ssec-devuser/uploads/G00001/E00001/tiny.csv' );
select * from _rawcsv;

select count(*) from _rawcsv;
select count(*) as n, nt_sequence, count(*)
  from _rawcsv
group by nt_sequence;

truncate table v1.data_files;
select * from v1.data_files;
***/












/****************************************
*******************************************************/

/* function v1.load_file  asdfasdfasdf;lkasdjf; */
drop function if exists v1.load_file(int,int,text,text);

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





