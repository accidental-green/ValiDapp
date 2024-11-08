const { contextBridge, ipcRenderer, shell } = require('electron');

contextBridge.exposeInMainWorld('electronShell', {
    openExternal: (url) => shell.openExternal(url)
});

contextBridge.exposeInMainWorld('electron', {
    getLogs: (service, lines) => ipcRenderer.invoke('get-logs', service, lines),
    checkClients: () => ipcRenderer.invoke('check-clients'),
    invoke: (channel, ...args) => ipcRenderer.invoke(channel, ...args),
});

contextBridge.exposeInMainWorld('api', {
    openStartupPopup: () => ipcRenderer.send('open-startup-popup'),
    openResourcesPopup: () => ipcRenderer.send('open-resources-popup'),
    openResourcesDashboardPopup: () => ipcRenderer.send('open-resources-dashboard-popup'),
    openFreshStartupPopup: () => ipcRenderer.send('open-fresh-startup-popup'),
    openConfigPopup: () => ipcRenderer.send('open-config-popup'),
    openPreConfigPopup: () => ipcRenderer.send('open-preconfig-popup'),
    openInstallPopup: () => ipcRenderer.send('open-install-popup'),
    openClientWarningPopup: () => ipcRenderer.send('open-client-warning-popup'),
    openInstallConfirmWindow: () => ipcRenderer.send('open-install-confirm-popup'),
    openUpdatePopup: () => ipcRenderer.send('open-update-popup'),
    openDeletePopup: () => ipcRenderer.send('open-delete-popup'),
    openImportPopup: () => ipcRenderer.send('open-import-popup'),
    openImportInstallPopup: () => ipcRenderer.send('open-import-install-popup'),
    openImportWarningPopup: () => ipcRenderer.send('open-import-warning-popup'),
    sendSettings: (settings) => ipcRenderer.send('settings-confirmed', settings),
    sendInstallSettings: (installSettings) => ipcRenderer.send('install-settings', installSettings),
    sendDeleteSettings: (deleteSettings) => ipcRenderer.send('delete-settings', deleteSettings),
    sendInstallationStart: (settings) => ipcRenderer.send('start-installation', settings),
    sendUpdateStart: (settings) => ipcRenderer.send('start-update', settings),
    sendDeleteStart: (settings) => ipcRenderer.send('start-delete', settings),
    sendImportStart: (settings) => ipcRenderer.send('start-import', settings),
    sendDashboardStart: () => ipcRenderer.send('minidash-start'),
    sendJournalsStart: () => ipcRenderer.send('journals-start'),
    
    sendInput: (input) => {
        ipcRenderer.send('send-input', input);
    },
    receive: (channel, func) => {
        ipcRenderer.on(channel, (event, ...args) => func(...args));
    },
    receiveSettings: (callback) => {
        ipcRenderer.on('load-install-settings', (event, settings) => callback(settings));
    },
});

contextBridge.exposeInMainWorld('electronAPI', {
    getStatus: (serviceName) => ipcRenderer.invoke('get-status', serviceName),
    checkServicesStatus: () => ipcRenderer.invoke('get-running-services'),
    startServices: (settings) => ipcRenderer.send('startServices', settings),
    stopServices: (settings) => ipcRenderer.send('stopServices', settings),
    requireSudo: () => ipcRenderer.invoke('check-sudo-privileges'),  // Add a new method for sudo checks
    notifySudoRequired: (callback) => {  // Setup a listener for sudo notifications
        ipcRenderer.on('sudo-required', (event, message) => {
            callback(message);
        });
    },
    receive: (channel, func) => {
        const validChannels = [
            'get-latest-versions', 'minidash-settings', 'get-installed-versions',
            'update-settings', 'delete-settings', 'install-settings', 'user-settings',
            'installed-users', 'process-output', 'process-complete', 'sudo-required' // Add 'sudo-required' to the list of valid channels
        ];
        if (validChannels.includes(channel)) {
            ipcRenderer.on(channel, (event, ...args) => func(...args));
        }
    },
});
