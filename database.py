import mysql.connector

# Establish the connection to MySQL
def connect_db():
    conn = mysql.connector.connect(
        host="localhost",    # Your MySQL server (localhost if running XAMPP locally)
        user="root",         # Your MySQL user (root is default for XAMPP)
        password="",         # Your MySQL password (if any, leave blank if none)
        database="cybersecurity_db"  # The database you create for storing predictions
    )
    return conn

def create_database():
    conn = connect_db()
    cursor = conn.cursor()
    
   
    conn.commit()
    conn.close()

def save_predictions(actual, predicted):
    conn = connect_db()
    cursor = conn.cursor()
    
    # Insert prediction results into the MySQL table
    cursor.execute("INSERT INTO predictions (actual_label, predicted_label) VALUES (%s, %s)", (actual, predicted))
    
    conn.commit()
    conn.close()
def fetch_incidents(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM incidents")  # Modify the SQL query as needed
    incidents = cursor.fetchall()
    cursor.close()
    return incidents

def fetch_predictions():
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM predictions")
    data = cursor.fetchall()
    
    conn.close()
    return data

def fetch_prediction_summary():
    conn = connect_db()
    cursor = conn.cursor()

    # Query to count correct and incorrect predictions
    query = """
        SELECT
            actual_label,
            COUNT(CASE WHEN actual_label = predicted_label THEN 1 END) AS correct,
            COUNT(CASE WHEN actual_label != predicted_label THEN 1 END) AS wrong
        FROM predictions
        GROUP BY actual_label
    """
    cursor.execute(query)
    result = cursor.fetchall()

    conn.close()
    return result

def log_incident(incident_type, status):
    """
    Logs an incident to the incidents table in the database.
    
    :param incident_type: Type of the incident (e.g., "DDoS Attack").
    :param status: The status of the incident (e.g., "Detected", "Mitigated").
    """
    conn = connect_db()
    cursor = conn.cursor()

    query = """
        INSERT INTO incidents (incident_type, status, timestamp)
        VALUES (%s, %s, NOW())
    """
    cursor.execute(query, (incident_type, status))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Incident logged: {incident_type}, Status: {status}")

def fetch_incidents(conn):
    """ Fetch incidents from the database """
    cursor = conn.cursor()
    cursor.execute("SELECT type, status, timestamp FROM incidents")
    return cursor.fetchall()  # Return all incidents as a list of tuples


