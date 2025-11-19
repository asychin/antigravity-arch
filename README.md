# antigravity-bin - Arch Linux Package

Automatically updated package for installing Google Antigravity on Arch Linux.

## Installation

### From this repository

```bash
git clone https://github.com/asychin/antigravity-arch.git
cd antigravity-arch
makepkg -si
```

## Update

The package is automatically checked for updates daily via GitHub Actions. When a new version of Antigravity is released, the PKGBUILD is automatically updated.

To update the installed package:

```bash
cd antigravity-arch
git pull
makepkg -si
```

## Repository Structure

- `PKGBUILD` - Arch Linux package build script
- `.SRCINFO` - Package metadata (generated automatically)
- `update_package.py` - Script for automatic version updates
- `.github/workflows/update.yml` - GitHub Actions workflow for automatic checking

## How it works

1. GitHub Actions runs daily or manually
2. The `update_package.py` script checks the Antigravity download page
3. If a new version is detected:
   - Downloads the file and calculates SHA256
   - Updates `PKGBUILD` with new version and checksum
   - Generates `.SRCINFO`
   - Commits changes to the repository

## Dependencies

The package requires the following dependencies:
- gtk3
- nss
- alsa-lib
- libxss
- libxtst
- xdg-utils
- glibc
- nspr
- at-spi2-core
- libdrm
- mesa

## License

Antigravity is proprietary software from Google.
