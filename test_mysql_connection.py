import pymysql

def test_connection():
    try:
        # Connect to MySQL
        print("Connecting to MySQL...")
        conn = pymysql.connect(
            host='127.0.0.1',
            user='root',
            password='Varunloni@12',
            database='dental_lab_db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        print("Connected successfully!")
        
        # Test query
        with conn.cursor() as cursor:
            # Read records from material table
            cursor.execute("SELECT * FROM material")
            materials = cursor.fetchall()
            print(f"Found {len(materials)} materials:")
            for material in materials:
                print(f"- {material['name']} (${material['price']})")
                
            # Read records from service table
            cursor.execute("SELECT * FROM service")
            services = cursor.fetchall()
            print(f"\nFound {len(services)} services:")
            for service in services:
                print(f"- {service['title']} ({service['price_range']})")
        
        conn.close()
        print("\nConnection closed.")
        return True
    
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")
        return False

if __name__ == "__main__":
    test_connection() 