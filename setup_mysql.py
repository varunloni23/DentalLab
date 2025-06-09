import pymysql
import getpass

def setup_database():
    # Get MySQL connection details from user
    username = input("Enter MySQL username (default: root): ") or "root"
    password = getpass.getpass("Enter MySQL password: ")
    host = input("Enter MySQL host (default: localhost): ") or "localhost"
    
    # Connect to MySQL
    print("Connecting to MySQL...")
    conn = pymysql.connect(
        host=host,
        user=username,
        password=password
    )
    
    cursor = conn.cursor()
    
    # Create database
    print("Creating database...")
    cursor.execute("CREATE DATABASE IF NOT EXISTS dental_lab_db")
    
    # Switch to the new database
    cursor.execute("USE dental_lab_db")
    
    # Update the app configuration
    config_file = "flask_dental_lab.py"
    with open(config_file, "r") as f:
        content = f.read()
    
    # Replace the connection string
    new_conn_string = f"mysql+pymysql://{username}:{password}@{host}/dental_lab_db"
    new_content = content.replace(
        "mysql+pymysql://root:password@localhost/dental_lab_db", 
        new_conn_string
    )
    
    with open(config_file, "w") as f:
        f.write(new_content)
    
    print(f"Database 'dental_lab_db' created successfully.")
    print(f"Updated connection string in {config_file}")
    print("Now you can run the Flask application with: python flask_dental_lab.py")
    
    conn.close()

if __name__ == "__main__":
    setup_database() 