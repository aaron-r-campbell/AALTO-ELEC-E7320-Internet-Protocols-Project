CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    friendly_name TEXT NOT NULL
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER REFERENCES users(id),
    message TEXT NOT NULL,
    sent TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE files (
    id SERIAL PRIMARY KEY
);
