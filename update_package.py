#!/usr/bin/env python3
"""
Antigravity Package Updater for Arch Linux
Fetches the latest version from antigravity.google and updates PKGBUILD
"""

import re
import sys
import hashlib
import subprocess
import urllib.request
from pathlib import Path


def fetch_latest_version_from_api():
    """
    Fetch the latest Antigravity version using Playwright.
    """
    print("Fetching latest version information with Playwright...")
    
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Error: Playwright not installed. Please install it with: pip install playwright && playwright install chromium", file=sys.stderr)
        return None, None, None

    url = "https://antigravity.google/download/linux"
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            
            # Wait for page to load (network idle is usually good for SPAs)
            try:
                page.wait_for_load_state("networkidle", timeout=10000)
            except:
                pass # Continue even if timeout, maybe content is already there
            
            content = page.content()
            browser.close()
            
            # Look for version patterns in the full HTML content
            # Pattern for version: 1.11.3
            version_pattern = r'["\']?(\d+\.\d+\.\d+)["\']?'
            # Pattern for build ID: 16 digits
            buildid_pattern = r'["\']?(\d{16})["\']?'
            
            versions = re.findall(version_pattern, content)
            buildids = re.findall(buildid_pattern, content)
            
            # Filter versions to look like reasonable semver (e.g. start with 1.)
            valid_versions = [v for v in versions if v.startswith('1.')]
            
            if valid_versions and buildids:
                # Use the most frequent or first valid version
                # Heuristic: The version we want usually appears multiple times
                version = valid_versions[0]
                buildid = buildids[0]
                
                print(f"Found potential version: {version}, buildid: {buildid}")
                
                # Construct the URL
                full_url = f"https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/{version}-{buildid}/linux-x64/Antigravity.tar.gz"
                
                # Verify the URL exists
                try:
                    request = urllib.request.Request(full_url, method='HEAD')
                    urllib.request.urlopen(request)
                    return version, buildid, full_url
                except Exception as e:
                    print(f"Generated URL check failed: {e}")
                    pass
            
            print("Could not extract version from page content.", file=sys.stderr)
            return None, None, None
            
    except Exception as e:
        print(f"Error using Playwright: {e}", file=sys.stderr)
        return None, None, None


def calculate_sha256(url):
    """Download the file and calculate SHA256 checksum."""
    print(f"Downloading {url} to calculate checksum...")
    
    try:
        sha256_hash = hashlib.sha256()
        
        with urllib.request.urlopen(url) as response:
            # Read in chunks to avoid memory issues
            while True:
                chunk = response.read(8192)
                if not chunk:
                    break
                sha256_hash.update(chunk)
        
        return sha256_hash.hexdigest()
        
    except Exception as e:
        print(f"Error downloading file: {e}", file=sys.stderr)
        return None


def update_pkgbuild(version, buildid, sha256sum):
    """Update the PKGBUILD file with new version information."""
    pkgbuild_path = Path("PKGBUILD")
    
    if not pkgbuild_path.exists():
        print("Error: PKGBUILD not found", file=sys.stderr)
        return False
    
    # Read current PKGBUILD
    content = pkgbuild_path.read_text()
    
    # Update pkgver
    content = re.sub(r'^pkgver=.*$', f'pkgver={version}', content, flags=re.MULTILINE)
    
    # Update _buildid
    content = re.sub(r'^_buildid=.*$', f'_buildid={buildid}', content, flags=re.MULTILINE)
    
    # Update sha256sums
    content = re.sub(r'^sha256sums=\(.*\)$', f"sha256sums=('{sha256sum}')", content, flags=re.MULTILINE)
    
    # Write updated PKGBUILD
    pkgbuild_path.write_text(content)
    print(f"Updated PKGBUILD: version={version}, buildid={buildid}")
    
    return True


def generate_srcinfo():
    """Generate .SRCINFO file using makepkg."""
    try:
        # Run makepkg --printsrcinfo
        result = subprocess.run(
            ['makepkg', '--printsrcinfo'],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Write to .SRCINFO
        Path('.SRCINFO').write_text(result.stdout)
        print("Generated .SRCINFO")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error generating .SRCINFO: {e}", file=sys.stderr)
        print(f"stderr: {e.stderr}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("Warning: makepkg not found, skipping .SRCINFO generation", file=sys.stderr)
        return False


def main():
    """Main function."""
    print("Checking for Antigravity updates...")
    
    # For now, provide a manual way to specify version if auto-detection fails
    # You can enhance this later with better scraping
    import os
    manual_version = os.getenv('ANTIGRAVITY_VERSION')
    manual_buildid = os.getenv('ANTIGRAVITY_BUILDID')
    
    if manual_version and manual_buildid:
        version = manual_version
        buildid = manual_buildid
        url = f"https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/{version}-{buildid}/linux-x64/Antigravity.tar.gz"
        print(f"Using manual version: {version} (buildid: {buildid})")
    else:
        # Fetch latest version info
        version, buildid, url = fetch_latest_version_from_api()
        if not version:
            print("Error: Could not determine latest version", file=sys.stderr)
            print("You can manually specify version with:", file=sys.stderr)
            print("  ANTIGRAVITY_VERSION=1.11.3 ANTIGRAVITY_BUILDID=6583016683339776 python update_package.py", file=sys.stderr)
            sys.exit(1)
    
    print(f"Found version: {version}")
    print(f"Build ID: {buildid}")
    print(f"URL: {url}")
    
    # Check if this is a new version
    pkgbuild_path = Path("PKGBUILD")
    if pkgbuild_path.exists():
        current_content = pkgbuild_path.read_text()
        current_version_match = re.search(r'^pkgver=(.*)$', current_content, re.MULTILINE)
        
        if current_version_match:
            current_version = current_version_match.group(1)
            if current_version == version:
                print(f"Already up to date (version {version})")
                sys.exit(0)
    
    # Calculate SHA256
    sha256sum = calculate_sha256(url)
    if not sha256sum:
        sys.exit(1)
    
    print(f"SHA256: {sha256sum}")
    
    # Update PKGBUILD
    if not update_pkgbuild(version, buildid, sha256sum):
        sys.exit(1)
    
    # Generate .SRCINFO
    generate_srcinfo()
    
    print("Update complete!")


if __name__ == '__main__':
    main()
