-- script that is executed only when the mysql container is first created
-- to make this script get executed again, run docker-compose down -v && docker-compose up --build 

CREATE DATABASE IF NOT EXISTS task_db;

-- create table tasks(
--    id INT AUTO_INCREMENT PRIMARY KEY,
--    name VARCHAR(255) NOT NULL,
--    description TEXT NOT NULL,
--    completed BOOLEAN NOT NULL,
--    startdate DATE,
--    enddate DATE
-- );