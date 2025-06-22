"""
Azure Blob Storage service for Baby Maker 5000
Handles image uploads and provides blob URIs for PhotoMaker API
"""

import os
import io
import uuid
from datetime import datetime, timedelta
from typing import Optional, Union, List, Tuple, Dict, Any
from PIL import Image
import streamlit as st
import requests
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from azure.core.exceptions import AzureError, ResourceNotFoundError
import hashlib

try:
    from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
    from azure.core.exceptions import AzureError
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

from config.settings import settings


class AzureBlobService:
    """Service for Azure Blob Storage operations"""
    
    def __init__(self):
        """Initialize Azure Blob Service"""
        self.connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        self.client = None
        self.account_key = None
        self.container_names = {
            'parent_photos': 'parent-photos',
            'generated_babies': 'generated-babies', 
            'generated_families': 'generated-families',
            'temp_uploads': 'temp-uploads'
        }
        
        if self.connection_string:
            try:
                self.client = BlobServiceClient.from_connection_string(self.connection_string)
                
                # Extract account key from connection string for SAS generation
                for part in self.connection_string.split(';'):
                    if part.startswith('AccountKey='):
                        self.account_key = part.split('=', 1)[1]
                        break
                        
            except Exception as e:
                print(f"Failed to initialize Azure Blob Service: {e}")
                self.client = None
                self.account_key = None
    
    def is_available(self) -> bool:
        """Check if Azure Blob Storage is available"""
        if not AZURE_AVAILABLE:
            return False
        return self.client is not None and self.connection_string is not None
    
    def _generate_sas_url(self, container_name: str, blob_name: str, expiry_hours: int = 24) -> Optional[str]:
        """Generate a SAS URL for secure access to a blob"""
        if not self.client or not self.account_key:
            return None
            
        try:
            # Generate SAS token
            sas_token = generate_blob_sas(
                account_name=self.client.account_name,
                container_name=container_name,
                blob_name=blob_name,
                account_key=self.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
            )
            
            # Construct the full SAS URL
            blob_url = f"https://{self.client.account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"
            return blob_url
            
        except Exception as e:
            print(f"Error generating SAS URL: {e}")
            return None
    
    def upload_parent_photo(self, image_data: bytes, filename: str = None) -> Optional[str]:
        """Upload parent photo to Azure Blob Storage and return SAS URL"""
        if not self.is_available():
            return None
            
        try:
            # Generate unique filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_id = hashlib.md5(image_data).hexdigest()[:8]
                filename = f"{timestamp}_{unique_id}.png"
            
            # Upload to parent-photos container
            blob_client = self.client.get_blob_client(
                container=self.container_names['parent_photos'], 
                blob=filename
            )
            
            blob_client.upload_blob(image_data, overwrite=True)
            
            # Return SAS URL for secure access
            return self._generate_sas_url(self.container_names['parent_photos'], filename, expiry_hours=2)
            
        except Exception as e:
            print(f"Error uploading parent photo: {e}")
            return None
    
    def save_generated_baby(self, image_url: str) -> Optional[str]:
        """Download generated baby image and upload to Azure, return SAS URL"""
        if not self.is_available():
            return None
            
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = hashlib.md5(response.content).hexdigest()[:8]
            filename = f"baby_{timestamp}_{unique_id}.png"
            
            # Upload to generated-babies container
            blob_client = self.client.get_blob_client(
                container=self.container_names['generated_babies'], 
                blob=filename
            )
            
            blob_client.upload_blob(response.content, overwrite=True)
            
            # Return SAS URL for secure access (longer expiry for generated images)
            return self._generate_sas_url(self.container_names['generated_babies'], filename, expiry_hours=24)
            
        except Exception as e:
            print(f"Error saving generated baby: {e}")
            return None
    
    def save_generated_family(self, image_url: str) -> Optional[str]:
        """Download generated family image and upload to Azure, return SAS URL"""
        if not self.is_available():
            return None
            
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = hashlib.md5(response.content).hexdigest()[:8]
            filename = f"family_{timestamp}_{unique_id}.png"
            
            # Upload to generated-families container
            blob_client = self.client.get_blob_client(
                container=self.container_names['generated_families'], 
                blob=filename
            )
            
            blob_client.upload_blob(response.content, overwrite=True)
            
            # Return SAS URL for secure access (longer expiry for generated images)
            return self._generate_sas_url(self.container_names['generated_families'], filename, expiry_hours=24)
            
        except Exception as e:
            print(f"Error saving generated family: {e}")
            return None
    
    def list_blobs(self, container_type: str) -> List[str]:
        """
        List all blobs in a container
        
        Args:
            container_type: Type of container to list
            
        Returns:
            List of blob URLs
        """
        if not self.is_available():
            return []
            
        try:
            container_name = self.container_names.get(container_type, 'temp-uploads')
            container_client = self.client.get_container_client(container_name)
            
            blob_urls = []
            for blob in container_client.list_blobs():
                blob_client = self.client.get_blob_client(
                    container=container_name,
                    blob=blob.name
                )
                blob_urls.append(blob_client.url)
            
            return blob_urls
            
        except Exception as e:
            print(f"Error listing blobs: {e}")
            return []
    
    def delete_blob(self, container_type: str, blob_name: str) -> bool:
        """
        Delete a blob from storage
        
        Args:
            container_type: Type of container
            blob_name: Name of the blob to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False
            
        try:
            container_name = self.container_names.get(container_type, 'temp-uploads')
            blob_client = self.client.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            
            blob_client.delete_blob()
            return True
            
        except Exception as e:
            print(f"Error deleting blob: {e}")
            return False
    
    def cleanup_temp_files(self, older_than_hours: int = 24) -> int:
        """
        Clean up temporary files older than specified hours
        
        Args:
            older_than_hours: Delete files older than this many hours
            
        Returns:
            Number of files deleted
        """
        if not self.is_available():
            return 0
            
        try:
            container_name = self.container_names['temp_uploads']
            container_client = self.client.get_container_client(container_name)
            
            cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
            deleted_count = 0
            
            for blob in container_client.list_blobs():
                if blob.last_modified.replace(tzinfo=None) < cutoff_time:
                    blob_client = self.client.get_blob_client(
                        container=container_name,
                        blob=blob.name
                    )
                    blob_client.delete_blob()
                    deleted_count += 1
            
            return deleted_count
            
        except Exception as e:
            print(f"Error cleaning up temp files: {e}")
            return 0
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get storage account information and status"""
        if not self.is_available():
            return {"status": "unavailable"}
            
        try:
            # Get account properties
            account_info = self.client.get_account_information()
            return {
                "status": "available",
                "account_kind": account_info.get('account_kind', 'Unknown'),
                "sku_name": account_info.get('sku_name', 'Unknown')
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


# Create singleton instance
azure_blob_service = AzureBlobService() 