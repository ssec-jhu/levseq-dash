/*
   11.tables.ref.sql
*/

/* ensure that the SQL schema exists */
create schema if not exists "v1" authorization "ssec-devuser";


/* table v1.mutagenesis_methods */
-- drop table if exists v1.mutagenesis_methods
create table if not exists v1.mutagenesis_methods
(
  pkey          smallint  not null generated always as identity,
  "method"      text      not null,
  abbreviation  text      not null
);

alter table if exists v1.mutagenesis_methods owner to "ssec-devuser";

drop index if exists v1.pk_mutagenesis_methods;

create unique index pk_mutagenesis_methods
                 on v1.mutagenesis_methods
              using btree (pkey asc)
               with (deduplicate_items=True)
         tablespace pg_default;
/*** test
delete from v1.pk_mutagenesis_methods where pkey > 0;
insert into v1.mutagenesis_methods( method, abbreviation )
     values ( 'site-saturation mutagenesis', 'SSM' ),
            ( 'error-prone', 'EP' );
select * from v1.mutagenesis_methods;
***/

/* table v1.assays */
-- drop table if exists v1.assays
create table if not exists v1.assays
(
  pkey  smallint  not null generated always as identity,
  assay text      not null
);

alter table if exists v1.assays owner to "ssec-devuser";

drop index if exists v1.pk_assays;

create unique index pk_assays
                 on v1.assays
              using btree (pkey asc)
               with (deduplicate_items=True)
         tablespace pg_default;
/*** test
truncate table v1.assays;
insert into v1.assays(assay)
     values ('assay 1'), ('assay 2'), ('assay 3');
select * from v1.assays;
***/

