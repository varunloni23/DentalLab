import pymysql
import urllib.parse

# Database connection parameters
DB_HOST = '127.0.0.1'
DB_USER = 'root'
DB_PASSWORD = 'Varunloni@12'  # The actual password
DB_NAME = 'dental_lab_db'

def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def execute_query(query, params=None, fetch=True):
    """Execute a database query and optionally return results"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            if fetch:
                result = cursor.fetchall()
            else:
                conn.commit()
                result = cursor.rowcount
        return result
    except Exception as e:
        print(f"Error executing query: {e}")
        return None
    finally:
        conn.close()

def get_all_materials():
    """Get all materials from the database"""
    return execute_query("SELECT * FROM material")

def get_all_services():
    """Get all services from the database"""
    return execute_query("SELECT * FROM service")

def get_all_appointments():
    """Get all appointments from the database"""
    return execute_query("SELECT * FROM appointment")

def get_all_orders():
    """Get all orders from the database"""
    return execute_query("SELECT * FROM `order`")

def add_appointment(name, email, phone, service, date, time, notes=None):
    """Add a new appointment to the database"""
    query = """
    INSERT INTO appointment (name, email, phone, service, date, time, notes)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    params = (name, email, phone, service, date, time, notes)
    return execute_query(query, params, fetch=False)

def add_order(customer_name, customer_email, customer_phone, material_id, quantity, total_price, delivery_address=None):
    """Add a new order to the database"""
    query = """
    INSERT INTO `order` (customer_name, customer_email, customer_phone, material_id, quantity, total_price, delivery_address)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    params = (customer_name, customer_email, customer_phone, material_id, quantity, total_price, delivery_address)
    return execute_query(query, params, fetch=False) 