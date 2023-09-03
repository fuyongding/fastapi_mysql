CREATE DATABASE IF NOT EXISTS task123;
USE task123;

-- Create the 'tasks' table
create table tasks (
   id INT AUTO_INCREMENT PRIMARY KEY,
   name VARCHAR(255) NOT NULL,
   description TEXT NOT NULL,
   completed BOOLEAN NOT NULL,
   startdate DATE,
   enddate DATE
);