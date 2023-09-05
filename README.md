**Docker-compose commands for running the application** \
- docker-compose up --build (running for the first time)
- docker-compose up (subsequent startups)
- docker-compose down (remove containers)
- docker-compose stop / ctrl + c in terminal (stop containers in docker-compose)
- docker-compose down -v (remove containers and volumes)

**FastAPI docs** : localhost:8000/docs

**TODOS:**
- Move sql.init logic to application side **(DONE)**
- Use SQLachemy ORM
- use pylint
- use pytest for testing
- have proper code structure
- SonarQube