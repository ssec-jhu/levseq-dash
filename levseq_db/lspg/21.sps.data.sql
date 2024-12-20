/*
   21.sps.data.sql
*/


/* function get_user_experiments */
drop function if exists v1.get_user_experiments(int);

create or replace function v1.get_user_experiments( in _uid int )
returns table ( pkey       int,
                dt         timestamptz,
                experiment varchar(64) )
language plpgsql
as $body$

--declare

begin

    -- return experiment load date and name for the specified user
    return query
    select pkey, dt_load, experiment
      from v1.experiments
     where pkey = _uid
  order by dt_load desc

end;

$body$;
/*** test
select * from v1.get_user_experiments( 1 );
***/
