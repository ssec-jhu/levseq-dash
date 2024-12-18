/*
   02.tables.admin.sql
*/

/* ensure that the SQL schema exists */
create schema if not exists v1 authorization "ssec-devuser";


/* table v1.usergroups */
-- drop table if exists v1.usergroups cascade; 
create table if not exists v1.usergroups
(
  pkey       smallint     not null generated always as identity,
  groupname  varchar(32)  not null,
  upload_dir varchar(320) not null default '/mnt/Data/ssec-devuser/uploads',
  "comment"  varchar(128) not null default ''
)
tablespace pg_default;

alter table if exists v1.usergroups
   owner to "ssec-devuser";

drop index if exists v1.pk_usergroups;

create unique index pk_usergroups
          on v1.usergroups
       using btree
             (pkey asc)
        with (deduplicate_items=True)
  tablespace pg_default;

/* table v1.users */
-- drop table if exists v1.users;
create table if not exists v1.users
(
  pkey       smallint     not null generated always as identity,
  username   varchar(32)  not null,
  grp        smallint     not null constraint fk_users_usergroup
                                   references v1.usergroups(pkey),
  last_ip    varchar(24)  not null default ''
)
tablespace pg_default;

alter table if exists v1.users owner to "ssec-devuser";

drop index if exists v1.pk_users;

create unique index pk_users
          on v1.users
       using btree
             (pkey asc)
        with (deduplicate_items=True)
  tablespace pg_default;

alter table if exists v1.users cluster on pk_users;

/*** test
truncate table v1.usergroups;
alter sequence v1.usergroups_pkey_seq restart with 1;
insert into v1.usergroups (groupname, "comment")
     values ('FHALAB', 'CalTech'), ('SSEC', 'JHU');
select * from v1.usergroups;

truncate table v1.users;
alter sequence v1.users_pkey_seq restart with 1;
insert into v1.users(username, usergroup)
     values ('Fatemeh', 2), ('Yueming', 1), ('Richard', 2);
select * from v1.users;
***/
