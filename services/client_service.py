"""Client service for managing ISP customers"""
from datetime import datetime
from sqlalchemy import or_
from models.client import Client
from extensions import db
from services.mikrotik_service import MikrotikService
from config import Config
import logging

logger = logging.getLogger(__name__)


class ClientService:
    """Service class for handling client management operations"""
    
    @staticmethod
    def create_client(data):
        """
        Create a new client with validation and Mikrotik PPPoE user creation.
        
        Args:
            data (dict): Client data containing full_name, address, contact_number,
                        email, pppoe_username, pppoe_password, plan_name, plan_amount, status
        
        Returns:
            Client: The created client object
            
        Raises:
            ValueError: If validation fails (e.g., duplicate PPPoE username)
        """
        # Validate PPPoE username uniqueness
        if not ClientService.validate_pppoe_username(data.get('pppoe_username')):
            raise ValueError('PPPoE username is already in use by another client.')
        
        # Validate required fields
        required_fields = ['full_name', 'pppoe_username', 'pppoe_password', 'plan_name', 'plan_amount']
        for field in required_fields:
            if not data.get(field):
                raise ValueError(f'The field {field} is required.')
        
        # Create client in database first
        client = Client(
            full_name=data['full_name'],
            address=data.get('address', ''),
            contact_number=data.get('contact_number', ''),
            email=data.get('email', ''),
            pppoe_username=data['pppoe_username'],
            mikrotik_profile=data.get('mikrotik_profile', 'default'),
            plan_name=data['plan_name'],
            plan_amount=float(data['plan_amount']),
            status=data.get('status', 'active')
        )
        
        # Set password hash for client portal login
        client.set_password(data['pppoe_password'])
        
        db.session.add(client)
        db.session.commit()
        
        # Create PPPoE user in Mikrotik
        try:
            mikrotik = MikrotikService(
                host=Config.MIKROTIK_HOST,
                username=Config.MIKROTIK_USER,
                password=Config.MIKROTIK_PASSWORD
            )
            # Use the selected Mikrotik profile
            profile = data.get('mikrotik_profile', 'default')
            mikrotik.create_pppoe_user(
                username=data['pppoe_username'],
                password=data['pppoe_password'],
                profile=profile
            )
            logger.info(f"Created PPPoE user '{data['pppoe_username']}' with profile '{profile}' in Mikrotik for client {client.id}")
        except Exception as e:
            logger.error(f"Failed to create PPPoE user in Mikrotik: {str(e)}")
            # Don't rollback database - client is created, just log the error
            # User can manually create PPPoE user in Mikrotik if needed
        
        return client
    
    @staticmethod
    def get_client(client_id):
        """
        Get a client by ID.
        
        Args:
            client_id (int): The client ID
            
        Returns:
            Client | None: The client object if found, None otherwise
        """
        return Client.query.get(client_id)
    
    @staticmethod
    def get_all_clients(filters=None):
        """
        Get all clients with optional filters.
        
        Args:
            filters (dict): Optional filters (status, search_query)
            
        Returns:
            list[Client]: List of client objects
        """
        query = Client.query
        
        if filters:
            # Filter by status
            if filters.get('status'):
                query = query.filter_by(status=filters['status'])
            
            # Search by name or PPPoE username
            if filters.get('search_query'):
                search = f"%{filters['search_query']}%"
                query = query.filter(
                    or_(
                        Client.full_name.ilike(search),
                        Client.pppoe_username.ilike(search)
                    )
                )
        
        return query.order_by(Client.full_name).all()
    
    @staticmethod
    def update_client(client_id, data):
        """
        Update a client's information.
        
        Args:
            client_id (int): The client ID
            data (dict): Updated client data
            
        Returns:
            Client: The updated client object
            
        Raises:
            ValueError: If client not found or validation fails
        """
        client = Client.query.get(client_id)
        if not client:
            raise ValueError('Client not found.')
        
        # Validate PPPoE username uniqueness if changed
        if 'pppoe_username' in data and data['pppoe_username'] != client.pppoe_username:
            if not ClientService.validate_pppoe_username(data['pppoe_username']):
                raise ValueError('PPPoE username is already in use by another client.')
        
        # Check if mikrotik_profile changed
        profile_changed = False
        old_profile = client.mikrotik_profile
        new_profile = data.get('mikrotik_profile')
        
        if new_profile and new_profile != old_profile:
            profile_changed = True
        
        # Update fields
        if 'full_name' in data:
            client.full_name = data['full_name']
        if 'address' in data:
            client.address = data['address']
        if 'contact_number' in data:
            client.contact_number = data['contact_number']
        if 'email' in data:
            client.email = data['email']
        if 'pppoe_username' in data:
            client.pppoe_username = data['pppoe_username']
        if 'mikrotik_profile' in data:
            client.mikrotik_profile = data['mikrotik_profile']
        if 'plan_name' in data:
            client.plan_name = data['plan_name']
        if 'plan_amount' in data:
            client.plan_amount = float(data['plan_amount'])
        if 'status' in data:
            client.status = data['status']
        
        client.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Update Mikrotik profile if it changed
        if profile_changed:
            try:
                mikrotik = MikrotikService(
                    host=Config.MIKROTIK_HOST,
                    username=Config.MIKROTIK_USER,
                    password=Config.MIKROTIK_PASSWORD
                )
                mikrotik.update_pppoe_user_profile(client.pppoe_username, new_profile)
                logger.info(f"Updated Mikrotik profile for '{client.pppoe_username}' from '{old_profile}' to '{new_profile}'")
            except Exception as e:
                logger.error(f"Failed to update Mikrotik profile: {str(e)}")
                # Don't rollback - client is updated in database, just log the error
        
        return client
    
    @staticmethod
    def delete_client(client_id):
        """
        Delete a client and their PPPoE user from Mikrotik.
        
        Args:
            client_id (int): The client ID to delete
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            ValueError: If client not found
        """
        client = Client.query.get(client_id)
        if not client:
            raise ValueError('Client not found.')
        
        pppoe_username = client.pppoe_username
        
        # Delete from database first
        db.session.delete(client)
        db.session.commit()
        
        # Delete PPPoE user from Mikrotik
        try:
            mikrotik = MikrotikService(
                host=Config.MIKROTIK_HOST,
                username=Config.MIKROTIK_USER,
                password=Config.MIKROTIK_PASSWORD
            )
            mikrotik.delete_pppoe_user(pppoe_username)
            logger.info(f"Deleted PPPoE user '{pppoe_username}' from Mikrotik for client {client_id}")
        except Exception as e:
            logger.error(f"Failed to delete PPPoE user from Mikrotik: {str(e)}")
            # Client is already deleted from database, just log the error
        
        return True
    
    @staticmethod
    def search_clients(query):
        """
        Search clients by name or PPPoE username.
        
        Args:
            query (str): Search query string
            
        Returns:
            list[Client]: List of matching client objects
        """
        if not query:
            return []
        
        search = f"%{query}%"
        return Client.query.filter(
            or_(
                Client.full_name.ilike(search),
                Client.pppoe_username.ilike(search),
                Client.contact_number.ilike(search)
            )
        ).order_by(Client.full_name).all()
    
    @staticmethod
    def validate_pppoe_username(username, exclude_client_id=None):
        """
        Validate that a PPPoE username is unique.
        
        Args:
            username (str): The PPPoE username to validate
            exclude_client_id (int): Optional client ID to exclude from check (for updates)
            
        Returns:
            bool: True if username is available, False if already in use
        """
        if not username:
            return False
        
        query = Client.query.filter_by(pppoe_username=username)
        
        if exclude_client_id:
            query = query.filter(Client.id != exclude_client_id)
        
        return query.first() is None
    
    @staticmethod
    def sync_from_mikrotik():
        """
        Sync all PPPoE users from Mikrotik to database.
        Creates new client records for users that don't exist in database.
        
        Returns:
            dict: Summary of sync operation with counts
        """
        try:
            # Get all PPPoE secrets from Mikrotik
            mikrotik = MikrotikService(
                host=Config.MIKROTIK_HOST,
                username=Config.MIKROTIK_USER,
                password=Config.MIKROTIK_PASSWORD
            )
            pppoe_users = mikrotik.get_all_pppoe_secrets()
            
            # Track sync results
            added_count = 0
            skipped_count = 0
            error_count = 0
            
            for user in pppoe_users:
                username = user.get('name', '')
                
                if not username:
                    continue
                
                # Check if client already exists
                existing_client = Client.query.filter_by(pppoe_username=username).first()
                
                if existing_client:
                    skipped_count += 1
                    logger.info(f"Skipped existing user: {username}")
                    continue
                
                try:
                    # Create new client with default values
                    client = Client(
                        full_name=username,  # Use username as name for now
                        address='',
                        contact_number='',
                        email='',
                        pppoe_username=username,
                        plan_name='Default Plan',  # Default plan
                        plan_amount=0.0,  # Default amount
                        status='active'
                    )
                    
                    db.session.add(client)
                    db.session.commit()
                    added_count += 1
                    logger.info(f"Added new client from Mikrotik: {username}")
                    
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error adding client {username}: {str(e)}")
                    db.session.rollback()
            
            return {
                'success': True,
                'total': len(pppoe_users),
                'added': added_count,
                'skipped': skipped_count,
                'errors': error_count
            }
            
        except Exception as e:
            logger.error(f"Error syncing from Mikrotik: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
