const { app, Menu, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const { exec, spawn, execSync } = require('child_process');

// Global variables
global.multipleClientsInstalled = null;
global.userSettings = {};
global.installSettings = {};
global.deleteSettings = {};
global.installedClients = [];
global.latestClients = [];
global.clientNames = [];

let startupWindow;
let resourcesWindow;
let resourcesDashboardWindow;
let freshStartupWindow;
let installWindow;
let installConfirmWindow;
let installProgress;
let installProgressKeystore;
let preConfigWindow;
let configWindow;
let loadingWindow;
let updateWindow;
let deleteWindow;
let deleteConfirmWindow;
let updateProgress;
let deleteProgress;
let importProgress;
let importWarning;
let importWarningInstall;
let importWindow;
let importInstallWindow;
let miniDash;
let journalsWindow;

const services = [
  'geth', 'besu', 'nethermind',
  'lighthousebeacon', 'lighthousevalidator',
  'nimbus', 'prysmbeacon', 'prysmvalidator',
  'teku', 'mevboost'
];

// Define the path to the system Python and set up the environment variables
const pythonPath = 'python3'; // Assuming Python 3 is installed system-wide
const pythonEnv = {
  ...process.env,
  PYTHONPATH: `/usr/lib/python3/dist-packages` // Update PYTHONPATH if needed for requests or other dependencies
};

// Function to execute Python script with the system's Python interpreter
function executePythonScript(scriptPath, args = [], callback) {
  const command = `python3 ${scriptPath} ${args.join(' ')}`; // Use system Python (assuming python3 is installed)
  exec(command, { env: pythonEnv }, (error, stdout, stderr) => {
    if (error) {
      console.error(`Execution error: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`Script error output: ${stderr}`);
      return;
    }
    if (stdout) {
      console.log(`Script output: ${stdout}`);
    }
    if (callback) {
      callback(stdout);
    }
  });
}

function firstCheckSudoPrivileges() {
  try {
    console.log("Starting ValiDapp and authenticating sudo access.\n\nPlease enter user password:\n");
    execSync('sudo -v', { stdio: 'inherit' }); // 'inherit' makes the prompt visible
    console.log("Sudo credentials authenticated.");
    return true; // Sudo success
  } catch (error) {
    console.error(`Failed to verify sudo credentials: ${error}`);
    return false; // Sudo failed
  }
}

function checkSudoPrivileges() {
  return new Promise((resolve, reject) => {
    exec('sudo -nv', (error, stdout, stderr) => {
      if (error) {
        console.error(`Sudo check failed: ${error}`);
        resolve(false); // Indicates that sudo privileges are not available without a password prompt
      } else {
        console.log("Sudo privileges are active.");
        resolve(true); // Indicates that sudo privileges are available
      }
    });
  });
}

function fetchInstalledClients(callback) {
  const scriptPath = path.join(process.resourcesPath, 'modules', 'prints.py'); // Assume app is packaged

  // Use system Python (assuming python3 is installed)
  const command = `python3 ${scriptPath}`;

  exec(command, { env: pythonEnv }, (error, stdout, stderr) => {
    if (error) {
      console.error(`Execution error: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`Script error output: ${stderr}`);
      return;
    }

    const jsonOutputLine = stdout.split('\n').find(line => line.startsWith('JSON_INSTALLED:'));
    if (jsonOutputLine) {
      try {
        const installedClients = JSON.parse(jsonOutputLine.replace('JSON_INSTALLED: ', ''));
        console.log('Installed Clients:', installedClients);
        global.installedClients = installedClients;
        showClientNames(installedClients);
      } catch (parseError) {
        console.error('Error parsing JSON from Python script:', parseError);
      }
    } else {
      console.error('No JSON output found in the script response.');
    }

    if (callback) {
      callback();
    }
  });
}

function showClientNames(installedClients) {
  const clientNames = installedClients.map(client => Object.keys(client)[0]);
  console.log('Client Names:', clientNames);
  global.clientNames = clientNames;
}

function fetchLatestVersions(callback) {
  const scriptPath = path.join(process.resourcesPath, 'modules', 'latest_versions.py'); // Assume app is packaged

  exec(`python3 ${scriptPath}`, (error, stdout, stderr) => {
    if (error) {
      console.error(`Execution error: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`Script error output: ${stderr}`);
      return;
    }

    const jsonLatestOutputLine = stdout.split('\n').find(line => line.startsWith('JSON_LATEST:'));
    if (jsonLatestOutputLine) {
      try {
        const latestClients = JSON.parse(jsonLatestOutputLine.replace('JSON_LATEST: ', ''));
        console.log('Latest Github Clients:', latestClients);
        global.latestClients = latestClients;
      } catch (parseError) {
        console.error('Error parsing JSON from Python script:', parseError);
      }
    } else {
      console.error('No JSON output found in the script response.');
    }

    if (callback) {
      callback();
    }
  });
}

// Function to count installed clients from a specific group
function countInstalledClients(clientGroup) {
  // Convert each client group name to the correct case to match the keys in the objects
  let count = 0;
  clientGroup.forEach(groupClient => {
      global.installedClients.forEach(installedClient => {
          if (Object.keys(installedClient)[0].toLowerCase() === groupClient.toLowerCase()) {
              count++;
          }
      });
  });
  console.log(`Count for ${clientGroup.join(', ')}: ${count}`);
  return count;
}

// Function to check if more than two clients from a specific group are installed
function checkMultipleInstallations(clientGroup) {
  const count = countInstalledClients(clientGroup);
  if (count > 1) {
      console.log(`Warning: More than two clients from the group [${clientGroup.join(', ')}] are installed.`);
      return true;
  }
  return false;
}

// Client groups with correct names as they appear as keys in the installed clients objects
const executionClients = ['Geth', 'Besu', 'Nethermind'];
const consensusClients = ['Lighthouse', 'Prysm', 'Nimbus', 'Teku'];

async function CheckSudo() {
  const hasSudo = await checkSudoPrivileges();
  if (!hasSudo) {
    mainWindow.webContents.send('sudo-required', 'Sudo authentication is required to start services. Please restart the application and eneter your password.');
    return; // Halt the function if sudo privileges are not verified
  }
}

async function startServices(data) {
  const hasSudo = await checkSudoPrivileges();
  if (!hasSudo) {
    mainWindow.webContents.send('sudo-required', 'Sudo authentication is required to start services. Please restart the application and enter your password.');
    return;
  }

  console.log("Starting services with the following configuration:", data);

  const pythonScriptPath = path.join(process.resourcesPath, 'modules', 'start.py'); // Assume app is packaged

  const command = `python3 ${pythonScriptPath} '${data.execution}' '${data.consensus}' '${data.validator}' '${data.mevboost}'`;

  exec(command, (error, stdout, stderr) => {
    if (error) {
      console.error(`Execution error: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`Script error output: ${stderr}`);
      return;
    }
    if (stdout) {
      console.log(`Service start script output: ${stdout}`);
    }
  });
}

async function stopServices(data) {
  const hasSudo = await checkSudoPrivileges();
  if (!hasSudo) {
    mainWindow.webContents.send('sudo-required', 'Sudo authentication is required to stop services. Please restart the application and enter your password.');
    return;
  }

  console.log("Stopping services with the following configuration:", data);

  const pythonScriptPath = path.join(process.resourcesPath, 'modules', 'stop.py'); // Assume app is packaged

  const command = `python3 ${pythonScriptPath} '${data.execution}' '${data.consensus}' '${data.validator}' '${data.mevboost}'`;

  exec(command, (error, stdout, stderr) => {
    if (error) {
      console.error(`Execution error: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`Script error output: ${stderr}`);
      return;
    }
    if (stdout) {
      console.log(`Service stop script output: ${stdout}`);
    }
  });
}

function createWindow(filename) {
  let window = new BrowserWindow({
      width: 800,
      height: 600,
      webPreferences: {
          preload: path.join(__dirname, 'preload.js'),
          contextIsolation: true,
          nodeIntegration: false,
          enableRemoteModule: false,
      }
  });
  window.setMenu(null);
  window.loadFile(filename);
  return window;
}

function createBigWindow(filename) {
  let window = new BrowserWindow({
      width: 800,
      height: 700,
      webPreferences: {
          preload: path.join(__dirname, 'preload.js'),
          contextIsolation: true,
          nodeIntegration: false,
          enableRemoteModule: false,
      }
  });
  window.setMenu(null);
  window.loadFile(filename);
  return window;
}

function createMiniDashWindow(filename) {
  let window = new BrowserWindow({
      width: 820,
      height: 530,
      webPreferences: {
          preload: path.join(__dirname, 'preload.js'),
          contextIsolation: true,
          nodeIntegration: false,
          enableRemoteModule: false,
      }
  });
  window.setMenu(null);
  window.loadFile(filename);
  return window;
}

function createWideWindow(filename) {
  let window = new BrowserWindow({
      width: 860,
      height: 580,
      webPreferences: {
          preload: path.join(__dirname, 'preload.js'),
          contextIsolation: true,
          nodeIntegration: false,
          enableRemoteModule: false,
      }
  });
  window.setMenu(null);
  window.loadFile(filename);
  return window;
}

function createWiderWindow(filename) {
  let window = new BrowserWindow({
      width: 1000,
      height: 540,
      webPreferences: {
          preload: path.join(__dirname, 'preload.js'),
          contextIsolation: true,
          nodeIntegration: false,
          enableRemoteModule: false,
      }
  });
  window.setMenu(null);
  window.loadFile(filename);
  return window;
}

function createTallWindow(filename) {
  let window = new BrowserWindow({
      width: 800,
      height: 670,
      webPreferences: {
          preload: path.join(__dirname, 'preload.js'),
          contextIsolation: true,
          nodeIntegration: false,
          enableRemoteModule: false,
      }
  });
  window.setMenu(null);
  window.loadFile(filename);
  return window;
}

function createStartupWindow() {
  startupWindow = createWindow('app/html/startup.html');
  startupWindow.webContents.send('get-installed-versions', global.installedClients);
}

function openResourcesWindow() {
  resourcesWindow = createTallWindow('app/html/resources.html');
}

function openResourcesDashboardWindow() {
  resourcesDashboardWindow = createTallWindow('app/html/resourcesDashboard.html');
}
 
function createFreshStartupWindow() {
  freshStartupWindow = createWiderWindow('app/html/freshStartup.html');
  freshStartupWindow.webContents.send('get-installed-versions', global.installedClients);
}

function OpenConfigWindow() {
  configWindow = createWindow('app/html/config.html');
  configWindow.webContents.send('get-installed-versions', global.installedClients);
}

function OpenPreConfigWindow() {
  if (global.installedClients && global.installedClients.length > 0) {
    if (global.multipleClientsInstalled) {
      // If multiple clients are installed, open the warning page
      preConfigWindow = createWindow('app/html/preConfigWarning.html');
      preConfigWindow.webContents.send('get-installed-versions', global.installedClients);
    } else {
      // Otherwise, call the createMiniDash function
      createMiniDash();
    }
  } else {
    // Open the noClients.html page if installedClients is empty or null
    preConfigWindow = createWindow('app/html/noClients.html');
  }
}

function createClientWarningPopup() {
  if (global.installedClients && global.installedClients.length > 0) {
      clientsWarningWindow = createWindow('app/html/clientsWarning.html');
      clientsWarningWindow.webContents.send('get-installed-versions', global.installedClients);
  } else {
    // Open the noClients.html page if installedClients is empty or null
    installWindow = createWiderWindow('app/html/installWindow.html');
  }
}

function createInstallPopup() {
  installWindow = createWiderWindow('app/html/installWindow.html');
}

function createInstallConfirmWindow() {
  installConfirmWindow = createWindow('app/html/installConfirm.html')

  installConfirmWindow.webContents.on('did-finish-load', () => {
    installConfirmWindow.webContents.send('install-settings', global.installSettings);
  });
}

function createInstallProgressWindow() {
  installProgress = createBigWindow('app/html/installProgress.html');
}

function createInstallProgressKeystoreWindow() {
  installProgressKeystore = createBigWindow('app/html/installProgressKeystore.html');
}

function createLoadingWindow() {
  loadingWindow = createWindow('app/html/loading.html')
}

function createUpdateWindow() {
  updateWindow = createWindow('app/html/updateWindow.html')

  updateWindow.webContents.on('did-finish-load', () => {
    // Assuming `global.installedClients` and `global.latestClients` are properly set
    updateWindow.webContents.send('get-installed-versions', global.installedClients, global.latestClients);
  });
}

function createUpdateProgressWindow() {
  updateProgress = createWindow('app/html/updateProgress.html');
  updateProgress.maximize();
}

function createDeleteWindow() {
  deleteWindow = createWindow('app/html/deleteWindow.html')

  deleteWindow.webContents.on('did-finish-load', () => {
    // Assuming `global.installedClients` and `global.latestClients` are properly set
    deleteWindow.webContents.send('get-installed-versions', global.installedClients, global.latestClients);
  });
}

function createDeleteConfirmWindow() {
  deleteConfirmWindow = createWindow('app/html/deleteConfirm.html')

  deleteConfirmWindow.webContents.on('did-finish-load', () => {
    deleteConfirmWindow.webContents.send('delete-settings', global.deleteSettings);
  });
}

function createDeleteProgressWindow() {
  deleteProgress = createWindow('app/html/deleteProgress.html');
}
function createImportWarningPopup() {
  importWarning = createWindow('app/html/importWarning.html')
}

function createImportWarningInstallPopup() {
  importWarningInstall = createWindow('app/html/importWarningInstall.html')
}

function createImportPopup() {
  importWindow = createWindow('app/html/importKeystore.html')
}

function createImportInstallPopup() {
  importInstallWindow = createWindow('app/html/importKeystoreInstall.html')
  
  importInstallWindow.webContents.on('did-finish-load', () => {
    importInstallWindow.webContents.send('install-settings', global.installSettings);
  });
}

function createImportProgressWindow() {
  importProgress = createWindow('app/html/importProgress.html')
}

function createMiniDash() {
  miniDash = createMiniDashWindow('app/html/miniDash.html');
  miniDash.webContents.on('did-finish-load', () => {
      // Check if userSettings is not null and has keys (assuming it's an object)
      if (global.userSettings && Object.keys(global.userSettings).length > 0) {
          miniDash.webContents.send('user-settings', global.userSettings);
      } else {
          miniDash.webContents.send('get-installed-versions', global.installedClients);
      }
  });
}

function createJournalsWindow() {
  journalsWindow = createWindow('app/html/journals.html');
  journalsWindow.maximize();
  journalsWindow.webContents.on('did-finish-load', () => {
      if (global.userSettings && Object.keys(global.userSettings).length > 0) {
          journalsWindow.webContents.send('user-settings', global.userSettings);
      } else {
        journalsWindow.webContents.send('get-installed-versions', global.installedClients);
      }
  });
}

app.disableHardwareAcceleration();

app.whenReady().then(() => {
  firstCheckSudoPrivileges();
  createLoadingWindow();
  fetchInstalledClients(() => {
    const multipleExecutionClientsInstalled = checkMultipleInstallations(executionClients);
    const multipleConsensusClientsInstalled = checkMultipleInstallations(consensusClients);
    const clientsInstalled = installedClients.length > 0;
  
    if (multipleExecutionClientsInstalled || multipleConsensusClientsInstalled) {
      console.log("Action needed: More than two clients from a group are installed.");
      global.multipleClientsInstalled = true;
    } else {
      console.log("No duplicates found.");
      global.multipleClientsInstalled = false;
    }

    if (clientsInstalled) {
      console.log(clientsInstalled)
      createMiniDash();
      loadingWindow.close();
    } else {
      createInstallPopup();
      loadingWindow.close();
    }
  });
  fetchLatestVersions();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

ipcMain.handle('check-sudo-privileges', async (event) => {
  const hasSudo = await checkSudoPrivileges();  // Assumes checkSudoPrivileges returns a promise that resolves to a boolean
  if (!hasSudo) {
      event.sender.send('sudo-required', 'Sudo privileges are required.');
  }
  return hasSudo;
});

ipcMain.on('startServices', (event, settings) => {
  const { execution, consensus, mevboost } = settings;
  startServices(settings);
});

ipcMain.on('stopServices', (event, settings) => {
  const { execution, consensus, mevboost } = settings;
  stopServices(settings);
});

ipcMain.on('open-resources-popup', (event, args) => {
  openResourcesWindow();
  if (miniDash) {
    miniDash.close();
    miniDash = null;
  }
  if (freshStartupWindow) {
    freshStartupWindow.close();
    freshStartupWindow = null;
  }
  if (installWindow) {
    installWindow.close();
    installWindow = null;
  }
});

ipcMain.on('open-resources-dashboard-popup', (event, args) => {
  openResourcesDashboardWindow();
  if (miniDash) {
    miniDash.close();
    miniDash = null;
  }
  if (freshStartupWindow) {
    freshStartupWindow.close();
    freshStartupWindow = null;
  }
  if (installWindow) {
    installWindow.close();
    installWindow = null;
  }
});

ipcMain.on('open-startup-popup', (event, args) => {
  startupWindow = null;
  freshStartupWindow = null;
  installWindow = null;
  installConfirmWindow = null;
  installProgress = null;
  preConfigWindow = null;
  configWindow = null;
  loadingWindow = null;
  updateWindow = null;
  deleteWindow = null;
  updateProgress = null;
  deleteProgress = null;
  importWarning = null;
  importWarningInstall = null;
  importWindow = null;
  importInstallWindow = null;
  importProgress = null;
  miniDash = null;
  journalsWindow = null;
  global.userSettings = null;
  createStartupWindow();
});

ipcMain.on('open-fresh-startup-popup', (event, args) => {
  startupWindow = null;
  resourcesWindow = null;
  freshStartupWindow = null;
  installWindow = null;
  installConfirmWindow = null;
  installProgress = null;
  preConfigWindow = null;
  configWindow = null;
  loadingWindow = null;
  updateWindow = null;
  deleteWindow = null;
  updateProgress = null;
  deleteProgress = null;
  importWarning = null;
  importWarningInstall = null;
  importWindow = null;
  importInstallWindow = null;
  importProgress = null;
  miniDash = null;
  journalsWindow = null;
  global.userSettings = null;
  createClientWarningPopup();
});

ipcMain.on('open-install-popup', (event, args) => {
  createInstallPopup();
  if (startupWindow) {
    startupWindow.close();
    startupWindow = null;
  }
});

ipcMain.on('open-client-warning-popup', (event, args) => {
  createClientWarningPopup();
  if (startupWindow) {
    startupWindow.close();
    startupWindow = null;
  }
});

ipcMain.on('open-install-confirm-popup', (event, args) => {
  createInstallConfirmWindow();
  if (installWindow) {
    installWindow.close();
    installWindow = null;
  }
  if (freshStartupWindow) {
    freshStartupWindow.close();
    freshStartupWindow = null;
  }
  if (installWindow) {
    installWindow.close();
    installWindow = null;
  }
});

ipcMain.on('settings-confirmed', (event, settings) => {
  global.userSettings = settings;
  console.log(userSettings)
  if (installWindow) {
    installWindow.close();
    installWindow = null;
  }
  if (installConfirmWindow) {
    installConfirmWindow.close();
    installConfirmWindow = null;
  }

});

ipcMain.on('install-settings', (event, installSettings) => {
  global.installSettings = installSettings;

  if (installSettings.keystore === 'yes') {
    createImportWarningInstallPopup();
  } else {
    createInstallConfirmWindow();
  }

  if (installWindow) {
    installWindow.close();
    installWindow = null;
  }
  if (freshStartupWindow) {
    freshStartupWindow.close();
    freshStartupWindow = null;
  }
  if (installWindow) {
    installWindow.close();
    installWindow = null;
  }
});

ipcMain.on('delete-settings', (event, deleteSettings) => {
  global.deleteSettings = deleteSettings;
  createDeleteConfirmWindow();
  if (deleteWindow) {
    deleteWindow.close();
    deleteWindow = null;
  }
});

ipcMain.on('open-update-popup', (event, args) => {
  createUpdateWindow();
  if (startupWindow) {
    startupWindow.close();
    startupWindow = null;
  }
  if (freshStartupWindow) {
    freshStartupWindow.close();
    freshStartupWindow = null;
  }
  if (installWindow) {
    installWindow.close();
    installWindow = null;
  }
});

ipcMain.on('open-delete-popup', (event, args) => {
  createDeleteWindow();
  if (startupWindow) {
    startupWindow.close();
    startupWindow = null;
  }
  if (freshStartupWindow) {
    freshStartupWindow.close();
    freshStartupWindow = null;
  }
  if (installWindow) {
    installWindow.close();
    installWindow = null;
  }
});

ipcMain.on('open-import-warning-popup', (event, args) => {
  createImportWarningPopup();
  if (startupWindow) {
    startupWindow.close();
    startupWindow = null;
  }
  if (freshStartupWindow) {
    freshStartupWindow.close();
    freshStartupWindow = null;
  }
  if (installWindow) {
    installWindow.close();
    installWindow = null;
  }
});

ipcMain.on('open-import-popup', (event, args) => {
  createImportPopup();
  importWarning = null
});

ipcMain.on('open-import-install-popup', (event, args) => {
  createImportInstallPopup();
  importWarning = null
  if (installProgressKeystore) {
    installProgressKeystore.close();
    installProgressKeystore = null;
  }
  if (installProgress) {
    installProgress.close();
    installProgress = null;
  }
});

ipcMain.on('send-input', (event, input) => {
    if (pythonProcess) {
        pythonProcess.stdin.write(input + "\n"); // Send input to Python process
    }
});

ipcMain.handle('get-logs', async (event, serviceName, lines) => {
  if (!serviceName) return 'Service name is required.';

  try {
    const command = `journalctl -u ${serviceName} --no-pager -n ${lines} --reverse`;
    const logs = await runCommand(command);
    return logs;
  } catch (error) {
    return `Error fetching logs for ${serviceName}`;
  }
});

function runCommand(command, args = []) {
  return new Promise((resolve, reject) => {
      exec(command, (error, stdout, stderr) => {
          if (error) {
              console.error(`exec error: ${error}`);
              return reject(stderr);
          }
          resolve(stdout);
      });
  });
}

ipcMain.handle('get-installed-versions', async (event) => {
    fetchInstalledClients();
  });

ipcMain.handle('get-running-services', async () => {
  const runningServices = await Promise.all(services.map(async (service) => {
      return new Promise((resolve) => {
          exec(`systemctl is-active ${service}`, (error, stdout, stderr) => {
              if (!error && stdout.trim() === 'active') {
                  resolve(service);
              } else {
                  resolve(null);
              }
          });
      });
  }));
  return runningServices.filter(Boolean); // Filter out null values
});

ipcMain.on('start-installation', (event, settings) => {
  if (settings.keystore === "yes") {
      if (!installProgressKeystore) createInstallProgressKeystoreWindow();
  } else {
      if (!installProgress) createInstallProgressWindow();
  }

  if (installWindow) {
      installWindow.close();
      installWindow = null;
  }
  if (installConfirmWindow) {
      installConfirmWindow.close();
      installConfirmWindow = null;
  }

  console.log("\nStarting installation with settings:");
  console.table(settings);

  const scriptPath = path.join(process.resourcesPath, 'modules', 'installer.py'); // Assume app is packaged

  const args = ['-u', scriptPath, settings.network, settings.execution, settings.consensus, settings.mevboost, settings.feeAddress];
  const childProcess = spawn('python3', args);

  childProcess.stdout.on('data', (data) => {
      const message = data.toString();
      const targetWindow = settings.keystore === "yes" ? installProgressKeystore : installProgress;
      if (message.includes("INSTALLATION") || message.includes("Version:") || message.includes("Network:")) {
          if (targetWindow) targetWindow.webContents.send('process-output', message);
      }
  });

  childProcess.on('close', (code) => {
      const message = code === 0 ? "---END OF INSTALLATION---" : "EXIT - PROCESS FAILED AT THIS POINT!";
      setTimeout(() => {
          const targetWindow = settings.keystore === "yes" ? installProgressKeystore : installProgress;
          if (targetWindow) targetWindow.webContents.send('process-complete', message);
          fetchInstalledClients();
      }, 3000);
  });

  handleChildProcessOutput(childProcess);
});

function postInstallationCheck() {
  fetchInstalledClients(() => {
    checkForMultipleClients();
  });
}

function checkForMultipleClients() {
  const multipleExecutionClientsInstalled = checkMultipleInstallations(executionClients);
  const multipleConsensusClientsInstalled = checkMultipleInstallations(consensusClients);
  
  if (multipleExecutionClientsInstalled || multipleConsensusClientsInstalled) {
    console.log("Action needed: More than two clients from a group are installed.");
    global.multipleClientsInstalled = true;
  } else {
    console.log("No duplicates found.");
    global.multipleClientsInstalled = false;
  }
}

ipcMain.on('start-update', (event, settings) => {
  if (!updateProgress) createUpdateProgressWindow();
  if (updateWindow) {
    updateWindow.close();
    updateWindow = null;
  }

  console.log("\nStarting Update with settings:");
  console.table(settings);

  global.appSettings = settings;

  const scriptPath = path.join(process.resourcesPath, 'modules', 'updater.py'); // Assume app is packaged

  const args = ['-u', scriptPath, settings.execution, settings.consensus, settings.mevboost];
  const childProcess = spawn('python3', args);

  childProcess.stdout.on('data', (data) => {
    let message = data.toString();
    if (message.includes("UPDATE") || message.includes("Version:") || message.includes("Execution:")) {
      if (updateProgress) updateProgress.webContents.send('process-output', message);
    }
  });

  childProcess.on('close', (code) => {
    setTimeout(() => {
      if (updateProgress) {
        let message = `Process exited with code ${code}`;
        if (code === 0) {
          message = "UPDATE COMPLETE! Click button to open Validator Dashboard.";
        } else if (code === 1) {
          message = "EXIT - UPDATE FAILED AT THIS POINT\n\n Please exit or go back to the main menu.";
        }
        updateProgress.webContents.send('process-complete', message);
        postInstallationCheck();
      }
    }, 3000);
  });

  handleChildProcessOutput(childProcess);
});

ipcMain.on('open-config-popup', (event, args) => {
  OpenConfigWindow();
  if (startupWindow) {
    startupWindow.close();
    startupWindow = null;
  }
  if (freshStartupWindow) {
    freshStartupWindow.close();
    freshStartupWindow = null;
  }
  if (installWindow) {
    installWindow.close();
    installWindow = null;
  }
});

ipcMain.on('open-preconfig-popup', (event, args) => {
  OpenPreConfigWindow();
  if (startupWindow) {
    startupWindow.close();
    startupWindow = null;
  }
  if (freshStartupWindow) {
    freshStartupWindow.close();
    freshStartupWindow = null;
  }
  if (installWindow) {
    installWindow.close();
    installWindow = null;
  }
});

ipcMain.on('minidash-start', (event) => {
  createMiniDash();
  if (installProgress) {
    installProgress.close();
    installProgress = null;
  }
  if (installProgressKeystore) {
    installProgressKeystore.close();
    installProgressKeystore = null;
  }

  if (updateProgress) {
    updateProgress.close();
    updateProgress = null;
  }

  if (importProgress) {
    importProgress.close();
    importProgress = null;
  }
});

ipcMain.on('journals-start', (event) => {
  journalsWindow = null;
  createJournalsWindow();
  if (miniDash) {
    miniDash.close();
    miniDash = null;
  }
});

function extractAndDisplayPrysmAccounts(logData) {
  const lines = logData.split('\n');
  const importedAccountsLine = lines.find(line => line.includes("Imported accounts"));

  if (importedAccountsLine) {
      const accountsInfo = importedAccountsLine.split('[')[1].split(']')[0];
      const accounts = accountsInfo.split(' ');

      // Use IPC to send the accounts to the renderer
      if (importProgress) {
          importProgress.webContents.send('process-output', "Imported Accounts:\n" + accounts.join('\n'));
      }
  } else {
      if (importProgress) {
          importProgress.webContents.send('process-output', "No accounts found in the log data.");
      }
  }
}

function extractAndDisplayNimbusKeystores(logData) {
  const lines = logData.split('\n');
  const keystoreFiles = [];
  const failureMessages = [];

  lines.forEach(line => {
      if (line.includes("Failed to import keystore")) {
          const filePathMatch = line.match(/file=(\/.*\.json)/);
          if (filePathMatch) {
              const errorMessageMatch = line.match(/err="(.*)"/);
              let errorMessage = errorMessageMatch ? errorMessageMatch[1] : "Unknown error";
              failureMessages.push(`FAILED TO IMPORT KEYSTORE:\n${filePathMatch[1]}\nError: ${errorMessage}\n`);
          }
      }
  });

  lines.forEach(line => { 
      if (line.includes("Keystore imported")) {
          const match = line.match(/file=(\/.*\.json)/);
          if (match) {
              keystoreFiles.push(match[1]);
          }
      }
  });

  // Use IPC to send the keystore file messages to the renderer
  if (importProgress && keystoreFiles.length > 0) {
      importProgress.webContents.send('process-output', "Successfully Imported Nimbus Keystores:\n\n" + keystoreFiles.join('\n\n'));
  } else if (importProgress) {
      importProgress.webContents.send('process-output', "No keystores imported or detected in the log data.");
  }
  if (importProgress) {
      if (failureMessages.length > 0) {
          importProgress.webContents.send('process-output', failureMessages.join('\n'));
      }
  }
}

function extractAndDisplayDuplicateKeys(logData) {
  const lines = logData.split('\n');
  const duplicateMessages = lines.filter(line => line.includes("Duplicate key in import"));

  if (duplicateMessages.length > 0) {
      const formattedDuplicates = duplicateMessages.map(line => {
          const parts = line.split("msg=");
          return parts[1] || "Unknown duplicate key message";
      }).join('\n');

      // Use IPC to send the duplicate key messages to the renderer
      if (importProgress) {
          importProgress.webContents.send('process-output', "Duplicate Keys Detected:\n" + formattedDuplicates);
      }
  }
}

function extractAndDisplayTekuKeystores(logData) {
  const lines = logData.split('\n');
  const keystoreFiles = [];

  lines.forEach(line => {
    if (line.includes("Processed Teku Keystore")) {
      const match = line.match(/keystore-m_.*\.json/); // Regex to match the keystore filename
      if (match) {
        keystoreFiles.push(match[0]);  // Push the found filename into keystoreFiles array
      }
    }
  });

    if (importProgress) {
        importProgress.webContents.send('process-output', "Successfully Imported Teku Keystore:\n" + keystoreFiles);
    }
}

function extractAndSendLighthouseMessages(logData) {
  const lines = logData.split('\n');
  lines.forEach(line => {
    // Define specific messages that should trigger output to the renderer
    const relevantMessages = [
      "Successfully imported",
      "Error: Command timed out."
    ];

    // Check if the line contains any of the relevant messages
    const isRelevantMessage = relevantMessages.some(message => line.includes(message));

    if (isRelevantMessage) {
      if (importProgress) {
        importProgress.webContents.send('process-output', line.trim());
      }
    }

    // Optionally, handle the enabled status separately if needed
    if (line.includes("(enabled)")) {
      if (importProgress) {
        importProgress.webContents.send('process-output', line.trim());
      }
    }
  });
}

function logEntry(type, data) {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] [${type.toUpperCase()}]: ${data.trim()}`);
}

// Function to handle output from child processes
function handleChildProcessOutput(child) {
  child.stdout.on('data', (data) => {
    logEntry('stdout', data.toString());
  });

  child.stderr.on('data', (data) => {
    logEntry('stderr', data.toString());
  });

  child.on('close', (code) => {
    logEntry('info', `Child process exited with code ${code}`);
  });
}

ipcMain.on('start-delete', (event, clientsToDelete) => {
  createDeleteProgressWindow();

  console.log("Received request to delete clients:", clientsToDelete);
  clientsToDelete.forEach(client => {
      deleteClient(client);
  });
});

function deleteClient(clientName) {
  const pythonScriptPath = path.join(process.resourcesPath, 'modules', 'deleter.py'); // Assume app is packaged

  const clientFunctionName = `delete_${clientName.toLowerCase()}`;
  console.log(`Deleting ${clientName} using function ${clientFunctionName}`);

  const env = { ...process.env }; // Inherit existing environment variables

  // Execute the Python script with the function name as an argument
  const childProcess = spawn('python3', [pythonScriptPath, clientFunctionName], { env });

  // Handle output from the child process
  childProcess.stdout.on('data', (data) => {
    let message = data.toString();
    console.log(message); // Log all output for debugging

    // Forward only the relevant "successfully deleted" messages to the renderer
    if (message.includes("Successfully Deleted")) {
      if (deleteProgress) {
        deleteProgress.webContents.send('process-output', message);
      }
    }
  });

  childProcess.stderr.on('data', (data) => {
    console.error(`ERROR: ${data.toString()}`);
    if (deleteProgress) {
      deleteProgress.webContents.send('process-output', `ERROR: ${data.toString()}`);
    }
  });

  childProcess.on('close', (code) => {
    console.log(`${clientName} deletion process exited with code ${code}`);
    let message = code === 0 ? "----DELETION PROCESS COMPLETE----" : `EXIT - PROCESS FAILED AT THIS POINT WITH CODE ${code}`;
    if (deleteProgress) {
      deleteProgress.webContents.send('process-complete', message);
    }
    postInstallationCheck();
  });
}

ipcMain.on('start-import', (event, settings) => {
  if (!importProgress) createImportProgressWindow();

  if (importWindow) {
    importWindow.close();
    importWindow = null;
  }

  if (importInstallWindow) {
    importInstallWindow.close();
    importInstallWindow = null;
  }

  console.log("\nStarting import with settings:");
  console.log("\nNetwork: ", settings.network, "\nConsensus: ", settings.consensus, "\nKeystore Path: ", settings.keystorePath);

  const scriptPath = path.join(process.resourcesPath, 'modules', 'importer.py'); // Assume app is packaged

  const env = {
    ...process.env, // Inherit existing environment variables
    MY_SECRET_PASSWORD: settings.password // Set the password only for the child process
  };

  const args = [settings.network, settings.consensus, settings.keystorePath];
  const childProcess = spawn('python3', ['-u', scriptPath, ...args], { env });

  childProcess.stderr.on('data', (data) => {
    let message = data.toString();
    if (message.includes("Successfully created new wallet")) {
      importProgress.webContents.send('process-output', "Successfully Created Prysm Wallet");
    }
    if (message.includes("Imported accounts")) {
      extractAndDisplayPrysmAccounts(message);
    }
    if (message.includes("no accounts were successfully imported")) {
      extractAndDisplayDuplicateKeys(message);
      importProgress.webContents.send('process-output', "No accounts were successfully imported");
    }
    if (message.includes("Keystore imported                          file=")) {
      extractAndDisplayNimbusKeystores(message);
    }
    if (settings.consensus.toLowerCase() === 'lighthouse' && message.includes("Successfully imported")) {
      extractAndSendLighthouseMessages(message);
    }
    if (message.includes("Error: Command timed out.")) {
      extractAndSendLighthouseMessages(message);
    }
  });

  childProcess.stdout.on('data', (data) => {
    let message = data.toString();
    if (message.includes("Keystore imported                          file=")) {
      extractAndDisplayNimbusKeystores(message);
    }
    if (message.includes("Failed to import keystore                  file=")) {
      extractAndDisplayNimbusKeystores(message);
    }
    if (message.includes("password was incorrect.")) {
      importProgress.webContents.send('process-output', "Incorrect Password");
    }
    if (message.includes("Processed Teku Keystore")) {
      extractAndDisplayTekuKeystores(message);
    }
    if (message.includes("Successfully imported")) {
      extractAndSendLighthouseMessages(message);
    }
    if (message.includes("LIGHTHOUSE VALIDATOR LIST")) {
      importProgress.webContents.send('process-output', "LIGHTHOUSE VALIDATOR LIST:");
    }
    if (message.includes("(enabled)")) {
      extractAndSendLighthouseMessages(message);
    }
  });

  childProcess.on('close', (code) => {
    const message = code === 0 ? "----END OF IMPORT PROCESS----" : "EXIT - PROCESS FAILED AT THIS POINT!";
    setTimeout(() => {
      if (importProgress) {
        importProgress.webContents.send('process-complete', message);
      }
      postInstallationCheck();
    }, 3000);
  });

  handleChildProcessOutput(childProcess);
});

process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  require('electron').dialog.showErrorBox('Uncaught Exception', error.message || "An error occurred");
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  require('electron').dialog.showErrorBox('Unhandled Rejection', reason.message || "An error occurred");
});
