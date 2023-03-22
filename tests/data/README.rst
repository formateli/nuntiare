Install all databases required by Nuntiare Test
-----------------------------------------------

1.- Create databases using psql:
    # sudo -u postgres psql
    # CREATE DATABASE database_name ENCODING 'UTF8';

    Do this for panama, adventureworks and northwind

    # \quit

2.- Run sql file for each database
    # sudo -u postgres psql -d database_name -a -f database_name.sql

3.- Create file with string connection for each database in tests/unittest directory

    string format: dbname=databasename user=username password=secret host=localhost port=5432

    1.- db_test_connection_northwind
    2.- db_test_connection_adventure
    3.- db_test_connection_panama

