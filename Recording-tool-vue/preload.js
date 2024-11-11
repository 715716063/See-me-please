// preload.js

const { contextBridge, ipcRenderer } = require('electron');

// 使用 contextBridge 将 ipcRenderer 安全地暴露给渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
    sendMessage: (channel, data) => {
        // 允许的 channels
        const validChannels = ['toMain'];
        if (validChannels.includes(channel)) {
            ipcRenderer.send(channel, data);
        }
    },
    onMessage: (channel, callback) => {
        const validChannels = ['fromMain'];
        if (validChannels.includes(channel)) {
            ipcRenderer.on(channel, (event, ...args) => callback(...args));
        }
    }
});
