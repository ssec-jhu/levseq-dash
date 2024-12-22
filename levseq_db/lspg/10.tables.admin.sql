/*
   10.tables.admin.sql
*/

/* ensure that the SQL schema exists */
create schema if not exists v1 authorization "ssec-devuser";


/* table v1.usergroups */
-- drop table if exists v1.usergroups cascade; 
create table if not exists v1.usergroups
(
  pkey        smallint  not null generated always as identity,
  groupname   text      not null,
  contact     text      not null default '',
  upload_dir  text      not null default '/mnt/Data/%s/uploads/%s'
)
tablespace pg_default;

alter table v1.usergroups owner to "ssec-devuser";
grant select,insert,update,delete on v1.usergroups to lsdb;

drop index if exists v1.pk_usergroups;

create unique index pk_usergroups
                 on v1.usergroups
              using btree (pkey asc)
               with (deduplicate_items=True)
         tablespace pg_default;
/*** test
delete from v1.usergroups where pkey >= 1;
alter sequence v1.usergroups_pkey_seq restart with 1;
insert into v1.usergroups (groupname, contact)
     values ('FHALAB', 'Yueming Long ylong@caltech.edu'),
	        ('SSEC',   'Fatemeh Abbasinejad fabbasinejad@jhu.edu');
select * from v1.usergroups;

-- (use this elsewhere)
select format( '/mnt/Data/%s/uploads', current_user )
select regexp_replace('/mnt/Data/ssec-devuser/uploads/','[^A-Za-z0-9_\-\/]','_','g');
***/

/* table v1.users */
-- drop table if exists v1.users cascade;
create table if not exists v1.users
(
  pkey      int       not null generated always as identity,
  username  text      not null,
  pwd       text      not null default '64-17-5',
  firstname text      not null default '',
  lastname  text      not null default '',
  gid       smallint  not null constraint fk_users_usergroup
                               references v1.usergroups(pkey),
  email     text      not null default '',
  last_ip   text      not null default ''
)
tablespace pg_default;

alter table v1.users owner to "ssec-devuser";
grant select,insert,update,delete on v1.users to lsdb;

--drop index v1.pk_users;

create unique index Pk_users
                 on v1.users
              using btree (pkey asc)
               with (deduplicate_items=True)
         tablespace pg_default;

alter table v1.users cluster on pk_users;

create unique index Ix_users_username_gid
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
