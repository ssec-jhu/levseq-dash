/*
   20.sps.admin.sql
*/

/* function get_pgid */
drop function v1.get_pgid(varchar);

create or replace function v1.get_pgid( in _wsid varchar(32) )
returns table( impl      varchar(32),
               impl_info varchar(64) )
language plpgsql
as $body$

begin

    return query
	select 'wsid'::varchar, _wsid
	 union
	select 'pgid'::varchar, (regexp_match(version(), '(^.*\s[\d\.]+)\s'))[1];

end;

$body$;
/*** test
select * from v1.get_pgid('LevSeq webservice v1.0');  -- tuples
select v1.get_pgid('LevSeq webservice v1.0');         -- (one column, comma-separated)
***/



/* function get_usernames */
drop function v1.get_usernames();

create or replace function v1.get_usernames()
returns table( json_row json )

/***
returns table ( pkey      int,
                username  varchar(32),
                groupname varchar(32)
              )
***/
language plpgsql
as $body$

begin
/****
    return query
    select t1.pkey, t1.username, t2.groupname
	  from v1.users t1
	  join v1.usergroups t2 on t2.pkey = t1.usergroup
  order by t1.username;
***/


    return query
	select json_build_object('uid',      t1.pkey,
	                         'username', t1.username,
							 'groupname', t2.groupname)
	  from v1.users t1
	  join v1.usergroups t2 on t2.pkey = t1.usergroup
  order by t1.username;

/*****

"json_test"
"{""promotions"" : {""one"": 1, ""two"": 2}, ""items"" : [1,2]}"
select 
select 
    json_build_object('promotions',
                      jsonb_build_object('one', 1, 'two', 2),
                                         'items', ARRAY[1, 2]
                     ) AS json_test;

what about row_to_json ????


  select *
  select json_agg(
          json_build_object(
    t1.pkey, t1.username, t2.groupname
	        from v1.users t1
	        join v1.usergroups t2 on t2.pkey = t1.usergroup)
			);
			
        order by t1.username
		 ) as subquery;

***/
end;

$body$;
/*** test
-- when returning json:
select * from v1.get_usernames();

-- when returning a raw SQL result set:
select * from v1.get_usernames();  -- returns three columns
select v1.get_usernames();         -- returns one column of comma-separated values
                                   --  (embedded commas are NOT escaped!)
select * from v1.users;
***/


/* function get_user_config */
drop function if exists v1.get_user_config(int);

create or replace function v1.get_user_config( _uid int ) 
returns table ( groupname varchar(32),
                upload_dir varchar(320)
              )
language plpgsql
as $body$

begin

    return query
    select t2.groupname, t2.upload_dir
      from v1.users t1
      join v1.usergroups t2 on t2.pkey = t1.usergroup
     where t1.pkey = _uid;

end;

$body$;
/*** test
select * from v1.get_user_config( 1 );
***/


/* procedure save_user_ip */
drop procedure if exists v1.save_user_ip(int,varchar);

create procedure v1.save_user_ip( in _pkey int, in _ip varchar(24) )
language plpgsql 
as $body$

begin
    update v1.users
	   set last_ip = _ip
	 where pkey = _pkey;
end;

$body$;

/*** test
call v1.save_user_ip(2, '123.456.789.000');
select * from v1.users;
***/
