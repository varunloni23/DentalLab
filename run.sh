#!/bin/bash

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 to run this application."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Please install pip3 to run this application."
    exit 1
fi

# Ensure required packages are installed
echo "Installing required packages..."
pip3 install flask flask-sqlalchemy flask-wtf pymysql

# Check if the database exists
echo "Checking database configuration..."
python3 -c "
import pymysql
import urllib.parse
import sys

password = urllib.parse.quote_plus('Varunloni@12')

try:
    conn = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='Varunloni@12',
        database='dental_lab_db'
    )
    print('Database connection successful.')
    conn.close()
except Exception as e:
    print(f'Database connection failed: {str(e)}')
    print('Please run setup_mysql.py to set up the database.')
    sys.exit(1)
"

# Exit if database check failed
if [ $? -ne 0 ]; then
    echo "Would you like to run the database setup script? (y/n)"
    read response
    if [ "$response" = "y" ]; then
        python3 setup_mysql.py
    else
        echo "Exiting. Please set up the database before running the application."
        exit 1
    fi
fi

# Create images directory if it doesn't exist
if [ ! -d "static/images" ]; then
    echo "Creating static/images directory..."
    mkdir -p static/images
fi

# Run the application
echo "Starting Dental Lab Management System..."
python3 flask_dental_lab.py 