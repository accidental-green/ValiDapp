import os
import utils
import install
import sys
import services
import prints

def validate_network(network):
    valid_networks = {'mainnet', 'holesky', 'sepolia'}
    return network.lower() in valid_networks

def validate_client(client):
    valid_clients = {'geth', 'nethermind', 'besu', 'not selected'}
    return client.lower() in valid_clients

def validate_consensus_client(client):
    valid_clients = {'lighthouse', 'prysm', 'nimbus', 'teku', 'not selected'}
    return client.lower() in valid_clients

def validate_mevboost(mev_on_off):
    return mev_on_off.lower() in {'on', 'off', 'not selected'}

def validate_fee_address(fee_address):
    return fee_address.startswith('0x') and len(fee_address) == 42 or fee_address.lower() == 'empty' or fee_address.lower() == ''

def handle_installation(network, ec_install, cc_install, mev_on_off, feeAddress):
    # Validate inputs
    if not validate_network(network):
        print("Invalid network specified.")
        return
    if not validate_client(ec_install):
        print("Invalid execution client specified.")
        return
    if not validate_consensus_client(cc_install):
        print("Invalid consensus client specified.")
        return
    if not validate_mevboost(mev_on_off):
        print("Invalid MEV-Boost setting specified.")
        return
    if not validate_fee_address(feeAddress):
        print("Invalid fee address specified.")
        return

    print("\n\nNetwork: ", network.upper(), "\nExecution: ", ec_install.upper(), "\nConsensus: ", cc_install.upper(), "\nMevboost: ", mev_on_off.upper(), "\nFee Address: ", feeAddress, "\n")
    
    # Run Updates
    print("INSTALLATION - STEP 1: Update System & Configure Firewall\n     Note: System updates may take a while")
    install.run_updates()
    install.install_ufw()
    install.create_jwt()

    # Install Execution Client
    if ec_install.lower() != "not selected":
        print(f"INSTALLATION - STEP 2: Installing Execution Client ({ec_install.upper()})")
        install.install_client(ec_install)
    else:
        print("INSTALLATION - STEP 2: Skipping Execution Client installation.")

    # Install Consensus Client
    if cc_install.lower() != "not selected":
        print(f"INSTALLATION - STEP 3: Installing Consensus Client ({cc_install.upper()})")
        install.install_client(cc_install)
    else:
        print("INSTALLATION - STEP 3: Skipping Consensus Client installation.")

    # Install MEV-Boost if applicable
    if mev_on_off.lower() == "on":
        print("INSTALLATION - STEP 4: Installing MEVboost")
        install.install_mev()
    elif mev_on_off.lower() == "off":
        print("INSTALLATION - STEP 4: Skipping MEVboost installation.")

    # Create Service Files
    print("INSTALLATION - STEP 5: Creating service files")
    if ec_install.lower() != "not selected":
        services.create_execution_service(ec_install, network.lower())
    if cc_install.lower() != "not selected":
        services.create_service_function(cc_install, network.lower(), feeAddress, utils.get_sync_url(network.upper()))
    if mev_on_off.lower() == "on":
        services.create_mevboost_service(network.lower())

    # Print & Version Check
    prints.print_installer(ec_install, cc_install, mev_on_off)

# Main script entry point
if __name__ == "__main__":
    if len(sys.argv) == 6:
        network = sys.argv[1]
        ec_install = sys.argv[2]
        cc_install = sys.argv[3]
        mev_on_off = sys.argv[4]
        feeAddress = sys.argv[5]
        
        handle_installation(network, ec_install, cc_install, mev_on_off, feeAddress)
    else:
        print("Please provide all required parameters.")
