import subprocess
import re
import json

def geth_print():
    try:
        geth_version_output = subprocess.run(["geth", "--version"], stdout=subprocess.PIPE).stdout
        if geth_version_output:
            geth_version = geth_version_output.decode().split(" ")[2].split("-")[0].strip()
            print(f'Geth Version: v{geth_version}')
            return f'v{geth_version}'
        else:
            print('Error: Unable to determine Geth version')
            return None
    except Exception as e:
        print(f'Error checking Geth version: {e}')
        return None

def besu_print():
    try:
        besu_version = subprocess.run(["sudo", "/usr/local/bin/besu/bin/besu", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if besu_version.stdout:
            version = besu_version.stdout.strip().split('/')[1].split('/')[0]
            print(f'Besu Version: {version}')
            return version
        else:
            print('Besu Version: Unable to determine version\n')
    except Exception as e:
        print(f'Error checking Besu version: {e}\n')
    return None

def nethermind_print():
    try:
        nethermind_version = subprocess.run(["sudo", "/usr/local/bin/nethermind/nethermind", "-v"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        version_match = re.search(r'Version:\s*(\S+)', nethermind_version.stdout)
        if version_match:
            version = version_match.group(1).split('+')[0]
            print(f'Nethermind Version: v{version}')
            return f'v{version}'
        else:
            print('Nethermind Version: Unable to determine version\n')
    except Exception as e:
        print(f'Error checking Nethermind version: {e}\n')
    return None

def teku_print():
    try:
        teku_version = subprocess.run(["sudo", "/usr/local/bin/teku/bin/teku", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if teku_version.stdout:
            version = teku_version.stdout.strip().split('/')[1].split('-')[0]
            print(f'Teku Version: {version}')
            return version
        else:
            print('Teku Version: Unable to determine version\n')
    except Exception as e:
        print(f'Error checking Teku version: {e}\n')
    return None

def prysm_print():
    try:
        prysm_version = subprocess.run(["beacon-chain", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if prysm_version.stdout:
            version_info = prysm_version.stdout.strip().splitlines()[0]
            version = version_info.split("/")[-2] if len(version_info.split("/")) > 1 else "Unknown format"
            print(f'Prysm Version: {version}')
            return version
        else:
            print('Prysm Version: Unable to determine version\n')
    except Exception as e:
        print(f'Error checking Prysm version: {e}\n')
    return None

def nimbus_print():
    try:
        nimbus_version = subprocess.run(["nimbus_beacon_node", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if nimbus_version.stdout:
            version_info = nimbus_version.stdout.strip().split()
            version = version_info[3].split('-')[0] if len(version_info) > 3 else "Unknown format"
            print(f'Nimbus Version: {version}')
            return version
        else:
            print('Nimbus Version: Unable to determine version\n')
    except Exception as e:
        print(f'Error checking Nimbus version: {e}\n')
    return None

def lighthouse_print():
    try:
        lighthouse_version = subprocess.run(["lighthouse", "-V"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if lighthouse_version.stdout:
            version_info = lighthouse_version.stdout.strip().split()
            full_version = version_info[-1] if version_info else "Unknown format"
            version = full_version.split('-')[0]
            print(f'Lighthouse Version: {version}')
            return version
        else:
            print('Lighthouse Version: Unable to determine version\n')
    except Exception as e:
        print(f'Error checking Lighthouse version: {e}\n')
    return None

def mevboost_print():
    try:
        # Run the mev-boost version command
        mevboost_version = subprocess.run(
            ["/usr/local/bin/mev-boost", "-version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )

        # Combine stdout and stderr and clean up the output
        output = (mevboost_version.stdout + mevboost_version.stderr).strip()
        
        if output:
            # Clean up the output by removing newlines and quotes
            version = output.split()[-1].replace('\n', '').replace('\\n', '').replace('"', '')
            print(f"Mevboost Version: {version}")
            return version
        else:
            print('Mevboost Version: Unable to determine version\n')
    except Exception as e:
        print(f'Error checking Mevboost version: {e}\n')
    return None


def print_output(execution_client, consensus_client, mev_on_off):
    print("\n########## CLIENT VERSIONS ##########\n")
    if execution_client == 'geth':
        geth_print()
    elif execution_client == 'besu':
        besu_print()
    elif execution_client == 'nethermind':
        nethermind_print()

    if consensus_client == 'teku':
        teku_print()
    elif consensus_client == 'prysm':
        prysm_print()
    elif consensus_client == 'nimbus':
        nimbus_print()
    elif consensus_client == 'lighthouse':
        lighthouse_print()

    if mev_on_off == "on":
        mevboost_print()
    
def print_version(client):
    function_name = f"{client}_print".lower()
    func = globals().get(function_name)
    func()

def print_installer(ec_install, cc_install, mev_on_off):
    print("\n########## INSTALLATION COMPLETE ##########\n")
    if ec_install != "Not Selected":
        print_version(ec_install)
    if cc_install != "Not Selected":   
        print_version(cc_install)
    if mev_on_off == "on":
        print_version("mevboost")

def print_updater(ec_update, cc_update, mev_on_off):
    print("\n####### UPDATED CLIENT VERSIONS #######\n")
    if ec_update != 'empty':
        print_version(ec_update)
    if cc_update != 'empty':
        print_version(cc_update)

    if mev_on_off == "on":
        print_version("mevboost")

def print_check_all():
    installed_clients = []
    client_names = []
    # Assuming all *_print() functions return version strings or None
    clients = {
        'Geth': geth_print(),
        'Besu': besu_print(),
        'Nethermind': nethermind_print(),
        'Teku': teku_print(),
        'Prysm': prysm_print(),
        'Nimbus': nimbus_print(),
        'Lighthouse': lighthouse_print(),
        'Mevboost': mevboost_print(),
    }

    for client, version in clients.items():
        if version:
            # Append a dictionary for each client with a version
            installed_clients.append({client: version})
            client_names.append(client)

    # Serialize the list of dictionaries to JSON and print it with a unique identifier for easy parsing
    print(f'JSON_INSTALLED: {json.dumps(installed_clients)}')
    print(f'JSON_CLIENTS: {json.dumps(client_names)}')

# Ensure this function is called when the script is executed directly
if __name__ == "__main__":
    print_check_all()