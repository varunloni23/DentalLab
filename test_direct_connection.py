import pymysql

def test_direct_connection():
    try:
        # Try a direct connection
        print("Attempting direct connection to MySQL...")
        conn = pymysql.connect(
            host='127.0.0.1',
            user='root',
            password='Varunloni@12',
            database='dental_lab_db'
        )
        
        print("Direct connection successful!")
        
        # Test a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM material")
        materials = cursor.fetchall()
        print(f"Found {len(materials)} materials in the database.")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Direct connection error: {e}")
        return False

if __name__ == "__main__":
    test_direct_connection() 