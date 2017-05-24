# REST-full-Api-Server

# To begin

### using docker
##### start server:
    docker-compose up -d
    docker ps
##### install default user-roles:
    docker exec -it server_online_couses python manage.py app install
    * after install you can login at system
    using login 'root', password 'root'

##### using:
    server api:
        http://localhost:5000/api/1.0/
    swagger-ui:
        http://localhost:5000/index.html
    swagger-api:
        http://localhost:5000/api-docs

    access to postgresql-db:
        localhost:5032 (postgres/postgres)

##### run python integrated-test:
    docker exec -it server_online_couses python http_client/run.py

### docker in vagrant (for 32 bit system)
    vagrant up
    vagrant ssh