const { app, BrowserWindow } = require('electron');
const path = require('path');

// 開発環境か本番環境かを判定
const isDev = process.env.NODE_ENV === 'development';

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 400,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js')
    },
    title: 'Orchestrix - AI Agent Orchestration Matrix',
    icon: path.join(__dirname, 'assets/icon.png') // アイコンがある場合
  });

  // 開発環境: localhost:3000 から読み込み
  // 本番環境: dist/index.html から読み込み
  if (isDev) {
    mainWindow.loadURL('http://localhost:3000');
    // 開発ツールを開く
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, 'dist/index.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// アプリの準備ができたらウィンドウを作成
app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    // macOS: Dockアイコンがクリックされたとき、ウィンドウがないなら作成
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// すべてのウィンドウが閉じられたらアプリを終了（macOS以外）
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// 開発環境: リロードショートカット
if (isDev) {
  app.on('ready', () => {
    // F5 または Command+R でリロード
    mainWindow.webContents.on('before-input-event', (event, input) => {
      if ((input.key === 'F5') || (input.key === 'r' && input.meta)) {
        mainWindow.reload();
      }
    });
  });
}
