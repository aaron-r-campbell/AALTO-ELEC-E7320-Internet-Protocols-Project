CREATE TABLE users (
    name TEXT NOT NULL PRIMARY KEY UNIQUE,
    password TEXT NOT NULL,
    friendly_name TEXT NOT NULL
);

CREATE TABLE rooms (
    id SERIAL NOT NULL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE user_room_mappings (
    user_name TEXT REFERENCES users(name),
    room_id INT REFERENCES rooms(id),
    PRIMARY KEY (user_name, room_id)
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    sender_name TEXT REFERENCES users(name),
    room_id INT REFERENCES rooms(id),
    message TEXT NOT NULL,
    sent TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE files (
    id SERIAL PRIMARY KEY
);
