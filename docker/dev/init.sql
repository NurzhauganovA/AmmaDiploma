CREATE USER smartschooladmin WITH PASSWORD '@WSX3edc';
CREATE DATABASE smartschool_diploma;
GRANT ALL PRIVILEGES ON DATABASE smartschool_diploma TO smartschooladmin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO smartschooladmin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO smartschooladmin;
ALTER DATABASE smartschool_diploma OWNER TO smartschooladmin;