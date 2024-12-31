/*
   21.sps.ref.sql
*/


/* function get_mutagenesis_methods */
drop function if exists v1.get_mutagenesis_methods();

create or replace function v1.get_mutagenesis_methods()
returns table( pkey     smallint,
               "method" text )
language plpgsql
as $body$
begin
    return query
    select t0.pkey, format( '%s - %s', t0.abbreviation, t0."method" )
      from v1.mutagenesis_methods t0;
end;
$body$;
/*** test
select * from v1.get_mutagenesis_methods();
***/

/* function get_assays */
drop function if exists v1.get_assays();

create or replace function v1.get_assays()
returns table
( pkey  smallint,
  assay text
)
language plpgsql
as $body$
begin
    return query
    select t0.pkey, format( '%s (%s)', t0.technique, t0.units )
      from v1.assays t0
  order by t0.pkey;
end;
$body$;
/*** test
select * from v1.assays;
select * from v1.get_assays();
select v1.get_assays();
***/
