# ValiDapp Installation Guide

## Quick Install - Single Command

Open a new terminal (press `Ctrl + Alt + T`) and copy/paste the following command to install ValiDapp:

**Note:** Use the copy button on the right side to copy the entire command.

```bash
sudo apt update && sudo apt install libfuse2 python3 python3-pip curl ntpdate -y && sudo ntpdate ntp.ubuntu.com && python3 -m pip install requests && wget https://github.com/accidental-green/ValiDapp/releases/download/v1.0.0-alpha/ValiDapp-1.0.0.AppImage && chmod +x ValiDapp-1.0.0.AppImage && sudo mv ValiDapp-1.0.0.AppImage /usr/bin/validapp && validapp
```

After entering your password, the required packages will be installed, and ValiDapp will open automatically once installation is complete.

## Features Overview

- **Validator Dashboard**: Start, stop, and monitor validator status
- **Install Validator**: Set up new validator clients
- **Update Validator**: Upgrade to the latest client versions
- **Import Keystore**: Import an existing validator keystore
- **Delete Validator**: Remove validator components and data

## Installation Steps

1. **Validator Installer**: Configure validator settings and click **Install Validator**.
   
   <img src="https://github.com/user-attachments/assets/e7d885d4-e8ca-4ef9-8642-299fc4a8b74f" alt="Validator Install" width="800">

2. **Keystore Warning**: For security, use the keystore import tool only for testnet keys.<br>For mainnet keys, select "Import Keystore? NO" and follow Somer's guides for manual import.
   
   <img src="https://github.com/user-attachments/assets/cc6854ea-6846-4144-aae6-fba20e6f001a" alt="Import Warning" width="600">

3. **Confirm Installation**: Review your settings and click **Start Installation**.
   
   <img src="https://github.com/user-attachments/assets/ba482f6f-5051-4843-9f02-58d077c79e89" alt="Confirm Install" width="600">

4. **Import Keystore**: Select the keystore file, enter the password, and click **Import Keystore**.
   
   <img src="https://github.com/user-attachments/assets/04fa895a-7b20-4eb6-aef1-ab3ebbc25ce2" alt="Import Keystore" width="600">

5. **Validator Dashboard**: Click **Start All** to begin syncing.
   
   <img src="https://github.com/user-attachments/assets/8ebb4282-a133-47c8-9850-400362b33ffa" alt="Dashboard" width="600">

6. **View Journals**: Access detailed logs and sync progress.
   
   <img src="https://github.com/user-attachments/assets/1d919a8d-a067-478e-917d-f4bd964c170f" alt="Journals" width="600">

7. **Main Menu**: Navigate back to the main menu for additional functions.
   
   <img src="https://github.com/user-attachments/assets/96dd0c79-25b2-4b4c-8fb4-c79ab44a8fb7" alt="Main Menu" width="600">

8. **Validator Updater**: Check and update to the latest versions by using the updater feature.
   
   <img src="https://github.com/user-attachments/assets/952c6655-529a-45e5-9c2e-5b0a33c33a95" alt="Updater" width="600">

9. **Validator Deleter**: Easily remove clients and data.
   
   <img src="https://github.com/user-attachments/assets/548bee98-e9ea-40e0-b405-c1e840e2a389" alt="Deleter" width="600">

## Starting ValiDapp

- Launch ValiDapp by searching for "Validapp" in your applications or add it to your favorites for quick access.

   <img src="https://github.com/user-attachments/assets/36e54392-b03a-4d69-bc4e-e120a05d0396" alt="ValiDapp Application" width="300"> 

   <img src="https://github.com/user-attachments/assets/335112b0-acd3-4088-82ca-0440418ecccd" alt="Favorites" width="300">

## Helpful Resources

Explore additional staking resources for more information.

<img src="https://github.com/user-attachments/assets/97b881bc-d869-4098-b539-bc133cf8c74a" alt="Resources" width="600">
