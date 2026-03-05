"""Tests for Firebase integration in app.py"""
import pytest
from unittest.mock import patch, MagicMock
from app import create_app


class TestFirebaseIntegration:
    """Test Firebase initialization in Flask application"""
    
    @patch('firebase_config.initialize_firebase')
    @patch('firebase_config.validate_firebase_connection')
    def test_firebase_initialized_on_app_creation(self, mock_validate, mock_initialize):
        """Test that Firebase is initialized when app is created"""
        # Setup mocks
        mock_firestore_db = MagicMock()
        mock_initialize.return_value = mock_firestore_db
        mock_validate.return_value = True
        
        # Create app
        app = create_app()
        
        # Verify Firebase was initialized
        mock_initialize.assert_called_once()
        mock_validate.assert_called_once_with(mock_firestore_db)
        
        # Verify Firestore client is stored in app config
        assert 'FIRESTORE_DB' in app.config
        assert app.config['FIRESTORE_DB'] == mock_firestore_db
    
    @patch('firebase_config.initialize_firebase')
    def test_app_creation_fails_when_firebase_initialization_fails(self, mock_initialize):
        """Test that app creation fails gracefully when Firebase initialization fails"""
        # Setup mock to raise exception
        mock_initialize.side_effect = FileNotFoundError("Firebase credentials not found")
        
        # Verify app creation raises exception
        with pytest.raises(FileNotFoundError):
            create_app()
    
    @patch('firebase_config.initialize_firebase')
    @patch('firebase_config.validate_firebase_connection')
    def test_app_creation_fails_when_firebase_validation_fails(self, mock_validate, mock_initialize):
        """Test that app creation fails when Firebase connection validation fails"""
        # Setup mocks
        mock_firestore_db = MagicMock()
        mock_initialize.return_value = mock_firestore_db
        mock_validate.side_effect = Exception("Firebase connection validation failed")
        
        # Verify app creation raises exception
        with pytest.raises(Exception):
            create_app()
    
    @patch('firebase_config.initialize_firebase')
    @patch('firebase_config.validate_firebase_connection')
    def test_firestore_client_accessible_from_app_config(self, mock_validate, mock_initialize):
        """Test that Firestore client can be accessed from app config"""
        # Setup mocks
        mock_firestore_db = MagicMock()
        mock_initialize.return_value = mock_firestore_db
        mock_validate.return_value = True
        
        # Create app
        app = create_app()
        
        # Verify Firestore client is accessible
        with app.app_context():
            firestore_db = app.config.get('FIRESTORE_DB')
            assert firestore_db is not None
            assert firestore_db == mock_firestore_db
