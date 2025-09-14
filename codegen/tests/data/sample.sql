CREATE TABLE user (
    id VARCHAR(40) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_password (
    id VARCHAR(40) PRIMARY KEY,
    user_id VARCHAR(40) NOT NULL,
    password TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id)
);
