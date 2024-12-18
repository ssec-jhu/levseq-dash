/*
   03.sps.admin.sql
*/

/* function get_usernames */
drop function if exists v1.get_usernames();

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
select * from v1.get_usernames();
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
