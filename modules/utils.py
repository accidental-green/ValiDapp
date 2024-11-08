import os
import sys
import re
import subprocess
import pwd
import random
import keystores

# Constants for valid networks
VALID_NETWORKS = ['MAINNET', 'HOLESKY', 'SEPOLIA']

# Constants for execution and consensus clients
VALID_EXECUTION_CLIENTS = ['GETH', 'BESU', 'NETHERMIND']
VALID_CONSENSUS_CLIENTS = ['LIGHTHOUSE', 'TEKU', 'PRYSM', 'NIMBUS']

# Constants for mevboost relays
MEV_RELAYS_MAINNET = [
    ("Aestus", "https://0xa15b52576bcbf1072f4a011c0f99f9fb6c66f3e1ff321f11f461d15e31b1cb359caa092c71bbded0bae5b5ea401aab7e@aestus.live"),
    ("Agnostic Gnosis", "https://0xa7ab7a996c8584251c8f925da3170bdfd6ebc75d50f5ddc4050a6fdc77f2a3b5fce2cc750d0865e05d7228af97d69561@agnostic-relay.net"),
    ("bloXroute Max Profit", "https://0x8b5d2e73e2a3a55c6c87b8b6eb92e0149a125c852751db1422fa951e42a09b82c142c3ea98d0d9930b056a3bc9896b8f@bloxroute.max-profit.blxrbdn.com"),
    ("bloXroute Regulated", "https://0xb0b07cd0abef743db4260b0ed50619cf6ad4d82064cb4fbec9d3ec530f7c5e6793d9f286c4e082c0244ffb9f2658fe88@bloxroute.regulated.blxrbdn.com"),
    ("Eden Network", "https://0xb3ee7afcf27f1f1259ac1787876318c6584ee353097a50ed84f51a1f21a323b3736f271a895c7ce918c038e4265918be@relay.edennetwork.io"),
    ("Flashbots", "https://0xac6e77dfe25ecd6110b8e780608cce0dab71fdd5ebea22a16c0205200f2f8e2e3ad3b71d3499c54ad14d6c21b41a37ae@boost-relay.flashbots.net"),
    ("Manifold", "https://0x98650451ba02064f7b000f5768cf0cf4d4e492317d82871bdc87ef841a0743f69f0f1eea11168503240ac35d101c9135@mainnet-relay.securerpc.com"),
    ("Ultra Sound", "https://0xa1559ace749633b997cb3fdacffb890aeebdb0f5a3b6aaa7eeeaf1a38af0a8fe88b9e4b1f61f236d2e64d95733327a62@relay.ultrasound.money"),
]

MEV_RELAYS_SEPOLIA = [
    ("Flashbots", "https://0x845bd072b7cd566f02faeb0a4033ce9399e42839ced64e8b2adcfc859ed1e8e1a5a293336a49feac6d9a5edb779be53a@boost-relay-sepolia.flashbots.net"),
]

MEV_RELAYS_HOLESKY = [
    ("Flashbots", "https://0xafa4c6985aa049fb79dd37010438cfebeb0f2bd42b115b89dd678dab0670c1de38da0c4e9138c9290a398ecd9a0b3110@boost-relay-holesky.flashbots.net"),
    ("Titan", "https://0xaa58208899c6105603b74396734a6263cc7d947f444f396a90f7b7d3e65d102aec7e5e5291b27e08d02c50a050825c2f@holesky.titanrelay.xyz"),
]

# Constants for sync URLs by network
SYNC_URLS_MAINNET = [
    ("Stakely", "https://mainnet-checkpoint-sync.stakely.io"),
    ("EthStaker", "https://beaconstate.ethstaker.cc"),
    ("Nimbus", "http://testing.mainnet.beacon-api.nimbus.team/"),
    ("beaconcha.in", "https://sync-mainnet.beaconcha.in"),
    ("Sigma Prime", "https://mainnet.checkpoint.sigp.io"),
    ("Lodestar (ChainSafe)", "https://beaconstate-mainnet.chainsafe.io"),
    ("BeaconState.info", "https://beaconstate.info"),
    ("invis.tools", "https://sync.invis.tools"),
    ("Attestant", "https://mainnet-checkpoint-sync.attestant.io"),
    ("PietjePuk", "https://checkpointz.pietjepuk.net"),
]

SYNC_URLS_HOLESKY = [
    ("EF DevOps", "https://checkpoint-sync.holesky.ethpandaops.io"),
    ("EthStaker", "https://holesky.beaconstate.ethstaker.cc/"),
    ("BeaconState.info", "https://holesky.beaconstate.info"),
    ("Lodestar (ChainSafe)", "https://beaconstate-holesky.chainsafe.io"),
    ("Stakely", "https://holesky-checkpoint-sync.stakely.io"),
]

SYNC_URLS_SEPOLIA = [
    ("Lodestar (ChainSafe)", "https://beaconstate-sepolia.chainsafe.io"),
    ("BeaconState.info", "https://sepolia.beaconstate.info"),
    ("EF DevOps", "https://checkpoint-sync.sepolia.ethpandaops.io"),
]

def check_sudo_privileges():
    print("Checking sudo privileges")
    try:
        subprocess.run(['sudo', '-v'], check=True)
        print("Sudo credentials authenticated.")
    except subprocess.CalledProcessError:
        print("Failed to verify sudo credentials.")
        exit(1)

def user_exists(username):
    """Check if a user exists."""
    try:
        pwd.getpwnam(username)
        return True
    except KeyError:
        return False

# Check if network is Valid
def is_valid_network(eth_network):
    return eth_network in VALID_NETWORKS

# Prompt for Network Choice
def prompt_for_network():
    while True:
        eth_network = input(f"\nSelect Ethereum network to use ({VALID_NETWORKS}): ").upper()
        if is_valid_network(eth_network):
            print(f"Ethereum network: {eth_network}")
            return eth_network
        else:
            print("Invalid network. Please try again.")

# Check if Execution Client is Valid
def is_valid_execution_client(execution_client):
    return execution_client in VALID_EXECUTION_CLIENTS

# Prompt user for Execution Client to Delete
def prompt_for_execution_client_delete():
    while True:
        execution_client_delete = input(f"\nSelect Execution Client to DELETE ({VALID_EXECUTION_CLIENTS}): ").upper()
        if is_valid_execution_client(execution_client_delete):
            print(f"Execution client selected for deletion: {execution_client_delete}")
            return execution_client_delete
        else:
            print("Invalid client. Please try again.")

# Prompt user for Execution Client Install
def prompt_for_execution_client_install():
    while True:
        execution_client_install = input(f"\nSelect Execution client to INSTALL ({VALID_EXECUTION_CLIENTS}): ").upper()
        if is_valid_execution_client(execution_client_install):
            print(f"Execution client selected for installation: {execution_client_install}")
            return execution_client_install
        else:
            print("Invalid client. Please try again.")

# Prompt user for Execution Client Update
def prompt_for_execution_client_update():
    while True:
        execution_client_update = input(f"\nSelect Execution client to UPDATE ({VALID_EXECUTION_CLIENTS}): ").upper()
        if is_valid_execution_client(execution_client_update):
            print(f"Execution client selected to update: {execution_client_update}")
            return execution_client_update
        else:
            print("Invalid client. Please try again.")

# Check if Consensus Client is Valid
def is_valid_consensus_client(consensus_client):
    return consensus_client in VALID_CONSENSUS_CLIENTS

# Prompt User for Consensus Client Install
def prompt_for_consensus_client_install():
    while True:
        consensus_client_install = input(f"\nSelect Consensus client to install ({VALID_CONSENSUS_CLIENTS}): ").upper()
        if is_valid_consensus_client(consensus_client_install):
            print(f"Consensus client selected for installation: {consensus_client_install}")
            return consensus_client_install
        else:
            print("Invalid client. Please try again.")

# Prompt User for Consensus Client for Import
def prompt_for_cc_import():
    while True:
        consensus_client_import = input(f"\nSelect Consensus client to import keystore ({VALID_CONSENSUS_CLIENTS}): ").upper()
        if is_valid_consensus_client(consensus_client_import):
            print(f"Consensus client selected: {consensus_client_import}\n")
            return consensus_client_import
        else:
            print("Invalid client. Please try again.")  

# Prompt User for Keystore Import
def prompt_for_keystore():
    temp_keystore_dir = f'{os.environ["HOME"]}/validator_keys'
    while True:    
        print(f"\n######### Keystore Import ###########\n\nIf you would like to import keystores, the keys must be located at:\n{temp_keystore_dir}")
        
        json_files_in_source = keystores.list_temp_jsons()
        keys_yes_no = input("\nWould you like to import validator keys? (yes/no): ").strip().lower()
        if keys_yes_no == "no":
            print("Skip keystore import")
            return keys_yes_no
        elif keys_yes_no == "yes" and json_files_in_source == []:
            print(f"No keystores found, exiting installation. Please be sure they are located at:\n{temp_keystore_dir}\n\nNote: The keystore must be in a folder called validator_keys in your home folder")
            sys.exit()
        elif keys_yes_no == "yes" and len(json_files_in_source) > 0:
            print(f"\nThe following keystores were found for import:\n{json_files_in_source}")
            return keys_yes_no
        else:
            print('Invalid selection. Please try again.')

# Prompt User for Consensus Client Update
def prompt_for_consensus_client_update():
    while True:
        consensus_client_update = input(f"\nSelect Consensus client to update ({VALID_CONSENSUS_CLIENTS}): ").upper()
        if is_valid_consensus_client(consensus_client_update):
            print(f"Consensus client selected to update: {consensus_client_update}")
            return consensus_client_update
        else:
            print("Invalid client. Please try again.")

# Prompt User for Consensus Client Deletion
def prompt_for_consensus_client_deletion():
    while True:
        consensus_client_delete = input(f"\nSelect Consensus client to delete ({VALID_CONSENSUS_CLIENTS}): ").upper()
        if is_valid_consensus_client(consensus_client_delete):
            print(f"Consensus client selected for deletion: {consensus_client_delete}")
            return consensus_client_delete
        else:
            print("Invalid client. Please try again.")

# Check if Eth Address is valid
def is_valid_eth_address(address):
    """Check if the specified address is a valid Ethereum address."""
    pattern = re.compile("^0x[a-fA-F0-9]{40}$")
    return bool(pattern.match(address))

# Prompt user for Validator Fee Address
def prompt_for_validator_fee_address():
    while True:
        fee_address = input("\n--- Enter Ethereum address to receive Validator fees / tips --- \n\nNote: Type 'skip' to set address later\n\n4) Enter Validator fee recipient address: ")
        if fee_address.lower() == "skip":
            print("Skipping Ethereum address input. You can set it later.")
            return "EMPTY"
        elif is_valid_eth_address(fee_address):
            print("Valid Ethereum address.")
            return fee_address
        else:
            print("Invalid Ethereum address. Please try again.")

# Get Checkpoint Sync URL based on Network Choice
def get_sync_url(eth_network):
    if eth_network == 'MAINNET':
        return random.choice(SYNC_URLS_MAINNET)[1]
    elif eth_network == 'HOLESKY':
        return random.choice(SYNC_URLS_HOLESKY)[1]
    elif eth_network == 'SEPOLIA':
        return random.choice(SYNC_URLS_SEPOLIA)[1]
    else:
        # If the network is not recognized, raise a ValueError
        raise ValueError(f"Network '{eth_network}' is not recognized.")

# Prompt User for Checkpoint Sync URL (yes/no)
def prompt_checkpoint_sync_url(eth_network):
    user_choice = input("\nWould you like to enable Checkpoint Sync? (yes/no): ").lower()
    if user_choice == 'yes':
        # Retrieve the sync URLs for the provided network
        sync_urls = get_sync_url(eth_network)
        if not sync_urls:
            print("No sync URLs available for the selected network.")
            return None
        print(f"Selected CheckpointSyncURL: {sync_urls}")
        return sync_urls
    elif user_choice == 'no':
        return None
    else:
        print("Invalid choice. Please try again.")
        return prompt_checkpoint_sync_url(eth_network)

# Prompt User for Mevboost (on/off)
def prompt_mev_boost():
    print("\n-----------------------------\n------- MEV INSTALLATION -------\n")
    user_choice = input("Would you like to install MEV-Boost? (yes/no): ")
    if user_choice.lower() == 'yes':
        print("MEV-Boost: On")
        return "on"
    elif user_choice.lower() == 'no':
        print("MEV-Boost: Not Installed")
        return "off"
    else:
        print("Invalid choice. Please try again.")
        return prompt_mev_boost()
    
# Prompt User for Mevboost Update
def prompt_mevboost_update():
    user_choice = input("\nWould you like to update MEV-Boost? (yes/no): ")
    if user_choice.lower() == 'yes':
        print("MEV-Boost: On")
        return "on"
    elif user_choice.lower() == 'no':
        print("MEV-Boost: Not Updated")
        return "off"
    else:
        print("Invalid choice. Please try again.")
        return prompt_mevboost_update()

def confirm_switcher(execution_client_delete, execution_client_install):    
    confirm_yes_no = input(f"\nPlease confirm to DELETE {execution_client_delete} and INSTALL {execution_client_install} (yes/no): ").upper()

    if confirm_yes_no == "NO":
        print("Operation canceled by the user.")
        sys.exit()

def confirm_updater(ec_update, cc_update, mev_on_off):    
    if mev_on_off == "off":
        confirm_yes_no = input(f"\nPlease confirm to update {ec_update} and {cc_update} (yes/no): ").upper()
    else:
        confirm_yes_no = input(f"\nPlease confirm to update {ec_update}, {cc_update}, and MEV (yes/no): ").upper()

    if confirm_yes_no == "NO":
        print("Operation canceled by the user.")
        sys.exit()

def confirm_installer(eth_network, ec_install, cc_install, mev_on_off, fee_address):    
    confirm_yes_no = input(f"""\nPlease confirm the following installation details:\n    
    Ethereum Network: {eth_network}\n
    Execution Install: {ec_install}\n
    Consensus Install: {cc_install}\n
    MEV (On/Off): {mev_on_off.upper()}\n
    Ethereum Fee Address: {fee_address}
    
Would you like to continue with the installation? (yes/no): """).upper()

    if confirm_yes_no == "NO":
        print("Operation canceled by the user.")
        sys.exit()

