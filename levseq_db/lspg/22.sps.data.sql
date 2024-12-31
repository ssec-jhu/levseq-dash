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
-- drop function if exists v1.get_user_experiments(int);
create or replace function v1.get_user_experiments( in _uid int )
returns table
( "id"               int,       -- column named "id" to serve as a Dash DataTable row index
  experiment_name    text,
  dt_experiment      timestamptz,
  dt_load            timestamptz,
  n_plates           int,
  cas_substrate      text,
  cas_product        text,
  mutagenesis_method text,
  assay              text
)
language plpgsql
as $body$
begin

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
           t1.abbreviation, t2.technique
      from v1.experiments t0
      join v1.mutagenesis_methods t1 on t1.pkey = t0.mutagenesis_method
      join v1.assays t2 on t2.pkey = t0.assay
     where t0.uid = _uid;

end;
$body$;
/*** test
select * from v1.experiments;
select * from v1.get_user_experiments( 5 );
select * from v1.get_user_experiments( null );
***/


/* function get_user_group_experiments */
-- drop function if exists v1.get_user_group_experiments(int);
create or replace function v1.get_user_group_experiments( in _uid int )
returns table
( "id"               int,    -- column named "id" to serve as a Dash DataTable row index
  experiment_name    text,
  dt_experiment      timestamptz,
  dt_load            timestamptz,
  n_plates           int,
  cas_substrate      text,
  cas_product        text,
  mutagenesis_method text,
  assay              text,
  uid                int,
  username           text
)
language plpgsql
as $body$
begin

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
           t3.pkey, t3.username
      from v1.experiments t0
      join v1.mutagenesis_methods t1 on t1.pkey = t0.mutagenesis_method
      join v1.assays t2 on t2.pkey = t0.assay
	  join v1.users t3 on t3.pkey = t0.uid
	  join v1.users t4 on t4.pkey = _uid
     where t3.gid = t4.gid;

end;
$body$;
/*** test
select * from v1.experiments
select * from v1.usergroups
select * from v1.users
select * from v1.get_user_group_experiments(1);
select * from v1.get_user_group_experiments(2);
select * from v1.get_user_group_experiments(4);
select * from v1.get_user_group_experiments(5);
***/
