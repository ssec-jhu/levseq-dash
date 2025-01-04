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


/* function v1.get_experiment_alignment_probabilities */
drop function if exists v1.get_experiment_alignment_probabilities(int);
create or replace function v1.get_experiment_alignment_probabilities( in _eid int )
returns table
( plate                 text,
  barcode_plate         int,
  well                  text,
  alignment_probability double precision
)
language plpgsql
as $body$
begin

    return query
    select t1.plate, t0.barcode_plate, t0.well, t0.alignment_probability
      from v1.variants t0
      join v1.plates t1 on t1.pkey = t0.pkplate
     where t0.pkexp = _eid
  order by t1.plate, t0.barcode_plate, t0.well;

end;
$body$;
/*** test
select * from v1.get_experiment_alignment_probabilities( 79 );
***/


/* function v1.get_experiment_p_values */
drop function if exists v1.get_experiment_p_values(int);
create or replace function v1.get_experiment_p_values( in _eid int )
returns table
( plate          text,
  barcode_plate  int,
  well           text,
  p              double precision,
  p_adj          double precision
)
language plpgsql
as $body$
begin

    return query
    select t1.plate, t0.barcode_plate, t0.well, t0.p_value, t0.p_adj_value
      from v1.variants t0
      join v1.plates t1 on t1.pkey = t0.pkplate
     where t0.pkexp = _eid
  order by t1.plate, t0.barcode_plate, t0.well;

end;
$body$;
/*** test
select * from v1.get_experiment_p_values( 79 );
***/

/* function v1.get_mutation_counts

   The specified CAS number must identify a substrate.
*/
drop function if exists v1.get_mutation_counts(text);
create or replace function v1.get_mutation_counts( in _cas text )
returns table
( posnt        int,
  n_mutations  int
)
language plpgsql
as $body$
begin

    -- build a temporary table of experiment IDs for the specified substrate CAS
	drop table if exists _eidcas;
    create temporary table _eidcas
    ( eid int not null );

    insert _eidcas( eid )
	select t0.pkexp
      from v1.experiment_cas t0
      join v1.cas t1 on t1.pkey = t0.pkcas
     where t0.substrate
       and t1.cas = _cas;

    return query
    select posnt, count(*)
      from v1.mutations t0
      join v1.variants t1 on t1.pkey = t0.pkvar
      join _eidcas t2 on t2.eid = t1.pkexp
     where t1.pkexp

	  select * from v1.mutations
	  select * from v1.variants
	  select * from v1.cas
	  select * from v1.experiment_cas
group by posnt
order by n desc;


/* function v1.get_mutation_counts

   The specified sequence ID must identify a parent (reference) sequence.
*/
drop function if exists v1.get_mutation_counts(int);
create or replace function v1.get_mutation_counts( in _pkseq int )
returns table
( pos         int,
  n_mutations int
)
language plpgsql
as $body$
begin

    return query
    select t0.posnt, count(*)::int as n
      from v1.mutations t0
      join v1.variants t1 on t1.pkey = t0.pkvar
      join v1.parent_sequences t2 on t2.pkey = t1.pkpar
     where t2.pkseq = _pkseq	  
     group by t0.posnt
     order by n desc;

end;
$body$;
/*** test
select * from v1.get_mutation_counts( 1 );
***/


/* function v1.get_variant_sequences

   Notes:
    It would be nice to represent sequences as text[] and update each of them
     "in place" in a table row.  But this doesn't work.

    Apparently an update statement such as this

        update _seqs t0
           set seq[t1.posnt] = t1.subnt
          from _muts t1;
         where t1.pkvar = t0.pkvar;

     only updates the text array once, even if multiple positions are
     encountered in the join.

    For this reason we split each sequence string into a table, do the
     join, and then recompose the strings.

    This implementation returns the entire nucleotide sequence, but it should
     probably be updated at some point:

        - if no experiment ID is specified, limit the result set to experiments
           in the LevSeq user's group
        - either truncate sequences that contain deletions, or else exclude them
           from the result set altogether
        - produce the corresponding amino acid sequence
*/
drop function if exists v1.get_variant_sequences(int,int);
create or replace function v1.get_variant_sequences( in _pkseq int, in _eid int )
returns table
( pkvar           int,
  experiment_name text,
  plate           text,
  barcode_plate   int,
  well            text,
  seqnt           text
)
language plpgsql
as $body$
begin

    -- get the specified reference sequence nucleotides as rows in a table
    drop table if exists _refseqnts;
    create temporary table _refseqnts
    ( pos  int generated always as identity primary key, 
      nt   char(1)
    );

    insert into _refseqnts(nt)
    select string_to_table(t0.seqnt, null)
      from v1.reference_sequences t0;

    -- get a set of reference sequence nucleotides for each mutation of the
    --  specified parent (reference) sequence
    drop table if exists _xseqnts;
    create temporary table _xseqnts
    ( pkvar  int not null,
      pos    int not null, 
      nt     char(1)
    );

    /* initial performance testing indicates that indexing does nothing, but
        if performance ever becomes an issue, we can try this:

        create index ix_xseqnts
                  on _xseqnts
               using btree (pkvar asc, pos asc)
             include (nt);

             cluster _xseqnts using ix_xseqnts;
    */

    /* produce a list of nucleotides and positions for each sequence that contains
        at least one variant (mutation); the CTE produces a row for each such
		sequence */
    with cte as (select distinct t0.pkvar
                   from v1.mutations t0
                   join v1.variants t1 on t1.pkey = t0.pkvar
                   join v1.parent_sequences t2 on t2.pkey = t1.pkpar
                  where t2.pkseq = _pkseq
                    and t1.pkexp = coalesce(_eid, t1.pkexp)
                 )
        insert into _xseqnts( pkvar, pos, nt )
        select t0.pkvar, t1.pos, t1.nt
          from cte t0
    cross join _refseqnts t1
      order by t0.pkvar, t1.pos;

    -- build a temporary table of mutations
	drop table if exists _muts;
	create temporary table _muts
	( pkvar int not null,
      pos   int not null,
      nt    char(1)
	);

    /* (same non-optimization as above)

        create index ix_muts
                  on _muts
         using btree (pkvar asc, pos asc)
       include (nt);
    */

    insert into _muts( pkvar, pos, nt )
    select t0.pkvar, t0.posnt,
           case t0.vartype when 'd' then '*' else t0.subnt end as nt
     from v1.mutations t0
     join v1.variants t1 on t1.pkey = t0.pkvar
     join v1.parent_sequences t2 on t2.pkey = t1.pkpar
    where t2.pkseq = _pkseq
      and t1.pkexp = coalesce(_eid,t1.pkexp)
 order by t0.pkvar, t0.posnt;

    -- from the list of all nucleotides, remove nucleotides at positions
	--  where a mutation exists
    delete from _xseqnts t0
     using _muts t1
     where t0.pkvar = t1.pkvar
       and t0.pos = t1.pos;
   
    -- insert the mutated nucleotides
    insert into _xseqnts(pkvar, pos, nt)
    select t0.pkvar, t0.pos, t0.nt
	  from _muts t0;

    -- generate a result set
	return query
    select t0.pkvar, t2.experiment_name, t3.plate, t1.barcode_plate, t1.well,
           string_agg( t0.nt, null order by t0.pos )
	  from _xseqnts t0
	  join v1.variants t1 on t1.pkey = t0.pkvar
	  join v1.experiments t2 on t2.pkey = t1.pkexp
	  join v1.plates t3 on t3.pkey = t1.pkplate
	 group by t0.pkvar, t2.experiment_name, t3.plate, t1.barcode_plate, t1.well
	 order by t0.pkvar, t2.experiment_name, t3.plate, t1.barcode_plate, t1.well;
	 
end;
$body$;
/*** test
select * from v1.reference_sequences;
select * from v1.experiments;
select * from v1.get_variant_sequences( 1, 83 );
***/
