#!/bin/bash

echo "bind-address = mariadb" >> /etc/mysql/mariadb.conf.d/50-server.cnf

mysqld_safe &

sleep 10

# Execute the SQL commands with MariaDB
mariadb -u root -p"$SQL_ROOT_PASSWORD" <<SQL
CREATE DATABASE IF NOT EXISTS \`$SQL_DATABASE\`;
CREATE USER 'root'@'%' IDENTIFIED BY '$SQL_ROOT_PASSWORD';
CREATE USER IF NOT EXISTS '$SQL_USER'@'%' IDENTIFIED BY '$SQL_PASSWORD';
GRANT ALL PRIVILEGES ON \`$SQL_DATABASE\`.* TO '$SQL_USER'@'%' IDENTIFIED BY '$SQL_PASSWORD';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
SQL

mariadb-admin -u root -p"$SQL_ROOT_PASSWORD" shutdown

mysqld_safe
