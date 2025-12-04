-- =====================================================
-- EduROOM Database Setup Script
-- =====================================================
-- Description: Creates database, tables, and test data
-- Author: Blesssss
-- Usage: Run this script in MySQL Workbench
-- =====================================================

-- =====================================================
-- TEST LOGIN CREDENTIALS
-- =====================================================
-- Use these credentials to test the application:
--
-- ADMIN ACCOUNT:
--   Email: admin@cspc.edu.ph
--   ID Number: 00000000
--   Password: admin123
--
-- FACULTY ACCOUNTS:
--   Email: profsmith@my.cspc.edu.ph
--   ID Number: 20231001
--   Password: faculty2025
--
--   Email: profjohnson@my.cspc.edu.ph
--   ID Number: 20231002
--   Password: faculty2025
--
-- STUDENT ACCOUNTS:
--   Email: johndoe@my.cspc.edu.ph
--   ID Number: 25123456
--   Password: student2025
--
--   Email: janesmith@my.cspc.edu.ph
--   ID Number: 25123457
--   Password: student2025
--

-- =====================================================

-- Create Database
CREATE DATABASE IF NOT EXISTS classroom_reservation_db;
USE classroom_reservation_db;

-- Drop existing tables if they exist (for fresh setup)
DROP TABLE IF EXISTS activity_logs;
DROP TABLE IF EXISTS reservations;
DROP TABLE IF EXISTS classrooms;
DROP TABLE IF EXISTS users;

-- Create Users Table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    id_number VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'faculty', 'student') NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_email (email),
    INDEX idx_id_number (id_number),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create Classrooms Table
CREATE TABLE classrooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_name VARCHAR(50) NOT NULL,
    building VARCHAR(100) NOT NULL,
    capacity INT NOT NULL,
    status ENUM('Available', 'Occupied', 'Maintenance') DEFAULT 'Available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create Reservations Table
CREATE TABLE reservations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    classroom_id INT NOT NULL,
    user_id INT NOT NULL,
    reservation_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    purpose TEXT NOT NULL,
    status ENUM('pending', 'approved', 'rejected', 'cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (classroom_id) REFERENCES classrooms(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_classroom_date (classroom_id, reservation_date),
    INDEX idx_user (user_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create Activity Logs Table
CREATE TABLE activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(255) NOT NULL,
    details TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_action (user_id, action),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert Sample Classrooms
INSERT INTO classrooms (room_name, building, capacity, status) VALUES
('Room 101', 'Main Building', 30, 'Available'),
('Room 102', 'Main Building', 25, 'Available'),
('Room 103', 'Main Building', 35, 'Available'),
('Lab 201', 'Science Building', 20, 'Available'),
('Lab 202', 'Science Building', 15, 'Available'),
('Lab 203', 'Science Building', 18, 'Available'),
('Room 301', 'Engineering Building', 40, 'Available'),
('Room 302', 'Engineering Building', 30, 'Available'),
('Computer Lab 1', 'IT Building', 25, 'Available'),
('Computer Lab 2', 'IT Building', 25, 'Available');

-- Insert Test Users
-- NOTE: Password hashes correspond to:
-- Admin: admin123
-- Faculty: faculty2025
-- Student: student2025

INSERT INTO users (email, id_number, password_hash, role, full_name) VALUES
-- Admin Account
('admin@cspc.edu.ph', '00000000', '$2b$12$PUPdb6Nzizg47zWbC7fCQO46bKTEfSkWrY.RrqFGX823lz2fOhONG', 'admin', 'Admin User'),

-- Faculty Accounts
('profsmith@my.cspc.edu.ph', '20231001', '$2b$12$tJzBR7wwDZ6mgx.dW8dk7OVo.RA13eIMK2HZX3BDvLqZtXIEGClyu', 'faculty', 'Prof. John Smith'),
('profjohnson@my.cspc.edu.ph', '20231002', '$2b$12$tJzBR7wwDZ6mgx.dW8dk7OVo.RA13eIMK2HZX3BDvLqZtXIEGClyu', 'faculty', 'Prof. Sarah Johnson'),

-- Student Accounts
('johndoe@my.cspc.edu.ph', '25123456', '$2b$12$9yGI7zOzRNxlmV5bX4i84eXujMFv86nOTWpw2H8IYuiIQjqmGWbQC', 'student', 'John Doe'),
('janesmith@my.cspc.edu.ph', '25123457', '$2b$12$9yGI7zOzRNxlmV5bX4i84eXujMFv86nOTWpw2H8IYuiIQjqmGWbQC', 'student', 'Jane Smith'),

-- Insert Sample Reservations
INSERT INTO reservations (classroom_id, user_id, reservation_date, start_time, end_time, purpose, status) VALUES
-- Pending reservations (need approval)
(1, 2, '2025-12-10', '09:00:00', '11:00:00', 'Computer Science Lecture', 'pending'),
(2, 3, '2025-12-10', '13:00:00', '15:00:00', 'Mathematics Class', 'pending'),
(4, 4, '2025-12-11', '10:00:00', '12:00:00', 'Chemistry Lab Session', 'pending'),

-- Approved reservations
(3, 2, '2025-12-08', '08:00:00', '10:00:00', 'English Literature Discussion', 'approved'),
(5, 3, '2025-12-09', '14:00:00', '16:00:00', 'Physics Lab Experiment', 'approved'),

-- Rejected reservations
(6, 4, '2025-12-07', '11:00:00', '13:00:00', 'Biology Dissection', 'rejected');

-- Verify Setup
SELECT '✓ Database setup complete!' as 'Status';
SELECT 
    (SELECT COUNT(*) FROM users) as 'Users',
    (SELECT COUNT(*) FROM classrooms) as 'Classrooms',
    (SELECT COUNT(*) FROM reservations) as 'Reservations';

-- Show test accounts
SELECT 
    role as 'Role',
    full_name as 'Name',
    email as 'Email',
    id_number as 'ID Number',
    CASE role
        WHEN 'admin' THEN 'admin123'
        WHEN 'faculty' THEN 'faculty2025'
        WHEN 'student' THEN 'student2025'
    END as 'Password'
FROM users
ORDER BY 
    CASE role
        WHEN 'admin' THEN 1
        WHEN 'faculty' THEN 2
        WHEN 'student' THEN 3
    END,
    full_name;