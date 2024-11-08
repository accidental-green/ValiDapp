import os
import subprocess
import utils

def create_and_deploy_service(service_name, service_content):
    temp_file_path = f'/tmp/{service_name}.service'
    service_file_path = f'/etc/systemd/system/{service_name}.service'
    
    with open(temp_file_path, 'w') as file:
        file.write(service_content)
    
    os.system(f'sudo mv {temp_file_path} {service_file_path}')
    os.system('sudo systemctl daemon-reload')

def create_geth_service(eth_network):
    service_content = f'''[Unit]
Description=Geth Execution Client ({eth_network})
After=network.target
Wants=network.target

[Service]
User=geth
Group=geth
Type=simple
Restart=always
RestartSec=5
TimeoutStopSec=600
ExecStart=/usr/local/bin/geth \\
  --{eth_network.lower()} \\
  --datadir /var/lib/geth \\
  --authrpc.jwtsecret /var/lib/jwtsecret/jwt.hex

[Install]
WantedBy=default.target
'''
    create_and_deploy_service('geth', service_content)

def create_besu_service(eth_network):
    service_content = f'''[Unit]
Description=Besu Execution Client ({eth_network})
Wants=network-online.target
After=network-online.target

[Service]
User=besu
Group=besu
Type=simple
Restart=always
RestartSec=5
Environment="JAVA_OPTS=-Xmx5g"
ExecStart=/usr/local/bin/besu/bin/besu \\
  --network={eth_network.lower()} \\
  --sync-mode=SNAP \\
  --data-path=/var/lib/besu \\
  --data-storage-format=BONSAI \\
  --engine-jwt-secret=/var/lib/jwtsecret/jwt.hex

[Install]
WantedBy=multi-user.target
'''
    create_and_deploy_service('besu', service_content)

def create_nethermind_service(eth_network):
    service_content = f'''[Unit]
Description=Nethermind Execution Client ({eth_network})
After=network.target
Wants=network.target

[Service]
User=nethermind
Group=nethermind
Type=simple
Restart=always
RestartSec=5
WorkingDirectory=/var/lib/nethermind
Environment="DOTNET_BUNDLE_EXTRACT_BASE_DIR=/var/lib/nethermind"
ExecStart=/usr/local/bin/nethermind/nethermind \\
  --config {eth_network.lower()} \\
  --datadir /var/lib/nethermind \\
  --Sync.SnapSync true \\
  --JsonRpc.JwtSecretFile /var/lib/jwtsecret/jwt.hex \\
  --Pruning.Mode Hybrid \\
  --Pruning.FullPruningTrigger VolumeFreeSpace \\
  --Pruning.FullPruningThresholdMb 285000

[Install]
WantedBy=default.target
'''
    create_and_deploy_service('nethermind', service_content)

def create_teku_service(eth_network, fee_address, sync_url):
    service_content = f'''[Unit]
Description=Teku Consensus Client ({eth_network})
Wants=network-online.target
After=network-online.target

[Service]
User=teku
Group=teku
Type=simple
Restart=always
RestartSec=5
Environment="JAVA_OPTS=-Xmx5g"
Environment="TEKU_OPTS=-XX:-HeapDumpOnOutOfMemoryError"
ExecStart=/usr/local/bin/teku/bin/teku \\
  --network={eth_network.lower()} \\
  --data-path=/var/lib/teku \\
  --validator-keys=/var/lib/teku/validator_keys:/var/lib/teku/validator_keys \\
  --ee-endpoint=http://127.0.0.1:8551 \\
  --ee-jwt-secret-file=/var/lib/jwtsecret/jwt.hex \\
  --validators-proposer-default-fee-recipient={fee_address}'''

    # Append the --initial-state option only if sync_url is provided
    if sync_url is not None and sync_url.strip():
        service_content += f" \\\n  --initial-state={sync_url}"

    # Continue the rest of the service file content
    service_content += f'''

[Install]
WantedBy=multi-user.target
'''

    create_and_deploy_service('teku', service_content)    

def create_nimbus_service(eth_network, fee_address, sync_url):
    service_content = f'''[Unit]
Description=Nimbus Consensus Client ({eth_network})
Wants=network-online.target
After=network-online.target

[Service]
User=nimbus
Group=nimbus
Type=simple
Restart=always
RestartSec=5
ExecStart=/usr/local/bin/nimbus_beacon_node \\
  --network={eth_network.lower()} \\
  --data-dir=/var/lib/nimbus \\
  --web3-url=http://127.0.0.1:8551 \\
  --jwt-secret=/var/lib/jwtsecret/jwt.hex \\
  --suggested-fee-recipient={fee_address}

[Install]
WantedBy=multi-user.target
'''

    create_and_deploy_service('nimbus', service_content)

    # Run Nimbus Checkpoint Sync
    if sync_url:
        subprocess.run([
            'sudo', '/usr/local/bin/nimbus_beacon_node', 'trustedNodeSync',
            f'--network={eth_network}', '--data-dir=/var/lib/nimbus',
            f'--trusted-node-url={sync_url}', '--backfill=false'
        ])

        # Set ownership for /var/lib/nimbus directory
        subprocess.run(['sudo', 'chown', '-R', 'nimbus:nimbus', '/var/lib/nimbus'])

def create_prysm_service(eth_network, fee_address, sync_url):
    # Prysm Beacon service file content
    common_exec_start_beacon = f'''/usr/local/bin/beacon-chain \\
    --{eth_network.lower()} \\
    --datadir=/var/lib/prysm/beacon \\
    --execution-endpoint=http://127.0.0.1:8551 \\
    --jwt-secret=/var/lib/jwtsecret/jwt.hex \\
    --suggested-fee-recipient={fee_address}'''

    # Conditional parts for beacon service based on sync_url
    sync_exec_part_beacon = f''' \\
    --checkpoint-sync-url={sync_url} \\
    --genesis-beacon-api-url={sync_url}''' if sync_url else ''

    # Full exec start command for beacon
    exec_start_beacon = common_exec_start_beacon + sync_exec_part_beacon + " \\\n    --accept-terms-of-use"

    service_content = f'''[Unit]
Description=Prysm Consensus Client BN ({eth_network})
Wants=network-online.target
After=network-online.target

[Service]
User=prysmbeacon
Group=prysmbeacon
Type=simple
Restart=always
RestartSec=5
ExecStart={exec_start_beacon}

[Install]
WantedBy=multi-user.target
'''

    create_and_deploy_service('prysmbeacon', service_content)

    # Prysm Validator service file content
    service_content = f'''[Unit]
Description=Prysm Consensus Client VC ({eth_network})
Wants=network-online.target
After=network-online.target

[Service]
User=prysmvalidator
Group=prysmvalidator
Type=simple
Restart=always
RestartSec=5
ExecStart=/usr/local/bin/validator \\
    --datadir=/var/lib/prysm/validator \\
    --wallet-dir=/var/lib/prysm/validator \\
    --wallet-password-file=/var/lib/prysm/validator/password.txt \\
    --suggested-fee-recipient={fee_address} \\
    --accept-terms-of-use

[Install]
WantedBy=multi-user.target
'''

    create_and_deploy_service('prysmvalidator', service_content)

def create_lighthouse_service(eth_network, fee_address, sync_url):
    # Start constructing the beacon service file content
    service_content = f'''[Unit]
Description=Lighthouse Consensus Client BN ({eth_network})
Wants=network-online.target
After=network-online.target

[Service]
User=lighthousebeacon
Group=lighthousebeacon
Type=simple
Restart=always
RestartSec=5
ExecStart=/usr/local/bin/lighthouse bn \\
  --network {eth_network.lower()} \\
  --datadir /var/lib/lighthouse \\
  --http \\
  --execution-endpoint http://127.0.0.1:8551 \\
  --execution-jwt /var/lib/jwtsecret/jwt.hex'''

    # Append the checkpoint sync URL conditionally
    if sync_url:
        service_content += f''' \\
  --checkpoint-sync-url {sync_url}'''

    # Finish the beacon service file content
    service_content += f'''

[Install]
WantedBy=multi-user.target
'''

    create_and_deploy_service('lighthousebeacon', service_content)

    # The validator service file content
    service_content = f'''[Unit]
Description=Lighthouse Consensus Client VC ({eth_network})
Wants=network-online.target
After=network-online.target

[Service]
User=lighthousevalidator
Group=lighthousevalidator
Type=simple
Restart=always
RestartSec=5
ExecStart=/usr/local/bin/lighthouse vc \\
  --network {eth_network.lower()} \\
  --datadir /var/lib/lighthouse \\
  --suggested-fee-recipient {fee_address}

[Install]
WantedBy=multi-user.target
'''

    create_and_deploy_service('lighthousevalidator', service_content)

def set_mev_relays(eth_network):
    if eth_network.lower() == 'mainnet':
        return utils.MEV_RELAYS_MAINNET
    elif eth_network.lower() == 'sepolia':
        return utils.MEV_RELAYS_SEPOLIA
    elif eth_network.lower() == 'holesky':
        return utils.MEV_RELAYS_HOLESKY
    else:
        return []

def create_mevboost_service(eth_network):
    # Capture the return value of set_mev_relays
    relays = set_mev_relays(eth_network)
    
    service_content = [
        '[Unit]',
        f'Description=MEV-Boost {eth_network.capitalize()}',
        'Wants=network-online.target',
        'After=network-online.target',
        '',
        '[Service]',
        'User=mevboost',
        'Group=mevboost',
        'Type=simple',
        'Restart=always',
        'RestartSec=5',
        f'ExecStart=/usr/local/bin/mev-boost -{eth_network.lower()} \\',
        '    -min-bid 0.05 \\',
        '    -relay-check \\',
    ]

    # Add relay lines
    for _, url in relays:
        service_content.append(f'    -relay {url} \\')

    if relays:
        # Correctly remove the trailing '\\' from the last relay line
        service_content[-1] = service_content[-1].rstrip(' \\')

    service_content.extend([
        '',
        '[Install]',
        'WantedBy=multi-user.target',
    ])

    service_content = '\n'.join(service_content)

    create_and_deploy_service('mevboost', service_content)


# Create Execution or MEV Service
def create_execution_service(client, eth_network):
    function_name = f"create_{client}_service".lower()
    func = globals().get(function_name)
    func(eth_network)

# Create Consensus Service File Function
def create_service_function(client, eth_network, fee_address, sync_url):
    function_name = f"create_{client}_service".lower()
    func = globals().get(function_name)
    func(eth_network, fee_address, sync_url)