/*
   21.sps.ref.sql
*/


/* function get_mutagenesis_methods */
drop function if exists v1.get_mutagenesis_methods();

create or replace function v1.get_mutagenesis_methods()
returns table( pkey               smallint,
               mutagenesis_method text )
language plpgsql
as $body$
begin
    return query
    select t0.pkey, "method"
      from v1.mutagenesis_methods t0;
end;
$body$;
/*** test
select * from v1.get_mutagenesis_methods();
***/

/* function get_assays */
drop function if exists v1.get_assays();

create or replace function v1.get_assays()
returns table( pkey  smallint,
               assay text )
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
***/
