/*
   12.tables.load.sql
*/

/* ensure that the SQL schema exists */
create schema if not exists "v1" authorization "ssec-devuser";


/* table v1.load_tasks */
-- drop table if exists v1.load_tasks
create table if not exists v1.load_tasks
(
  pkey smallint     not null generated always as identity,
  task varchar(32)  not null
);

alter table if exists v1.load_tasks owner to "ssec-devuser";

drop index if exists v1.pk_load_tasks;

create unique index pk_load_tasks
          on v1.load_tasks
       using btree
             (pkey asc)
        with (deduplicate_items=True)
  tablespace pg_default;

truncate table v1.load_tasks;
alter sequence v1.load_tasks_pkey_seq restart with 1;
insert into v1.load_tasks (task)
     values ('upload'),      -- upload file to server filesystem (all file types)
            ('load'),        -- copy file data to temporary table (CSV)
            ('validate'),    -- validate file data (CSV)
            ('save');        -- copy file data to tables (CSV)
select * from v1.load_tasks;


/* table v1.load_states */
-- drop table if exists v1.load_states
create table if not exists v1.load_states
(
  pkey   smallint     not null generated always as identity,
  status varchar(32)  not null );

alter table if exists v1.load_states owner to "ssec-devuser";

drop index if exists v1.pk_load_states;

create unique index pk_load_states
          on v1.load_states
       using btree
             (pkey asc)
        with (deduplicate_items=True)
  tablespace pg_default;

truncate table v1.load_states;
alter sequence v1.load_states_pkey_seq restart with 1;
insert into v1.load_states (status)
     values ('started'),
            ('completed'),
            ('failed');
select * from v1.load_states;


/* table v1.load_log_msgs */
-- drop table if exists v1.load_log_msgs
create table if not exists v1.load_log_msgs
(
  pkey   smallint     not null generated always as identity,
  msg    varchar(64)  not null );

alter table if exists v1.load_log_msgs owner to "ssec-devuser";

drop index if exists v1.pk_load_log_msgs;

create unique index pk_load_log_msgs
          on v1.load_log_msgs
       using btree
             (pkey asc)
        with (deduplicate_items=True)
  tablespace pg_default;

truncate table v1.load_log_msgs;
alter sequence v1.load_log_msgs_pkey_seq restart with 1;
insert into v1.load_log_msgs (pkey, msg)
     values (  0, ''),
            (  1, 'invalid CAS: %s'),
            (  2, 'whatever');
select * from v1.load_log_msgs;



/* table v1.load_log */
-- drop table if exists v1.load_log;
create table if not exists v1.load_log
(
  pkey       int           not null generated always as identity,
  uid        smallint      not null constraint fk_load_log_users
                               references v1.users(pkey),
  esn        int           not null constraint fk_data_files_experiments
                               references v1.experiments(pkey),
  task       smallint      not null constraint fk_load_log_tasks
                               references v1.load_tasks(pkey),
  filespec   varchar(320)  not null,
  dt         timestamptz   not null default current_timestamp,
  status     smallint      not null constraint fk_load_log_status
                               references v1.load_tasks(pkey),
);

alter table if exists v1.load_log owner to "ssec-devuser";

drop index if exists v1.pk_load_log;

create unique index pk_load_log
          on v1.load_log
       using btree (pkey asc, uid  asc, experiment asc)
        with (deduplicate_items=True)
  tablespace pg_default;

alter table if exists v1.load_log cluster on pk_load_log;

/*** test
insert into v1.load_log( uid, task, status, details)
values (2, 1, 2, 'flatten_ep_processed_xy_cas.csv');
select t0.pkey,
       t1.username,
	   t2.task,
	   t3.status,
	   t0.details
  from v1.load_log t0
  join v1.users t1 on t1.pkey = t0.uid
  join v1.load_tasks t2 on t2.pkey = t0.task
  join v1.load_states t3 on t3.pkey = t0.status;

truncate table v1.load_log;
alter sequence v1.load_log_pkey_seq restart with 1;
***/
