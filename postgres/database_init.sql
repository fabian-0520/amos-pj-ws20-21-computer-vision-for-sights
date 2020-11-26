-- initialize DWH structure
----------------------------------------------------------------------------------------------------------------
-- create necessary DWH schemas

drop schema if exists load_layer cascade;
drop schema if exists integration_layer cascade;
drop schema if exists data_mart_layer cascade;

create schema if not exists load_layer;
create schema if not exists integration_layer;
create schema if not exists data_mart_layer;

-- create bounding box type 

drop type if exists bounding_box;
create type bounding_box as (
	ul_x smallint,
	ul_y smallint,
	lr_x smallint,
	lr_y smallint,
	box_label VARCHAR(100)
);

-- create load layer
create table if not exists load_layer.sight_images (
	id serial not null,
	sight_image bytea not null,
	sight_city VARCHAR(100) not null,			
	sight_image_width INT not null,  
	sight_image_height INT not null, 
	sight_image_bounding_box_x1y1 point not null,
	sight_image_bounding_box_x2y2 point not null,
	sight_image_data_source VARCHAR(300) not null,
	primary key (id)
);

create table if not exists load_layer.sight_image_labels(
	id serial not null,
	sight_image_data_source varchar(300) not null,
	sight_labels bounding_box[] not null,
	primary key (id)
);

create table if not exists load_layer.trained_models (
	id serial not null,
	city VARCHAR(100) not null,
	trained_model bytea not null,
	mapping_table json not null,
	primary key (id)
);

-- create sights structure for integration layer: dimension tables

create table if not exists integration_layer.dim_sights_cities(
	city_id serial not null,
	city_name VARCHAR(100) not null,
	primary key (city_id)
);

create table if not exists integration_layer.dim_sights_resolutions(
	resolution_id serial not null,
	resolution_height INT not null,
	resolution_width INT not null,
	primary key (resolution_id)
);

create table if not exists integration_layer.dim_sights_images(
	image_id serial not null,
	image_file BYTEA not null,
	image_source VARCHAR(300) not null,
	image_labels bounding_box[],
	primary key (image_id)
);

create table if not exists integration_layer.dim_sights_timestamps (
	timestamp_id serial not null,
	timestamp_unix BIGINT not null,
	primary key (timestamp_id)
);

-- create models structure for integration layer: dimension tables

create table if not exists integration_layer.dim_models_timestamps (
	timestamp_id serial not null,
	timestamp_unix BIGINT not null,
	primary key (timestamp_id)
);

create table if not exists integration_layer.dim_models_trained_models (
	trained_model_id serial not null,
	trained_model_model BYTEA not null,
	output_sight_mapping json not null,
	surrogate_key INT not null,
	primary key (trained_model_id)
);

-- create fact tables for integration layer

create table if not exists integration_layer.fact_sights(
	city_id INT not null,
	timestamp_id INT not null,
	image_id INT not null,
	resolution_id INT not null,
	primary key (city_id, timestamp_id, image_id, resolution_id)
);

create table if not exists integration_layer.fact_models(
	city_id INT not null,
	timestamp_id INT not null,
	trained_model_id INT not null,
	primary key (city_id, timestamp_id, trained_model_id)
);

-- create data mart layer as materialized views

CREATE MATERIALIZED VIEW if not exists data_mart_layer.current_trained_models as (
	select cities.city_name as city_name, 
		   models.output_sight_mapping as output_sight_mapping, 
		   models.trained_model_model as trained_model
	from integration_layer.fact_models as fact_models,   
		(select inner_facts.city_id as city_id, max(timestamp_id) as timestamp_id, max(trained_model_id) as trained_model_id
		from integration_layer.fact_models as inner_facts
		group by inner_facts.city_id) as latest_facts,
		integration_layer.dim_sights_cities as cities, 
		integration_layer.dim_models_trained_models as models
	where fact_models.city_id = latest_facts.city_id and 
	fact_models.timestamp_id = latest_facts.timestamp_id and 
	fact_models.trained_model_id = latest_facts.trained_model_id and 
	cities.city_id = latest_facts.city_id and 
	models.trained_model_id = fact_models.trained_model_id
); 

-- integration layer: add foreign key constraints between fact and dimension tables
----------------------------------------------------------------------------------------------------------------
do $$
begin
	-- foreign keys for sight entities

	if not exists (SELECT 1 FROM pg_constraint WHERE conname = 'sights_city_id_fk') THEN
		alter table integration_layer.fact_sights 
		add constraint sights_city_id_fk 
		foreign key (city_id) 
		references integration_layer.dim_sights_cities (city_id);
	end if;

	if not exists (SELECT 1 FROM pg_constraint WHERE conname = 'sights_timestamp_id_fk') THEN
		alter table integration_layer.fact_sights 
		add constraint sights_timestamp_id_fk 
		foreign key (timestamp_id) 
		references integration_layer.dim_sights_timestamps (timestamp_id);
	end if;

	if not exists (SELECT 1 FROM pg_constraint WHERE conname = 'sights_image_id_fk') THEN
		alter table integration_layer.fact_sights 
		add constraint sights_image_id_fk 
		foreign key (image_id) 
		references integration_layer.dim_sights_images (image_id);
	end if;

	if not exists (SELECT 1 FROM pg_constraint WHERE conname = 'sights_resolution_id_fk') THEN
		alter table integration_layer.fact_sights 
		add constraint sights_resolution_id_fk 
		foreign key (resolution_id) 
		references integration_layer.dim_sights_resolutions (resolution_id);
	end if;

	-- foreign keys for model entities
  if not exists (SELECT 1 FROM pg_constraint WHERE conname = 'models_city_id_fk') THEN
		alter table integration_layer.fact_models 
		add constraint models_city_id_fk 
		foreign key (city_id) 
		references integration_layer.dim_sights_cities (city_id);
	end if;

	if not exists (SELECT 1 FROM pg_constraint WHERE conname = 'models_timestamp_id_fk') THEN
		alter table integration_layer.fact_models 
		add constraint models_timestamp_id_fk 
		foreign key (timestamp_id) 
		references integration_layer.dim_models_timestamps (timestamp_id);
	end if;

	if not exists (SELECT 1 FROM pg_constraint WHERE conname = 'models_trained_model_id_fk') THEN
		alter table integration_layer.fact_models 
		add constraint models_trained_model_id_fk 
		foreign key (trained_model_id) 
		references integration_layer.dim_models_trained_models (trained_model_id);
	end if;
end;
$$;
----------------------------------------------------------------------------------------------------------------
-- create automated load job for image pushes
CREATE OR REPLACE FUNCTION load_images_into_dwh()
  RETURNS trigger as $$
  declare formatted_city VARCHAR(100) := NULL;
	declare temp_city_key INTEGER := NULL;   
	declare temp_image_key INTEGER := NULL; 
	declare temp_fact_key INTEGER := NULL; 
	declare temp_resolution_key INTEGER := NULL;   
	declare temp_timestamp_key INTEGER := NULL;   
	declare temp_city_images_data_mart_query VARCHAR(1000) := NULL;   
	declare current_time_stamp BIGINT := (SELECT extract(epoch from now() at time zone 'utc'));

begin	
	-- get sights images dimension table key
	temp_image_key := (select image_id from integration_layer.dim_sights_images where image_source = new.sight_image_data_source limit 1);
	
	-- avoid persisting the same image several times
	if temp_image_key is not null then
		-- image already existing
		delete from load_layer.sight_images where id = new.id;
	
		RETURN NEW;
	end if;
	
	-- insert image into according dimension table
	INSERT INTO integration_layer.dim_sights_images(image_file, image_source) values (new.sight_image, new.sight_image_data_source);
		temp_image_key := (select image_id from integration_layer.dim_sights_images where image_source = new.sight_image_data_source limit 1);

	-- remove special characters from city name before insertion
	formatted_city := (select UPPER(regexp_replace(NEW.sight_city,'[^-0-9A-Za-zÖÜÄßöüä ]','')));
	
	-- get city dimension table key
	temp_city_key := (select city_id from integration_layer.dim_sights_cities where city_name = formatted_city limit 1);
	if temp_city_key is null then
		INSERT INTO integration_layer.dim_sights_cities(city_name) values (formatted_city);
		temp_city_key := (select city_id from integration_layer.dim_sights_cities where city_name = formatted_city limit 1);
	end if;

	-- get timestamp dimension table key
	temp_timestamp_key := (select timestamp_id from integration_layer.dim_sights_timestamps where timestamp_unix = current_time_stamp limit 1);
	if temp_timestamp_key is null then
		insert into integration_layer.dim_sights_timestamps(timestamp_unix) values (current_time_stamp); 
	temp_timestamp_key := (select timestamp_id from integration_layer.dim_sights_timestamps where timestamp_unix = current_time_stamp limit 1);
	end if;

	-- get sights resolution table key
	temp_resolution_key := (select resolution_id from integration_layer.dim_sights_resolutions 
							where resolution_height = new.sight_image_height and resolution_width = new.sight_image_width limit 1);
	if temp_resolution_key is null then
		INSERT INTO integration_layer.dim_sights_resolutions(resolution_height, resolution_width) 
			values (new.sight_image_height, new.sight_image_width);
		temp_resolution_key := (select resolution_id from integration_layer.dim_sights_resolutions 
								where resolution_height = new.sight_image_height and resolution_width = new.sight_image_width limit 1);
	end if;

	-- create fact table entry
	temp_fact_key := (select count(*) from integration_layer.fact_sights as facts
						where facts.city_id = temp_city_key and facts.image_id = temp_image_key and 
							facts.resolution_id = temp_resolution_key and facts.timestamp_id = temp_timestamp_key);
	if temp_fact_key = 0 then
		insert into integration_layer.fact_sights(city_id, timestamp_id, image_id, resolution_id) 
			values (temp_city_key, temp_timestamp_key, temp_image_key, temp_resolution_key);
	end if;
	-- create 

	-- remove loaded entry from load layer
	delete from load_layer.sight_images where id = new.id;

	-- initialize data mart for city - if not there yet
	temp_city_images_data_mart_query := format('select
		image_data.image_file as image_file,
		image_data.image_labels as image_labels, 
		image_data.resolution_height as resolution_height,
		image_data.resolution_height as resolution_width
		from (
			select distinct(images.image_source) as url, 
				images.image_file as image_file, 
				images.image_labels as image_labels, 
				resolutions.resolution_height as resolution_height, 
				resolutions.resolution_width as resolution_width
			from integration_layer.dim_sights_images as images, 
				integration_layer.fact_sights AS facts, 
				integration_layer.dim_sights_resolutions AS resolutions
			WHERE facts.city_id = %s and resolutions.resolution_id = facts.resolution_id and 
				images.image_id = facts.image_id) as image_data', temp_city_key);
	
	EXECUTE format('CREATE MATERIALIZED VIEW IF NOT EXISTS data_mart_layer.%s AS %s', 'images_' || LOWER(formatted_city), temp_city_images_data_mart_query);  -- TODO check

    RETURN NEW;
END;
$$ 
LANGUAGE 'plpgsql';

-- create new image load trigger
drop trigger if exists load_images_into_dwh_trigger on load_layer.sight_images;

create trigger load_images_into_dwh_trigger
after insert on load_layer.sight_images
for each row
EXECUTE PROCEDURE load_images_into_dwh();
----------------------------------------------------------------------------------------------------------------
-- create sequence for trained models surrogate keys: model comparison would be way too slow!
create sequence if not exists trained_model_surrogate_key_sequuence;

-- create load job for model pushes
CREATE OR REPLACE FUNCTION load_models_into_dwh()
  RETURNS trigger as $$
  declare formatted_city VARCHAR(100) := (select UPPER(regexp_replace(NEW.city,'[^-0-9A-Za-zÖÜÄßöüä ]','')));
	declare temp_city_key INTEGER := NULL;   
	declare temp_trained_model_key INTEGER := NULL;   
	declare temp_timestamp_key INTEGER := NULL;   
	declare temp_trained_model_surrogate_key INTEGER := (select nextval('trained_model_surrogate_key_sequuence'));
	declare current_time_stamp BIGINT := (SELECT extract(epoch from now() at time zone 'utc'));

begin	
	-- get city dimension table key
	temp_city_key := (select city_id from integration_layer.dim_sights_cities where city_name = formatted_city limit 1);
	if temp_city_key is null then
		INSERT INTO integration_layer.dim_sights_cities(city_name) VALUES(formatted_city);
		temp_city_key := (select city_id from integration_layer.dim_sights_cities where city_name = formatted_city limit 1);
	end if;

	-- get timestamp dimension table key
	temp_timestamp_key := (select timestamp_id from integration_layer.dim_models_timestamps where timestamp_unix = current_time_stamp limit 1);
	if temp_timestamp_key is null then
		insert into integration_layer.dim_models_timestamps(timestamp_unix) values (current_time_stamp); 
	temp_timestamp_key := (select timestamp_id from integration_layer.dim_models_timestamps where timestamp_unix = current_time_stamp limit 1);
	end if;

	-- get trained models dimension table key
	INSERT INTO integration_layer.dim_models_trained_models(trained_model_model, output_sight_mapping, surrogate_key) 
		values (new.trained_model, new.mapping_table, temp_trained_model_surrogate_key);
	temp_trained_model_key := (select trained_model_id from integration_layer.dim_models_trained_models 
								where surrogate_key = temp_trained_model_surrogate_key limit 1);

	-- create fact table entry
	insert into integration_layer.fact_models(city_id, timestamp_id, trained_model_id) 
	values (temp_city_key, temp_timestamp_key, temp_trained_model_key);

	-- remove loaded entry from load layer
	delete from load_layer.trained_models where id = new.id;

    RETURN NEW;
END;
$$ 
LANGUAGE 'plpgsql';

-- create new image load trigger
drop trigger if exists load_models_into_dwh_trigger on load_layer.trained_models;

create trigger load_models_into_dwh_trigger
after insert on load_layer.trained_models
for each row
EXECUTE PROCEDURE load_models_into_dwh();
----------------------------------------------------------------------------------------------------------------
-- create load job for image sight labels pushes
CREATE OR REPLACE FUNCTION load_sight_labels_into_dwh()
  RETURNS trigger as $$
  declare temp_image_key INTEGER := NULL;   
  
begin	
	-- get image dimension table key
	temp_image_key := (select image_id from integration_layer.dim_sights_images where image_source = new.sight_image_data_source limit 1);
	if temp_image_key is not null then
		-- update persisted labels for respective image in integration layer
		update integration_layer.dim_sights_images set image_labels = new.sight_labels where image_id = temp_image_key;
	end if;	

	-- remove loaded entry from load layer
	delete from load_layer.sight_image_labels where id = new.id;

    RETURN NEW;
END;
$$ 
LANGUAGE 'plpgsql';

-- create new image sight labels load trigger
drop trigger if exists load_labels_into_dwh_trigger on load_layer.sight_image_labels;

create trigger load_labels_into_dwh_trigger
after insert on load_layer.sight_image_labels
for each row
EXECUTE PROCEDURE load_sight_labels_into_dwh();
----------------------------------------------------------------------------------------------------------------
-- speed up load jobs even more
drop index if exists idx_image_source;
drop index if exists idx_surrogate_key;

create index idx_image_source on integration_layer.dim_sights_images (image_source);
create index idx_surrogate_key on integration_layer.dim_models_trained_models (surrogate_key);
----------------------------------------------------------------------------------------------------------------
-- refresh all materialized views at once -> triggered by cron job
-- source: https://github.com/sorokine/RefreshAllMaterializedViews/blob/master/RefreshAllMaterializedViews.sql (12:43 AM, 14 November 2020)
CREATE OR REPLACE FUNCTION RefreshAllMaterializedViews(schema_arg TEXT DEFAULT 'public')
RETURNS INT AS $$
	DECLARE
		r RECORD;
	BEGIN
		RAISE NOTICE 'Refreshing materialized view in schema %', schema_arg;
		FOR r IN SELECT matviewname FROM pg_matviews WHERE schemaname = schema_arg 
		LOOP
			RAISE NOTICE 'Refreshing %.%', schema_arg, r.matviewname;
			EXECUTE 'REFRESH MATERIALIZED VIEW ' || schema_arg || '.' || r.matviewname; 
		END LOOP;
		
		RETURN 1;
	END 
$$ LANGUAGE plpgsql;

select RefreshAllMaterializedViews('data_mart_layer');
