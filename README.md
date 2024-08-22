# ValiDapp Installation
## Install Command
Open a new terminal (ctrl + alt + T) and enter the following command:

```bash
sudo apt update && sudo apt install libfuse2 -y && wget https://github.com/accidental-green/ValiDapp/releases/download/v1.0.0-alpha/ValiDapp-1.0.0.AppImage && chmod +x ValiDapp-1.0.0.AppImage && sudo mv ValiDapp-1.0.0.AppImage /usr/bin/validapp && validapp
```

## Summary
ValiDapp is a user-friendly desktop interface for Ethereum Home Validators:

- **Multi-Client Support**: Besu, Geth, Nethermind, Lighthouse, Nimbus, Prysm, Teku, and Mevboost.
- **Validator Dashboard**: Monitor validator performance and easily start/stop operations.
- **Validator Installer**: Install new Validator and import validator keystores.
- **Validator Updater**: Checks for the latest versions and updates validators with a single click.
- **Validator Deleter**: Provides an option to remove or uninstall validator clients.
- **Standard Compatibility**: Works with existing Validator installations (Ubuntu / Somer's Guides).
