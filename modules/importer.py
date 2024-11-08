import sys
import os
from keystores import teku_keystore_import, nimbus_keystore_import, prysm_keystore_import, lighthouse_keystore_import

def validate_network(network):
    valid_networks = {'mainnet', 'holesky', 'sepolia'}
    return network.lower() in valid_networks

def validate_consensus(consensus):
    valid_consensuses = {'teku', 'nimbus', 'prysm', 'lighthouse'}
    return consensus.lower() in valid_consensuses

print("Starting Keystore Import")

def main():
    if len(sys.argv) == 4:
        network = sys.argv[1]
        consensus = sys.argv[2]
        keystorePath = sys.argv[3]

        # Validate network and consensus
        if not validate_network(network):
            print(f"Invalid network specified: {network}. Valid options are: mainnet, holesky, sepolia.")
            return

        if not validate_consensus(consensus):
            print(f"Invalid consensus client specified: {consensus}. Valid options are: teku, nimbus, prysm, lighthouse.")
            return

        # Import keystore based on the chosen client
        if consensus == "teku":
            teku_keystore_import(network, keystorePath)
        elif consensus == "nimbus":
            nimbus_keystore_import(network, keystorePath)
        elif consensus == "prysm":
            prysm_keystore_import(network, keystorePath)
        elif consensus == "lighthouse":
            lighthouse_keystore_import(network, keystorePath)
    else:
        print("Invalid arguments! Please provide all required parameters: network, consensus, and keystorePath.")

if __name__ == "__main__":
    main()
