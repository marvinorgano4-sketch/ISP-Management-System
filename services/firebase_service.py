"""
Firebase Service Base Class

This module provides a base service class for Firebase Firestore operations.
It implements common CRUD operations that can be inherited by specific service classes.
"""

from firebase_admin import firestore
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


class FirebaseService:
    """
    Base service class for Firebase Firestore operations.
    
    This class provides common CRUD operations for Firestore collections:
    - create: Add new documents with automatic timestamps
    - get: Retrieve documents by ID
    - get_all: Query all documents with optional filters and ordering
    - update: Modify existing documents with automatic timestamps
    - delete: Remove documents with existence checks
    - query: Execute custom queries with operators
    
    Attributes:
        db: Firestore database client
        collection_name: Name of the Firestore collection
        collection: Firestore collection reference
    
    Example:
        >>> db = firestore.client()
        >>> service = FirebaseService(db, 'users')
        >>> user_id = service.create({'username': 'admin', 'full_name': 'Admin User'})
        >>> user = service.get(user_id)
    """
    
    def __init__(self, db, collection_name: str):
        """
        Initialize the FirebaseService.
        
        Args:
            db: Firestore database client instance
            collection_name: Name of the Firestore collection to operate on
        """
        self.db = db
        self.collection_name = collection_name
        self.collection = db.collection(collection_name)
        logger.debug(f"FirebaseService initialized for collection: {collection_name}")
    
    def create(self, data: Dict[str, Any]) -> str:
        """
        Create a new document in the collection.
        
        Automatically adds a 'created_at' timestamp to the document.
        
        Args:
            data: Dictionary containing the document data
            
        Returns:
            str: The auto-generated document ID
            
        Raises:
            Exception: If the create operation fails
            
        Example:
            >>> user_id = service.create({'username': 'john', 'full_name': 'John Doe'})
            >>> print(user_id)  # 'abc123xyz'
        """
        try:
            # Add created_at timestamp
            data['created_at'] = firestore.SERVER_TIMESTAMP
            
            # Create document with auto-generated ID
            doc_ref = self.collection.document()
            doc_ref.set(data)
            
            logger.info(f"Created document in {self.collection_name}: {doc_ref.id}")
            return doc_ref.id
            
        except Exception as e:
            logger.error(f"Failed to create document in {self.collection_name}: {e}")
            raise
    
    def get(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID.
        
        Retrieves a single document and includes the document ID in the returned data.
        
        Args:
            doc_id: The document ID to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: Document data with 'id' field, or None if not found
            
        Example:
            >>> user = service.get('abc123xyz')
            >>> if user:
            ...     print(user['id'], user['username'])
        """
        try:
            doc = self.collection.document(doc_id).get()
            
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                logger.debug(f"Retrieved document from {self.collection_name}: {doc_id}")
                return data
            
            logger.debug(f"Document not found in {self.collection_name}: {doc_id}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get document from {self.collection_name} ({doc_id}): {e}")
            raise
    
    def get_all(self, filters: Optional[Dict[str, Any]] = None, order_by: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all documents with optional filters and ordering.
        
        Args:
            filters: Optional dictionary of field-value pairs to filter by (equality only)
            order_by: Optional field name to order results by
            
        Returns:
            List[Dict[str, Any]]: List of documents, each with 'id' field included
            
        Example:
            >>> # Get all active clients ordered by name
            >>> clients = service.get_all(
            ...     filters={'status': 'active'},
            ...     order_by='full_name'
            ... )
        """
        try:
            query = self.collection
            
            # Apply filters
            if filters:
                for field, value in filters.items():
                    query = query.where(field, '==', value)
            
            # Apply ordering
            if order_by:
                query = query.order_by(order_by)
            
            # Execute query
            docs = query.stream()
            results = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)
            
            logger.debug(f"Retrieved {len(results)} documents from {self.collection_name}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to get all documents from {self.collection_name}: {e}")
            raise
    
    def update(self, doc_id: str, data: Dict[str, Any]) -> bool:
        """
        Update an existing document.
        
        Automatically adds an 'updated_at' timestamp to the update.
        Checks if the document exists before updating.
        
        Args:
            doc_id: The document ID to update
            data: Dictionary containing the fields to update
            
        Returns:
            bool: True if update succeeded, False if document doesn't exist
            
        Raises:
            Exception: If the update operation fails
            
        Example:
            >>> success = service.update('abc123xyz', {'status': 'inactive'})
            >>> if success:
            ...     print("Update successful")
        """
        try:
            # Add updated_at timestamp
            data['updated_at'] = firestore.SERVER_TIMESTAMP
            
            # Get document reference
            doc_ref = self.collection.document(doc_id)
            
            # Check if document exists
            if not doc_ref.get().exists:
                logger.warning(f"Document not found for update in {self.collection_name}: {doc_id}")
                return False
            
            # Update document
            doc_ref.update(data)
            
            logger.info(f"Updated document in {self.collection_name}: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update document in {self.collection_name} ({doc_id}): {e}")
            raise
    
    def delete(self, doc_id: str) -> bool:
        """
        Delete a document.
        
        Checks if the document exists before deleting.
        
        Args:
            doc_id: The document ID to delete
            
        Returns:
            bool: True if deletion succeeded, False if document doesn't exist
            
        Raises:
            Exception: If the delete operation fails
            
        Example:
            >>> success = service.delete('abc123xyz')
            >>> if success:
            ...     print("Deletion successful")
        """
        try:
            # Get document reference
            doc_ref = self.collection.document(doc_id)
            
            # Check if document exists
            if not doc_ref.get().exists:
                logger.warning(f"Document not found for deletion in {self.collection_name}: {doc_id}")
                return False
            
            # Delete document
            doc_ref.delete()
            
            logger.info(f"Deleted document from {self.collection_name}: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document from {self.collection_name} ({doc_id}): {e}")
            raise
    
    def query(self, field: str, operator: str, value: Any) -> List[Dict[str, Any]]:
        """
        Execute a custom query with a specific operator.
        
        Supports Firestore query operators: ==, <, <=, >, >=, !=, array_contains, in, not_in
        
        Args:
            field: The field name to query
            operator: The comparison operator (e.g., '==', '<', '>', 'in')
            value: The value to compare against
            
        Returns:
            List[Dict[str, Any]]: List of matching documents, each with 'id' field included
            
        Example:
            >>> # Find all clients with plan_amount > 1000
            >>> clients = service.query('plan_amount', '>', 1000)
            >>> 
            >>> # Find users with specific usernames
            >>> users = service.query('username', 'in', ['admin', 'user1', 'user2'])
        """
        try:
            # Execute query
            docs = self.collection.where(field, operator, value).stream()
            
            # Build results
            results = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)
            
            logger.debug(f"Query on {self.collection_name} ({field} {operator} {value}) returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Failed to query {self.collection_name} ({field} {operator} {value}): {e}")
            raise
