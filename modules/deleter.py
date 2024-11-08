import sys
import subprocess

def execute_command(command):
    """Executes a given command."""
    subprocess.run(command, check=False)

def delete_geth():
    print("\nDeleting Geth...")
    execute_command(['sudo', 'userdel', 'geth'])
    execute_command(['sudo', 'rm', '-rf', '/var/lib/geth'])
    execute_command(['sudo', 'rm', '-f', '/etc/systemd/system/geth.service'])
    execute_command(['sudo', 'rm', '-rf', '/usr/local/bin/geth'])
    print("Successfully Deleted Geth")

def delete_besu():
    print("\nDeleting Besu...")
    execute_command(['sudo', 'userdel', 'besu'])
    execute_command(['sudo', 'rm', '-rf', '/var/lib/besu'])
    execute_command(['sudo', 'rm', '-f', '/etc/systemd/system/besu.service'])
    execute_command(['sudo', 'rm', '-rf', '/usr/local/bin/besu'])
    print("Successfully Deleted Besu")

def delete_nethermind():
    print("\nDeleting Nethermind...")
    execute_command(['sudo', 'userdel', 'nethermind'])
    execute_command(['sudo', 'rm', '-rf', '/var/lib/nethermind'])
    execute_command(['sudo', 'rm', '-f', '/etc/systemd/system/nethermind.service'])
    execute_command(['sudo', 'rm', '-rf', '/usr/local/bin/nethermind'])
    print("Successfully Deleted Nethermind")

def delete_teku():
    print("\nDeleting Teku...")
    execute_command(['sudo', 'userdel', 'teku'])
    execute_command(['sudo', 'rm', '-rf', '/var/lib/teku'])
    execute_command(['sudo', 'rm', '-f', '/etc/systemd/system/teku.service'])
    execute_command(['sudo', 'rm', '-rf', '/usr/local/bin/teku'])
    print("Successfully Deleted Teku")

def delete_nimbus():
    print("\nDeleting Nimbus...")
    execute_command(['sudo', 'userdel', 'nimbus'])
    execute_command(['sudo', 'rm', '-rf', '/var/lib/nimbus'])
    execute_command(['sudo', 'rm', '-f', '/etc/systemd/system/nimbus.service'])
    execute_command(['sudo', 'rm', '-rf', '/usr/local/bin/nimbus_beacon_node'])
    execute_command(['sudo', 'rm', '-rf', '/usr/local/bin/nimbus_validator_client'])
    print("Successfully Deleted Nimbus")

def delete_lighthouse():
    print("\nDeleting Lighthouse...")
    execute_command(['sudo', 'userdel', 'lighthousebeacon'])
    execute_command(['sudo', 'userdel', 'lighthousevalidator'])
    execute_command(['sudo', 'rm', '-rf', '/var/lib/lighthouse'])
    execute_command(['sudo', 'rm', '-f', '/etc/systemd/system/lighthousebeacon.service'])
    execute_command(['sudo', 'rm', '-f', '/etc/systemd/system/lighthousevalidator.service'])
    execute_command(['sudo', 'rm', '-rf', '/usr/local/bin/lighthouse'])
    print("Successfully Deleted Lighthouse")

def delete_prysm():
    print("\nDeleting Prysm...")
    execute_command(['sudo', 'userdel', 'prysmbeacon'])
    execute_command(['sudo', 'userdel', 'prysmvalidator'])
    execute_command(['sudo', 'rm', '-rf', '/var/lib/prysm'])
    execute_command(['sudo', 'rm', '-f', '/etc/systemd/system/prysmbeacon.service'])
    execute_command(['sudo', 'rm', '-f', '/etc/systemd/system/prysmvalidator.service'])
    execute_command(['sudo', 'rm', '-rf', '/usr/local/bin/beacon-chain'])
    execute_command(['sudo', 'rm', '-rf', '/usr/local/bin/validator'])
    print("Successfully Deleted Prysm")

def delete_mevboost():
    print("\nDeleting MEV-Boost...")
    execute_command(['sudo', 'userdel', 'mevboost'])
    execute_command(['sudo', 'rm', '-f', '/etc/systemd/system/mevboost.service'])
    execute_command(['sudo', 'rm', '-rf', '/usr/local/bin/mev-boost'])
    print("Successfully Deleted Mevboost")

def reload_systemd_daemon():
    print("Reloading the systemd daemon...")
    execute_command(['sudo', 'systemctl', 'daemon-reload'])

# Delete Execution Cleint
def delete_execution(execution_client_delete):
    function_name = f"delete_{execution_client_delete}".lower()
    func = globals().get(function_name)
    func()

# Delete Consensus Cleint
def delete_consensus(consensus_client_delete):
    function_name = f"delete_{consensus_client_delete}".lower()
    func = globals().get(function_name)
    func()

def delete_all():
    delete_geth()
    delete_besu()
    delete_nethermind()
    delete_teku()
    delete_nimbus()
    delete_lighthouse()
    delete_prysm()
    delete_mevboost()
    reload_systemd_daemon()

def main():
    if len(sys.argv) != 2:
        print("Usage: python deleter.py [function_name]")
        sys.exit(1)

    function_name = sys.argv[1]
    func = globals().get(function_name)
    if func and callable(func):
        func()
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
