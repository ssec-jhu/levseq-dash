/*
   11.tables.ref.sql
*/


/* table v1.mutagenesis_methods */
-- drop table if exists v1.mutagenesis_methods
create table if not exists v1.mutagenesis_methods
(
  pkey          smallint  not null generated always as identity primary key,
  "method"      text      not null,
  abbreviation  text      not null
);
grant select on v1.mutagenesis_methods to lsdb;
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
  pkey  smallint  not null generated always as identity primary key,
  assay text      not null
);
grant select on v1.assays to lsdb;
/*** test
truncate table v1.assays;
insert into v1.assays(assay)
     values ('assay 1'), ('assay 2'), ('assay 3');
select * from v1.assays;
***/
