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
  # Enable universe repository for Ubuntu
  sudo add-apt-repository universe
  sudo apt update
  
  if [ "$1" == "24.04" ]; then
    # Special handling for Ubuntu 24.04
    sudo apt install -y python3 python3-pip python3-requests libfuse2
  else
    sudo apt install -y python3 python3-pip libfuse2
    sudo pip3 install requests
  fi
}

# Function to install ValiDapp for Ubuntu 24.04 (extracting the AppImage)
install_validapp_24_04() {
  echo "Downloading and extracting ValiDapp for Ubuntu 24.04..."
  wget https://github.com/accidental-green/ValiDapp/releases/download/v1.0.0-alpha/ValiDapp-1.0.0.AppImage -O ValiDapp-1.0.0.AppImage
  chmod +x ValiDapp-1.0.0.AppImage
  ./ValiDapp-1.0.0.AppImage --appimage-extract

  # Remove existing /opt/validapp directory if it exists
  if [ -d "/opt/validapp" ]; then
    echo "/opt/validapp already exists. Removing it..."
    sudo rm -rf /opt/validapp
  fi

  # Move extracted files to /opt/validapp
  sudo mv squashfs-root /opt/validapp

  # Set the correct permissions for chrome-sandbox
  sudo chown root:root /opt/validapp/chrome-sandbox
  sudo chmod 4755 /opt/validapp/chrome-sandbox

  # Create a symlink to the executable in /usr/bin for easy access
  sudo ln -sf /opt/validapp/validapp /usr/bin/validapp

  echo "ValiDapp has been successfully installed. You can run it by typing 'validapp'"
}

# Function to install ValiDapp for Ubuntu 20.04 and 22.04 (direct AppImage usage)
install_validapp_20_22() {
  echo "Downloading and installing ValiDapp for Ubuntu 20.04/22.04..."
  wget https://github.com/accidental-green/ValiDapp/releases/download/v1.0.0-alpha/ValiDapp-1.0.0.AppImage -O ValiDapp-1.0.0.AppImage
  chmod +x ValiDapp-1.0.0.AppImage
  sudo mv ValiDapp-1.0.0.AppImage /usr/bin/validapp

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
Icon=/opt/validapp/resources/app/assets/logo.png
Terminal=false
Type=Application
Categories=Utility;
EOF
  echo "Desktop entry for ValiDapp has been created."
}

# Main script execution
ubuntu_version=$(get_ubuntu_version)

case "$ubuntu_version" in
  "20.04"|"22.04")
    install_python_and_dependencies "$ubuntu_version"
    install_validapp_20_22
    ;;
  "24.04")
    install_python_and_dependencies "$ubuntu_version"
    install_validapp_24_04
    ;;
  *)
    echo "Unsupported Ubuntu version or non-Ubuntu system detected. Attempting general installation."
    install_python_and_dependencies "other"
    install_validapp_20_22
    ;;
esac

create_desktop_icon

# Run the application
validapp &
