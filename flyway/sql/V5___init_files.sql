-- Inserting a file with default name and content
INSERT INTO files (room_id)
VALUES (1);

-- Inserting a file with a specified name and content
INSERT INTO files (name, room_id)
VALUES ('example_file', 1);

-- Inserting another file with default name and content
INSERT INTO files (room_id)
VALUES (2);