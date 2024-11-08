import subprocess
import sys

def stop_service(service_name):
    # Validate the service name before attempting to stop it
    if not validate_service_name(service_name):
        print(f"Invalid service name provided: {service_name}")
        return
    print(f"Stopping {service_name} service")
    subprocess.run(['sudo', 'systemctl', 'stop', service_name], check=True)

def validate_service_name(service_name):
    valid_services = {
        'geth', 'nethermind', 'besu', 
        'teku', 'lighthousebeacon', 'lighthousevalidator', 
        'prysmbeacon', 'prysmvalidator', 'nimbus', 'mevboost'
    }
    return service_name.lower() in valid_services

def stop_services(execution_client, consensus_client, validator_client, mevboost_on_off):
    print("\n########### STOPPING SERVICES ###############\n")

    # Normalize names for Lighthouse and Prysm services
    if consensus_client.lower() == "lighthouse":
        consensus_client = 'lighthousebeacon'
        validator_client = 'lighthousevalidator'
    elif consensus_client.lower() == "prysm":
        consensus_client = 'prysmbeacon'
        validator_client = 'prysmvalidator'

    # Stop execution client service if not "none" or "empty"
    if execution_client.lower() not in ["none", "empty"]:
        stop_service(execution_client.lower())

    # Stop consensus client service if not "none" or "empty"
    if consensus_client.lower() not in ["none", "empty"]:
        stop_service(consensus_client.lower())

    # Stop validator client service if not "none" or "empty" and if different from consensus
    if validator_client.lower() not in ["none", "empty"] and validator_client.lower() != consensus_client.lower():
        stop_service(validator_client.lower())

    # Stop MEV-Boost if requested
    if mevboost_on_off.lower() == "on":
        stop_service('mevboost')

def main():
    if len(sys.argv) != 5:
        print("Usage: python stop.py <execution_client> <consensus_client> <validator_client> <mevboost_on_off>")
        sys.exit(1)

    execution_client = sys.argv[1]
    consensus_client = sys.argv[2]
    validator_client = sys.argv[3]
    mevboost_on_off = sys.argv[4]

    stop_services(execution_client, consensus_client, validator_client, mevboost_on_off)

if __name__ == "__main__":
    main()
