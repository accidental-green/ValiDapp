import os
import sys
import subprocess

def keystore_import(cc_import, network, keystorePath):
    function_name = f"{cc_import}_keystore_import".lower()
    directory = os.path.dirname(keystorePath)
    func = globals().get(function_name)
    func(network.lower(), directory)

def check_temp_keystore_dir(temp_keystore_dir):
    # Ensure the 'validator_keys_temp' directory exists
    json_files_in_source = [f for f in os.listdir(temp_keystore_dir)] if os.path.exists(temp_keystore_dir) else []
    json_files_in_source = [f for f in json_files_in_source if f.endswith('.json')]

    if not len(json_files_in_source) > 0:
        print(f"No Keystore files found at {temp_keystore_dir}")

    return json_files_in_source

def list_temp_jsons(temp_keystore_dir):
    json_files_in_source = [f for f in os.listdir(temp_keystore_dir)] if os.path.exists(temp_keystore_dir) else []
    json_files_in_source = [f for f in json_files_in_source if f.endswith('.json')]
    
    if not len(json_files_in_source) > 0:
        print(f"No Keystore files found at {temp_keystore_dir}")
    
    return json_files_in_source

# TEKU KEYSTORE IMPORT
def teku_keystore_import(network, keystorePath):
    
    password = os.getenv('MY_SECRET_PASSWORD')
    if not password:
        print("Password not set.")
        sys.exit(1)

    temp_keystore_dir = keystorePath
    teku_keystore_dir = '/var/lib/teku/validator_keys'
    json_files_in_source = check_temp_keystore_dir(temp_keystore_dir)

    if len(json_files_in_source) > 0:
        # Check if teku validator key dir exists, otherwise create
        if not os.path.exists(teku_keystore_dir):
            subprocess.run(['sudo', 'mkdir', '-p', teku_keystore_dir])

        for json_file in json_files_in_source:
            source_path = os.path.join(temp_keystore_dir, json_file)
            dest_path = os.path.join(teku_keystore_dir, json_file)
            subprocess.run(['sudo', 'cp', source_path, dest_path])
            print(f"Successfully copied keystore {json_file}.\n")
        
        def get_and_store_password(json_file, password):
            txt_file_name = os.path.splitext(json_file)[0] + '.txt'
            txt_file_path = os.path.join(teku_keystore_dir, txt_file_name)
            
            # Store the password directly in a bytearray
            teku_pass = bytearray(password, 'utf-8')
            
            # Use a temporary file for writing the password.txt file
            temp_file_name = 'temp_password_file.txt'
            with open(temp_file_name, 'wb') as f:
                os.write(f.fileno(), teku_pass)
            
            # Use sudo to move the temp file to the actual desired location
            subprocess.run(['sudo', 'mv', temp_file_name, txt_file_path])
            
            # Modify permissions of the text file so it's not readable by others
            subprocess.run(['sudo', 'chmod', '600', txt_file_path])
            
            # Overwrite the password in memory with zero bytes
            for i in range(len(teku_pass)):
                teku_pass[i] = 0
                
            print(f"\nPassword for {json_file} has been saved and stored securely.\n")

        # List all files ending with .json in the teku keystore directory
        teku_json_files = [f for f in os.listdir(teku_keystore_dir) if f.endswith('.json')]

        # For each json file, store the password in a corresponding txt file
        for json_file in teku_json_files:
            get_and_store_password(json_file, password)
            print(f"Processed Teku Keystore: {json_file}")
        
        # Change Ownership
        subprocess.run(['sudo', 'chown', '-R', 'teku:teku', '/var/lib/teku'])

# Function to check the temporary keystore directory and return JSON files
def check_temp_keystore_dir(directory):
    return [f for f in os.listdir(directory) if f.endswith('.json')]

# NIMBUS KEYSTORE IMPORT
def nimbus_keystore_import(network, keystorePath):

    password = os.getenv('MY_SECRET_PASSWORD')
    if not password:
        print("Password not set.")
        sys.exit(1)

    # Check if the temp_keystore_dir exists and is not empty
    temp_keystore_dir = keystorePath
    if os.path.exists(temp_keystore_dir) and os.listdir(temp_keystore_dir):
        # Construct the Nimbus command
        cmd = [
            'sudo',
            '/usr/local/bin/nimbus_beacon_node',
            'deposits', 'import',
            '--data-dir=/var/lib/nimbus',
            temp_keystore_dir
        ]

        # Start the process
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Send the password followed by a newline to simulate Enter key
        process.stdin.write(password + '\n')
        process.stdin.flush()  # Ensure the password is sent to the process

        # Optionally, read the output
        stdout, stderr = process.communicate()
        if stdout:
            print(stdout)
        if stderr:
            print(stderr)

    else:
        print(f"No keystores found at {temp_keystore_dir}")

    # Change file ownership to the nimbus user
    subprocess.run(['sudo', 'chown', '-R', 'nimbus:nimbus', '/var/lib/nimbus'])

# PRYSM IMPORT

def prysm_keystore_import(network, keystorePath):
    password = os.getenv('MY_SECRET_PASSWORD')
    if not password:
        print("Password not set.")
        sys.exit(1)

    temp_keystore_dir = keystorePath
    password_file = '/var/lib/prysm/validator/password.txt'
    wallet_dir = '/var/lib/prysm/validator'

    if os.path.exists(temp_keystore_dir) and os.listdir(temp_keystore_dir):
        # Ensure the wallet directory exists
        if not os.path.exists(wallet_dir):
            os.makedirs(wallet_dir)
            subprocess.run(['sudo', 'chown', '-R', 'prysmvalidator:prysmvalidator', wallet_dir], check=True)

        # Temporarily change ownership to the current user
        current_user = os.getlogin()
        subprocess.run(['sudo', 'chown', '-R', f'{current_user}:{current_user}', wallet_dir], check=True)

        # Write the password to a temporary file
        with open('temp_password.txt', 'w') as temp_file:
            temp_file.write(password)

        # Use sudo to move the temp file to the actual desired location and set permissions
        subprocess.run(['sudo', 'mv', 'temp_password.txt', password_file], check=True)
        subprocess.run(['sudo', 'chmod', '600', password_file], check=True)

        import_command = [
            'sudo',
            '/usr/local/bin/validator',
            'accounts', 'import',
            '--accept-terms-of-use',
            '--keys-dir', temp_keystore_dir,
            '--wallet-dir', wallet_dir,
            '--wallet-password-file', password_file,
            '--account-password-file', password_file,
            f'--{network}'
        ]

        # Execute the command and capture output
        process = subprocess.Popen(import_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Stream output
        for line in process.stdout:
            print(line, end='')  # Or send this line to your frontend

        # Ensure the process has completed
        stdout, stderr = process.communicate()
        if stderr:
            print(stderr, file=sys.stderr)

        subprocess.run(['sudo', 'chown', '-R', 'prysmvalidator:prysmvalidator', wallet_dir], check=True)
    else:
        print(f"No keystores found at {temp_keystore_dir}")



def lighthouse_keystore_import(network, keystorePath):

    password = os.getenv('MY_SECRET_PASSWORD')
    if not password:
        print("Password not set.")
        sys.exit(1)

    lighthousePath = '/var/lib/lighthouse'
    validatorPath = '/var/lib/lighthouse/validators'
    password_file_path = 'password.txt'

    # Write the password to a temporary file
    with open(password_file_path, 'w') as f:
        f.write(password)

    try:
        # Prepare and execute the import command
        import_command = [
            'sudo', '/usr/local/bin/lighthouse', 'account', 'validator', 'import',
            '--network', network,
            '--directory', keystorePath,
            '--datadir', lighthousePath,
            '--password-file', password_file_path,
            '--reuse-password',
            '--stdin-inputs'
        ]

        try:
            import_process = subprocess.run(import_command, text=True, capture_output=True, timeout=10)  # Set a timeout of 10 seconds
            if "invalid password" in import_process.stderr.lower():
                print("Error: Incorrect password provided.", file=sys.stderr)
                return  # Exit the function if the password is incorrect
            print(import_process.stdout)
            print(import_process.stderr, file=sys.stderr)
        except subprocess.TimeoutExpired:
            print("Error: Command timed out. Possible incorrect password or no response.", file=sys.stderr)
            return  # Exit the function if the command times out

        # Prepare and execute the list command
        list_command = [
            'sudo', '/usr/local/bin/lighthouse', 'account', 'validator', 'list',
            '--datadir', lighthousePath
        ]
        list_process = subprocess.run(list_command, text=True, capture_output=True)
        print('LIGHTHOUSE VALIDATOR LIST:\n')
        print(list_process.stdout)
        print(list_process.stderr, file=sys.stderr)

    finally:
        # Cleanup: Remove the temporary password file and change ownership
        os.remove(password_file_path)
        subprocess.run(['sudo', 'chown', '-R', 'lighthousevalidator:lighthousevalidator', validatorPath])