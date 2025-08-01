#!/usr/bin/env python3
"""
LSR Download Monitor
Monitors https://lsr.di.unimi.it/download/ for changes and downloads updated files.
"""

import os
import sys
import json
import hashlib
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

# Configuration
BASE_URL = "https://lsr.di.unimi.it/download/"
DOWNLOADS_DIR = "downloads"
METADATA_FILE = os.path.join(DOWNLOADS_DIR, "metadata.json")

def get_page_content():
    """Fetch the download page content."""
    try:
        response = requests.get(BASE_URL, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching page: {e}")
        sys.exit(1)

def parse_file_list(html_content):
    """Parse the HTML to extract file information."""
    soup = BeautifulSoup(html_content, 'html.parser')
    files = {}
    
    # Find all links that point to files (not directories)
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and not href.endswith('/') and href != '../':
            # Extract file info from the table row
            row = link.find_parent('tr')
            if row:
                cells = row.find_all('td')
                if len(cells) >= 3:
                    filename = href
                    # Try to get last modified date and size
                    try:
                        last_modified = cells[1].get_text(strip=True)
                        size = cells[2].get_text(strip=True)
                        files[filename] = {
                            'last_modified': last_modified,
                            'size': size,
                            'url': urljoin(BASE_URL, href)
                        }
                    except (IndexError, AttributeError):
                        # Fallback if table structure is different
                        files[filename] = {
                            'last_modified': '',
                            'size': '',
                            'url': urljoin(BASE_URL, href)
                        }
    
    return files

def load_metadata():
    """Load existing metadata about downloaded files."""
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            print("Warning: Could not load metadata file, starting fresh")
    return {}

def save_metadata(metadata):
    """Save metadata about downloaded files."""
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=2)

def calculate_file_hash(filepath):
    """Calculate MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except IOError:
        return None

def download_file(url, filepath, retries=3):
    """Download a file with retry logic."""
    for attempt in range(retries):
        try:
            print(f"Downloading {url} (attempt {attempt + 1}/{retries})")
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Successfully downloaded: {filepath}")
            return True
            
        except requests.RequestException as e:
            print(f"Download attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(5)  # Wait before retry
            else:
                print(f"Failed to download {url} after {retries} attempts")
                return False
    
    return False

def main():
    """Main monitoring and download logic."""
    print(f"Starting LSR monitor at {datetime.now().isoformat()}")
    
    # Fetch current page content
    html_content = get_page_content()
    current_files = parse_file_list(html_content)
    
    if not current_files:
        print("No files found on the download page")
        return
    
    print(f"Found {len(current_files)} files on download page")
    
    # Load existing metadata
    metadata = load_metadata()
    
    changes_detected = False
    
    # Check each file
    for filename, file_info in current_files.items():
        filepath = os.path.join(DOWNLOADS_DIR, filename)
        
        # Check if file is new or modified
        should_download = False
        reason = ""
        
        if filename not in metadata:
            should_download = True
            reason = "new file"
        elif file_info['last_modified'] != metadata[filename].get('last_modified'):
            should_download = True
            reason = "modified date changed"
        elif file_info['size'] != metadata[filename].get('size'):
            should_download = True
            reason = "size changed"
        elif not os.path.exists(filepath):
            should_download = True
            reason = "local file missing"
        
        if should_download:
            print(f"Downloading {filename} ({reason})")
            if download_file(file_info['url'], filepath):
                # Update metadata
                file_hash = calculate_file_hash(filepath)
                metadata[filename] = {
                    'last_modified': file_info['last_modified'],
                    'size': file_info['size'],
                    'url': file_info['url'],
                    'downloaded_at': datetime.now().isoformat(),
                    'hash': file_hash
                }
                changes_detected = True
            else:
                print(f"Failed to download {filename}")
        else:
            print(f"No changes detected for {filename}")
    
    # Clean up metadata for files that no longer exist on the server
    files_to_remove = []
    for filename in metadata:
        if filename not in current_files:
            files_to_remove.append(filename)
            local_file = os.path.join(DOWNLOADS_DIR, filename)
            if os.path.exists(local_file):
                print(f"Removing outdated file: {filename}")
                os.remove(local_file)
                changes_detected = True
    
    for filename in files_to_remove:
        del metadata[filename]
    
    # Save updated metadata
    save_metadata(metadata)
    
    if changes_detected:
        print("Changes detected and files updated")
    else:
        print("No changes detected")
    
    print(f"Monitor completed at {datetime.now().isoformat()}")

if __name__ == "__main__":
    main()
