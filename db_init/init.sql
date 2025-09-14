-- Crear base de datos y configurar
USE jdmmitagente_db;

-- Tabla de conversaciones
CREATE TABLE IF NOT EXISTS conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_message TEXT NOT NULL,
    assistant_message TEXT NOT NULL,
    session_id VARCHAR(255),
    INDEX idx_timestamp (timestamp),
    INDEX idx_session (session_id)
);

-- Tabla de memoria a largo plazo
CREATE TABLE IF NOT EXISTS long_term_memory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    key_info VARCHAR(255) NOT NULL,
    details TEXT,
    importance_level INT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_key_info (key_info),
    INDEX idx_importance (importance_level)
);

-- Tabla de configuraciones del usuario
CREATE TABLE IF NOT EXISTS user_configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla de tareas programadas
CREATE TABLE IF NOT EXISTS scheduled_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_name VARCHAR(255) NOT NULL,
    description TEXT,
    scheduled_time DATETIME NOT NULL,
    status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME NULL,
    INDEX idx_scheduled_time (scheduled_time),
    INDEX idx_status (status)
);

-- Insertar configuraciones por defecto
INSERT INTO user_configs (config_key, config_value) VALUES 
('assistant_name', 'JDMMitAgente'),
('voice_enabled', 'true'),
('notification_enabled', 'true'),
('language', 'es-ES')
ON DUPLICATE KEY UPDATE config_value = VALUES(config_value);
