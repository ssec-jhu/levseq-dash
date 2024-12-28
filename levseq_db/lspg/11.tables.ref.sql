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
/*** test
delete from v1.pk_mutagenesis_methods where pkey > 0;
insert into v1.mutagenesis_methods( method, abbreviation )
     values ( 'site-saturation mutagenesis', 'SSM' ),
            ( 'error-prone', 'EP' );
select * from v1.mutagenesis_methods;
***/

/* table v1.assays */
-- drop table if exists v1.assays cascade;
create table if not exists v1.assays
(
  pkey      smallint  not null generated always as identity primary key,
  technique text      not null,
  units     text      not null  
);
insert into v1.assays(technique, units)  -- ·ÅΔμ°²³¹⁻
     values ('LC-MS', 'M, μg/mL, ng/mL, counts'),
	        ('GC-MS', 'ng/mL, μg/mL, ppm'),
			('Fluorescence spectroscopy', 'AU, RFU, μM, mM'),
			('UV-Vis spectroscopy', 'absorbance (unitless), M, mg/mL'),
			('ELISA', 'ng/mL, pg/mL, counts'),
			('Western blotting', 'relative expression levels (unitless), band intensity (AU)'),
			('SPR', 'Kd (M), ka (1/(M·s)), kd (1/s)'),
			('ITC', 'Kd (M), ΔH (kcal/mol), ΔS (cal/(mol·K))'),
			('CD spectroscopy', 'molar ellipticity (degrees·cm²/dmol)'),
            ('NMR spectroscopy', 'ppm, mM, unitless ratios'),
			('X-ray crystallography', 'Å, degrees'),
			('Flow cytometry', 'AU, events/μL'),
            ('MSIA', 'ng/mL, μg/mL, counts'),
			('MRM', 'fmol/μL, amol/μL, counts'),
			('SILAC', 'relative abundance ratios (unitless)'),
			('ICAT', 'relative abundance ratios (unitless)'),
			('iTRAC', 'relative abundance ratios, reporter ion intensity (counts)'),
			('Dynamic Light Scattering (DLS)', 'particle size (nm), intensity (AU)'),
			('Microplate readers', 'absorbance (unitless), AU, RFU, RLU'),
			('Capillary electrophoresis', 'seconds, cm²/V·s)'),
			('Thermal shift assays', 'Tm (°C)'),
			('FTIR', 'wavenumber (cm⁻¹)'),
			('HPLC', 'μg/mL, mg/mL, retention time (minutes), area'),
			('Spectrofluorometers', 'ns, AU, RFU');
/*** test
truncate table v1.assays;
select * from v1.assays;
***/

/* table v1.cas */
-- drop table if exists v1.cas cascade;
create table if not exists v1.cas
(
  pkey  int   not null generated always as identity primary key,
  cas   text  not null
);

create unique index ix_cas_cas
                 on v1.cas
              using btree (cas asc)
            include (pkey)
               with (deduplicate_items=True)
         tablespace pg_default;
/*** test
truncate table v1.cas;
alter sequence v1.cas_pkey_seq restart with 1;
insert into v1.cas(cas)
values ('7732-18-5'),    -- water
       ('64-17-5'),      -- ethanol
       ('439-14-5'),     -- diazepam
       ('99685-96-8');   -- buckminsterfullerene
select * from v1.cas;
***/
