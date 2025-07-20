import os
import requests
from django.conf import settings
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.utils.deconstruct import deconstructible

@deconstructible
class BunnyStorage(Storage):
    def __init__(self, location=None, base_url=None):
        self.location = location or ''
        self.base_url = base_url or settings.BUNNYCDN_PULL_ZONE_URL
        self.storage_zone_name = settings.BUNNYCDN_STORAGE_ZONE_NAME
        self.api_key = settings.BUNNYCDN_API_KEY
        self.region = settings.BUNNYCDN_REGION or ''
        
        # Construct the storage API URL
        if self.region:
            self.storage_url = f"https://{self.region}.storage.bunnycdn.com/{self.storage_zone_name}/"
        else:
            self.storage_url = f"https://storage.bunnycdn.com/{self.storage_zone_name}/"

    def _open(self, name, mode='rb'):
        # For reading files, we'll redirect to the CDN URL
        return ContentFile(self._read(name))

    def _read(self, name):
        # Read file from bunny.net storage
        url = f"{self.storage_url}{name}"
        headers = {
            'AccessKey': self.api_key,
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.content
        else:
            raise FileNotFoundError(f"File {name} not found in bunny.net storage")

    def _save(self, name, content):
        # Save file to bunny.net storage
        url = f"{self.storage_url}{name}"
        headers = {
            'AccessKey': self.api_key,
            'Content-Type': getattr(content, 'content_type', 'application/octet-stream'),
        }
        
        # Debug information
        print(f"DEBUG: Uploading to {url}")
        print(f"DEBUG: API Key: {self.api_key[:20]}...")
        print(f"DEBUG: Storage Zone: {self.storage_zone_name}")
        
        # Ensure the content is at the beginning
        if hasattr(content, 'seek'):
            content.seek(0)
        
        response = requests.put(url, data=content, headers=headers)
        
        print(f"DEBUG: Response status: {response.status_code}")
        print(f"DEBUG: Response text: {response.text}")
        
        if response.status_code in [200, 201]:
            return name
        else:
            raise Exception(f"Failed to upload file to bunny.net: {response.status_code} - {response.text}")

    def delete(self, name):
        # Delete file from bunny.net storage
        url = f"{self.storage_url}{name}"
        headers = {
            'AccessKey': self.api_key,
        }
        response = requests.delete(url, headers=headers)
        return response.status_code in [200, 204]

    def exists(self, name):
        # Check if file exists in bunny.net storage
        url = f"{self.storage_url}{name}"
        headers = {
            'AccessKey': self.api_key,
        }
        response = requests.head(url, headers=headers)
        return response.status_code == 200

    def url(self, name):
        # Return the CDN URL for the file
        if self.base_url:
            return f"{self.base_url}/{name}"
        return name

    def size(self, name):
        # Get file size from bunny.net storage
        url = f"{self.storage_url}{name}"
        headers = {
            'AccessKey': self.api_key,
        }
        response = requests.head(url, headers=headers)
        if response.status_code == 200:
            return int(response.headers.get('Content-Length', 0))
        return 0

    def get_accessed_time(self, name):
        # Bunny.net doesn't provide access time, return modification time
        return self.get_modified_time(name)

    def get_created_time(self, name):
        # Bunny.net doesn't provide creation time, return modification time
        return self.get_modified_time(name)

    def get_modified_time(self, name):
        # Get modification time from bunny.net storage
        url = f"{self.storage_url}{name}"
        headers = {
            'AccessKey': self.api_key,
        }
        response = requests.head(url, headers=headers)
        if response.status_code == 200:
            from datetime import datetime
            last_modified = response.headers.get('Last-Modified')
            if last_modified:
                return datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S %Z')
        return None 