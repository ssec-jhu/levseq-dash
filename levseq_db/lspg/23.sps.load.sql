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

/* function is_valid_cas */
drop function if exists v1.is_valid_cas(text);

create or replace function v1.is_valid_cas( in _cas text )
returns boolean
language plpgsql
as $body$

declare
    ccc int;
    is_valid boolean;	

begin

    -- validate CAS syntax
	if not regexp_like(_cas, '\d{2,7}-\d\d-\d') then return 0; end if;

    -- validate checksum (https://en.wikipedia.org/wiki/CAS_Registry_Number)
	create temporary table _casx
	( ordinal smallint not null generated always as identity (minvalue 0),
      digit   smallint not null );

    -- there is one row for each digit; the ordinals correspond to right-to-left
	--  positions of digits in the string
    insert into _casx(digit)
    select cast(digit[1] as smallint)
      from regexp_matches( reverse(_cas), '\d', 'g' ) as digit;

    -- compute the checksum
    select sum(ordinal*digit) % 10 from _casx into ccc;

	-- the checksum is valid if it matches the final cas digit
    select (digit=ccc) from _casx where ordinal = 0 into is_valid;

    drop table _casx;

	return is_valid;

end;
$body$;
/*** test
select v1.is_valid_cas( '7732-18-5' );    -- ok: water
select v1.is_valid_cas( '64-17-5');       -- ok: ethanol
select v1.is_valid_cas( '439-14-5');      -- ok: diazepam
select v1.is_valid_cas( '99685-96-8');    -- ok: buckminsterfullerene
select v1.is_valid_cas( '57-88-5');       -- ok: cholesterol

select v1.is_valid_cas( '345905-97-7' );  -- ok:
select v1.is_valid_cas( '3459O5-97-7' );  -- fail: O, not zero
select v1.is_valid_cas( '345905-97-6' );  -- fail: checksum
***/

/* function is_valid_cas_csv */
drop function if exists v1.is_valid_cas_csv( text );

create or replace function v1.is_valid_cas_csv( _cascsv text )
returns text
language plpgsql
as $body$

declare
	details text = '';
    i smallint;
	s text;

begin
    -- split the list of comma-separated substrate CAS numbers
    i = 1;
    s = trim( both ' ' from split_part(_cascsv, ',', i) );

    raise notice 'i: %, s: -->%<--', i, s;

    while (details = '') and (s != '')
    loop
        -- verify that we have a valid CAS number
        if not v1.is_valid_cas(s)
        then
            details = format( 'Invalid CAS number ''%s''', s );
        end if;

        -- iterate
        i = i + 1;
        s = trim( both ' ' from split_part(_cascsv, ',', i) );
    end loop;

    if (details != '') and (strpos( _cascsv, ',' ) > 0)
	then
	    details = details || ' in ''' || _cascsv || '''';
	end if;
	
    return details;
	
end;
$body$;
/*** test
select v1.is_valid_cas_csv( '7732-18-5' );                         -- ok
select v1.is_valid_cas_csv( '7732-18-5,64-17-5,439-14-5' );        -- ok
select v1.is_valid_cas_csv( ' 7732-18-5 , 64-17-5 , 439-14-5 ' );  -- ok

select v1.is_valid_cas_csv( '' );
select v1.is_valid_cas_csv( '7732-18-4' );                         -- bad check digit
select v1.is_valid_cas_csv( '7732-19-5,64-17-5');                  -- bad CAS number
select v1.is_valid_cas_csv( '7732-18-5,641-17-5,439-14-5');        -- bad CAS number
***/
    
/* function init_load

   Notes:
    This function returns a unique experiment ID.
*/
-- drop function if exists v1.init_load(int,text,timestamptz,int,int,text,text);
create or replace function v1.init_load
(
  in _uid                int,
  in _experiment_name    text,
  in _dt_experiment      timestamptz,
  in _assay              int,
  in _mutagenesis_method int,
  in _cas_substrate      text,  -- comma-separated list of CAS numbers
  in _cas_product        text   -- comma-separated list of CAS numbers
)
returns int
language plpgsql
as $body$

declare
    details text = '';
	dt_prev timestamptz;
	new_eid int;
	
begin

    -- verify that all the required elements are non-null and not empty strings
	_experiment_name = trim(_experiment_name);
	if( _experiment_name = '') is not false
	then
        details = 'missing experiment name.';
	end if;

    if details = '' then
        if( _dt_experiment is null ) then details = 'missing experiment date'; end if;
    end if;

    if details = '' then
        if( _assay is null ) then details = 'assay method not specified'; end if;
    end if;

    if details = '' then details = v1.is_valid_cas_csv( _cas_substrate ); end if;
    if details = '' then details = v1.is_valid_cas_csv( _cas_product ); end if;

	if exists (select *
                 from v1.experiments t0
                where t0.uid = _uid
                  and t0.experiment_name = _experiment_name)
    then
        -- ensure that the user has not already used the specified experiment name
	    select dt_experiment into dt_prev
		  from v1.experiments t0
         where t0.uid = _uid
           and t0.experiment_name = _experiment_name;
		   
        details = format( '''%s'' identifies a previous experiment dated %s',
                          _experiment_name, to_char(dt_prev, 'DD-Mon-YYYY') );
    end if;

    -- throw an exception if anything failed validation
    if details != ''
	then
        raise exception 'cannot initialize experiment metadata: %', details;
    end if;

    -- get a new primary key for the v1.experiments table
    new_eid = nextval( 'v1.experiments_pkey_seq' );

    -- zap all previous metadata in the "pending" table for all other
	--  pending uploads by the LevSeq user
	delete from v1.experiments_pending
     where uid = _uid;

    -- add the experiment metadata to the "pending" table
    insert into v1.experiments_pending
          ( eid, uid, experiment_name,
            assay, mutagenesis_method, dt_experiment,
            cas_substrate, cas_product )
    values( new_eid, _uid, _experiment_name,
            _assay, _mutagenesis_method, _dt_experiment,
            _cas_substrate, _cas_product );

    -- return the pending experiment ID
    return new_eid;

end;
$body$;
/*** test
select * from v1.experiments_pending;
truncate table v1.experiments_pending;
select * from v1.users;
select v1.init_load( 5, 'an experiment', '2024-12-24', 8, 1, '7732-18-5', '64-17-5,439-14-5' );
select * from v1.experiments_pending;

select nextval( 'v1.experiments_pkey_seq' );					
select * from v1.experiments;
insert into v1.experiments (uid, experiment_name, assay, mutagenesis_method, dt_experiment)
     values (5, 'whatever', 20, 2, '2020-12-20' );
insert into v1.experiments overriding system value values (3, now(), 'bla', 2, 1 );
***/


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
	cb_file  int;
	filespec text;
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
	filespec = dirpath || _filename;
    select "size" into cb_file from pg_stat_file(filespec, true);
    if cb_file > 0
    then
        -- the specified file has already been uploaded
        select t0.experiment_name into expname
          from v1.experiments t0
         where t0.pkey = _eid;

        raise exception 'Duplicate filename % for group=%, experiment ID=% (%)',
                        _filename, grpname, _eid, coalesce(expname, 'pending');
    end if;

	-- conditionally verify that the group/experiment/extension tuple is unique
	if right(_filename,4) = '.csv'
	then
        if exists (select *
                     from v1.experiments t0
                     join v1.users t1 on t1.pkey = _uid
                    where t0.experiment_name = expname
                      and t1.gid = grp)
        then
            -- the specified file has already been uploaded by the user or
			--  by another member of the user's group
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

/* procedure v1.save_experiment_cas */
drop procedure if exists v1.save_experiment_cas(int,int);

create or replace procedure v1.save_experiment_cas
( in _uid int,
  in _eid int )
language plpgsql
as $body$

declare
    bad_cas text;

begin

    /* verify that CAS numbers in the data match the user-specified lists */

	-- get CAS numbers from user-specified metadata
    drop table if exists _rawcas;
    create temporary table _rawcas
    ( cas       text not null,
      substrate bool not null default False,
      product   bool not null default False,
	  n         int  not null default 0 );

    insert into _rawcas (cas, substrate)
    select unnest(regexp_matches( cas_substrate, '\d+-\d+-\d', 'g')), True
      from v1.experiments_pending
     where eid = _eid
       and uid = _uid;

    insert into _rawcas (cas, product)
    select unnest(regexp_matches( cas_product, '\d+-\d+-\d', 'g')), True
      from v1.experiments_pending
     where eid = _eid
       and uid = _uid;

    -- get CAS numbers from CSV data
    drop table if exists _csvcas;
	create temporary table _csvcas
    ( cas  text not null,
      n    int  not null );

    insert into _csvcas( cas, n )
    select cas_number, count(*) as n
      from _rawcsv
     group by cas_number;
 
	update _rawcas t0
	   set n = t1.n
      from _csvcas t1
	 where t1.cas = t0.cas;

    -- look for user-specified CAS numbers that did not appear in the data
    select cas into bad_cas
      from _rawcas
     where n = 0;

    if bad_cas is not null
	then
        raise exception 'No data for specified CAS number %', bad_cas;
	end if;

    -- look for CAS numbers in the data that were not specified by the user
    select t0.cas into bad_cas
      from _csvcas t0
    except
    select t1.cas
      from _rawcas t1;
 
	if bad_cas is not null
	then
		raise exception 'CAS number % is not identified as substrate or product', bad_cas;
	end if;
	
    /* conditionally add CAS numbers to the reference list */
	insert into v1.cas (cas)
	select cas
      from _rawcas
     where cas not in (select cas from v1.cas);

	/* save CAS numbers for the specified experiment */
	insert into v1.experiment_cas (pkexp, pkcas, substrate, product, n)
	select _eid, t1.pkey, t0.substrate, t0.product, t0.n
      from _rawcas t0
	  join v1.cas t1 on t1.cas = t0.cas
on conflict (pkexp,pkcas) do
    update set substrate = excluded.substrate,
               product = excluded.product,
               n = excluded.n;

    return;
end;
$body$;
/*** test
truncate table v1.cas cascade;
truncate table v1.experiment_cas cascade;
select * from v1.cas;
select * from v1.experiment_cas;
***/

/* procedure v1.save_parent_sequences */
-- drop procedure if exists v1.save_parent_sequences cascade;
create or replace procedure v1.save_parent_sequences( in _eid int )
language plpgsql
as $body$
begin

    /* save parent sequences as reference sequences */
    with cte as (select nt_sequence, aa_sequence, count(*)
                   from _rawcsv
                  where nucleotide_mutation like '%PARENT%'
               group by nt_sequence, aa_sequence)
        insert into v1.reference_sequences (seqnt, seqaa)
		select nt_sequence, aa_sequence
		  from cte
   on conflict (seqnt) do nothing;

    /* save reference sequences for each plate/barcode_plate combination */
    insert into v1.parent_sequences(pkexp, pkplate, barcode_plate, pkseqs, n)
	select _eid, t1.pkey, t0.barcode_plate, t2.pkey, count(*)
	  from _rawcsv t0
      join v1.plates t1 on t1.plate = t0.plate_name
	  join v1.reference_sequences t2 on t2.seqnt = t0.nt_sequence
	 where t0.nucleotide_mutation like '%PARENT%'
  group by t1.pkey, t0.barcode_plate, t2.pkey
on conflict (pkexp, pkplate, barcode_plate) do
    update set pkseqs = excluded.pkseqs,
               n = excluded.n;
end;
$body$;
/*** test
***/


/* procedure v1.save_mutations */
-- drop procedure if exists v1.save_mutations(int);
create or replace procedure v1.save_mutations( in _eid int )
language plpgsql
as $body$
begin

    -- delete any previously-loaded rows for the specified experiment
    delete from v1.variants t0 where pkexp = _eid;

    -- insert new rows for the specified experiment into the table of variants
    insert into v1.variants( pkexp, pkplate, barcode_plate, well,
                             alignment_count, parent_seq,
                             alignment_probability, avg_mutation_freq,
                             p_value, p_adj_value,
                             x_coordinate, y_coordinate )
    select distinct _eid, t1.pkey, t0.barcode_plate,
                    left(t0.well,1) || lpad(substring(t0.well,2),2,'0'),
                    alignment_count, t2.pkey,
                    alignment_probability, average_mutation_frequency,
		            case when p_value >= 1E-5 then p_value else 0.0 end case,
		            case when p_adj_value >= 1e-5 then p_adj_value else 0.0 end case,
		            x_coordinate, y_coordinate
      from _rawcsv t0
	  join v1.plates t1 on t1.plate = t0.plate_name
	  join v1.parent_sequences t2 on t2.pkexp = _eid
                                     and
                                     t2.pkplate = t1.pkey
                                     and
                                     t2.barcode_plate = t0.barcode_plate;

    /* build a table of mutations for each observed substrate/product pair */

	-- bind nucleotide variants and amino acid substitutions to each plate/barcode/well
    drop table if exists _rawvm1;
    create temporary table _rawvm1
    ( pkvar                    int  not null,
      nucleotide_mutation      text not null,  -- (e.g., 'T124C_G269T_G369T_G519C')
      amino_acid_substitutions text not null   -- (e.g., 'C42R_G90V_K123N_L173F')
    );
	
    insert into _rawvm1( pkvar, nucleotide_mutation, amino_acid_substitutions)
    select distinct t2.pkey, t0.nucleotide_mutation, amino_acid_substitutions
      from _rawcsv t0
      join v1.plates t1 on t1.plate = t0.plate_name
      join v1.variants t2 on t2.pkexp = _eid
                             and
                             t2.pkplate = t1.pkey
                             and
                             t2.barcode_plate = t0.barcode_plate
                             and
                             t2.well = left(t0.well,1) || lpad(substring(t0.well,2),2,'0')
     where regexp_match( nucleotide_mutation, '([ACGT]\d+[ACGTDEL]+)') is not null;

    -- in a CTE, generate a row for each nucleotide variant; then shred each
    --  nucleotide and amino acid variation into its components
    drop table if exists _rawvm2;
    create temporary table _rawvm2
    ( pkvar int not null,
      nm3    text[] not null,
      pm3    text[] null );
  
    with cte as (select pkvar,
                        unnest(regexp_matches( nucleotide_mutation, '([ACGT]\d+[ACGTDEL]+)', 'g')) as nm1,
                        unnest(regexp_matches( amino_acid_substitutions, '([A-Z]\d+[A-Z\*])', 'g')) as pm1
                   from (select pkvar, nucleotide_mutation, amino_acid_substitutions
                           from _rawvm1)
                )
        insert into _rawvm2( pkvar, nm3, pm3 )
        select pkvar,
               regexp_matches( nm1, '([ACGT]|INS|DEL)(\d+)([ACGT]|INS|DEL)'),
               regexp_matches( pm1, '([A-Z])(\d+)([A-Z]|\*)')
          from cte;

    -- delete previously-stored mutation details (this should normally be a noop)
    delete from v1.variant_mutations
          where pkvar in (select distinct pkvar from _rawvm2);
	
    -- save mutation details for each variant
    insert into v1.variant_mutations( pkvar, vartype, varposnt,
                                      varparnt, varsubnt,
                                      varposaa, varparaa, varsubaa)
    select pkvar,
           case when nm3[1] = 'INS' or nm3[3] = 'INS' then 'i'
                when nm3[1] = 'DEL' or nm3[3] = 'DEL' then 'd'
                else 's'
           end,
           nm3[2]::int,
           case when position(nm3[1] in 'ACGT') > 0 then nm3[1] else null end,
           case when position(nm3[3] in 'ACGT') > 0 then nm3[3] else null end,
           case when pm3 is not null then pm3[2]::int else null end,
           case when pm3 is not null then pm3[1] else null end,
           case when pm3 is not null then pm3[3] else null end
      from _rawvm2;
end;
$body$;
/*** test
select * from v1.variant_mutations
***/


/* procedure v1.save_fitness_values */
-- drop procedure if exists v1.save_fitness_values(int);
create or replace procedure v1.save_fitness_values( in _eid int )
language plpgsql
as $body$
begin

    -- delete previously-stored fitness values (this should normally be a noop)
    delete from v1.fitness
          where pkvar in (select pkey from v1.variants where pkexp = _eid);
		  
    insert into v1.fitness( pkvar, pkexpcas, fitness )	
    select t2.pkey, t4.pkey, t0.fitness_value
      from _rawcsv t0
      join v1.plates t1 on t1.plate = t0.plate_name
      join v1.variants t2 on t2.pkexp = _eid
                             and
                             t2.pkplate = t1.pkey
                             and
                             t2.barcode_plate = t0.barcode_plate
                             and
                             t2.well = left(t0.well,1) || lpad(substring(t0.well,2),2,'0')
      join v1.cas t3 on t3.cas = t0.cas_number
      join v1.experiment_cas t4 on t4.pkcas = t3.pkey
     where t0.fitness_value is not null;

end;
$body$;
/*** test
select * from v1.fitness
***/

/* procedure v1.load_experiment_data

   The call to copy ... from requires either superuser or
    pg_read_server_files permission.
*/
-- drop procedure if exists v1.load_experiment_data(int,int,text);
create or replace procedure v1.load_experiment_data
( in _uid int,
  in _eid int,
  in _filespec text )
language plpgsql
as $body$

declare
    execsql  text = 'copy _rawcsv ("id", barcode_plate, cas_number, plate, well,'
                    || ' alignment_count, nucleotide_mutation, amino_acid_substitutions,'
                    || ' alignment_probability, average_mutation_frequency, p_value,'					
                    || ' p_adj_value, nt_sequence, aa_sequence, x_coordinate, y_coordinate,'
                    || ' fitness_value)'					
                    || ' from '
                    || quote_literal(_filespec)
                    || ' with (format csv, header match)';
begin

    if not exists (select *
                     from v1.experiments_pending
                    where eid = _eid
                          and
                          uid = _uid)
    then						  
        raise exception 'missing experiment metadata for user %, experiment ID %',
                        _uid, _eid;
    end if;
	
    /* Load csv into a temporary table.

       We can extract the plate string from either of the "id" and "plate"
        columns, which are formatted like this:

            "id":    <plate>-<barcode_plate>-<well>
            "plate": <plate>-<barcode_plate>

        For example:
            "id":            20240422-ParLQ-ep1-300-1-A1
            "plate":         20240422-ParLQ-ep1-300-1
            "barcode_plate": 1
            "well":          A1
            --->             20240422-ParLQ-ep1-300

        Here we use a regex to capture the given "plate" string without
         the trailing "barcode_plate" value.
    */
	drop table if exists _rawcsv;
    create temporary table _rawcsv
    ( ordinal                     int              not null generated always as identity,
      plate_name                  text             generated always as (
                                                    (regexp_match(plate, '([\w\W]+)-\d+$'))[1]
                                                   ) stored,
	  "id"                        text             not null,
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

    /* add a new row to the experiments list; if a row already exists for the
        specified experiment ID and user ID, we update the existing row */
    insert into v1.experiments( pkey, uid, experiment_name, assay, mutagenesis_method, dt_experiment, dt_load)
           overriding system value
	select eid, uid, experiment_name, assay, mutagenesis_method, dt_experiment, dt_load
      from v1.experiments_pending
     where eid = _eid
       and uid = _uid
on conflict (pkey) do
    update set experiment_name = excluded.experiment_name,
               assay = excluded.assay,
               mutagenesis_method = excluded.mutagenesis_method,
               dt_experiment = excluded.dt_experiment,
               dt_load = excluded.dt_load;

    /* save CAS numbers */
    call v1.save_experiment_cas( _uid, _eid );

    /* save plate names */
    delete from v1.plates where pkexp = _eid;

	with cte as (select distinct plate_name
                   from _rawcsv)
        insert into v1.plates(pkexp, plate)
        select _eid, plate_name
          from cte;

	/* save parent sequences */
	call v1.save_parent_sequences( _eid );

    /* save mutation data */
	call v1.save_mutations( _eid );

	/* save fitness values */
	call v1.save_fitness_values( _eid );
	
    -- zap all previous metadata in the "pending" table for...
	--  - the specified experiment
	--  - any other pending uploads by any LevSeq user that are over 24 hours old
	delete from v1.experiments_pending
     where eid = _eid
        or dt_load < (now() - interval '24 hours');

end;
$body$;
/*** test
call v1.load_experiment_data( 5, 28, '/mnt/Data/lsdb/uploads/G00002/E00028/flatten_ep_processed_xy_cas.csv');

select * from _rawcsv
select * from _rawcas
select * from _csvcas
select * from v1.experiments
select * from v1.experiments_pending
select * from v1.reference_sequences
select * from v1.parent_sequences
select * from v1.plates
select * from v1.variants
select * from v1.fitness


select varposnt, count(*) as n
  from v1.variant_mutations
group by varposnt
order by n desc;


update v1.experiments_pending set cas_product = '395683-37-1' where eid = 28


select * from v1.cas;
select * from v1.experiments_pending;
select * from v1.experiment_cas;

select alignment_count, amino_acid_substitutions, count(*)
  from _rawcsv
 group by alignment_count, amino_acid_substitutions
 order by alignment_count, amino_acid_substitutions

select * from _rawcsv where amino_acid_substitutions = '-'

 select cas_number, count(*) as n
      from _rawcsv
     group by cas_number;
	 select *
	  from _csvcas
     where cas not in (select cas from _rawcas);
	 select cas from _rawcas
	 select cas from _csvcas
***/

/* function v1.load_file

   The call to pg_stat_file requires either superuser or
    pg_read_server_files permission.
*/
-- drop function if exists v1.load_file(int,int,text);
create or replace function v1.load_file
( in _uid int,
  in _eid int,
  in _filespec text )
returns int
language plpgsql
as $body$

declare
    grp           int;
    grpname       text;
    expname       text;
	filespec_eid  int;
    cb_file       int;
	filename      text;
	m             text[];

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

    -- validate the experiment ID against the filespec
    select cast((regexp_match( _filespec, '/E(\d+)/') )[1] as int) into filespec_eid;
	if filespec_eid != _eid then
        raise exception 'inconsistent file specification ''%'' for experiment ID %',
                        _filespec, _eid;
    end if;	 

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

        -- ensure that we still have metadata for the specified experiment ID
	    if not exists (select * from v1.experiments_pending where eid = _eid) then
            raise exception 'missing metadata for experiment ID %', _eid;
        end if;

        call v1.load_experiment_data( _uid, _eid, _filespec );
    end if;

    -- return the number of bytes in the file
    return cb_file;

end;
$body$;
/*** test
drop table _rawcsv;
select v1.load_file( 1, 1, '/mnt/Data/ssec-devuser/uploads/G00001/E00014/tiny.csv' );
select * from _rawcsv;

select count(*) from _rawcsv;
select count(*) as n, nt_sequence, count(*)
  from _rawcsv
group by nt_sequence;

truncate table v1.data_files;
select * from v1.data_files;

***/
