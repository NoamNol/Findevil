#!/bin/bash
set -e

# flaskdbUser is the userName used from applicatoin code to interact with databases
# and flaskdbPwd is the password for this user.
# MONGO_INITDB_ROOT_USERNAME & MONGO_INITDB_ROOT_PASSWORD is the config for db admin.
# admin user is expected to be already created when this script executes.
# We use it here to authenticate as admin to create flaskdbUser and databases.

echo ">>>>>>> trying to create database and users"
if [ -n "${MONGO_INITDB_ROOT_USERNAME:-}" ] && 
   [ -n "${MONGO_INITDB_ROOT_PASSWORD:-}" ] && 
   [ -n "${flaskdbUser:-}" ] && 
   [ -n "${flaskdbPwd:-}" ]; then
mongosh -u $MONGO_INITDB_ROOT_USERNAME -p $MONGO_INITDB_ROOT_PASSWORD<<EOF
use flaskdb;
db.createUser({user: '$flaskdbUser', pwd: '$flaskdbPwd', roles: [{role: 'readWrite', db: 'flaskdb'}]})
EOF
else
    echo "MONGO_INITDB_ROOT_USERNAME, MONGO_INITDB_ROOT_PASSWORD, flaskdbUser and flaskdbPwd must be provided."
    echo "Some of these are missing, hence exiting database and user creatioin"
    exit 403
fi