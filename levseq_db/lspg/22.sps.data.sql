/*
   22.sps.data.sql
*/


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
select * from v1.get_user_experiments( 1 );
***/
