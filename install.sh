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
    sudo apt install -y python3 python3-pip libfuse2
    sudo pip3 install requests
  fi
}

# Function to install ValiDapp
install_validapp() {
  echo "Downloading and installing ValiDapp..."
  wget https://github.com/accidental-green/ValiDapp/releases/download/v1.0.0-alpha/ValiDapp-1.0.0.AppImage -O ValiDapp-1.0.0.AppImage
  chmod +x ValiDapp-1.0.0.AppImage
  sudo mv ValiDapp-1.0.0.AppImage /usr/bin/validapp

  # Update permissions for chrome-sandbox to enable sandboxing
  echo "Setting permissions for chrome-sandbox..."
  if [[ -f "/usr/bin/validapp/chrome-sandbox" ]]; then
    sudo chmod 4755 /usr/bin/validapp/chrome-sandbox
  else
    echo "Warning: chrome-sandbox not found in /usr/bin/validapp. Please ensure it is correctly bundled."
  fi

  echo "ValiDapp has been successfully installed. You can run it by typing 'validapp'"
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
create_desktop_icon

# Run the application
validapp &
