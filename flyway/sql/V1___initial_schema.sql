CREATE TABLE users (
    username TEXT NOT NULL PRIMARY KEY UNIQUE,
    password TEXT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT FALSE,
    last_seen TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE rooms (
    id SERIAL NOT NULL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE user_room_mappings (
    user_name TEXT REFERENCES users(username),
    room_id INT REFERENCES rooms(id),
    PRIMARY KEY (user_name, room_id)
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    sender TEXT REFERENCES users(username),
    room_id INT REFERENCES rooms(id),
    content TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE files (
    id SERIAL PRIMARY KEY
);

