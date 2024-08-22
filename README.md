# ValiDapp Installation
## Installation Command
Open a new terminal (ctrl + alt + T) and enter the following command to run ValiDapp:

```bash
sudo apt update && sudo apt install libfuse2 -y && wget https://github.com/accidental-green/ValiDapp/releases/download/v1.0.0-alpha/ValiDapp-1.0.0.AppImage && chmod +x ValiDapp-1.0.0.AppImage && sudo mv ValiDapp-1.0.0.AppImage /usr/bin/validapp && validapp
```
Enter your password, let everything install and wait for the validator install screen to appear as shown below

## Validator Installer
Choose validator settings and click **Install Validator**

<img src="https://github.com/user-attachments/assets/e7d885d4-e8ca-4ef9-8642-299fc4a8b74f" alt="Validator Install" width="600">

### Keystore Warning
ValiDapp has not been audited and the keystore import tool should only be used for testnet keys.<br>
To safely import mainnet keystores, choose "Import Keystore? NO" and manually import using Somer's guides.

<img src="https://github.com/user-attachments/assets/cc6854ea-6846-4144-aae6-fba20e6f001a" alt="Import Warning" width="500">

### Confirm Installation
Review the information and click **Start Installation**

<img src="https://github.com/user-attachments/assets/ba482f6f-5051-4843-9f02-58d077c79e89" alt="Confirm Install" width="500">

### Import Keystore
Click "Choose File", then select the keystore, enter the password, and click **Import Keystore**:

<img src="https://github.com/user-attachments/assets/04fa895a-7b20-4eb6-aef1-ab3ebbc25ce2" alt="Import Keystore" width="500">

Once the keystore has been imported, installation is complete!

### Validator Dashboard
Continue to the Dashboard, then click **Start All** to begin syncing:

<img src="https://github.com/user-attachments/assets/8ebb4282-a133-47c8-9850-400362b33ffa" alt="Dashboard" width="500">

### View Journals
You can use the Journals to view detailed logs and sync progress

<img src="https://github.com/user-attachments/assets/1d919a8d-a067-478e-917d-f4bd964c170f" alt="Journals" width="700">

### Main Menu
You can return to the main menu to complete any of the basic functions

<img src="https://github.com/user-attachments/assets/96dd0c79-25b2-4b4c-8fb4-c79ab44a8fb7" alt="Main Menu" width="500">

### Validator Updater
Use Updater to check latest versions and update with a single click

<img src="https://github.com/user-attachments/assets/952c6655-529a-45e5-9c2e-5b0a33c33a95" alt="Updater" width="500">

### Validator Deleter
Deleter can be used to easily remove clients and data

<img src="https://github.com/user-attachments/assets/548bee98-e9ea-40e0-b405-c1e840e2a389" alt="Deleter" width="500">

## Starting ValiDapp
**Note**: You can start ValiDapp anytime by searching "Validapp" in applications or add to favorites in the sidebar

<img src="https://github.com/user-attachments/assets/36e54392-b03a-4d69-bc4e-e120a05d0396" alt="ValiDapp Application" width="300">
<img src="https://github.com/user-attachments/assets/335112b0-acd3-4088-82ca-0440418ecccd" alt="Favorites" width="300">
