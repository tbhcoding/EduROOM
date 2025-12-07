-- =====================================================
-- Sampl EduROOM Database Setup Script
-- =====================================================
-- Description: Creates database, tables, and test data
-- Author: TechValks
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
--   Email: ibo@my.cspc.edu.ph
--   ID Number: 20231001
--   Password: faculty2025
--
--   Email: colle@my.cspc.edu.ph
--   ID Number: 20231002
--   Password: faculty2025
--
--   Email: fortuno@my.cspc.edu.ph
--   ID Number: 20231003
--   Password: faculty2025
--
--   (Additional faculty: pandes, onesa, olleres, buena, aurillas)
--   ID Numbers: 20231004-20231008
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

-- =====================================================
-- DROP EXISTING TABLES SAFELY (INCLUDING NOTIFICATIONS)
-- =====================================================
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS activity_logs;
DROP TABLE IF EXISTS reservations;
DROP TABLE IF EXISTS classrooms;
DROP TABLE IF EXISTS users;

SET FOREIGN_KEY_CHECKS = 1;

-- =====================================================
-- CREATE TABLES
-- =====================================================

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
    image_url VARCHAR(255) DEFAULT NULL,
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
    status ENUM('pending', 'approved', 'rejected', 'cancelled', 'ongoing', 'done') DEFAULT 'pending',
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

-- Create Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    message TEXT NOT NULL,
    reservation_id INT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (reservation_id) REFERENCES reservations(id) ON DELETE CASCADE,
    INDEX idx_user_read (user_id, is_read),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- INSERT SAMPLE DATA
-- =====================================================

-- Insert Real Classrooms
INSERT INTO classrooms (room_name, building, capacity, status, image_url) VALUES
('CS Lab', '2nd Floor', 30, 'Available', '../assets/images/cs-lab.png'),
('ERP Lab', '3rd Floor', 25, 'Available', '../assets/images/erp-lab.png'),
('IT Lab 1', '2nd Floor', 35, 'Available', '../assets/images/it-lab-1.png'),
('IT Lab 2', '2nd Floor', 35, 'Available', '../assets/images/it-lab-2.png'),
('Lecture Room 1', '1st Floor', 50, 'Available', '../assets/images/lecture-room-1.png'),
('Lecture Room 2', '1st Floor', 45, 'Available', '../assets/images/lecture-room-2.png'),
('LIS Lab', '4th Floor', 20, 'Available', '../assets/images/lis-lab.png'),
('MAC Lab', '3rd Floor', 30, 'Available', '../assets/images/mac-lab.png'),
('NAS Lab', '3rd Floor', 25, 'Available', '../assets/images/nas-lab.png'),
('Open Lab', '2nd Floor', 40, 'Available', '../assets/images/open-lab.png'),
('RISE Lab', '4th Floor', 15, 'Available', '../assets/images/rise-lab.png');

-- Insert Test Users
-- NOTE: Password hashes correspond to:
-- Admin: admin123
-- Faculty: faculty2025
-- Student: student2025

INSERT INTO users (email, id_number, password_hash, role, full_name) VALUES
-- Admin Account
('admin@cspc.edu.ph', '00000000', '$2b$12$PUPdb6Nzizg47zWbC7fCQO46bKTEfSkWrY.RrqFGX823lz2fOhONG', 'admin', 'Admin User'),

-- Faculty Accounts
('ibo@my.cspc.edu.ph', '20231001', '$2b$12$tJzBR7wwDZ6mgx.dW8dk7OVo.RA13eIMK2HZX3BDvLqZtXIEGClyu', 'faculty', 'Mr. Ibo'),
('colle@my.cspc.edu.ph', '20231002', '$2b$12$tJzBR7wwDZ6mgx.dW8dk7OVo.RA13eIMK2HZX3BDvLqZtXIEGClyu', 'faculty', 'Mr. Colle'),
('fortuno@my.cspc.edu.ph', '20231003', '$2b$12$tJzBR7wwDZ6mgx.dW8dk7OVo.RA13eIMK2HZX3BDvLqZtXIEGClyu', 'faculty', 'Ms. Fortuno'),
('pandes@my.cspc.edu.ph', '20231004', '$2b$12$tJzBR7wwDZ6mgx.dW8dk7OVo.RA13eIMK2HZX3BDvLqZtXIEGClyu', 'faculty', 'Ms. Pandes'),
('onesa@my.cspc.edu.ph', '20231005', '$2b$12$tJzBR7wwDZ6mgx.dW8dk7OVo.RA13eIMK2HZX3BDvLqZtXIEGClyu', 'faculty', 'Mrs. Onesa'),
('olleres@my.cspc.edu.ph', '20231006', '$2b$12$tJzBR7wwDZ6mgx.dW8dk7OVo.RA13eIMK2HZX3BDvLqZtXIEGClyu', 'faculty', 'Mr. Olleres'),
('buena@my.cspc.edu.ph', '20231007', '$2b$12$tJzBR7wwDZ6mgx.dW8dk7OVo.RA13eIMK2HZX3BDvLqZtXIEGClyu', 'faculty', 'Mr. Buena'),
('aurillas@my.cspc.edu.ph', '20231008', '$2b$12$tJzBR7wwDZ6mgx.dW8dk7OVo.RA13eIMK2HZX3BDvLqZtXIEGClyu', 'faculty', 'Mrs. Aurillas'),

-- Student Accounts
('johndoe@my.cspc.edu.ph', '25123456', '$2b$12$9yGI7zOzRNxlmV5bX4i84eXujMFv86nOTWpw2H8IYuiIQjqmGWbQC', 'student', 'John Doe'),
('janesmith@my.cspc.edu.ph', '25123457', '$2b$12$9yGI7zOzRNxlmV5bX4i84eXujMFv86nOTWpw2H8IYuiIQjqmGWbQC', 'student', 'Jane Smith');

-- Insert Sample Reservations with Realistic Schedules for Today and Tomorrow
-- Today's date: 2025-12-06
INSERT INTO reservations (classroom_id, user_id, reservation_date, start_time, end_time, purpose, status) VALUES
-- TODAY (2025-12-06) - Approved schedules for showcase
(1, 2, '2025-12-06', '08:00:00', '10:00:00', 'Programming Fundamentals', 'approved'),
(1, 3, '2025-12-06', '10:30:00', '12:30:00', 'Data Structures Lab', 'approved'),
(1, 4, '2025-12-06', '14:00:00', '16:00:00', 'Algorithm Design Workshop', 'approved'),

(2, 2, '2025-12-06', '09:00:00', '11:00:00', 'Enterprise Systems Training', 'approved'),
(2, 3, '2025-12-06', '13:00:00', '15:00:00', 'SAP Module Demo', 'approved'),

(3, 4, '2025-12-06', '08:00:00', '10:00:00', 'Network Configuration Lab', 'approved'),
(3, 2, '2025-12-06', '13:00:00', '15:00:00', 'Cybersecurity Essentials', 'approved'),

(5, 3, '2025-12-06', '09:00:00', '11:00:00', 'Software Engineering Lecture', 'approved'),
(5, 4, '2025-12-06', '14:00:00', '16:00:00', 'Project Management Seminar', 'approved'),

(6, 2, '2025-12-06', '10:00:00', '12:00:00', 'Research Methodology Lecture', 'approved'),
(6, 3, '2025-12-06', '15:00:00', '17:00:00', 'Thesis Defense', 'approved'),

(7, 2, '2025-12-06', '10:00:00', '12:00:00', 'iOS Development Workshop', 'approved'),

(9, 3, '2025-12-06', '08:00:00', '10:00:00', 'Open Lab Session', 'approved'),
(9, 4, '2025-12-06', '15:00:00', '17:00:00', 'Student Hackathon', 'approved'),

-- TOMORROW (2025-12-07) - Mix of approved and pending
(1, 2, '2025-12-07', '08:00:00', '10:00:00', 'Web Development Class', 'approved'),
(1, 3, '2025-12-07', '13:00:00', '15:00:00', 'Database Management', 'pending'),

(4, 4, '2025-12-07', '09:00:00', '11:00:00', 'IT Lab Practical Exam', 'approved'),
(4, 2, '2025-12-07', '14:00:00', '16:00:00', 'Mobile App Development', 'pending'),

(5, 3, '2025-12-07', '10:00:00', '12:00:00', 'Digital Marketing Lecture', 'approved'),

(6, 4, '2025-12-07', '13:00:00', '15:00:00', 'Academic Writing Workshop', 'pending'),

(7, 3, '2025-12-07', '10:00:00', '12:00:00', 'Information Systems Research', 'approved'),

(8, 4, '2025-12-07', '08:00:00', '10:00:00', 'Network Administration Lab', 'approved'),

(9, 2, '2025-12-07', '13:00:00', '15:00:00', 'AI Research Session', 'approved'),

-- FUTURE DATES (2025-12-10) - For testing availability
(1, 2, '2025-12-10', '09:00:00', '11:00:00', 'Advanced Programming', 'pending'),
(2, 3, '2025-12-10', '13:00:00', '15:00:00', 'Business Intelligence Workshop', 'pending'),
(6, 4, '2025-12-10', '10:00:00', '12:00:00', 'Capstone Project Presentation', 'pending');

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

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

-- Show today's schedule for showcase
SELECT 
    c.room_name as 'Room',
    c.building as 'Floor',
    DATE_FORMAT(r.start_time, '%H:%i') as 'Start',
    DATE_FORMAT(r.end_time, '%H:%i') as 'End',
    r.purpose as 'Purpose',
    r.status as 'Status'
FROM reservations r
JOIN classrooms c ON r.classroom_id = c.id
WHERE r.reservation_date = '2025-12-06'
ORDER BY c.room_name, r.start_time;
