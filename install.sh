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
  sudo apt install -y python3 python3-requests libfuse2
}

# Function to install ValiDapp
install_validapp() {
  echo "Downloading and installing ValiDapp..."
  wget https://github.com/accidental-green/ValiDapp/releases/download/v1.0.0-alpha/ValiDapp-1.0.0.AppImage -O ValiDapp-1.0.0.AppImage
  chmod +x ValiDapp-1.0.0.AppImage
  sudo mv ValiDapp-1.0.0.AppImage /usr/bin/validapp

  echo "ValiDapp has been successfully installed. You can run it by typing 'validapp'"
}

# Function to extract the AppImage and set permissions for chrome-sandbox
set_chrome_sandbox_permissions() {
  echo "Extracting ValiDapp and setting permissions for chrome-sandbox..."
  
  # Create a temporary directory for extraction
  temp_dir=$(mktemp -d)
  cp /usr/bin/validapp "$temp_dir/"
  cd "$temp_dir"
  
  # Extract the AppImage
  ./validapp --appimage-extract

  # Set permissions for chrome-sandbox
  if [[ -f "$temp_dir/squashfs-root/chrome-sandbox" ]]; then
    sudo chmod 4755 "$temp_dir/squashfs-root/chrome-sandbox"
    echo "Permissions for chrome-sandbox have been set."
  else
    echo "Warning: chrome-sandbox not found in the extracted files. The application might not run correctly without proper sandboxing."
  fi

  # Clean up
  cd -
  rm -rf "$temp_dir"
}

# Function to create desktop icon for ValiDapp
create_desktop_icon() {
  echo "Creating desktop entry for ValiDapp..."
  cat <<EOF | sudo tee /usr/share/applications/validapp.desktop > /dev/null
[Desktop Entry]
Version=1.0
Name=ValiDapp
Exec=/usr/bin/validapp
Icon=/usr/bin/validapp
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
