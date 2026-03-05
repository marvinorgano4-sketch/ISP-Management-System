"""
Data Migration Tool: SQLite to Firebase Firestore

This script migrates all data from the SQLite database to Firebase Firestore.
It handles:
- Connection initialization for both SQLite and Firebase
- ID mapping from SQLite integers to Firestore document IDs
- Data transformation and validation
- Migration logging and error handling
- Rollback capability on failure

Usage:
    python migrate_to_firebase.py

Requirements:
    - SQLite database at instance/isp_billing.db
    - Firebase credentials configured in environment
    - Network connectivity to Firebase
"""

import sqlite3
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from firebase_admin import firestore
from firebase_config import initialize_firebase


class MigrationLogger:
    """
    Handles logging for the migration process.
    
    Provides structured logging with different levels (info, warning, error)
    and maintains a migration log file for audit purposes.
    """
    
    def __init__(self, log_file: str = 'logs/migration.log'):
        """
        Initialize the migration logger.
        
        Args:
            log_file: Path to the log file (default: logs/migration.log)
        """
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Configure logger
        self.logger = logging.getLogger('migration')
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers = []
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # Migration statistics
        self.stats = {
            'start_time': None,
            'end_time': None,
            'total_records': 0,
            'migrated_records': 0,
            'failed_records': 0,
            'errors': []
        }
    
    def info(self, message: str):
        """Log an info message."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(message)
    
    def error(self, message: str, exception: Optional[Exception] = None):
        """
        Log an error message.
        
        Args:
            message: Error message
            exception: Optional exception object for stack trace
        """
        if exception:
            self.logger.error(f"{message}: {str(exception)}", exc_info=True)
            self.stats['errors'].append({
                'message': message,
                'exception': str(exception),
                'timestamp': datetime.now().isoformat()
            })
        else:
            self.logger.error(message)
            self.stats['errors'].append({
                'message': message,
                'timestamp': datetime.now().isoformat()
            })
    
    def start_migration(self):
        """Mark the start of migration."""
        self.stats['start_time'] = datetime.now()
        self.info("=" * 80)
        self.info("MIGRATION STARTED")
        self.info(f"Start Time: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        self.info("=" * 80)
    
    def end_migration(self, success: bool = True):
        """
        Mark the end of migration.
        
        Args:
            success: Whether the migration completed successfully
        """
        self.stats['end_time'] = datetime.now()
        duration = self.stats['end_time'] - self.stats['start_time']
        
        self.info("=" * 80)
        if success:
            self.info("MIGRATION COMPLETED SUCCESSFULLY")
        else:
            self.error("MIGRATION FAILED")
        self.info(f"End Time: {self.stats['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        self.info(f"Duration: {duration}")
        self.info(f"Total Records: {self.stats['total_records']}")
        self.info(f"Migrated Records: {self.stats['migrated_records']}")
        self.info(f"Failed Records: {self.stats['failed_records']}")
        if self.stats['errors']:
            self.info(f"Errors: {len(self.stats['errors'])}")
        self.info("=" * 80)
    
    def log_table_start(self, table_name: str, record_count: int):
        """
        Log the start of a table migration.
        
        Args:
            table_name: Name of the table being migrated
            record_count: Number of records to migrate
        """
        self.info(f"\n--- Migrating {table_name} ({record_count} records) ---")
        self.stats['total_records'] += record_count
    
    def log_record_migrated(self, table_name: str, sqlite_id: int, firestore_id: str):
        """
        Log a successful record migration.
        
        Args:
            table_name: Name of the table
            sqlite_id: Original SQLite ID
            firestore_id: New Firestore document ID
        """
        self.logger.debug(f"Migrated {table_name} record: SQLite ID {sqlite_id} -> Firestore ID {firestore_id}")
        self.stats['migrated_records'] += 1
    
    def log_record_failed(self, table_name: str, sqlite_id: int, error: str):
        """
        Log a failed record migration.
        
        Args:
            table_name: Name of the table
            sqlite_id: Original SQLite ID
            error: Error message
        """
        self.error(f"Failed to migrate {table_name} record (SQLite ID {sqlite_id}): {error}")
        self.stats['failed_records'] += 1


class FirebaseMigration:
    """
    Main migration class for migrating data from SQLite to Firebase Firestore.
    
    This class handles:
    - Database connections (SQLite and Firebase)
    - ID mapping between SQLite and Firestore
    - Data transformation and migration
    - Validation and rollback
    
    Attributes:
        sqlite_path: Path to the SQLite database file
        sqlite_conn: SQLite database connection
        firestore_db: Firestore database client
        logger: Migration logger instance
        id_mapping: Dictionary mapping SQLite IDs to Firestore IDs
    """
    
    def __init__(self, sqlite_path: str = 'instance/isp_billing.db'):
        """
        Initialize the migration tool.
        
        Args:
            sqlite_path: Path to the SQLite database file
            
        Raises:
            FileNotFoundError: If SQLite database doesn't exist
            Exception: If Firebase initialization fails
        """
        self.sqlite_path = sqlite_path
        self.sqlite_conn = None
        self.firestore_db = None
        self.logger = MigrationLogger()
        
        # ID mapping: {table_name: {sqlite_id: firestore_id}}
        self.id_mapping: Dict[str, Dict[int, str]] = {
            'users': {},
            'clients': {},
            'billings': {},
            'payments': {},
            'receipts': {}
        }
        
        # Initialize connections
        self._initialize_sqlite()
        self._initialize_firebase()
    
    def _initialize_sqlite(self):
        """
        Initialize SQLite database connection.
        
        Raises:
            FileNotFoundError: If the database file doesn't exist
            sqlite3.Error: If connection fails
        """
        self.logger.info(f"Initializing SQLite connection: {self.sqlite_path}")
        
        # Check if database file exists
        if not os.path.exists(self.sqlite_path):
            error_msg = f"SQLite database not found at: {self.sqlite_path}"
            self.logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        try:
            # Connect to SQLite database
            self.sqlite_conn = sqlite3.connect(self.sqlite_path)
            # Enable row factory for dict-like access
            self.sqlite_conn.row_factory = sqlite3.Row
            
            # Test connection
            cursor = self.sqlite_conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            self.logger.info(f"SQLite connection established. Found {len(tables)} tables: {', '.join(tables)}")
            
        except sqlite3.Error as e:
            error_msg = f"Failed to connect to SQLite database"
            self.logger.error(error_msg, e)
            raise
    
    def _initialize_firebase(self):
        """
        Initialize Firebase Firestore connection.
        
        Raises:
            Exception: If Firebase initialization fails
        """
        self.logger.info("Initializing Firebase Firestore connection")
        
        try:
            # Initialize Firebase and get Firestore client
            self.firestore_db = initialize_firebase()
            
            # Test connection by listing collections
            collections = list(self.firestore_db.collections())
            self.logger.info(f"Firebase connection established. Found {len(collections)} existing collections")
            
        except Exception as e:
            error_msg = "Failed to initialize Firebase"
            self.logger.error(error_msg, e)
            raise
    
    def get_sqlite_record_count(self, table_name: str) -> int:
        """
        Get the number of records in a SQLite table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Number of records in the table
        """
        cursor = self.sqlite_conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        return count
    
    def get_firestore_record_count(self, collection_name: str) -> int:
        """
        Get the number of documents in a Firestore collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Number of documents in the collection
        """
        docs = self.firestore_db.collection(collection_name).stream()
        count = sum(1 for _ in docs)
        return count
    
    def close_connections(self):
        """Close database connections."""
        if self.sqlite_conn:
            self.sqlite_conn.close()
            self.logger.info("SQLite connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_connections()


def main():
    """
    Main entry point for the migration script.
    
    This function:
    1. Creates a FirebaseMigration instance
    2. Validates connections
    3. Displays migration summary
    4. Waits for user confirmation
    """
    print("\n" + "=" * 80)
    print("SQLite to Firebase Firestore Migration Tool")
    print("=" * 80 + "\n")
    
    try:
        # Initialize migration tool
        with FirebaseMigration() as migration:
            print("✓ SQLite connection established")
            print("✓ Firebase connection established\n")
            
            # Display record counts
            print("Current database status:")
            print("-" * 40)
            
            tables = ['users', 'clients', 'billings', 'payments', 'receipts']
            for table in tables:
                sqlite_count = migration.get_sqlite_record_count(table)
                firestore_count = migration.get_firestore_record_count(table)
                print(f"{table:15} - SQLite: {sqlite_count:4} | Firestore: {firestore_count:4}")
            
            print("\n" + "=" * 80)
            print("Migration tool initialized successfully!")
            print("=" * 80 + "\n")
            
            print("Next steps:")
            print("1. Backup your SQLite database")
            print("2. Ensure Firebase credentials are properly configured")
            print("3. Run the migration methods (to be implemented in next tasks)")
            print("\nMigration structure is ready for implementation.")
            
    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease ensure the SQLite database exists at the specified path.")
        return 1
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease check the error logs for more details.")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
