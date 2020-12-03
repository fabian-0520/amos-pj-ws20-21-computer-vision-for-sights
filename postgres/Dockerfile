FROM postgres

#Set User and Password
ENV POSTGRES_USER docker
ENV POSTGRES_PASSWORD docker

EXPOSE 5432

# Copy init script and execute it
COPY database_init.sql /docker-entrypoint-initdb.d/

# Run with:
# docker build -t postgres:v1 .
# $ docker run -d -p 5432:5432 postgres:v1
