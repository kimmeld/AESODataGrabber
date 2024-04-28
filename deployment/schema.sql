-- PostgreSQL schema for the AESO Data Grabber

create table aeso_generation(
	ts timestamptz,
	asset_id char(5),
	fuel_type varchar(30),
	sub_fuel_type varchar(30),
	maximum_capability numeric(5),
	net_generation numeric(5),
	dispatched_contingency_reserve numeric(5),
	primary key (ts, asset_id)	
);