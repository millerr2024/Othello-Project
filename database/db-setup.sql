CREATE DATABASE login;

\c login;

CREATE TABLE userInfo (
	username TEXT,
	pass TEXT,
	date_joined TEXT
);

-- Dummy users for testing
INSERT INTO userInfo (username, pass, date_joined) VALUES ('TestUsername', 'TestPassword', '08 Mar 2024');
INSERT INTO userInfo (username, pass, date_joined) VALUES ('TestUsername2', 'TestPassword2', '08 Mar 2024');
INSERT INTO userInfo (username, pass, date_joined) VALUES ('test1', 'test1', '27 May 2024');
INSERT INTO userInfo (username, pass, date_joined) VALUES ('test2', 'test2', '27 May 2024');
INSERT INTO userInfo (username, pass, date_joined) VALUES ('test3', 'test3', '27 May 2024');


CREATE TABLE gameInfo (
	gameID INT PRIMARY KEY,
	gameJSON json,
	blackPlayerID TEXT,
	whitePlayerID TEXT
);

CREATE USER webapp;

alter user webapp with encrypted password 'dbPass';

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO webapp;

CREATE SEQUENCE game_id_sequence;

GRANT USAGE, SELECT ON SEQUENCE game_id_sequence TO webapp;

-- Dummy gameInfo values for testing
INSERT INTO gameInfo VALUES
	(10000, '{"gameID": 19, "board": "WWWWWWBBWWWBWWBBWBBWBWBBWBWWBWBBWWWBBWBBWWBBBBBBWWWBBBBBBBBBBBBB", "W": "test1", "B": "test2", "legalMoves": [], "turn": "B", "flips": [[1, 5], [0, 4], [1, 4], [2, 3], [3, 2], [4, 1]], "lastMove": [0, 5], "status": "B"}', 'test2', 'test1'),
	(10001, '{"gameID": 13, "board": "WWWWWWWWBBBBBBWBBBBWBWBBBBBBBWBBBWBBWWBBBBBWBWBBBWWBWWWBBWWWWWBB", "W": "ai2", "B": "test1", "legalMoves": [], "turn": "W", "flips": [], "lastMove": [9, 9], "status": "B"}', 'test1', 'ai2'),
	(10002, '{"gameID": 12, "board": "BBBBBBBBBBWWWWWBBBWBBBWBBBBWWWWBBBWWWBWBBWBBWBBBWBBBBBBBBBBBBBWB", "W": "ai2", "B": "test1", "legalMoves": [], "turn": "W", "flips": [], "lastMove": [9, 9], "status": "B"}', 'test1', 'ai2'),
	(10003, '{"gameID": 11, "board": "WBBBBBBBBBBBBBBWBBWBBBBWWWBWBWBWWBBBWWBWWWBWBWBWBBWBWBBBBBBBBBBB", "W": "test1", "B": "test3", "legalMoves": [], "turn": "W", "flips": [[7, 1], [7, 2], [7, 3], [6, 1], [5, 2]], "lastMove": [7, 0], "status": "B"}', 'test3', 'test1'),
	(10004, '{"gameID": 91, "board": "WWWWWWBBWWWBWWBBWBBWBWBBWBWWBWBBWWWBBWBBWWBBBBBBWWWBBBBBBBBBBBBB", "W": "test2", "B": "test1", "legalMoves": [], "turn": "B", "flips": [[1, 5], [0, 4], [1, 4], [2, 3], [3, 2], [4, 1]], "lastMove": [0, 5], "status": "B"}', 'test2', 'test1'),
	(10005, '{"gameID": 31, "board": "WWWWWWWWBBBBBBWBBBBWBWBBBBBBBWBBBWBBWWBBBBBWBWBBBWWBWWWBBWWWWWBB", "W": "test1", "B": "ai", "legalMoves": [], "turn": "W", "flips": [], "lastMove": [9, 9], "status": "B"}', 'test1', 'ai'),
	(10006, '{"gameID": 21, "board": "BBBBBBBBBBWWWWWBBBWBBBWBBBBWWWWBBBWWWBWBBWBBWBBBWBBBBBBBBBBBBBWB", "W": "test1", "B": "ai2", "legalMoves": [], "turn": "W", "flips": [], "lastMove": [9, 9], "status": "B"}', 'ai2', 'test1'),
	(10007, '{"gameID": 10, "board": "WBBBBBBBBBBBBBBWBBWBBBBWWWBWBWBWWBBBWWBWWWBWBWBWBBWBWBBBBBBBBBBB", "W": "test3", "B": "test1", "legalMoves": [], "turn": "W", "flips": [[7, 1], [7, 2], [7, 3], [6, 1], [5, 2]], "lastMove": [7, 0], "status": "B"}', 'test1', 'test3');