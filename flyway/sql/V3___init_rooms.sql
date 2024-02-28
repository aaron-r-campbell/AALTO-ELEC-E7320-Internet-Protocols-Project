-- Create dummy rooms
INSERT INTO rooms (name) VALUES ('user1:user2');
INSERT INTO rooms (name) VALUES ('user3:user4');
INSERT INTO rooms (name) VALUES ('Aalto Internet Protocols');

-- Distribute users to rooms. Exclude user5
INSERT INTO user_room_mappings (user_name, room_id) VALUES ('user1', 1);
INSERT INTO user_room_mappings (user_name, room_id) VALUES ('user2', 1);
INSERT INTO user_room_mappings (user_name, room_id) VALUES ('user3', 2);
INSERT INTO user_room_mappings (user_name, room_id) VALUES ('user4', 2);
INSERT INTO user_room_mappings (user_name, room_id) VALUES ('user1', 3);
INSERT INTO user_room_mappings (user_name, room_id) VALUES ('user2', 3);
INSERT INTO user_room_mappings (user_name, room_id) VALUES ('user3', 3);
INSERT INTO user_room_mappings (user_name, room_id) VALUES ('user4', 3);