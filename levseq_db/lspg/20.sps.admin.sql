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


/* function v1.get_experiment_dirpath */
drop function if exists v1.get_experiment_dirpath(int,int);
create or replace function v1.get_experiment_dirpath
( in _uid int,
  in _eid int )
returns text
language plpgsql
as $body$

declare
    grp      int;
	dirpath  text;
	grpname  text;

begin

    -- get the LevSeq user's group ID
	select t0.gid into grp
	  from v1.users t0
     where t0.pkey = _uid;

    /* build the file specification by injecting the current database
	    user name into the directory path */	    
	select format(t0.upload_dir, current_user), t0.groupname
      into dirpath, grpname
      from v1.usergroups t0
     where t0.pkey = grp;

	-- limit the character set
    dirpath = regexp_replace( dirpath, '[^A-Za-z0-9_\-\/]', '_', 'g' );
	
    -- append group and experiment subdirectories
    dirpath = dirpath
              || 'G' || right('0000'||grp, 5) || '/'
              || 'E' || right('0000'||_eid, 5) || '/';

    -- return the slash-terminated directory path
    return dirpath;

end;
$body$;
/*** test
select v1.get_experiment_dirpath( 5, 3 );
***/


/* function v1.files_in_dir */
-- drop function if exists v1.files_in_dir(text);
create or replace function v1.files_in_dir( in _dir text )
returns text[]
language plpgsql
as $body$

declare
    pgm     text = 'find ' || _dir || ' -maxdepth 1 -type f -printf "%f\n"';
    execcmd text = 'copy _fid from program ' || quote_literal(pgm);
    cb_file int;
	
begin

    -- if the specified directory does not exist, return an empty result set
    select "size" into cb_file from pg_stat_file(_dir, true);
    if coalesce(cb_file, 0) = 0 then return array[]::text[]; end if;

    -- use Linux "find" to list files in the specified directory
    drop table if exists _fid;
	create temporary table _fid
	( fname text not null );

    raise notice 'pgm: %', pgm;
	raise notice 'execcmd: %', execcmd;
	
	execute execcmd;

    -- return the list of filenames as a text array
    return array( select fname
                    from _fid
                order by fname asc );

end;
$body$;
/*** test
select v1.files_in_dir( '/mnt/Data/lsdb/uploads/G00002/E00026' );
select v1.files_in_dir( '/mnt/Data/lsdb/uploads/G00002/E00027' );
***/


/* function get_pginfo */
drop function if exists v1.get_pginfo(text);
create or replace function v1.get_pginfo( in _wsid text )
returns table
( wsinfo         text,
  pginfo         text,
  n_groups       int,
  n_users        int,
  n_experiments  int,
  dt_last_update timestamptz
)
language plpgsql
as $body$
declare
    dtlu timestamptz;
begin

    -- get a "last update" timestamp
    select max(dt_load) into dtlu
      from v1.experiments;

    if dtlu is null
    then
        select max(last_dt) into dtlu
          from v1.users;
    end if;
	
    return query
    select _wsid,
           (regexp_match(version(), '(^.*\s[\d\.]+)\s'))[1],
           (select count(*)::int from v1.usergroups),
           (select count(*)::int from v1.users where enabled),
           (select count(*)::int from v1.experiments),
           dtlu;

end;
$body$;
/*** test
select * from v1.get_pginfo('LevSeq webservice');  -- result set
select v1.get_pginfo('LevSeq webservice');         -- record
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
drop function if exists v1.get_user_info(int);
create or replace function v1.get_user_info( in _uid int )
returns table
( username  text,
  pwd       text,
  enabled   bool,
  firstname text,
  lastname  text,
  gid       int,
  groupname text,
  email     text,
  last_dt   timestamptz
)
language plpgsql
as $body$
begin

    return query
    select t0.username, t0.pwd, t0.enabled, t0.firstname, t0.lastname, t0.gid,
           t1.groupname, t0.email, t0.last_dt
      from v1.users t0
      join v1.usergroups t1 on t1.pkey = t0.gid
     where t0.pkey = _uid;

end;
$body$;
/*** test
select * from v1.users
select * from v1.get_user_info( 4 );
***/


/* function save_user_info */
drop function if exists v1.save_user_info(text,text,bool,text,text,text,text);
create or replace function v1.save_user_info
( in _username  text,
  in _pwd       text,
  in _enabled   bool,
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
	insert into v1.users(username, pwd, enabled, firstname, lastname, gid, email)
	     values (_username, _pwd, _enabled, _firstname, _lastname, pkgrp, _email)
    on conflict (username,gid)
	  do update set username = _username,
                    pwd = _pwd,
                    enabled = _enabled,
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
select v1.save_user_info('Fatemeh', 'pwdF', true, 'Fatemeh', 'Abbasinejad', 'SSEC', 'fabbasinejad@jhu.edu');
select v1.save_user_info('Yueming', 'pwdY', true, 'Yueming', 'Long', 'FHALAB', 'ylong@caltech.edu');
select v1.save_user_info('Richard', 'pwdR', true, 'Richard', 'Wilton', 'SSEC', 'a@b.com');
select v1.save_user_info('RJSquirrel', 'nuts', true, 'Rocket J', 'Squirrel', 'SSEC', 'moose@bullwinkle.com');
select * from v1.users;
select * from v1.usergroups;
***/

/* procedure save_user_ip */
drop procedure if exists v1.save_user_ip(int,text);
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


/*****************************************************************************/
/*****************************************************************************/
/*                                                                           */
/* The following functions are for interest and/or test purposes only.       */
/*                                                                           */
/*****************************************************************************/
/*****************************************************************************/

/* function get_experiment_row_counts */
drop function if exists v1.get_experiment_row_counts(int);
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
    select 'v1.mutations', count(*)
      from v1.mutations t0
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
select * from v1.get_experiment_row_counts(88);
***/


/* function get_test_queries */
drop function if exists v1.get_test_queries(int,int,int);
create or replace function v1.get_test_queries( in _eid int, in _uid int, in _gid int )
returns table
( verb     text,
  param1   text,
  param2   text
)
language plpgsql
as $body$
declare
    _pkseq int = null::int;

begin

    -- a few stereotyped queries that return results to the remote client
    return query
    values ( 'get_pginfo', 'Dash', null ),
           ( 'get_experiment_row_counts', _eid::text, null ),
           ( 'get_experiments_u', _uid::text, null ),
           ( 'get_experiments_g', _gid::text, null ),
	       ( 'get_experiment_parent_sequence', _eid::text, null ),
	       ( 'get_experiment_alignments', _eid::text, null ),
           ( 'get_experiment_alignment_probabilities', _eid::text, null ),
           ( 'get_experiment_p_values', _eid::text, null );


    if _eid is not null
    then

        -- get the parent sequence for the specified experiment
        select pkseq into _pkseq
          from v1.parent_sequences
         where pkexp = _eid
         limit 1;

        if _pkseq is not null
        then
            return query
            values ( 'get_mutation_counts', _pkseq::text, null ),
                   ( 'get_variant_sequences', _pkseq::text, _eid::text );
        end if;
    end if;

end;
$body$;
/*** test
select * from v1.experiments;
select * from v1.get_test_queries( 83, 4, 2 );
***/
