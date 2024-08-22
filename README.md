# ValiDapp Installation
## Install Command
Open a new terminal (ctrl + alt + T) and enter the following command:

```bash
sudo apt update && sudo apt install libfuse2 -y && wget https://github.com/accidental-green/ValiDapp/releases/download/v1.0.0-alpha/ValiDapp-1.0.0.AppImage && chmod +x ValiDapp-1.0.0.AppImage && sudo mv ValiDapp-1.0.0.AppImage /usr/bin/validapp && validapp
```
Enter your password let installation run. If you don't have any Eth clients installed, the following screen should appear:

## Validator Installer
Choose validator settings and click **Install Validator**<br>

<img src="https://github.com/user-attachments/assets/e7d885d4-e8ca-4ef9-8642-299fc4a8b74f" alt="Validator Install" width="800">


## Keystore Warning
ValiDapp has not been audited, and the keystore import tool should be used with caution.<br>
To safely import keystores, choose "Import Keystore? **NO**" and manually import the keystore using Somer's guides.

<img src="https://github.com/user-attachments/assets/cc6854ea-6846-4144-aae6-fba20e6f001a" alt="Import Warning" width="600">

## Confirm Installation
Review the information and click Confirm to begin installation.

<img src="https://github.com/user-attachments/assets/ba482f6f-5051-4843-9f02-58d077c79e89" alt="Confirm Install" width="400">

## Summary
ValiDapp is a user-friendly desktop interface for Ethereum Home Validators:

- **Multi-Client Support**: Besu, Geth, Nethermind, Lighthouse, Nimbus, Prysm, Teku, and Mevboost.
- **Validator Dashboard**: Monitor validator performance and easily start/stop operations.
- **Validator Installer**: Install new Validator and import validator keystores.
- **Validator Updater**: Checks for the latest versions and updates validators with a single click.
- **Validator Deleter**: Provides an option to remove or uninstall validator clients.
- **Standard Compatibility**: Works with existing Validator installations (Ubuntu / Somer's Guides).
