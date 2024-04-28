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


create table aeso_summary(
	ts timestamptz,
	total_max_generation_capability numeric(7),
	total_net_generation numeric(7),
	net_to_grid_generation numeric(7),
	net_actual_interchange numeric(7),
	alberta_internal_load numeric(7),
	contingency_reserve_required numeric(7),
	dispatched_contingency_reserve_total numeric(7),
	dispatched_contingency_reserve_gen numeric(7),
	dispatched_contingency_reserve_other numeric(7),
	lssi_armed_dispatch numeric(7),
	lssi_offered_volume numeric(7),
	primary key (ts)
);

create table aeso_summary_generation(
	ts timestamptz,
	fuel_type varchar(30),
	aggregated_maximum_capability numeric(7),
	aggregated_net_generation numeric(7),
	aggregated_dispatched_contingency_reserve numeric(7),
	primary key (ts, fuel_type)
);

create table aeso_summary_interchange(
	ts timestamptz,
	flow_path varchar(30),
	actual_flow numeric(7),
	primary key (ts, flow_path)
);

