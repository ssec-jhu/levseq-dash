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
select * from v1.get_user_experiments( 1 );
***/

/* function get_user_experiments */
drop function if exists v1.get_user_experiments(int);

create or replace function v1.get_user_experiments( in _uid int )
returns table ( pkey            int,
                experiment_name text,
                experiment_dt   timestamptz,
                n_plates        int,
                cas_substrate   text,
                cas_product     text,
				assay           text )

language plpgsql
as $body$

--declare

begin

-- return experiment info for the specified user
    return query
    select 1, '* experiment name *', now(), 1,
	          '64-17-5', '439-14-5',
			  '* assay *';

end;
$body$;
/*** test
select * from v1.experiments
select * from v1.get_user_experiments( 1 );
***/
