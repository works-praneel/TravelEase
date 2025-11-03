#!/bin/bash

# 🟢 Fetch values from Terraform outputs
DB_HOST=$(terraform output -raw rds_endpoint)
DB_PORT=$(terraform output -raw rds_port)
DB_USER=$(terraform output -raw db_username)
DB_SECRET_NAME=$(terraform output -raw db_secret_name)
AWS_REGION="eu-north-1"   # <-- keep this same unless your region changes
DB_NAME="travelease"      # <-- your database name (as created in Terraform)

# 🟢 Update Booking_Service/.env file
ENV_FILE="../Booking_Service/.env"

if [ -f "$ENV_FILE" ]; then
    sed -i "s|^DB_HOST=.*|DB_HOST=$DB_HOST|" $ENV_FILE
    sed -i "s|^DB_PORT=.*|DB_PORT=$DB_PORT|" $ENV_FILE
    sed -i "s|^DB_USER=.*|DB_USER=$DB_USER|" $ENV_FILE
    sed -i "s|^DB_NAME=.*|DB_NAME=$DB_NAME|" $ENV_FILE
    sed -i "s|^DB_SECRET_NAME=.*|DB_SECRET_NAME=$DB_SECRET_NAME|" $ENV_FILE
    sed -i "s|^AWS_REGION=.*|AWS_REGION=$AWS_REGION|" $ENV_FILE
else
    echo "DB_HOST=$DB_HOST" > $ENV_FILE
    echo "DB_PORT=$DB_PORT" >> $ENV_FILE
    echo "DB_USER=$DB_USER" >> $ENV_FILE
    echo "DB_NAME=$DB_NAME" >> $ENV_FILE
    echo "DB_SECRET_NAME=$DB_SECRET_NAME" >> $ENV_FILE
    echo "AWS_REGION=$AWS_REGION" >> $ENV_FILE
fi

echo "✅ .env file updated successfully!"
cat $ENV_FILE
