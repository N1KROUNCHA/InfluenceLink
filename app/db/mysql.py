import mysql.connector
from dotenv import load_dotenv
import os
import threading
import time

load_dotenv()

class Database:
    def __init__(self):
        self.lock = threading.RLock()
        self.connect()

    def connect(self):
        self.conn = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            port=int(os.getenv("MYSQL_PORT")),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DB"),
            pool_name="api_pool",
            pool_size=5
        )
        self.cursor = self.conn.cursor(dictionary=True)

    def ensure_connection(self):
        try:
            self.conn.ping(reconnect=True, attempts=3, delay=2)
        except mysql.connector.Error:
            self.connect()

class SafeCursor:
    def __init__(self, db):
        self.db = db

    def execute(self, query, params=None):
        with self.db.lock:
            self.db.ensure_connection()
            try:
                # Refresh cursor just in case
                self.db.cursor = self.db.conn.cursor(dictionary=True)
                return self.db.cursor.execute(query, params)
            except mysql.connector.Error as err:
                 # Try once more
                self.db.connect()
                return self.db.cursor.execute(query, params)

    def fetchall(self):
        return self.db.cursor.fetchall()

    def fetchone(self):
        return self.db.cursor.fetchone()

    @property
    def lastrowid(self):
        return self.db.cursor.lastrowid
    
    @property
    def rowcount(self):
        return self.db.cursor.rowcount

class SafeConnection:
    def __init__(self, db):
        self.db = db
    
    def commit(self):
        with self.db.lock:
             self.db.ensure_connection()
             self.db.conn.commit()

    def cursor(self, *args, **kwargs):
        with self.db.lock:
            self.db.ensure_connection()
            return self.db.conn.cursor(*args, **kwargs)
            
    def close(self):
        # We don't actually close the persistent connection here
        pass

db_instance = Database()
cursor = SafeCursor(db_instance)
conn = SafeConnection(db_instance)
lock = db_instance.lock
