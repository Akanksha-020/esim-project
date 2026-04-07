"""
File downloader with progress tracking and checksum verification
"""

import os
import hashlib
from pathlib import Path
from typing import Optional, Callable
import requests
from tqdm import tqdm
from src.utils.logger import get_logger

class FileDownloader:
    """Download files with progress tracking and verification"""
    
    CHUNK_SIZE = 1024 * 1024  # 1 MB chunks
    
    def __init__(self, timeout: int = 300):
        """
        Initialize downloader
        
        Args:
            timeout: Download timeout in seconds
        """
        self.timeout = timeout
        self.logger = get_logger()
    
    def download_file(
        self,
        url: str,
        destination: str,
        progress_callback: Optional[Callable] = None,
        verify_ssl: bool = True
    ) -> bool:
        """
        Download file from URL to destination
        
        Args:
            url: URL to download from
            destination: Local file path
            progress_callback: Optional callback for progress updates
            verify_ssl: Whether to verify SSL certificate
            
        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Starting download: {url}")
            
            # Create destination directory
            Path(destination).parent.mkdir(parents=True, exist_ok=True)
            
            # Get file size
            response = requests.head(url, timeout=self.timeout, verify=verify_ssl)
            total_size = int(response.headers.get('content-length', 0))
            
            # Download file
            response = requests.get(
                url,
                timeout=self.timeout,
                verify=verify_ssl,
                stream=True
            )
            response.raise_for_status()
            
            # Write to file with progress
            downloaded = 0
            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=self.CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback:
                            progress_callback(downloaded, total_size)
            
            self.logger.success(f"Download completed: {destination}")
            return True
            
        except requests.RequestException as e:
            self.logger.error(f"Download failed: {url}", e)
            # Clean up partial file
            if Path(destination).exists():
                Path(destination).unlink()
            return False
        except Exception as e:
            self.logger.error(f"Error during download: {str(e)}", e)
            return False
    
    def download_with_progress(self, url: str, destination: str) -> bool:
        """
        Download file with progress bar
        
        Args:
            url: URL to download
            destination: Local destination path
            
        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Downloading: {url}")
            
            Path(destination).parent.mkdir(parents=True, exist_ok=True)
            
            response = requests.get(
                url,
                timeout=self.timeout,
                stream=True
            )
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(destination, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
                    for chunk in response.iter_content(chunk_size=self.CHUNK_SIZE):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            
            self.logger.success(f"Download completed: {Path(destination).name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Download failed: {str(e)}", e)
            if Path(destination).exists():
                Path(destination).unlink()
            return False
    
    def verify_checksum(
        self,
        file_path: str,
        expected_hash: str,
        algorithm: str = "sha256"
    ) -> bool:
        """
        Verify file checksum
        
        Args:
            file_path: Path to file
            expected_hash: Expected hash value
            algorithm: Hash algorithm (md5, sha1, sha256)
            
        Returns:
            True if checksum matches
        """
        try:
            self.logger.info(f"Verifying {algorithm} checksum for {file_path}")
            
            # Calculate hash
            hash_obj = hashlib.new(algorithm)
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(self.CHUNK_SIZE), b''):
                    hash_obj.update(chunk)
            
            calculated_hash = hash_obj.hexdigest().lower()
            expected_hash = expected_hash.lower()
            
            if calculated_hash == expected_hash:
                self.logger.success(f"Checksum verification passed")
                return True
            else:
                self.logger.error(
                    f"Checksum mismatch: expected {expected_hash}, got {calculated_hash}"
                )
                return False
                
        except Exception as e:
            self.logger.error(f"Error verifying checksum: {str(e)}", e)
            return False
    
    def calculate_checksum(
        self,
        file_path: str,
        algorithm: str = "sha256"
    ) -> Optional[str]:
        """
        Calculate checksum of file
        
        Args:
            file_path: Path to file
            algorithm: Hash algorithm
            
        Returns:
            Hex hash string or None
        """
        try:
            hash_obj = hashlib.new(algorithm)
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(self.CHUNK_SIZE), b''):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculating checksum: {str(e)}", e)
            return None
