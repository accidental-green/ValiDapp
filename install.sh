#!/bin/bash

set -e

# Function to detect the Ubuntu version
get_ubuntu_version() {
  . /etc/os-release
  echo "$VERSION_ID"
}

# Function to install Python and dependencies
install_python_and_dependencies() {
  echo "Installing dependencies for Ubuntu $1"
  sudo apt update
  if [ "$1" == "24.04" ]; then
    # Special handling for Ubuntu 24.04
    sudo apt install -y python3 python3-pip python3-requests libfuse2
  else
    sudo apt install -y python3 python3-pip python3-requests libfuse2
  fi
}

# Function to install ValiDapp
install_validapp() {
  echo "Downloading and installing ValiDapp..."
  wget https://github.com/accidental-green/ValiDapp/releases/download/v1.0.0-alpha/ValiDapp-1.0.0.AppImage -O ValiDapp-1.0.0.AppImage
  chmod +x ValiDapp-1.0.0.AppImage
  sudo mv ValiDapp-1.0.0.AppImage /usr/bin/validapp

  echo "ValiDapp has been successfully installed. You can run it by typing 'validapp'"
}

# Function to set permissions for chrome-sandbox
set_chrome_sandbox_permissions() {
  echo "Setting permissions for chrome-sandbox..."
  
  # Extract AppImage to find chrome-sandbox
  mkdir -p /tmp/validapp-extract
  /usr/bin/validapp --appimage-extract -C /tmp/validapp-extract || true

  # Find the chrome-sandbox file in the extracted files
  chrome_sandbox_path=$(find /tmp/validapp-extract -name "chrome-sandbox" | head -n 1)

  if [[ -f "$chrome_sandbox_path" ]]; then
    sudo chmod 4755 "$chrome_sandbox_path"
    sudo mv "$chrome_sandbox_path" /usr/bin/
    echo "Permissions for chrome-sandbox have been set."
  else
    echo "Warning: chrome-sandbox not found in the extracted files. The application might not run correctly without proper sandboxing."
  fi
}

# Function to extract logo and create a desktop icon for ValiDapp
create_desktop_icon() {
  echo "Extracting logo and creating desktop entry for ValiDapp..."

  # Extract the logo from the AppImage (assuming you have a logo in app/assets/logo.png within the AppImage)
  logo_path="/usr/share/pixmaps/validapp.png"
  mkdir -p /tmp/validapp-extract
  /usr/bin/validapp --appimage-extract -C /tmp/validapp-extract || true

  # Check if the logo exists in the extracted files
  if [[ -f "/tmp/validapp-extract/squashfs-root/app/assets/logo.png" ]]; then
    sudo mkdir -p /usr/share/pixmaps/
    sudo cp "/tmp/validapp-extract/squashfs-root/app/assets/logo.png" "$logo_path"
  else
    echo "Warning: Logo not found in the extracted AppImage. Using default icon path."
  fi

  # Create the desktop entry with the logo path
  cat <<EOF | sudo tee /usr/share/applications/validapp.desktop > /dev/null
[Desktop Entry]
Version=1.0
Name=ValiDapp
Exec=/usr/bin/validapp
Icon=$logo_path
Terminal=false
Type=Application
Categories=Utility;
EOF
  echo "Desktop entry for ValiDapp has been created."
}

# Main script execution
ubuntu_version=$(get_ubuntu_version)

case "$ubuntu_version" in
  "20.04"|"22.04"|"24.04")
    install_python_and_dependencies "$ubuntu_version"
    ;;
  *)
    echo "Unsupported Ubuntu version or non-Ubuntu system detected. Attempting general installation."
    install_python_and_dependencies "other"
    ;;
esac

install_validapp
set_chrome_sandbox_permissions
create_desktop_icon

# Run the application
validapp &
