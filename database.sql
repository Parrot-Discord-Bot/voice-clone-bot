DROP TABLE IF EXISTS `prompts`;

CREATE TABLE prompts (
    prompt_id INT AUTO_INCREMENT PRIMARY KEY,
    date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    command VARCHAR(255),
    voice_id VARCHAR(255) REFERENCES voices(voice_id),
    user_id BIGINT REFERENCES users(user_id),
    server_id BIGINT NOT NULL,
    prompt TEXT,
    response TEXT,
    path VARCHAR(255) DEFAULT NULL
);

DROP TABLE IF EXISTS `users`;

CREATE TABLE users (
    user_id BIGINT NOT NULL PRIMARY KEY,
    date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    username VARCHAR(255) NOT NULL,
    privileges VARCHAR(255) DEFAULT 'normal_user'
);

DROP TABLE IF EXISTS `voices`;

CREATE TABLE voices (
    voice_id INT AUTO_INCREMENT PRIMARY KEY,
    date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    name VARCHAR(255),
    shortcut VARCHAR(5),
    user_id BIGINT REFERENCES users(user_id),
    server_id BIGINT REFERENCES servers(server_id),
    path VARCHAR(255) DEFAULT NULL,
    CONSTRAINT unique_server_name UNIQUE (server_id, name)
);

DROP TABLE IF EXISTS `servers`;

CREATE TABLE servers(
    server_id BIGINT NOT NULL PRIMARY KEY,
    server_name VARCHAR(255) NOT NULL
);