import pymysql

def create_database():
    try:
        # Connect to MySQL server
        print("Connecting to MySQL...")
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='Varunloni@12'
        )
        
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        print("Creating database...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS dental_lab_db")
        
        print("Database 'dental_lab_db' created successfully.")
        print("You can now run the Flask application with: python flask_dental_lab.py")
        
        conn.close()
        
        return True
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

if __name__ == "__main__":
    create_database() 