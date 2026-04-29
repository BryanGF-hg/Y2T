CREATE DATABASE ytt_copilot
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER 'ytt_user'@'localhost' IDENTIFIED BY 'contrasenya123$';
GRANT ALL PRIVILEGES ON ytt_copilot.* TO 'ytt_user'@'localhost';
FLUSH PRIVILEGES;



CREATE TABLE videos (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  youtube_url VARCHAR(500) NOT NULL,
  title VARCHAR(300),
  source_lang VARCHAR(20),
  target_lang VARCHAR(20),
  transcript LONGTEXT,
  transcript_translated LONGTEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY uq_youtube_url (youtube_url),
  INDEX idx_title (title),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;
  
  
  
  
  CREATE TABLE settings (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  config_key VARCHAR(100) NOT NULL,
  config_value VARCHAR(500),

  UNIQUE KEY uq_config_key (config_key)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;

INSERT INTO settings (config_key, config_value) VALUES
('default_target_lang', 'es'),
('selenium_headless', 'true'),
('translator_provider', 'none');




CREATE TABLE activity_log (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  action VARCHAR(50) NOT NULL,
  entity VARCHAR(50),
  entity_id INT UNSIGNED,
  details TEXT,

  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  INDEX idx_action (action),
  INDEX idx_entity (entity, entity_id)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;
  
INSERT INTO activity_log (action, entity, entity_id, details)
VALUES ('SCRAPE', 'videos', 1, 'Transcript obtenido vía Selenium');



Queries CRUD básicas (para debug o pruebas)
Insertar video:
INSERT INTO videos (youtube_url, target_lang)
VALUES ('https://www.youtube.com/watch?v=XXXXX', 'es');

Listar últimos:
SELECT id, title, youtube_url, created_at
FROM videos
ORDER BY updated_at DESC
LIMIT 20;

Actualizar transcript:
UPDATE videos
SET transcript = 'texto...',
    transcript_translated = 'texto traducido...'
WHERE id = 1;

Eliminar:
DELETE FROM videos WHERE id = 1;
