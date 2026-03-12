import mysql.connector
from mysql.connector import Error, pooling
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Database:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.user = os.getenv('DB_USER', 'root')
        password = os.getenv('DB_PASSWORD', '')
        self.password = password if password else ''
        self.database = os.getenv('DB_NAME', 'classroom_reservation_db')
        self.port = os.getenv('DB_PORT', '3306')
        self.pool = None
        self._init_pool()

    def _init_pool(self):
        """Create a connection pool"""
        try:
            ssl_args = {}
            if self.host != 'localhost' and self.host != '127.0.0.1':
                ssl_args = {
                    "ssl_ca": "ca.pem",
                    "ssl_disabled": False,
                }

            self.pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="eduroom_pool",
                pool_size=5,
                pool_reset_session=True,
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                connection_timeout=10,
                **ssl_args
            )
            print("✅ Database pool created")
        except Exception as e:
            print(f"❌ Pool creation failed: {e}")
            self.pool = None

    def connect(self):
        """No-op for backward compatibility. Models call this but don't need it."""
        return True

    def disconnect(self):
        """No-op for backward compatibility. Connections are returned to pool automatically."""
        pass

    def _get_connection(self):
        """Internal: get a real connection from the pool for query methods."""
        try:
            if self.pool:
                return self.pool.get_connection()
        except Exception as e:
            print(f"❌ DB connect error: {e}")
        return None

    def execute_query(self, query, params=None):
        """Execute INSERT, UPDATE, DELETE queries"""
        conn = self._get_connection()
        if not conn:
            return None
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"Error executing query: {e}")
            conn.rollback()
            return None
        finally:
            cursor.close()
            conn.close()

    def fetch_one(self, query, params=None):
        """Fetch single record"""
        conn = self._get_connection()
        if not conn:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchone()
        except Error as e:
            print(f"Error fetching data: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def fetch_all(self, query, params=None):
        """Fetch multiple records"""
        conn = self._get_connection()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching data: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

# Singleton instance
db = Database()