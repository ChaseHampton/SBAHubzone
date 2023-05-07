create table if not exists searches (
	search_id int not null auto_increment primary key,
	cert_type varchar(50),
	body varchar(500),
	is_searched bool default false
);

create table if not exists businesses (
	businesses_id int not null auto_increment primary key,
	bus_name varchar(100),
	url varchar(100),
	uei varchar(100),
	is_searched bool default false
);

