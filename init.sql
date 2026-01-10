-- Initial MySQL setup script
-- This runs automatically when MySQL container starts for the first time

CREATE DATABASE IF NOT EXISTS taskdb4 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

GRANT ALL PRIVILEGES ON taskdb4.* TO 'taskuser'@'%';
GRANT ALL PRIVILEGES ON taskdb4.* TO 'taskuser'@'localhost';

FLUSH PRIVILEGES;

USE taskdb4;