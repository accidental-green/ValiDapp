import re
import tarfile
import shutil
import os
import subprocess
import requests
import urllib.request
import json
import tempfile
import zipfile
import tarfile
from html.parser import HTMLParser

# CREATE JWT FILE
def create_jwt():
    # Create JWT directory
    subprocess.run(['sudo', 'mkdir', '-p', '/var/lib/jwtsecret'])

    # Generate random hex string and save to file
    rand_hex = subprocess.run(['openssl', 'rand', '-hex', '32'], stdout=subprocess.PIPE)
    subprocess.run(['sudo', 'tee', '/var/lib/jwtsecret/jwt.hex'], input=rand_hex.stdout, stdout=subprocess.DEVNULL)

# RUN UPDATES
def run_updates():
    # Change to home dir
    os.chdir(os.path.expanduser('~'))

    # Update and upgrade packages
    subprocess.run(['sudo', 'apt', '-y', 'update'])
    subprocess.run(['sudo', 'apt', '-y', 'upgrade'])

# INSTALL AND CONFIGURE FIREWALL
def install_ufw():
    """Installs UFW, configures it, and enables it."""
    subprocess.run(['sudo', 'apt-get', 'update'])
    subprocess.run(['sudo', 'apt-get', 'install', 'ufw', '-y'])
    subprocess.run(['sudo', 'ufw', 'default', 'deny', 'incoming'])
    subprocess.run(['sudo', 'ufw', 'default', 'allow', 'outgoing'])
    subprocess.run(['sudo', 'ufw', 'allow', '6673/tcp'])
    subprocess.run(['sudo', 'ufw', 'allow', '30303'])
    subprocess.run(['sudo', 'ufw', 'allow', '9000'])
    subprocess.run(['sudo', 'ufw', '--force', 'enable'])
    subprocess.run(['sudo', 'ufw', 'status', 'numbered'])

# INSTALL MEV
class GoReleaseLinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.linux_links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr in attrs:
                if attr[0] == 'href' and 'linux-amd64' in attr[1]:
                    self.linux_links.append(attr[1])
                    break

def get_latest_go_linux_release():
    try:
        response = requests.get("https://go.dev/dl/")
        response.raise_for_status()
        parser = GoReleaseLinkParser()
        parser.feed(response.text)
        if parser.linux_links:
            return "https://go.dev" + parser.linux_links[0]
        else:
            raise Exception("No 64-bit Linux release found")
    except requests.RequestException as e:
        raise Exception("Failed to load the Go downloads page") from e

def install_go(go_url):
    subprocess.run(["sudo", "apt", "-y", "install", "build-essential"], check=True)
    subprocess.run(["wget", "-O", "go.tar.gz", go_url], check=True)
    subprocess.run(["sudo", "rm", "-rf", "/usr/local/go"], check=True)
    subprocess.run(["sudo", "tar", "-C", "/usr/local", "-xzf", "go.tar.gz"], check=True)
    os.remove("go.tar.gz")
    os.environ["PATH"] += os.pathsep + "/usr/local/go/bin"
    with open(os.path.expanduser("~/.bashrc"), 'a') as bashrc:
        bashrc.write('\nexport PATH=$PATH:/usr/local/go/bin\n')

def get_latest_mev_boost_version():
    response = requests.get("https://api.github.com/repos/flashbots/mev-boost/releases/latest")
    response.raise_for_status()
    latest_release = response.json()
    return latest_release['tag_name']

def install_mev_commands():
    # Attempt to create the mevboost user; ignore errors if the user already exists
    try:
        subprocess.run(['sudo', 'useradd', '--no-create-home', '--shell', '/bin/false', 'mevboost'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"User 'mevboost' already exists or couldn't be created: {e}")
    
    # Get the latest MEV-Boost version
    latest_version = get_latest_mev_boost_version()

    # Define the Go install command for MEV-Boost
    install_command = 'CGO_CFLAGS="-O -D__BLST_PORTABLE__" go install github.com/flashbots/mev-boost/cmd/mev-boost@latest'
    
    # Try to install MEV-Boost
    try:
        subprocess.run(install_command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error installing mev-boost: {e}")
        return

    # Define the path to the MEV-Boost binary
    mev_boost_path = os.path.join(os.path.expanduser("~"), "go/bin/mev-boost")

    # Copy the MEV-Boost binary to /usr/local/bin and set ownership
    try:
        subprocess.run(["sudo", "cp", mev_boost_path, "/usr/local/bin"], check=True)
        subprocess.run(["sudo", "chown", "mevboost:mevboost", "/usr/local/bin/mev-boost"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error moving and setting ownership of mev-boost binary: {e}")

def install_mev():
    try:
        subprocess.run(["which", "go"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Go is already installed.")
    except subprocess.CalledProcessError:
        print("Go not found. Installing...")
        go_url = get_latest_go_linux_release()
        install_go(go_url)
    
    os.environ["PATH"] += os.pathsep + "/usr/local/go/bin"
    install_mev_commands()

def update_mev():
    print("Starting MEV-Boost update...")
    install_mev()
    print("MEV-Boost update complete.")

# INSTALL GETH
def create_geth_user_and_directories():
    """Create user and directories for Geth."""
    subprocess.run(['sudo', 'useradd', '--no-create-home', '--shell', '/bin/false', 'geth'])
    subprocess.run(['sudo', 'mkdir', '-p', '/var/lib/geth'])
    subprocess.run(['sudo', 'chown', '-R', 'geth:geth', '/var/lib/geth'])

def download_and_cleanup_geth():
    # Download and extract Geth
    github_url = "https://api.github.com/repos/ethereum/go-ethereum/releases/latest"
    url = 'https://geth.ethereum.org/downloads/'
    response = requests.get(url)
    html = response.text
    match = re.search(r'href="(https://gethstore\.blob\.core\.windows\.net/builds/geth-linux-amd64-[0-9]+\.[0-9]+\.[0-9]+-[0-9a-f]+\.tar\.gz)"', html)

    download_url = match.group(1)
    filename = os.path.expanduser('~/geth.tar.gz')
    response = requests.get(download_url)
    with open(filename, 'wb') as f:
        f.write(response.content)

    with tarfile.open(filename, 'r:gz') as tar:
        dirname = tar.getnames()[0].split('/')[0]
        tar.extractall(os.path.expanduser('~'))

    # Update Geth executable
    if dirname:
        if os.path.exists('/usr/local/bin/geth'):
            subprocess.run(['sudo', 'rm', '/usr/local/bin/geth'])

        src = os.path.expanduser(f'~/{dirname}/geth')
        subprocess.run(['sudo', 'cp', src, '/usr/local/bin/'])

    # Cleanup
    if filename and dirname:
        os.remove(filename)
        shutil.rmtree(os.path.expanduser(f'~/{dirname}'))

def install_geth():
    create_geth_user_and_directories()
    download_and_cleanup_geth()
    
def update_geth():
    run_updates()
    download_and_cleanup_geth()

# BESU INSTALL
def create_besu_user_and_directories():
	subprocess.run(['sudo', 'useradd', '--no-create-home', '--shell', '/bin/false', 'besu'])
	subprocess.run(['sudo', 'mkdir', '-p', '/var/lib/besu'])
	subprocess.run(['sudo', 'chown', '-R', 'besu:besu', '/var/lib/besu'])

def install_besu_dependencies():
    subprocess.run(["sudo", "apt", "-y", "install", "openjdk-21-jre"])
    subprocess.run(["sudo", "apt", "install", "-y", "libjemalloc-dev"])

def download_and_extract_besu():
    # Fetch the latest Besu version
    url = "https://api.github.com/repos/hyperledger/besu/releases/latest"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read().decode("utf-8"))
    latest_version = data['tag_name']

    # Download and extract Besu
    download_url = f"https://github.com/hyperledger/besu/releases/download/{latest_version}/besu-{latest_version}.tar.gz"
    file_path, _ = urllib.request.urlretrieve(download_url)
    dirname = f"besu-{latest_version}"

    with tarfile.open(file_path, "r:gz") as tar:
        tar.extractall()

    # Update Besu executable in /usr/local/bin
    if os.path.exists('/usr/local/bin/besu'):
        subprocess.run(['sudo', 'rm', '-r', '/usr/local/bin/besu'])

    subprocess.run(["sudo", "cp", "-a", dirname, "/usr/local/bin/besu"], check=True)

    # Cleanup
    os.remove(file_path)
    shutil.rmtree(dirname)

    return latest_version

def install_besu():
    install_besu_dependencies()
    create_besu_user_and_directories()
    download_and_extract_besu()

def update_besu():
    run_updates()
    install_besu_dependencies()
    latest_version = download_and_extract_besu()
    print(f'Successfully updated Besu {latest_version}')

# NETHERMIND INSTALL
def create_nethermind_user_and_directories():
    subprocess.run(['sudo', 'useradd', '--no-create-home', '--shell', '/bin/false', 'nethermind'])
    subprocess.run(['sudo', 'mkdir', '-p', '/var/lib/nethermind'])
    subprocess.run(['sudo', 'chown', '-R', 'nethermind:nethermind', '/var/lib/nethermind'])

def install_nethermind_dependencies():
    subprocess.run(["sudo", "apt-get", "install", "libsnappy-dev", "libc6-dev", "libc6", "unzip", "-y"], check=True)

def download_and_extract_nethermind():
    # Download Nethermind
    url = 'https://api.github.com/repos/NethermindEth/nethermind/releases/latest'
    response = requests.get(url)
    assets = response.json()['assets']
    download_url = next((asset['browser_download_url'] for asset in assets if asset['name'].endswith('linux-x64.zip')), None)

    if not download_url:
        print("Error: Could not find the download URL for the latest release.")
        return

    subprocess.run(['sudo', 'rm', '-rf', '/usr/local/bin/nethermind'])

    match = re.search(r'/download/([^/]+)/', download_url)
    if match:
        latest_version = match.group(1)

    with tempfile.NamedTemporaryFile('wb', suffix='.zip', delete=False) as temp_file:
        temp_file.write(requests.get(download_url).content)
        temp_path = temp_file.name

    # Extract Nethermind
    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(temp_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        subprocess.run(["sudo", "cp", "-a", f"{temp_dir}/.", "/usr/local/bin/nethermind"])

    os.remove(temp_path)

    # Set permissions for Nethermind
    subprocess.run(["sudo", "chown", "-R", "nethermind:nethermind", "/usr/local/bin/nethermind"])
    subprocess.run(["sudo", "chmod", "a+x", "/usr/local/bin/nethermind/nethermind"])

    return latest_version

def install_nethermind():
    create_nethermind_user_and_directories()
    latest_version = download_and_extract_nethermind()

def update_nethermind():
    run_updates()
    latest_version = download_and_extract_nethermind()
    print(f"Nethermind {latest_version} successfully updated!")

# TEKU INSTALL
def create_teku_user_and_directories():
    """Create user and directories for Teku."""
    subprocess.run(['sudo', 'useradd', '--no-create-home', '--shell', '/bin/false', 'teku'])
    subprocess.run(['sudo', 'mkdir', '-p', '/var/lib/teku/validator_keys'])
    subprocess.run(['sudo', 'chown', '-R', 'teku:teku', '/var/lib/teku'])

def download_and_extract_teku():
    # Download Teku
    url = 'https://api.github.com/repos/ConsenSys/teku/releases/latest'
    response = requests.get(url)
    latest_version = response.json()['tag_name']

    download_url = f"https://artifacts.consensys.net/public/teku/raw/names/teku.tar.gz/versions/{latest_version}/teku-{latest_version}.tar.gz"

    response = requests.get(download_url)
    tar_path = os.path.expanduser('~/teku.tar.gz')
    with open(tar_path, 'wb') as file:
        file.write(response.content)

    # Extract
    with tarfile.open(tar_path, 'r:gz') as tar:
        tar.extractall(path=os.path.expanduser("~"))

    dirname = f"teku-{latest_version}"

    # Delete old binary
    subprocess.run(["sudo", "rm", "-r", "/usr/local/bin/teku"], check=False)

    # Move binary
    subprocess.run(["sudo", "cp", "-r", os.path.expanduser(f"~/{dirname}"), "/usr/local/bin/teku"], check=True)

    # Cleanup
    os.remove(tar_path)
    shutil.rmtree(os.path.expanduser(f"~/{dirname}"))

    return latest_version

def install_teku():
    create_teku_user_and_directories()
    latest_version = download_and_extract_teku()

def update_teku():
    run_updates()
    latest_version = download_and_extract_teku()
    print(f"Teku {latest_version} successfully updated!")

# PRYSM INSTALL
def create_prysm_users_and_directories():
    # Create prysmbeacon user and dir
    subprocess.run(['sudo', 'useradd', '--no-create-home', '--shell', '/bin/false', 'prysmbeacon'])
    subprocess.run(['sudo', 'mkdir', '-p', '/var/lib/prysm/beacon'])
    subprocess.run(['sudo', 'chown', '-R', 'prysmbeacon:prysmbeacon', '/var/lib/prysm/beacon'])

    # Create prysmvalidator user and dir
    subprocess.run(['sudo', 'useradd', '--no-create-home', '--shell', '/bin/false', 'prysmvalidator'])
    subprocess.run(['sudo', 'mkdir', '-p', '/var/lib/prysm/validator'])
    subprocess.run(['sudo', 'chown', '-R', 'prysmvalidator:prysmvalidator', '/var/lib/prysm/validator'])

def download_and_install_prysm_binaries():
    base_url = "https://api.github.com/repos/prysmaticlabs/prysm/releases/latest"
    response = requests.get(base_url)
    response_json = response.json()
    beacon_chain_link = None
    validator_link = None

    # Search for download links in the assets
    for asset in response_json["assets"]:
        if re.search(r'beacon-chain-v\d+\.\d+\.\d+-linux-amd64$', asset["browser_download_url"]):
            beacon_chain_link = asset["browser_download_url"]
        elif re.search(r'validator-v\d+\.\d+\.\d+-linux-amd64$', asset["browser_download_url"]):
            validator_link = asset["browser_download_url"]

    # Download the binaries if links are found
    if beacon_chain_link and validator_link:
        beacon_chain_filename = beacon_chain_link.split('/')[-1]
        validator_filename = validator_link.split('/')[-1]

        os.system(f"curl -LO {beacon_chain_link}")
        os.system(f"curl -LO {validator_link}")

        # Rename and move the binaries
        os.system(f"mv {beacon_chain_filename} beacon-chain")
        os.system(f"mv {validator_filename} validator")
        os.system("chmod +x beacon-chain")
        os.system("chmod +x validator")
        os.system("sudo cp beacon-chain /usr/local/bin")
        os.system("sudo cp validator /usr/local/bin")

        # Cleanup
        os.system("rm beacon-chain")
        os.system("rm validator")

        return True
    else:
        print("Error: Could not find the latest release links.")
        return False

def install_prysm():
    create_prysm_users_and_directories()
    download_and_install_prysm_binaries()

def update_prysm():
    run_updates()
    download_and_install_prysm_binaries()

# NIMBUS INSTALL
def create_nimbus_directory_and_user():
    subprocess.run(['sudo', 'mkdir', '-p', '/var/lib/nimbus'])
    subprocess.run(['sudo', 'chmod', '700', '/var/lib/nimbus'])
    subprocess.run(['sudo', 'useradd', '--no-create-home', '--shell', '/bin/false', 'nimbus'])
    subprocess.run(['sudo', 'chown', '-R', 'nimbus:nimbus', '/var/lib/nimbus'])

def download_and_extract_nimbus():
    url = 'https://api.github.com/repos/status-im/nimbus-eth2/releases/latest'
    response = requests.get(url)
    assets = response.json()['assets']
    download_url = None

    for asset in assets:
        if '_Linux_amd64' in asset['name'] and asset['name'].endswith('.tar.gz'):
            download_url = asset['browser_download_url']
            break

    if download_url is None:
        print("Error: Could not find the download URL for the latest release.")
        return None

    # Save and extract the binary
    tar_path = os.path.expanduser('~/nimbus.tar.gz')
    with open(tar_path, 'wb') as f:
        f.write(requests.get(download_url).content)

    with tarfile.open(tar_path, 'r:gz') as tar:
        tar.extractall(path=os.path.expanduser("~"))
    
    # Find the extracted folder
    extracted_folder = None
    for item in os.listdir():
        if item.startswith("nimbus-eth2_Linux_amd64"):
            extracted_folder = item
            break

    if extracted_folder is None:
        print("Error: Could not find the extracted folder.")
        exit(1)
    
    # Move Nimbus binary to /usr/local/bin
    nimbus_binary = f"{extracted_folder}/build/nimbus_beacon_node"
    if os.path.exists(nimbus_binary):
        subprocess.run(["sudo", "cp", nimbus_binary, "/usr/local/bin"])
    else:
        print("Error: Nimbus binary not found after extraction.")

    # Remove files
    os.remove(tar_path)
    shutil.rmtree(extracted_folder, ignore_errors=True)

def install_nimbus():
    create_nimbus_directory_and_user()
    download_and_extract_nimbus()

def update_nimbus():
    run_updates()
    download_and_extract_nimbus()

# LIGHTHOUSE INSTALL
def create_lighthouse_users_and_directories():
    # Create lighthousebeacon user and directory
    subprocess.run(['sudo', 'useradd', '--no-create-home', '--shell', '/bin/false', 'lighthousebeacon'])
    subprocess.run(['sudo', 'mkdir', '-p', '/var/lib/lighthouse/beacon/logs'])
    subprocess.run(['sudo', 'chown', '-R', 'lighthousebeacon:lighthousebeacon', '/var/lib/lighthouse/beacon'])

    # Create lighthousevalidator user and directory
    subprocess.run(['sudo', 'useradd', '--no-create-home', '--shell', '/bin/false', 'lighthousevalidator'])
    subprocess.run(['sudo', 'mkdir', '-p', '/var/lib/lighthouse/validators'])
    subprocess.run(['sudo', 'chown', '-R', 'lighthousevalidator:lighthousevalidator', '/var/lib/lighthouse/validators'])

def download_and_extract_lighthouse():
    url = 'https://api.github.com/repos/sigp/lighthouse/releases/latest'
    response = requests.get(url)
    assets = response.json()['assets']
    download_url = next((asset['browser_download_url'] for asset in assets if asset['name'].endswith('x86_64-unknown-linux-gnu.tar.gz')), None)

    if not download_url:
        print("Error: Could not find the download URL for the latest release.")
        return

    tar_path = os.path.expanduser('~/lighthouse.tar.gz')
    with open(tar_path, 'wb') as f:
        f.write(requests.get(download_url).content)

    with tarfile.open(tar_path, 'r:gz') as tar:
        tar.extractall(path=os.path.expanduser("~"))

    # Move the Lighthouse binary to /usr/local/bin
    binary_path = os.path.expanduser('~/lighthouse')
    if os.path.exists(binary_path):
        subprocess.run(["sudo", "cp", binary_path, "/usr/local/bin"])
    else:
        print("Error: Lighthouse binary not found after extraction.")

    # Remove files
    os.remove(tar_path)
    shutil.rmtree(os.path.expanduser('~/lighthouse'), ignore_errors=True)

def install_lighthouse():
    create_lighthouse_users_and_directories()
    download_and_extract_lighthouse()

def update_lighthouse():
    run_updates()
    download_and_extract_lighthouse()    


# Install Client
def install_client(client):
    function_name = f"install_{client}".lower()
    func = globals().get(function_name)
    func()

# Update Client
def update_client(client):
    function_name = f"update_{client}".lower()
    func = globals().get(function_name)
    func()
