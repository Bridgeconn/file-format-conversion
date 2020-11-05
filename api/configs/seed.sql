DROP DATABASE IF EXISTS bridgeengine;
CREATE DATABASE file_converter_data;

CREATE TABLE users (
	user_id BIGSERIAL PRIMARY KEY, 
	public_id TEXT UNIQUE NOT NULL,
	email TEXT UNIQUE NOT NULL,
	password TEXT NOT NULL,
	user_name TEXT NOT NULL,
	verification_code TEXT,
	email_verified BOOLEAN DEFAULT FALSE,
	created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP(2), 
	updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP(2) 
);

CREATE TABLE files_data (
	file_id BIGSERIAL PRIMARY KEY, 
	user_id BIGINT REFERENCES users(user_id) NOT NULL,
	file_path TEXT NOT NULL,
	file_name TEXT NOT NULL,
	target_file_name TEXT,
	target_type TEXT NOT NULL,
	file_converted BOOLEAN DEFAULT FALSE,
	created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP(2), 
	updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP(2) 
);
