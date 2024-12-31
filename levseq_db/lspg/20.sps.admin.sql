/*
   20.sps.admin.sql
*/

/* procedure do_nothing */
-- drop procedure if exists v1.do_nothing( int );
create or replace procedure v1.do_nothing(in _uid int )
language plpgsql
as $body$
begin
    raise notice '% nothing', _uid;
end;
$body$;
/*** test
call v1.do_nothing( 12345 );
***/


/* function v1.files_in_dir */
-- drop function if exists v1.files_in_dir(text);
create or replace function v1.files_in_dir( in _dir text )
returns table
( filename text )
language plpgsql
as $body$

declare
    pgm     text = 'find ' || _dir || ' -maxdepth 1 -type f -printf "%f\n"';
    execcmd text = 'copy _fid from program ' || quote_literal(pgm);
    cb_file int;
	
begin

    -- if the specified directory does not exist, return an empty result set
    select "size" into cb_file from pg_stat_file(_dir, true);
    if coalesce(cb_file, 0) = 0 then return; end if;

    -- use Linux "find" to list files in the specified directory
    drop table if exists _fid;
	create temporary table _fid
	( fname text not null );

    raise notice 'pgm: %', pgm;
	raise notice 'execcmd: %', execcmd;
	
	execute execcmd;

    return query
    select fname
      from _fid
  order by fname asc;

end;
$body$;
/*** test
select v1.files_in_dir( '/mnt/Data/lsdb/uploads/G00002/E00027' );
***/


/* function get_pginfo */
-- drop function v1.get_pginfo(text);
create or replace function v1.get_pginfo( in _wsid text )
returns table
( wsinfo text,
  pginfo text,
  dt     timestamptz,
  n      int,
  f      double precision
)
language plpgsql
as $body$
begin

    return query
    select _wsid,
           (regexp_match(version(), '(^.*\s[\d\.]+)\s'))[1],
           now(),
		   (1e5*pi())::int,
		   pi();

end;
$body$;
/*** test
select * from v1.get_pginfo('LevSeq webservice');
select v1.get_pginfo('LevSeq webservice');         -- (one column, comma-separated)
***/


/* function get_group_info */
-- drop function if exists v1.get_group_info(int);
create or replace function v1.get_group_info( in _gid int = null)
returns table
( gid        smallint,
  groupname  text,
  contact    text,
  upload_dir text
)
language plpgsql
as $body$
begin

    return query
    select pkey, t0.groupname, t0.contact, t0.upload_dir
      from v1.usergroups t0
     where pkey = _gid
	    or _gid is null;

end;
$body$;
/*** test
select * from v1.usergroups;
select * from v1.get_group_info();
select * from v1.get_group_info(2);
***/


/* function get_usernames */
-- drop function v1.get_usernames(int);
create or replace function v1.get_usernames( in _gid int = null )
returns table
( uid       int,
  username  text,
  gid       int,
  groupname text
)
language plpgsql
as $body$
begin

    return query
    select t1.pkey, t1.username, t2.pkey, t2.groupname
	  from v1.users t1
	  join v1.usergroups t2 on t2.pkey = t1.gid
     where t2.pkey = _gid
	    or _gid is null
  order by t1.username;

end;
$body$;
/*** test
select * from v1.get_usernames();  -- returns three columns
select * from v1.get_usernames( 2 );
select v1.get_usernames();         -- returns one column of comma-separated values
                                   --  (embedded commas are NOT escaped!)
select * from v1.usergroups;
select * from v1.users;

delete from v1.users where pkey = 2;
***/


/* function get_user_info(int) */
-- drop function if exists v1.get_user_info(int);
create or replace function v1.get_user_info( in _uid int )
returns table
( groupname text,
  firstname text,
  lastname  text,
  email     text
)
language plpgsql
as $body$
begin

    return query
    select t2.groupname, t1.firstname, t1.lastname, t1.email
      from v1.users t1
      join v1.usergroups t2 on t2.pkey = t1.gid
     where t1.pkey = _uid;

end;
$body$;
/*** test
select * from v1.users
select * from v1.get_user_info( 1 );
***/

/* function get_user_info(text,text) */
-- drop function if exists v1.get_user_info(text,text);
create or replace function v1.get_user_info( in _u text, in _p text )
returns table
( uid       int,
  groupname text,
  firstname text,
  lastname  text,
  email     text
)
language plpgsql
as $body$
begin

    return query
    select t1.pkey, t2.groupname, t1.firstname, t1.lastname, t1.email
      from v1.users t1
      join v1.usergroups t2 on t2.pkey = t1.gid
     where t1.username = _u;

end;
$body$;
/*** test
select * from v1.users
select * from v1.get_user_info( 'Richard', '64-17-5' );
***/

/* function save_user_info */
-- drop function if exists v1.save_user_info(text,text,text,text,text,text);
create or replace function v1.save_user_info
( in _username  text,
  in _pwd       text,
  in _firstname text,
  in _lastname  text,
  in _groupname text,
  in _email     text )
returns int
language plpgsql
as $body$
declare
    pkgrp smallint = (select pkey
                        from v1.usergroups
                       where groupname = _groupname);
    rval int = 0;

begin

    -- insert/update the users table
	insert into v1.users(username, pwd, firstname, lastname, gid, email)
	     values (_username, _pwd, _firstname, _lastname, pkgrp, _email)
    on conflict (username,gid)
	  do update set username = _username,
                    pwd = _pwd,
                    firstname = _firstname,
                    lastname = _lastname,
                    gid = pkgrp,
                    email = _email
	  returning pkey into rval;

	  return rval;

end;
$body$;
/*** test
delete from v1.users where pkey >= 1;
alter sequence v1.users_pkey_seq restart with 1;
select v1.save_user_info('Richard', 'monkey', 'Richard', 'Wilton', 'SSEC', 'a@b.com');
select v1.save_user_info('RJSquirrel', 'nuts', 'Rocket J', 'Squirrel', 'SSEC', 'bull@winkle.com');
select * from v1.users;
delete from v1.users where pkey > 5
***/

/* procedure save_user_ip */
-- drop procedure if exists v1.save_user_ip(int,text);
create procedure v1.save_user_ip( in _pkey int, in _ip text )
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


/* function get_experiment_row_counts */
-- drop function if exists v1.get_experiment_row_counts(int);
create or replace function v1.get_experiment_row_counts( in _eid int )
returns table
( "table_name"  text,
  n_rows        bigint )
language plpgsql
as $body$
begin

    return query
    select 'v1.fitness', count(*)
      from v1.fitness t0
      join v1.experiment_cas t1 on t1.pkey = t0.pkexpcas
      join v1.experiments t2 on t2.pkey = t1.pkexp
     where t2.pkey = _eid;

    return query
    select 'v1.variant_mutations', count(*)
      from v1.variant_mutations t0
      join v1.variants t1 on t1.pkey = t0.pkvar
      join v1.experiments t2 on t2.pkey = t1.pkexp
     where t2.pkey = _eid;

    return query
    select 'v1.variants', count(*)
      from v1.variants t0
      join v1.experiments t1 on t1.pkey = t0.pkexp
     where t1.pkey = _eid;

    return query
    select 'v1.parent_sequences', count(*)
      from v1.parent_sequences t0
      join v1.experiments t1 on t1.pkey = t0.pkexp
     where t1.pkey = _eid;

    return query
    select 'v1.experiment_cas', count(*)
      from v1.experiment_cas t0
      join v1.experiments t1 on t1.pkey = t0.pkexp
     where t1.pkey = _eid;

    return query
    select 'v1.plates', count(*)
      from v1.plates t0
      join v1.experiments t1 on t1.pkey = t0.pkexp
     where t1.pkey = _eid;

    return query
    select 'v1.experiments', count(*)
      from v1.experiments
     where pkey = _eid;

    return query
    select 'v1.experiments_pending', count(*)
      from v1.experiments_pending
     where eid = _eid;

end;
$body$;
/*** test
select * from v1.experiments;
select * from v1.get_experiment_row_counts(27);
***/
