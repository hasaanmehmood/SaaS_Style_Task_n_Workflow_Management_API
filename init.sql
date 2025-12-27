-- Initial MySQL setup script
-- This runs automatically when the MySQL container starts

CREATE DATABASE IF NOT EXISTS taskdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Grant privileges
GRANT ALL PRIVILEGES ON taskdb.* TO 'taskuser'@'%';
FLUSH PRIVILEGES;