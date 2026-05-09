--El presente script tiene los scripts de los objetos de la base de datos
--Crear las tablas

DROP USER HCA CASCADE;

CREATE USER HCA IDENTIFIED BY "hca" account UNLOCK;

GRANT UNLIMITED TABLESPACE TO HCA;

GRANT CREATE DATABASE LINK,
    CREATE DIMENSION,
    CREATE MATERIALIZED VIEW,
    CREATE PROCEDURE,
    CREATE SEQUENCE,
    CREATE SESSION,
    CREATE TABLE
TO hca;

create table hca.HOSPITALS 
(HOS_ID NUMBER(10) not null,
HOS_NAME VARCHAR(40) not null);

alter table hca.HOSPITALS add constraint "HOS_PK" primary key (HOS_ID);

create table hca.HEADQUARTERS 
(HEQ_ID NUMBER(10) not null,
HEQ_NAME VARCHAR(40) not null,
HEQ_ADDRESS VARCHAR(40) not null,
HEQ_PROVINCE VARCHAR(40),
HEQ_COUNTRY VARCHAR(40),
HOS_ID NUMBER(10) not null);

alter table hca.HEADQUARTERS add constraint "HEQ_PK" primary key (HEQ_ID);
alter table hca.HEADQUARTERS add constraint "HEQ_HOS_FK" foreign key (HOS_ID) references hca.HOSPITALS(HOS_ID);


create table hca.medical_specialties
(MSP_ID NUMBER(10) not null,
MSP_NAME VARCHAR(40) not null,
HOS_ID NUMBER(10) not null);

alter table hca.MEDICAL_SPECIALTIES add constraint "MSP_PK" primary key (MSP_ID);
alter table hca.MEDICAL_SPECIALTIES add constraint "MSP_HOS_FK" foreign key (HOS_ID) references hca.HOSPITALS(HOS_ID);


create table hca.DOCTORS
(DOC_ID NUMBER(10) NOT NULL,
 DOC_LAST_NAME VARCHAR(40) NOT NULL,
 DOC_FIRST_NAME VARCHAR(40) NOT null,
 MSP_ID NUMBER(10) not null);

alter table hca.DOCTORS add constraint "DOC_PK" primary key (DOC_ID);
alter table hca.DOCTORS add constraint "DOC_MSP_FK" foreign key (MSP_ID) references hca.MEDICAL_SPECIALTIES(MSP_ID);


create table hca.HEALTH_INSURANCE
(HIN_ID NUMBER(10) not null,
HIN_NAME VARCHAR(100),
HOS_ID NUMBER(10) not null);

alter table hca.HEALTH_INSURANCE add constraint "HIN_PK" primary key (HIN_ID);
alter table hca.HEALTH_INSURANCE add constraint "HIN_HEQ_FK" foreign key (HOS_ID) references hca.HOSPITALS(HOS_ID);


create table hca.HEALTH_RELATIONS
(DOC_ID NUMBER(10) not null,
 HEQ_ID NUMBER(10) not null,
 HRE_CALENDAR_ID varchar(100),
 HRE_CALENDAR_DESCRIPTION varchar(100));

alter table hca.HEALTH_RELATIONS add constraint "HRE_PK" primary key (DOC_ID, HEQ_ID);
alter table hca.HEALTH_RELATIONS add constraint "HRE_DOC_FK" foreign key (DOC_ID) references hca.DOCTORS(DOC_ID);
alter table hca.HEALTH_RELATIONS add constraint "HRE_HEQ_FK" foreign key (HEQ_ID) references hca.HEADQUARTERS(HEQ_ID);


create table hca.health_care_parameters
(hpa_id varchar(40) not null,
hpa_valor_char varchar(40),
hpa_valor_date date,
hpa_valor_NUMBER NUMBER);

alter table hca.health_care_parameters add constraint "HPA_PK" primary key (HPA_ID);


--Insertar los datos
--Insert en tabla de hospitales
insert into hca.hospitals (hos_id, hos_name) values(1,'Clínica Universitaria Reina Fabiola');


--Insert en tabla de Sedes
insert into hca.headquarters (heq_id, heq_name, heq_address, heq_province, heq_country, hos_id) 
VALUES(1, 'Sede Central', 'Oncativo N1248 B General Paz', 'Cordoba', 'Argentina', 1);

insert into hca.headquarters (heq_id, heq_name, heq_address, heq_province, heq_country, hos_id) 
VALUES(2, 'Consultorios Externos Jacinto Ríos', 'Jacinto Ríos N554 B General Paz', 'Cordoba', 'Argentina', 1);


--Insert en tablas de Obras Sociales
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(1, 'OSDE', 1);

insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(2, 'OMINT', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(3, 'Swiss Medical', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(4, 'Galeno', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(5, 'Medife', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(6, 'Union Personal', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(7, 'Accord Salud', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(8, 'Bristol Medicine', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(9, 'OSECAC', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(10, 'ACA Salud', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(11, 'AMFFA', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(12, 'COMI', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(13, 'Construir Salud', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(14, 'FEMEBA', 1);

insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(15, 'DOSUBA', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(16, 'OSDEPyM', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(17, 'IOMA', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(18, 'IOSE', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(19, 'Forjar Salud', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(20, 'Sancor Salud', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(21, 'Accord Salud', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(22, 'MOA', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(23, 'OSALARA', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(24, 'OSDEM', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(25, 'OSMEBA', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(26, 'OSMECON', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(27, 'OSMEDICA', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(28, 'OSDIPP', 1);

insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(29, 'OSJOMN', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(30, 'OSFOT', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(31, 'OSPAT', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(32, 'OSPE', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(33, 'OSPEPBA', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(34, 'OSPETAX', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(35, 'OSPERYHRA', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(36, 'OSPIA', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(37, 'OSPPEA', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(38, 'OSPP', 1);
insert into hca.HEALTH_INSURANCE (hin_id, hin_name, hos_id) VALUES(39, 'OSSdeB', 1);
commit;

--Insertar datos en la tabla de Especialidades Médicas
insert into hca.medical_specialties (msp_id, msp_name, hos_id) VALUES(1, 'CLINICA MEDICA', 1);
insert into hca.medical_specialties (msp_id, msp_name, hos_id) VALUES(2, 'ALERGIA E INMUNOLOGIA', 1);
insert into hca.medical_specialties (msp_id, msp_name, hos_id) VALUES(3, 'ENDOCRINOLOGIA', 1);
insert into hca.medical_specialties (msp_id, msp_name, hos_id) VALUES(4, 'DERMATOLOGIA', 1);
insert into hca.medical_specialties (msp_id, msp_name, hos_id) VALUES(5, 'SALUD MENTAL', 1);
insert into hca.medical_specialties (msp_id, msp_name, hos_id) VALUES(6, 'DIABETES', 1);

SELECT COUNT(*) from hca.medical_specialties as ms;
commit;

--Insertar en la tabla de médicos
insert into hca.doctors (doc_id, doc_last_name, doc_first_name, msp_id) 
VALUES(1, 'Chamale', 'Oscar Elias', 1);

insert into hca.doctors (doc_id, doc_last_name, doc_first_name, msp_id) 
VALUES(2, 'Lozano', 'Alejandro', 2);

insert into hca.doctors (doc_id, doc_last_name, doc_first_name, msp_id) 
VALUES(3, 'Berardi', 'Yanina Viviana', 2);

insert into hca.doctors (doc_id, doc_last_name, doc_first_name, msp_id) 
VALUES(4, 'Bertolino', 'Maria Lorena', 3);

insert into hca.doctors (doc_id, doc_last_name, doc_first_name, msp_id) 
VALUES(5, 'Consigli', 'Nicolas Ernesto', 4);

insert into hca.doctors (doc_id, doc_last_name, doc_first_name, msp_id) 
VALUES(6, 'Antonelli', 'Romina', 5);

insert into hca.doctors (doc_id, doc_last_name, doc_first_name, msp_id) 
VALUES(7, 'Bartolacci', 'Ines', 6);

insert into hca.doctors (doc_id, doc_last_name, doc_first_name, msp_id) 
VALUES(8, 'Majul', 'Enrique', 6);

commit;

select count(*) from hca.doctors;


--Inserción en tablas de relaciones 
insert into hca.health_relations (doc_id, heq_id, hre_calendar_id, hre_calendar_description) 
VALUES(1, 1, 'jpm6u4d42c788gm934o97rb1mg@group.calendar.google.com', '');

insert into hca.health_relations (doc_id, heq_id, hre_calendar_id, hre_calendar_description) 
VALUES(1, 2, 'ch4n1dfutp6jib5emsvs5qos84@group.calendar.google.com', '');

insert into hca.health_relations (doc_id, heq_id, hre_calendar_id, hre_calendar_description) 
VALUES(2, 1, 'hepuqhvit813cnc4ne7n8vifj0@group.calendar.google.com', '');

insert into hca.health_relations (doc_id, heq_id, hre_calendar_id, hre_calendar_description) 
VALUES(2, 2, 'e9cq73quhsjrsggbs6u05g1o6c@group.calendar.google.com', '');

insert into hca.health_relations (doc_id, heq_id, hre_calendar_id, hre_calendar_description) 
VALUES(3, 1, '43mi3hd2t39o8pv1i7l9hcf9fk@group.calendar.google.com', '');

insert into hca.health_relations (doc_id, heq_id, hre_calendar_id, hre_calendar_description) 
VALUES(4, 1, 'ekqstdglvcsev0prescj7lqrao@group.calendar.google.com', '');

insert into hca.health_relations (doc_id, heq_id, hre_calendar_id, hre_calendar_description) 
VALUES(4, 2, '5og9d782l1dsc4mrd3v6dh81r8@group.calendar.google.com', '');

insert into hca.health_relations (doc_id, heq_id, hre_calendar_id, hre_calendar_description) 
VALUES(5, 1, 'e6gqktkmjj3sjp88sltkamue9s@group.calendar.google.com', '');

insert into hca.health_relations (doc_id, heq_id, hre_calendar_id, hre_calendar_description) 
VALUES(5, 2, '9l5u8hjcnf7dhgre7oupnjlbgk@group.calendar.google.com', '');

insert into hca.health_relations (doc_id, heq_id, hre_calendar_id, hre_calendar_description) 
VALUES(6, 1, 'mutnlmfi9003acp7lpheggaur4@group.calendar.google.com', '');

insert into hca.health_relations (doc_id, heq_id, hre_calendar_id, hre_calendar_description) 
VALUES(7, 1, '1bimogbosoh1q33jkuc01v5sr4@group.calendar.google.com', '');

insert into hca.health_relations (doc_id, heq_id, hre_calendar_id, hre_calendar_description) 
VALUES(7, 2, 'a325eu5p1uo3ritvddg9qrh2m4@group.calendar.google.com', '');

insert into hca.health_relations (doc_id, heq_id, hre_calendar_id, hre_calendar_description) 
VALUES(8, 1, 'ft5so4pnmhro9obj6b4gqms8c4@group.calendar.google.com', '');

insert into hca.health_relations (doc_id, heq_id, hre_calendar_id, hre_calendar_description) 
VALUES(8, 2, 'n9nrh9uq5kq3p2feoafecaq1s0@group.calendar.google.com', '');

COMMIT;

