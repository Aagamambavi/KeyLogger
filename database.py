"""
Database module for KeyLogger
Handles MongoDB connection, error handling, and data storage
"""

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
import logging
from config import MONGODB_HOST, MONGODB_PORT, MONGODB_DB, MONGODB_COLLECTION
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages MongoDB connection and operations"""

    def __init__(self):
        """Initialize database manager and test connection"""
        self.client = None
        self.db = None
        self.collection = None
        self.connected = False
        self._connect()

    def _connect(self):
        """
        Attempt to connect to MongoDB
        Includes timeout handling and retry logic
        """
        try:
            print(f"[*] Attempting to connect to MongoDB at {MONGODB_HOST}:{MONGODB_PORT}...")

            # Create client with timeout of 5 seconds
            self.client = MongoClient(
                host=MONGODB_HOST,
                port=MONGODB_PORT,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )

            # Test connection by pinging server
            self.client.admin.command('ping')

            # Get database and collection
            self.db = self.client[MONGODB_DB]
            self.collection = self.db[MONGODB_COLLECTION]

            # Create index on timestamp for faster queries
            self.collection.create_index('timestamp')

            self.connected = True
            print("[+] Successfully connected to MongoDB!")

        except (ServerSelectionTimeoutError, ConnectionFailure) as e:
            self.connected = False
            print(f"[-] Failed to connect to MongoDB: {e}")
            print("[!] WARNING: MongoDB is not running or not accessible")
            print("[!] Data will be stored locally and synced when connection is available")
            logger.error(f"MongoDB connection failed: {e}")
        except Exception as e:
            self.connected = False
            print(f"[-] Unexpected error connecting to MongoDB: {e}")
            logger.error(f"Unexpected error: {e}")

    def is_connected(self):
        """Check if connected to MongoDB"""
        return self.connected

    def insert_session(self, session_data):
        """
        Insert session data into MongoDB
        Falls back to local storage if connection fails

        Args:
            session_data (dict): Session data to store

        Returns:
            bool: True if stored successfully
        """
        try:
            if self.connected:
                result = self.collection.insert_one(session_data)
                print(f"[+] Session stored in MongoDB with ID: {result.inserted_id}")
                return True
            else:
                print("[-] MongoDB not connected. Storing locally...")
                self._store_locally(session_data)
                return False
        except Exception as e:
            print(f"[-] Error inserting session: {e}")
            logger.error(f"Error inserting session: {e}")
            self._store_locally(session_data)
            return False

    def _store_locally(self, session_data):
        """
        Store session data locally if MongoDB fails
        Creates a backup directory for offline storage
        """
        import os
        import json

        backup_dir = 'local_backups'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{backup_dir}/session_{timestamp}.json"

        try:
            # Convert non-serializable objects to strings
            serializable_data = self._make_serializable(session_data)

            with open(filename, 'w') as f:
                json.dump(serializable_data, f, indent=2)

            print(f"[+] Session backed up locally to {filename}")
            logger.info(f"Session backed up locally to {filename}")
        except Exception as e:
            print(f"[-] Error storing locally: {e}")
            logger.error(f"Error storing locally: {e}")

    def _make_serializable(self, obj):
        """Convert non-serializable objects to serializable format"""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return str(obj)

    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("[*] MongoDB connection closed")
