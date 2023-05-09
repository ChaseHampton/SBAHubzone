-- public.businesses definition

-- Drop table

-- DROP TABLE businesses;

CREATE TABLE businesses (
	businesses_id int4 NOT NULL GENERATED BY DEFAULT AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE),
	bus_name varchar(100) NULL,
	url varchar(100) NULL,
	uei varchar(100) NULL,
	is_searched bool NULL DEFAULT false,
	CONSTRAINT businesses_pkey PRIMARY KEY (businesses_id)
);