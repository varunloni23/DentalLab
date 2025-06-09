-- Dental Lab Database Schema

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS dental_lab_db;

-- Use the database
USE dental_lab_db;

-- Appointment table
CREATE TABLE IF NOT EXISTS appointment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    service VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- Material table
CREATE TABLE IF NOT EXISTS material (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock INT DEFAULT 0,
    category VARCHAR(50),
    image_url VARCHAR(200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Service table
CREATE TABLE IF NOT EXISTS service (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(10),
    features TEXT,
    price_range VARCHAR(50)
);

-- Order table
CREATE TABLE IF NOT EXISTS `order` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    customer_email VARCHAR(120) NOT NULL,
    customer_phone VARCHAR(20),
    material_id INT NOT NULL,
    quantity INT NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'processing',
    payment_status VARCHAR(20) DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    delivery_address TEXT,
    FOREIGN KEY (material_id) REFERENCES material(id)
);

-- Sample data for materials
INSERT INTO material (name, description, price, stock, category, image_url) VALUES
('Dental Ceramics', 'High-quality ceramic materials for crowns and bridges', 299.00, 50, 'Ceramics', '/static/images/ceramics.jpg'),
('Impression Materials', 'Precise impression materials for accurate molds', 149.00, 25, 'Impressions', '/static/images/impression.jpg'),
('Dental Alloys', 'Premium metal alloys for prosthetic work', 450.00, 15, 'Metals', '/static/images/alloys.jpg'),
('Composite Resins', 'Advanced composite materials for restorations', 199.00, 30, 'Composites', '/static/images/composite.jpg');

-- Sample data for services
INSERT INTO service (title, description, icon, features, price_range) VALUES
('Crown & Bridge', 'Premium ceramic and metal crowns with precision fitting for optimal patient comfort.', '👑', '["Zirconia Crowns", "PFM Crowns", "Full Metal Crowns", "3-Unit Bridges"]', '$200-$800'),
('Dental Implants', 'Custom implant solutions with titanium abutments and ceramic restorations.', '🦷', '["Implant Crowns", "Abutments", "Surgical Guides", "All-on-4 Solutions"]', '$500-$2000'),
('Orthodontics', 'Precision orthodontic appliances for effective treatment outcomes.', '📐', '["Clear Aligners", "Retainers", "Space Maintainers", "Expanders"]', '$150-$600'),
('Dentures', 'Complete and partial dentures with natural aesthetics and comfortable fit.', '😊', '["Full Dentures", "Partial Dentures", "Implant-Supported", "Repairs"]', '$300-$1200'); 