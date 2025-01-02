/*
   22.sps.data.sql
*/

/* function get_mutagenesis_methods */
drop function if exists v1.get_mutagenesis_methods();

create or replace function v1.get_mutagenesis_methods()
returns table
( pkey         smallint,
  "method"     text,
  abbreviation text
)
language plpgsql
as $body$

begin

    return query
    select t0.pkey, t0."method", t0.abbreviation
      from v1.mutagenesis_methods t0
  order by t0."method";

end;
$body$;
/*** test
select * from v1.get_mutagenesis_methods();
***/

/* function get_assays */
drop function if exists v1.get_assays();

create or replace function v1.get_assays()
returns table
( pkey   smallint,
  assay  text
)
language plpgsql
as $body$

begin

    return query
    select t0.pkey, t0.assay
      from v1.assays t0
  order by t0.assay;

end;
$body$;
/*** test
select * from v1.get_assays();
select * from v1.experiments;
select * from v1.get_user_experiments( 5 );
***/


/* function get_experiments */
drop function if exists v1.get_experiments(int,int,int);
create or replace function v1.get_experiments( in _eid int, in _uid int, in _gid int )
returns table
( eid                int,
  experiment_name    text,
  dt_experiment      timestamptz,
  dt_load            timestamptz,
  n_plates           int,
  cas_substrate      text,
  cas_product        text,
  mutagenesis_method text,
  assay              text,
  filenames          text
)
language plpgsql
as $body$
begin

    -- return a list of experiments, limited to the specified experiment ID and/or
    --  the specified LevSeq user ID and/or the specified group ID
    return query
    select t0.pkey, t0.experiment_name, t0.dt_experiment, t0.dt_load,
           (select count(*)::int from v1.plates u0 where u0.pkexp = t0.pkey),
           (select string_agg(u2.cas, ',')
              from v1.experiment_cas u1
              join v1.cas u2 on u2.pkey = u1.pkcas
             where u1.pkexp = t0.pkey
               and u1.substrate),
           (select string_agg(u2.cas, ',')
              from v1.experiment_cas u1
              join v1.cas u2 on u2.pkey = u1.pkcas
             where u1.pkexp = t0.pkey
               and u1.product),
           t1.abbreviation, t2.technique,
           array_to_string(v1.files_in_dir(v1.get_experiment_dirpath(t3.pkey,t0.pkey)), ', ')
      from v1.experiments t0
      join v1.mutagenesis_methods t1 on t1.pkey = t0.mutagenesis_method
      join v1.assays t2 on t2.pkey = t0.assay
	  join v1.users t3 on t3.pkey = t0.uid
     where t0.pkey = coalesce( _eid, t0.pkey )
       and t3.pkey = coalesce( _uid, t3.pkey )
       and t3.gid = coalesce( _gid, t3.gid );

end;
$body$;
/*** test
select * from _expdirs;
select * from v1.experiments;
select * from v1.get_experiments( null, null, null );
select * from v1.get_experiments( 60, null, null );    -- eid
select * from v1.get_experiments( null, 5, null );     -- uid
select * from v1.get_experiments( null, null, 1 );     -- gid
***/


/* function get_experiment_e */
drop function if exists v1.get_experiments_e(int);
create or replace function v1.get_experiments_e( in _eid int )
returns table
( eid                int,
  experiment_name    text,
  dt_experiment      timestamptz,
  dt_load            timestamptz,
  n_plates           int,
  cas_substrate      text,
  cas_product        text,
  mutagenesis_method text,
  assay              text,
  filenames          text
)
language plpgsql
as $body$
begin

    -- the returned list contains only the specified experiment
    return query
    select *
      from v1.get_experiments( _eid, null, null );

end;
$body$;
/*** test
select * from v1.get_experiments_e( null );
select * from v1.get_experiments_e( 66 );
***/

/* function get_experiments_u */
drop function if exists v1.get_experiments_u(int);
create or replace function v1.get_experiments_u( in _uid int )
returns table
( eid                int,
  experiment_name    text,
  dt_experiment      timestamptz,
  dt_load            timestamptz,
  n_plates           int,
  cas_substrate      text,
  cas_product        text,
  mutagenesis_method text,
  assay              text,
  filenames          text
)
language plpgsql
as $body$
begin

    -- the returned list contains experiments for the specified LevSeq user
    return query
    select *
      from v1.get_experiments( null, _uid, null );

end;
$body$;
/*** test
select * from v1.get_experiments_u( 4 );
select * from v1.get_experiments_u( 2 );
***/

/* function get_experiments_g */
drop function if exists v1.get_experiments_g(int);
create or replace function v1.get_experiments_g( in _gid int )
returns table
( eid                int,
  experiment_name    text,
  dt_experiment      timestamptz,
  dt_load            timestamptz,
  n_plates           int,
  cas_substrate      text,
  cas_product        text,
  mutagenesis_method text,
  assay              text,
  filenames          text
)
language plpgsql
as $body$
begin

    -- the returned list contains experiments for the specified LevSeq group
    return query
    select *
      from v1.get_experiments( null, null, _gid );

end;
$body$;
/*** test
select * from v1.get_experiments_g( 1 );
select * from v1.get_experiments_g( 2 );
***/


/* function get_experiments_ug */
drop function if exists v1.get_experiments_ug(int);
create or replace function v1.get_experiments_ug( in _uid int )
returns table
( eid                int,
  experiment_name    text,
  dt_experiment      timestamptz,
  dt_load            timestamptz,
  n_plates           int,
  cas_substrate      text,
  cas_product        text,
  mutagenesis_method text,
  assay              text,
  filenames          text
)
language plpgsql
as $body$
declare
    grp int;

begin

    -- the returned list contains experiments for everyone in the
    --  specified LevSeq user's group
	select gid into grp
      from v1.users
     where pkey = _uid;

    return query
    select *
      from v1.get_experiments( null, null, coalesce(grp,0) );

end;
$body$;
/*** test
select * from v1.users;
select * from v1.experiments;
select * from v1.get_experiments_ug( 1 );
select * from v1.get_experiments_ug( 2 );
select * from v1.get_experiments_ug( 4 );
select * from v1.get_experiments_ug( 5 );
***/


/* function v1.get_experiment_parent_sequence */
drop function if exists v1.get_experiment_parent_sequence(int);
create or replace function v1.get_experiment_parent_sequence( in _eid int )
returns table
( seqnt text,
  seqaa text
)
language plpgsql
as $body$
begin

    return query
    select distinct t1.seqnt, t1.seqaa
      from v1.parent_sequences t0
      join v1.reference_sequences t1 on t1.pkey = t0.pkseq
     where t0.pkexp = _eid;

end;
$body$;
/*** test
select * from v1.parent_sequences;
select * from v1.reference_sequences;
select * from v1.get_experiment_parent_sequence( 47 );
select v1.get_experiment_parent_sequence( 51 );
***/


/* function v1.get_experiment_alignments */
drop function if exists v1.get_experiment_alignments(int);
create or replace function v1.get_experiment_alignments( in _eid int )
returns table
( plate           text,
  barcode_plate   int,
  well            text,
  alignment_count int
)
language plpgsql
as $body$
begin

    return query
    select distinct t1.plate, t0.barcode_plate, t0.well, t0.alignment_count
      from v1.variants t0
      join v1.plates t1 on t1.pkey = t0.pkplate
     where t0.pkexp = _eid
  order by t1.plate, t0.barcode_plate, t0.well;

end;
$body$;
/*** test
select * from v1.variants;
select * from v1.plates;
select * from v1.experiments;
select * from v1.get_experiment_alignments( 60 );
***/