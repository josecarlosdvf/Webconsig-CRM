"""Storage abstraction for file management (S3/Cloudflare/local)."""

import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import BinaryIO
from uuid import UUID

from pydantic import BaseModel


logger = logging.getLogger(__name__)


class StorageConfig(BaseModel):
    """Storage configuration."""
    provider: str  # "s3", "cloudflare", "local"
    bucket: str | None = None
    region: str | None = None
    endpoint: str | None = None
    access_key: str | None = None
    secret_key: str | None = None
    public_base_url: str | None = None
    local_path: str | None = None


class StorageProvider(ABC):
    """Abstract storage provider interface."""
    
    @abstractmethod
    async def upload(
        self,
        file: BinaryIO,
        key: str,
        content_type: str | None = None,
        metadata: dict | None = None,
    ) -> str:
        """
        Upload a file to storage.
        
        Args:
            file: File object to upload
            key: Storage key (path)
            content_type: MIME type
            metadata: Additional metadata
            
        Returns:
            URL to access the file
        """
        pass
    
    @abstractmethod
    async def download(self, key: str) -> bytes:
        """
        Download a file from storage.
        
        Args:
            key: Storage key (path)
            
        Returns:
            File content as bytes
        """
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """
        Delete a file from storage.
        
        Args:
            key: Storage key (path)
        """
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        Check if a file exists in storage.
        
        Args:
            key: Storage key (path)
            
        Returns:
            True if file exists
        """
        pass
    
    @abstractmethod
    async def generate_signed_url(self, key: str, expires_in: int = 3600) -> str:
        """
        Generate a signed URL for secure download.
        
        Args:
            key: Storage key (path)
            expires_in: Expiration time in seconds
            
        Returns:
            Signed URL
        """
        pass


class LocalStorageProvider(StorageProvider):
    """Local filesystem storage provider."""
    
    def __init__(self, config: StorageConfig):
        self.base_path = Path(config.local_path or "/tmp/storage")
        self.base_url = config.public_base_url or "http://localhost:8000/storage"
        self.base_path.mkdir(parents=True, exist_ok=True)
        
    async def upload(
        self,
        file: BinaryIO,
        key: str,
        content_type: str | None = None,
        metadata: dict | None = None,
    ) -> str:
        """Upload file to local filesystem."""
        file_path = self.base_path / key
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "wb") as f:
            f.write(file.read())
            
        logger.info(f"Uploaded file to {file_path}")
        return f"{self.base_url}/{key}"
    
    async def download(self, key: str) -> bytes:
        """Download file from local filesystem."""
        file_path = self.base_path / key
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {key}")
            
        with open(file_path, "rb") as f:
            return f.read()
    
    async def delete(self, key: str) -> None:
        """Delete file from local filesystem."""
        file_path = self.base_path / key
        
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Deleted file {file_path}")
    
    async def exists(self, key: str) -> bool:
        """Check if file exists in local filesystem."""
        file_path = self.base_path / key
        return file_path.exists()
    
    async def generate_signed_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate signed URL (for local storage, just return public URL)."""
        # For local storage, we don't have real signed URLs
        # In production, this would be implemented with a token system
        return f"{self.base_url}/{key}"


class S3StorageProvider(StorageProvider):
    """S3-compatible storage provider (AWS S3, Cloudflare R2, MinIO, etc.)."""
    
    def __init__(self, config: StorageConfig):
        self.config = config
        self.bucket = config.bucket
        self.public_base_url = config.public_base_url
        
        # Initialize aioboto3 session
        try:
            import aioboto3
            self.session = aioboto3.Session(
                aws_access_key_id=config.access_key,
                aws_secret_access_key=config.secret_key,
                region_name=config.region,
            )
            logger.info(f"Initialized S3 storage provider for bucket {self.bucket}")
        except ImportError:
            raise ImportError("aioboto3 is required for S3 storage. Install with: pip install aioboto3")
    
    async def upload(
        self,
        file: BinaryIO,
        key: str,
        content_type: str | None = None,
        metadata: dict | None = None,
    ) -> str:
        """Upload file to S3."""
        async with self.session.client(
            's3',
            endpoint_url=self.config.endpoint,
        ) as s3:
            # Prepare upload parameters
            upload_params = {
                'Bucket': self.bucket,
                'Key': key,
                'Body': file.read(),
            }
            
            if content_type:
                upload_params['ContentType'] = content_type
                
            if metadata:
                upload_params['Metadata'] = metadata
            
            # Upload to S3
            await s3.put_object(**upload_params)
            
            logger.info(f"Uploaded file to S3: {self.bucket}/{key}")
            
            # Return public URL
            if self.public_base_url:
                return f"{self.public_base_url}/{key}"
            elif self.config.endpoint:
                return f"{self.config.endpoint}/{self.bucket}/{key}"
            else:
                return f"https://s3.{self.config.region}.amazonaws.com/{self.bucket}/{key}"
    
    async def download(self, key: str) -> bytes:
        """Download file from S3."""
        async with self.session.client(
            's3',
            endpoint_url=self.config.endpoint,
        ) as s3:
            try:
                response = await s3.get_object(Bucket=self.bucket, Key=key)
                content = await response['Body'].read()
                logger.info(f"Downloaded file from S3: {self.bucket}/{key}")
                return content
            except Exception as e:
                logger.error(f"Failed to download from S3: {e}")
                raise FileNotFoundError(f"File not found: {key}")
    
    async def delete(self, key: str) -> None:
        """Delete file from S3."""
        async with self.session.client(
            's3',
            endpoint_url=self.config.endpoint,
        ) as s3:
            await s3.delete_object(Bucket=self.bucket, Key=key)
            logger.info(f"Deleted file from S3: {self.bucket}/{key}")
    
    async def exists(self, key: str) -> bool:
        """Check if file exists in S3."""
        async with self.session.client(
            's3',
            endpoint_url=self.config.endpoint,
        ) as s3:
            try:
                await s3.head_object(Bucket=self.bucket, Key=key)
                return True
            except Exception:
                return False
    
    async def generate_signed_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate S3 pre-signed URL."""
        async with self.session.client(
            's3',
            endpoint_url=self.config.endpoint,
        ) as s3:
            url = await s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': key},
                ExpiresIn=expires_in
            )
            logger.info(f"Generated signed URL for {self.bucket}/{key} (expires in {expires_in}s)")
            return url


def create_storage_provider(config: StorageConfig) -> StorageProvider:
    """
    Factory to create storage provider based on config.
    
    Args:
        config: Storage configuration
        
    Returns:
        StorageProvider instance
    """
    if config.provider == "local":
        return LocalStorageProvider(config)
    elif config.provider in ("s3", "cloudflare"):
        return S3StorageProvider(config)
    else:
        raise ValueError(f"Unsupported storage provider: {config.provider}")


# Default storage instance (will be configured at app startup)
_default_storage: StorageProvider | None = None


def configure_storage(config: StorageConfig) -> None:
    """Configure the default storage provider."""
    global _default_storage
    _default_storage = create_storage_provider(config)
    logger.info(f"Configured storage provider: {config.provider}")


def get_storage() -> StorageProvider:
    """Get the default storage provider."""
    if _default_storage is None:
        # Fallback to local storage if not configured
        logger.warning("Storage not configured, using local storage fallback")
        return LocalStorageProvider(StorageConfig(provider="local", local_path="/tmp/storage"))
    return _default_storage


def generate_storage_key(tenant_id: UUID, domain: str, filename: str) -> str:
    """
    Generate a storage key for a file.
    
    Args:
        tenant_id: Tenant ID
        domain: Domain (e.g., "hr", "finance")
        filename: Original filename
        
    Returns:
        Storage key (path)
    """
    # Format: {tenant_id}/{domain}/{year}/{month}/{filename}
    now = datetime.now()
    return f"{tenant_id}/{domain}/{now.year}/{now.month:02d}/{filename}"

