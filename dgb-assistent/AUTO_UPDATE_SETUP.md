# 🚀 DGB Assistent Auto-Update Setup Guide

## ✅ What's Been Added

Your DGB Assistent now includes a **professional auto-update system** that:

- ✨ **Automatically checks for updates** from your GitHub releases
- 🔔 **Shows beautiful update notifications** in Danish
- ⬇️ **Downloads and installs updates** with a single click
- ⚙️ **Full settings control** - users can configure update preferences
- 🔒 **Safe updates** with automatic backups
- 🎨 **Modern UI** matching your app's premium design

## 📋 Setup Instructions

### 1. Update Your GitHub Repository Settings

In your `config.py` file, update these lines with your actual GitHub info:
```python
# GitHub Repository for Updates
GITHUB_REPO_OWNER = "your-username"  # Replace with your GitHub username
GITHUB_REPO_NAME = "dgb-assistent"   # Replace with your repository name
```

### 2. Create GitHub Repository

1. Go to GitHub.com and create a new repository named `dgb-assistent`
2. Upload your project files to this repository
3. Make sure the repository is **public** (for releases to work)

### 3. Create Releases for Updates

When you want to push an update:

1. **Update the version** in `config.py`:
   ```python
   APP_VERSION = "1.1.0"  # Increment version number
   ```

2. **Build your new executable**:
   ```bash
   .\build.bat
   ```

3. **Create a GitHub Release**:
   - Go to your repository on GitHub
   - Click "Releases" → "Create a new release"
   - Tag version: `v1.1.0` (must match your APP_VERSION)
   - Release title: `DGB Assistent v1.1.0`
   - Description: Write what's new in Danish
   - **Upload your executable**: Drag `DGB-Assistent.exe` as an asset
   - **Important**: The file must be in a ZIP file for auto-update to work
   - Click "Publish release"

### 4. Test the Auto-Update

1. Run your app on another computer
2. It will automatically check for updates when launched
3. If a newer version is available, users will see an update popup
4. They can click "Opdater Nu" to automatically install

## 🎛️ User Settings

Your users can control updates via **Indstillinger** (Settings):

- **Enable/disable auto-updates**
- **Set check frequency** (daily, weekly, etc.)
- **Control notifications**
- **Backup preferences**

## 📱 How It Works

1. **Background Check**: When the app starts, it checks GitHub for new releases
2. **Version Comparison**: Compares current version with latest release
3. **User Notification**: Shows a beautiful popup if update is available
4. **One-Click Update**: Downloads, backs up, and installs automatically
5. **App Restart**: Restarts with the new version

## 🛡️ Safety Features

- **Automatic backups** before updating
- **Internet connectivity checks**
- **Error handling** with user-friendly messages
- **Rollback capability** if update fails
- **User control** over all update preferences

## 🎨 Example Release Process

1. Make your code changes
2. Update version: `APP_VERSION = "1.2.0"`
3. Build: `.\build.bat`
4. Zip your executable: `DGB-Assistent-v1.2.0.zip`
5. Create GitHub release with this zip file
6. All users will automatically be notified!

## 🔧 Technical Details

- Uses GitHub Releases API for version checking
- Supports semantic versioning (1.0.0, 1.1.0, etc.)
- Downloads updates to user's AppData folder
- Creates timestamped backups
- Settings stored in user's AppData/Local/DGB-Assistent

Your auto-update system is now **production-ready** and will work just like commercial applications! 🎉