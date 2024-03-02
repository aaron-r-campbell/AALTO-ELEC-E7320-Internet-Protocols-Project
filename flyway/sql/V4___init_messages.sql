-- Room: user1:user2
INSERT INTO messages (sender, room_id, content) VALUES ('user1', 1, 'Hello user2! How are you today?');
INSERT INTO messages (sender, room_id, content) VALUES ('user2', 1, 'Hi user1! I''m doing well, thanks. Any plans for the day?');
INSERT INTO messages (sender, room_id, content) VALUES ('user1', 1, 'Thinking about lunch. Any preferences?');
INSERT INTO messages (sender, room_id, content) VALUES ('user2', 1, 'How about grabbing some pizza?');

-- Room: user3:user4
INSERT INTO messages (sender, room_id, content) VALUES ('user3', 2, 'Hey user4! What''s up?');
INSERT INTO messages (sender, room_id, content) VALUES ('user4', 2, 'Not much, just chilling. Any exciting news?');
INSERT INTO messages (sender, room_id, content) VALUES ('user3', 2, 'I was thinking of watching a movie this weekend. Any suggestions?');
INSERT INTO messages (sender, room_id, content) VALUES ('user4', 2, 'How about checking out the new action movie at the theater?');

-- Room: Aalto Internet Protocols
INSERT INTO messages (sender, room_id, content) VALUES ('user1', 3, 'Hello team! Excited about our upcoming chat-app project!');
INSERT INTO messages (sender, room_id, content) VALUES ('user2', 3, 'Absolutely! Let''s discuss our roles and responsibilities.');
INSERT INTO messages (sender, room_id, content) VALUES ('user3', 3, 'I''ve been brainstorming some ideas for the user interface. Any preferences?');
INSERT INTO messages (sender, room_id, content) VALUES ('user4', 3, 'I''m focusing on the backend.');
INSERT INTO messages (sender, room_id, content) VALUES ('user2', 3, 'Great! Are there any specific functionalities we should prioritize?');
INSERT INTO messages (sender, room_id, content) VALUES ('user1', 3, 'I think real time communication would be a nice goal.');
