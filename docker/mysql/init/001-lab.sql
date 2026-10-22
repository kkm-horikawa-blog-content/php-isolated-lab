-- 公開された検証専用データと資格情報。空の MySQL volume の初回のみ実行。
CREATE DATABASE IF NOT EXISTS laravel_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS wp_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'laravel_lab'@'%' IDENTIFIED BY 'LaravelLab_2026_SampleOnly';
CREATE USER 'wp_lab'@'%' IDENTIFIED BY 'WpLab_2026_SampleOnly';
GRANT ALL PRIVILEGES ON laravel_db.* TO 'laravel_lab'@'%';
GRANT ALL PRIVILEGES ON wp_db.* TO 'wp_lab'@'%';

USE laravel_db;
CREATE TABLE users (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    email_verified_at TIMESTAMP NULL,
    password VARCHAR(255) NOT NULL,
    remember_token VARCHAR(100) NULL,
    created_at TIMESTAMP NULL,
    updated_at TIMESTAMP NULL
) ENGINE=InnoDB;
-- bcrypt ハッシュは公開サンプル password に対応する。実在の人物を含まない。
INSERT INTO users (name, email, password, created_at, updated_at) VALUES
('Sample Alice', 'alice@example.test', '$2y$12$/J.pY1He2cf1cTpep1eD8eTijipuzvziEFWcpLlB16b7pNNEJW.Dy', NOW(), NOW()),
('Sample Bob', 'bob@example.test', '$2y$12$/J.pY1He2cf1cTpep1eD8eTijipuzvziEFWcpLlB16b7pNNEJW.Dy', NOW(), NOW()),
('Sample Carol', 'carol@example.test', '$2y$12$/J.pY1He2cf1cTpep1eD8eTijipuzvziEFWcpLlB16b7pNNEJW.Dy', NOW(), NOW());
