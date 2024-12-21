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
	select 'pgid'::varchar, (regexp_match(version(), '(^.*\s[\d\.]+)\s'))[1]
	 union
	select 'pgcu'::varchar, current_user::varchar;

end;

$body$;
/*** test
select * from v1.get_pgid('LevSeq webservice v1.0');  -- tuples
select v1.get_pgid('LevSeq webservice v1.0');         -- (one column, comma-separated)
***/



/* function get_usernames */
drop function v1.get_usernames();

create or replace function v1.get_usernames()
returns table ( pkey      int,
                username  varchar(32),
                groupname varchar(32)
              )
language plpgsql
as $body$

begin

    return query
    select t1.pkey, t1.username, t2.groupname
	  from v1.users t1
	  join v1.usergroups t2 on t2.pkey = t1.usergroup
  order by t1.username;

end;

$body$;
/*** test
select * from v1.get_usernames();  -- returns three columns
select v1.get_usernames();         -- returns one column of comma-separated values
                                   --  (embedded commas are NOT escaped!)
select * from v1.users;
***/


/* function get_user_config */
drop function if exists v1.get_user_config(int);

create or replace function v1.get_user_config( _uid int ) 
returns table ( groupname text,
                upload_dir text
              )
language plpgsql
as $body$

begin

    return query
    select t2.groupname, t2.upload_dir
      from v1.users t1
      join v1.usergroups t2 on t2.pkey = t1.grp
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
