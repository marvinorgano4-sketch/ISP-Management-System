"""Tests for configuration management system"""
import os
import pytest
from pathlib import Path
from config import Config


class TestConfigValidation:
    """Test configuration validation methods"""
    
    def test_validate_with_missing_secret_key(self, monkeypatch):
        """Test that validation fails when SECRET_KEY is missing or default"""
        # Set SECRET_KEY to default value
        monkeypatch.setattr(Config, 'SECRET_KEY', 'dev-secret-key-change-in-production')
        
        with pytest.raises(ValueError) as exc_info:
            Config.validate()
        
        assert 'FLASK_SECRET_KEY is not set or using default value' in str(exc_info.value)
        assert 'Fix: Set FLASK_SECRET_KEY in .env file' in str(exc_info.value)
    
    def test_validate_with_missing_zerotier_config(self, monkeypatch):
        """Test that validation warns about missing ZeroTier configuration"""
        # Set valid SECRET_KEY but missing ZeroTier config
        monkeypatch.setattr(Config, 'SECRET_KEY', 'valid-secret-key-for-testing-purposes-123456')
        monkeypatch.setattr(Config, 'ZEROTIER_NETWORK_ID', None)
        monkeypatch.setattr(Config, 'FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
        monkeypatch.setattr(Config, 'FIREBASE_PROJECT_ID', None)
        
        with pytest.raises(ValueError) as exc_info:
            Config.validate()
        
        assert 'ZEROTIER_NETWORK_ID is not set' in str(exc_info.value)
    
    def test_validate_with_missing_firebase_credentials_file(self, monkeypatch, tmp_path):
        """Test that validation fails when Firebase credentials file doesn't exist"""
        # Set valid SECRET_KEY and ZeroTier config
        monkeypatch.setattr(Config, 'SECRET_KEY', 'valid-secret-key-for-testing-purposes-123456')
        monkeypatch.setattr(Config, 'ZEROTIER_NETWORK_ID', 'a0cbf4b62a1234567')
        
        # Set Firebase credentials path to non-existent file
        non_existent_path = str(tmp_path / 'non-existent-credentials.json')
        monkeypatch.setattr(Config, 'FIREBASE_CREDENTIALS_PATH', non_existent_path)
        monkeypatch.setattr(Config, 'FIREBASE_PROJECT_ID', 'test-project-id')
        
        with pytest.raises(ValueError) as exc_info:
            Config.validate()
        
        assert 'Firebase credentials file not found' in str(exc_info.value)
        assert non_existent_path in str(exc_info.value)
    
    def test_validate_with_missing_firebase_project_id(self, monkeypatch, tmp_path):
        """Test that validation fails when Firebase project ID is missing"""
        # Set valid SECRET_KEY and ZeroTier config
        monkeypatch.setattr(Config, 'SECRET_KEY', 'valid-secret-key-for-testing-purposes-123456')
        monkeypatch.setattr(Config, 'ZEROTIER_NETWORK_ID', 'a0cbf4b62a1234567')
        
        # Create a temporary credentials file
        creds_file = tmp_path / 'firebase-credentials.json'
        creds_file.write_text('{}')
        monkeypatch.setattr(Config, 'FIREBASE_CREDENTIALS_PATH', str(creds_file))
        monkeypatch.setattr(Config, 'FIREBASE_PROJECT_ID', None)
        
        with pytest.raises(ValueError) as exc_info:
            Config.validate()
        
        assert 'FIREBASE_PROJECT_ID is not set' in str(exc_info.value)
    
    def test_validate_with_all_valid_config(self, monkeypatch, tmp_path):
        """Test that validation passes with all valid configuration"""
        # Set all valid configuration
        monkeypatch.setattr(Config, 'SECRET_KEY', 'valid-secret-key-for-testing-purposes-123456')
        monkeypatch.setattr(Config, 'ZEROTIER_NETWORK_ID', 'a0cbf4b62a1234567')
        
        # Create a temporary credentials file
        creds_file = tmp_path / 'firebase-credentials.json'
        creds_file.write_text('{}')
        monkeypatch.setattr(Config, 'FIREBASE_CREDENTIALS_PATH', str(creds_file))
        monkeypatch.setattr(Config, 'FIREBASE_PROJECT_ID', 'test-project-id')
        
        # Should not raise any exception
        assert Config.validate() is True
    
    def test_validate_required_only_with_valid_secret_key(self, monkeypatch):
        """Test that validate_required_only passes with valid SECRET_KEY"""
        monkeypatch.setattr(Config, 'SECRET_KEY', 'valid-secret-key-for-testing-purposes-123456')
        
        # Should not raise any exception
        assert Config.validate_required_only() is True
    
    def test_validate_required_only_with_missing_secret_key(self, monkeypatch):
        """Test that validate_required_only fails with missing SECRET_KEY"""
        monkeypatch.setattr(Config, 'SECRET_KEY', 'dev-secret-key-change-in-production')
        
        with pytest.raises(ValueError) as exc_info:
            Config.validate_required_only()
        
        assert 'FLASK_SECRET_KEY is not set or using default value' in str(exc_info.value)


class TestConfigAttributes:
    """Test configuration attributes"""
    
    def test_zerotier_config_attributes(self):
        """Test that ZeroTier configuration attributes exist"""
        assert hasattr(Config, 'ZEROTIER_NETWORK_ID')
        assert hasattr(Config, 'ZEROTIER_INTERFACE')
        assert Config.ZEROTIER_INTERFACE == 'zt0'  # Default value
    
    def test_firebase_config_attributes(self):
        """Test that Firebase configuration attributes exist"""
        assert hasattr(Config, 'FIREBASE_CREDENTIALS_PATH')
        assert hasattr(Config, 'FIREBASE_PROJECT_ID')
        assert Config.FIREBASE_CREDENTIALS_PATH == 'firebase-credentials.json'  # Default value
    
    def test_server_config_attributes(self):
        """Test that server configuration attributes exist"""
        assert hasattr(Config, 'BIND_HOST')
        assert hasattr(Config, 'BIND_PORT')
        assert Config.BIND_HOST == '0.0.0.0'  # Default value
        assert Config.BIND_PORT == 5000  # Default value
