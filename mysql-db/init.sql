-- script that is executed only when the mysql container is first created
-- to make this script get executed again, run docker-compose down -v to remove the volume for the container
-- then run docker-compose up --build 

-- move this logic to application code

CREATE DATABASE IF NOT EXISTS task_db;
USE task_db;

-- Create the 'tasks' table
create table tasks (
   id INT AUTO_INCREMENT PRIMARY KEY,
   name VARCHAR(255) NOT NULL,
   description TEXT NOT NULL,
   completed BOOLEAN NOT NULL,
   startdate DATE,
   enddate DATE
);