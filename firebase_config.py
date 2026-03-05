"""
Firebase Configuration Module

This module handles Firebase Admin SDK initialization for the ISP Billing System.
It loads credentials from a JSON file and initializes the Firestore client with
proper error handling.
"""

import firebase_admin
from firebase_admin import credentials, firestore
import os
import logging

logger = logging.getLogger(__name__)


def initialize_firebase():
    """
    Initialize Firebase Admin SDK and return Firestore client.
    
    This function:
    1. Loads Firebase credentials from the path specified in environment variables
    2. Initializes the Firebase Admin SDK
    3. Returns a Firestore client instance
    
    Returns:
        firestore.Client: Initialized Firestore database client
        
    Raises:
        FileNotFoundError: If the credentials file doesn't exist
        ValueError: If the credentials file is invalid or missing required fields
        Exception: If Firebase initialization fails
        
    Environment Variables:
        FIREBASE_CREDENTIALS_PATH: Path to the Firebase service account JSON file
                                  (defaults to 'firebase-credentials.json')
    
    Example:
        >>> db = initialize_firebase()
        >>> users = db.collection('users').get()
    """
    try:
        # Get credentials path from environment variable
        cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
        
        # Check if credentials file exists
        if not os.path.exists(cred_path):
            error_msg = (
                f"Firebase credentials file not found at: {cred_path}\n"
                f"Please ensure the file exists and FIREBASE_CREDENTIALS_PATH "
                f"environment variable is set correctly."
            )
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        # Check if credentials file is readable
        if not os.access(cred_path, os.R_OK):
            error_msg = (
                f"Firebase credentials file is not readable: {cred_path}\n"
                f"Please check file permissions (should be readable by the application)."
            )
            logger.error(error_msg)
            raise PermissionError(error_msg)
        
        logger.info(f"Loading Firebase credentials from: {cred_path}")
        
        # Load credentials
        try:
            cred = credentials.Certificate(cred_path)
        except Exception as e:
            error_msg = (
                f"Failed to load Firebase credentials from {cred_path}: {str(e)}\n"
                f"Please ensure the file is a valid Firebase service account JSON file."
            )
            logger.error(error_msg)
            raise ValueError(error_msg) from e
        
        # Initialize Firebase Admin SDK
        try:
            # Check if already initialized
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
                logger.info("Firebase Admin SDK initialized successfully")
            else:
                logger.info("Firebase Admin SDK already initialized")
        except Exception as e:
            error_msg = f"Failed to initialize Firebase Admin SDK: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg) from e
        
        # Get Firestore client
        try:
            db = firestore.client()
            logger.info("Firestore client created successfully")
            return db
        except Exception as e:
            error_msg = f"Failed to create Firestore client: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg) from e
            
    except (FileNotFoundError, PermissionError, ValueError) as e:
        # Re-raise known errors
        raise
    except Exception as e:
        # Catch any unexpected errors
        error_msg = f"Unexpected error during Firebase initialization: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg) from e


def get_firestore_client():
    """
    Get the Firestore client instance.
    
    This is a convenience function that returns the Firestore client.
    If Firebase hasn't been initialized yet, it will initialize it first.
    
    Returns:
        firestore.Client: Firestore database client
        
    Raises:
        Exception: If Firebase initialization fails
        
    Example:
        >>> db = get_firestore_client()
        >>> clients = db.collection('clients').get()
    """
    try:
        # Try to get existing client
        return firestore.client()
    except Exception:
        # If not initialized, initialize first
        logger.info("Firestore client not found, initializing Firebase...")
        return initialize_firebase()


def validate_firebase_connection(db):
    """
    Validate that the Firebase connection is working.
    
    This function performs a simple test operation to verify that:
    1. The Firestore client is properly initialized
    2. The credentials have the necessary permissions
    3. The network connection to Firebase is working
    
    Args:
        db (firestore.Client): Firestore database client to validate
        
    Returns:
        bool: True if connection is valid
        
    Raises:
        Exception: If connection validation fails
        
    Example:
        >>> db = initialize_firebase()
        >>> validate_firebase_connection(db)
        True
    """
    try:
        logger.info("Validating Firebase connection...")
        
        # Try to list collections (this requires read permission)
        # This is a lightweight operation that verifies connectivity
        collections = list(db.collections())
        
        logger.info(f"Firebase connection validated successfully. Found {len(collections)} collections.")
        return True
        
    except Exception as e:
        error_msg = (
            f"Firebase connection validation failed: {str(e)}\n"
            f"Please check:\n"
            f"1. Network connectivity to Firebase\n"
            f"2. Service account credentials are valid\n"
            f"3. Service account has Firestore permissions"
        )
        logger.error(error_msg)
        raise Exception(error_msg) from e
