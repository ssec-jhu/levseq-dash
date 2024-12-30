/*
   10.tables.admin.sql
*/


/* table v1.usergroups

   The upload directory path must...
    - contain a wildcard into which the current database username
	  is inserted (see function	v1.get_upload_dirpath())
    - terminate with a path separator ('/')
*/
-- drop table if exists v1.usergroups cascade; 
create table if not exists v1.usergroups
(
  pkey        int   not null generated always as identity primary key,
  groupname   text  not null,
  contact     text  not null default '',
  upload_dir  text  not null default '/mnt/Data/%s/uploads/'
)
tablespace pg_default;

/* The SQL regex in the check expression is:
    /      slash
    %      any sequence of characters (hopefully slashes, alphanumeric, and underscore)
    /      slash
    \%s    %s (format specifier; see v1.get_upload_dirpath())
    /      slash
    %      any sequence of characters
    /      slash

   It's surely possible to use postgres's posix regex extension to
    enforce the character set as well, but this is already ugly
	enough as it is.
*/	
alter table v1.usergroups drop constraint if exists ck_usergroups_upload_dir;
alter table v1.usergroups
        add constraint ck_usergroups_upload_dir
            check (upload_dir similar to '/%/\%s/%/');
/*** test
delete from v1.usergroups where pkey >= 1;
alter sequence v1.usergroups_pkey_seq restart with 1;
insert into v1.usergroups (groupname, contact)
     values ('FHALAB', 'Yueming Long ylong@caltech.edu'),
	        ('SSEC',   'Fatemeh Abbasinejad fabbasinejad@jhu.edu');
select * from v1.usergroups;

update v1.usergroups set upload_dir = '/mnt/Data/%s/uploads/'
***/

/* table v1.users */
-- drop table if exists v1.users cascade;
create table if not exists v1.users
(
  pkey      int   not null generated always as identity primary key,
  username  text  not null,
  pwd       text  not null default '64-17-5',
  firstname text  not null default '',
  lastname  text  not null default '',
  gid       int   not null constraint fk_users_usergroup
                           references v1.usergroups(pkey),
  email     text  not null default '',
  last_ip   text  not null default ''
)
tablespace pg_default;

create unique index ix_users_username_gid
                 on v1.users
              using btree (username asc, gid asc)
			   with (deduplicate_items=True)
         tablespace pg_default;
/*** test
truncate table v1.users;
alter sequence v1.users_pkey_seq restart with 1;
insert into v1.users(username, gid)
     values ('Fatemeh', 2), ('Yueming', 1), ('Richard', 2);
select * from v1.users;
***/
