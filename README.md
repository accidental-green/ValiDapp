# ValiDapp Installation Guide

## Ethereum Validator Desktop App

<img src="https://github.com/user-attachments/assets/ddaf8dd2-e82b-4f44-88e4-f23ee6ab4f27" alt="Validator Install" width="800" />

## Ubuntu - Single Line Install

To install ValiDapp on Ubuntu, follow these steps:

1. Open a new terminal by pressing `Ctrl + Alt + T`.
2. Copy and paste the following command into the terminal:

**Note:** Use the copy button (right edge of code block) to copy the entire command.

### ValiDapp Installation Command:

```bash
sudo apt update && sudo apt install -y curl && bash <(curl -s https://raw.githubusercontent.com/accidental-green/ValiDapp/main/install.sh)
```

After entering your password, the required packages will be installed, and ValiDapp will open automatically once installation is complete.

## Startup Notes

ValiDapp works with both new and existing validator installations that follow [Somer Esat's Staking Guides](https://github.com/SomerEsat/ethereum-staking-guides) (directories, commands, etc.).

- If clients are already installed, ValiDapp will open the validator dashboard.
- If no  clients are installed, ValiDapp will open to the welcome screen.
- Use the Main Menu to update, delete, import keytstores etc.

## Install New Validator

1. **Validator Installer** - Configure validator settings and click **Install Validator**.

<img src="https://github.com/user-attachments/assets/949afeea-eba7-4cbb-85e7-03ed0231aee0" alt="Validator Install" width="600" />

2. **Keystore Warning** - Only use the keystore import tool for testnet keys.

For mainnet keys, select "Import Keystore? NO" and follow Somer's guides to manually import.

<img src="https://github.com/user-attachments/assets/cc6854ea-6846-4144-aae6-fba20e6f001a" alt="Import Warning" width="600" />

3. **Confirm Installation**- Review your settings and click **Start Installation**.

<img src="https://github.com/user-attachments/assets/ba482f6f-5051-4843-9f02-58d077c79e89" alt="Confirm Install" width="600" />

4. **Import Keystore** - Select the keystore file, enter the password, and click **Import Keystore**.

<img src="https://github.com/user-attachments/assets/04fa895a-7b20-4eb6-aef1-ab3ebbc25ce2" alt="Import Keystore" width="600" />

## Validator Dashboard
Monitor your validator status. Click **Start All** to begin syncing.

<img src="https://github.com/user-attachments/assets/9a73ae45-f6cb-4830-95cd-98764f980990" alt="Dashboard" width="600" />

### View Journals
Access detailed logs and sync progress.

<img src="https://github.com/user-attachments/assets/1d919a8d-a067-478e-917d-f4bd964c170f" alt="Journals" width="600" />

## Main Menu
Navigate back to the main menu for additional functions.

<img src="https://github.com/user-attachments/assets/96dd0c79-25b2-4b4c-8fb4-c79ab44a8fb7" alt="Main Menu" width="600" />

## Validator Updater
Check and update to the latest versions.

 <img src="https://github.com/user-attachments/assets/952c6655-529a-45e5-9c2e-5b0a33c33a95" alt="Updater" width="400" />

## Validator Deleter
Easily remove clients and data.

<img src="https://github.com/user-attachments/assets/548bee98-e9ea-40e0-b405-c1e840e2a389" alt="Deleter" width="400" />

## Starting ValiDapp
Launch ValiDapp by searching for "ValiDapp" in your applications or add it to your favorites for quick access.
<img src="https://github.com/user-attachments/assets/36e54392-b03a-4d69-bc4e-e120a05d0396" alt="ValiDapp Application" width="300" />
<img src="https://github.com/user-attachments/assets/335112b0-acd3-4088-82ca-0440418ecccd" alt="Favorites" width="300" />

## Helpful Resources

Explore additional staking resources for more information.

<img src="https://github.com/user-attachments/assets/97b881bc-d869-4098-b539-bc133cf8c74a" alt="Resources" width="600" />
