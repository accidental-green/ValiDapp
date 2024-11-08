import requests
import json

# LATEST VERSIONS ON GITHUB
def check_latest_versions():
    latest_versions = []
    urls = {
        "Geth": "https://api.github.com/repos/ethereum/go-ethereum/releases/latest",
        "Besu": "https://api.github.com/repos/hyperledger/besu/releases/latest",
        "Nethermind": 'https://api.github.com/repos/NethermindEth/nethermind/releases/latest',
        "Teku": 'https://api.github.com/repos/ConsenSys/teku/releases/latest',
        "Prysm": "https://api.github.com/repos/prysmaticlabs/prysm/releases/latest",
        "Nimbus": 'https://api.github.com/repos/status-im/nimbus-eth2/releases/latest',
        "Lighthouse": 'https://api.github.com/repos/sigp/lighthouse/releases/latest',
        "Mevboost": 'https://api.github.com/repos/flashbots/mev-boost/releases/latest'
    }

    for client, url in urls.items():
        response = requests.get(url)
        data = response.json()
        version = data.get('tag_name', 'Unavailable')

        # Prepend 'v' if it's not already at the start of the version string and the version is available
        if not version.startswith('v') and version != 'Unavailable':
            version = 'v' + version

        # Append a dictionary to the list
        latest_versions.append({client: version})

    # Serialize the list of dictionaries to JSON and print it with a unique identifier
    print(f'JSON_LATEST: {json.dumps(latest_versions)}')

# Ensure this function is called when the script is executed directly
if __name__ == "__main__":
    check_latest_versions()
