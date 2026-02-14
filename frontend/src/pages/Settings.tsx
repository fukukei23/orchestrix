import React, { useState } from 'react';
import { useStore } from '../state/store';
import { Save, X, Server, Database, Globe, Sliders, RefreshCw, Download, Key } from 'lucide-react';

export function Settings() {
  const apiBaseUrl = useStore(state => state.apiBaseUrl);
  const [settings, setSettings] = useState({
    apiBaseUrl: apiBaseUrl,
    theme: 'light',
    notifications: true,
    autoRefresh: false,
  });

  const handleSave = () => {
    // TODO: 設定を保存する
    alert('設定が保存されました');
  };

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">
          設定
        </h1>
        <p className="text-gray-600 mt-2">
          Orchestrix の動作設定
        </p>
      </div>

      {/* API設定 */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex items-center gap-3 mb-6 pb-4 border-b border-gray-200">
          <Server className="h-6 w-6 text-purple-500" />
          <h2 className="text-lg font-semibold text-gray-900">
            API設定
          </h2>
        </div>

        {/* APIベースURL */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            APIベースURL
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={settings.apiBaseUrl}
              onChange={(e) => setSettings({ ...settings, apiBaseUrl: e.target.value })}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
              placeholder="http://localhost:8000/api/v1"
            />
            <button
              onClick={() => setSettings({ ...settings, apiBaseUrl: 'http://localhost:8000/api/v1' })}
              className="px-3 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
            </button>
          </div>
          <p className="text-sm text-gray-600 mt-1">
            Orchestrix APIのベースURLを設定
          </p>
        </div>

        {/* ヘルスチェック間隔 */}
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            ヘルスチェック間隔（秒）
          </label>
          <input
            type="number"
            value={30000}
            onChange={(e) => setSettings({ ...settings, healthCheckInterval: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
            min="5"
          />
        </div>

        {/* ボタン */}
        <div className="flex justify-end gap-3 mt-4">
          <button
            onClick={() => setSettings({ ...settings, apiBaseUrl: 'http://localhost:8000/api/v1' })}
            className="px-4 py-2 text-gray-700 hover:bg-gray-100 transition-colors"
          >
            リセット
          </button>
          <button
            onClick={handleSave}
            className="flex items-center gap-2 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            <Save className="h-4 w-4" />
            <span>保存</span>
          </button>
        </div>
      </div>

      {/* エージェント設定 */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex items-center gap-3 mb-6 pb-4 border-b border-gray-200">
          <Zap className="h-6 w-6 text-purple-500" />
          <h2 className="text-lg font-semibold text-gray-900">
            エージェント設定
          </h2>
        </div>

        {/* デフォルトエージェント */}
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            デフォルトエージェント
          </label>
          <select
            value="claude_code"
            onChange={(e) => setSettings({ ...settings, defaultAgent: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
          >
            <option value="claude_code">Claude Code</option>
            <option value="codex_cli">Codex CLI</option>
            <option value="gemini_cli">Gemini CLI</option>
          </select>
          <p className="text-sm text-gray-600 mt-1">
            複雑なタスクに使用するデフォルトのエージェント
          </p>
        </div>

        {/* 自動切替設定 */}
        <div className="mt-4">
          <label className="flex items-center gap-2 mb-2">
            <input
              type="checkbox"
              checked={settings.autoFallback}
              onChange={(e) => setSettings({ ...settings, autoFallback: e.target.checked })}
              className="w-4 h-4 text-purple-600 focus:ring-purple-500"
            />
            <span className="text-sm font-medium text-gray-700">
              失敗時に自動的にエージェントを切り替える
            </span>
          </label>
          <p className="text-sm text-gray-600 mt-1">
            タスク実行が失敗したら、自動的に代替エージェントを使用
          </p>
        </div>

        {/* 最大リトライ回数 */}
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            最大リトライ回数
          </label>
          <input
            type="number"
            value={3}
            onChange={(e) => setSettings({ ...settings, maxRetries: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
            min="1"
            max="10"
          />
          <p className="text-sm text-gray-600 mt-1">
            エージェント切替時の最大試行回数
          </p>
        </div>

        {/* ボタン */}
        <div className="flex justify-end gap-3 mt-4">
          <button
            onClick={() => setSettings({ ...settings, maxRetries: 3 })}
            className="px-4 py-2 text-gray-700 hover:bg-gray-100 transition-colors"
          >
            リセット
          </button>
          <button
            onClick={handleSave}
            className="flex items-center gap-2 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            <Save className="h-4 w-4" />
            <span>保存</span>
          </button>
        </div>
      </div>

      {/* データベース設定 */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex items-center gap-3 mb-6 pb-4 border-b border-gray-200">
          <Database className="h-6 w-6 text-purple-500" />
          <h2 className="text-lg font-semibold text-gray-900">
            データベース設定
          </h2>
        </div>

        {/* データベース接続文字列 */}
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            データベースURL（環境変数から読み取り）
          </label>
          <div className="p-3 bg-gray-100 rounded-lg font-mono text-sm">
            postgresql://orchestrix:orchestrix_dev@localhost:5432/orchestrix
          </div>
          <p className="text-sm text-gray-600 mt-1">
            .env ファイルの DATABASE_URL から設定されます
          </p>
        </div>

        {/* 接続プール設定 */}
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            接続プールサイズ
          </label>
          <select
            value="10"
            onChange={(e) => setSettings({ ...settings, connectionPoolSize: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
          >
            <option value="5">5</option>
            <option value="10">10</option>
            <option value="20">20</option>
            <option value="50">50</option>
          </select>
          <p className="text-sm text-gray-600 mt-1">
            同時接続数の上限
          </p>
        </div>

        {/* ボタン */}
        <div className="flex justify-end gap-3 mt-4">
          <button
            onClick={() => {
              // TODO: データベース接続をテスト
              alert('データベース接続をテスト中...');
            }}
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
          >
            <RefreshCw className="h-4 w-4" />
            <span>接続テスト</span>
          </button>
          <button
            onClick={handleSave}
            className="flex items-center gap-2 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            <Save className="h-4 w-4" />
            <span>保存</span>
          </button>
        </div>
      </div>

      {/* Redis設定 */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex items-center gap-3 mb-6 pb-4 border-b border-gray-200">
          <Database className="h-6 w-6 text-red-500" />
          <h2 className="text-lg font-semibold text-gray-900">
            Redis設定
          </h2>
        </div>

        {/* Redis接続文字列 */}
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Redis URL（環境変数から読み取り）
          </label>
          <div className="p-3 bg-gray-100 rounded-lg font-mono text-sm">
            redis://localhost:6379/0
          </div>
          <p className="text-sm text-gray-600 mt-1">
            .env ファイルの REDIS_URL から設定されます
          </p>
        </div>

        {/* キーの有効期限 */}
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            キーの有効期限（秒）
          </label>
          <input
            type="number"
            value={3600}
            onChange={(e) => setSettings({ ...settings, keyExpiry: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
            min="60"
          />
          <p className="text-sm text-gray-600 mt-1">
            結果保存の有効期限（デフォルト: 1時間）
          </p>
        </div>

        {/* ボタン */}
        <div className="flex justify-end gap-3 mt-4">
          <button
            onClick={() => {
              // TODO: Redis接続をテスト
              alert('Redis接続をテスト中...');
            }}
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
          >
            <RefreshCw className="h-4 w-4" />
            <span>接続テスト</span>
          </button>
          <button
            onClick={handleSave}
            className="flex items-center gap-2 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            <Save className="h-4 w-4" />
            <span>保存</span>
          </button>
        </div>
      </div>

      {/* 通知設定 */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex items-center gap-3 mb-6 pb-4 border-b border-gray-200">
          <Key className="h-6 w-6 text-purple-500" />
          <h2 className="text-lg font-semibold text-gray-900">
            通知設定
          </h2>
        </div>

        {/* 自動更新 */}
        <div className="flex items-center gap-2 mb-4">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={settings.autoRefresh}
              onChange={(e) => setSettings({ ...settings, autoRefresh: e.target.checked })}
              className="w-4 h-4 text-purple-600 focus:ring-purple-500"
            />
            <span className="text-sm font-medium text-gray-700">
              自動的にデータを更新
            </span>
          </label>
        </div>
        <p className="text-sm text-gray-600 mt-1 ml-6">
          有効にすると、ダッシュボードが自動的に最新データを取得
        </p>
        </div>

        {/* 更新間隔 */}
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            更新間隔（秒）
          </label>
          <input
            type="number"
            value={30}
            onChange={(e) => setSettings({ ...settings, refreshInterval: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
            min="5"
            disabled={!settings.autoRefresh}
          />
        </div>

        {/* ボタン */}
        <div className="flex justify-end gap-3 mt-4">
          <button
            onClick={handleSave}
            className="flex items-center gap-2 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            <Save className="h-4 w-4" />
            <span>保存</span>
          </button>
        </div>
      </div>

      {/* アプリケーション設定 */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center gap-3 mb-6 pb-4 border-b border-gray-200">
          <Globe className="h-6 w-6 text-purple-500" />
          <h2 className="text-lg font-semibold text-gray-900">
            アプリケーション設定
          </h2>
        </div>

        {/* 言語設定 */}
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            言語
          </label>
          <select
            value="ja"
            onChange={(e) => setSettings({ ...settings, language: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
          >
            <option value="ja">日本語</option>
            <option value="en">English</option>
          </select>
        </div>

        {/* テーマ設定 */}
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            テーマ
          </label>
          <select
            value={settings.theme}
            onChange={(e) => setSettings({ ...settings, theme: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
          >
            <option value="light">ライト</option>
            <option value="dark">ダーク</option>
            <option value="system">システム</option>
          </select>
        </div>

        {/* ボタン */}
        <div className="flex justify-end gap-3 mt-6 pt-4 border-t border-gray-200">
          <button
            onClick={() => setSettings({
              apiBaseUrl: 'http://localhost:8000/api/v1',
              defaultAgent: 'claude_code',
              autoFallback: false,
              maxRetries: 3,
              connectionPoolSize: 10,
              keyExpiry: 3600,
              autoRefresh: false,
              refreshInterval: 30,
              language: 'ja',
              theme: 'light',
            })}
            className="px-4 py-2 text-gray-700 hover:bg-gray-100 transition-colors"
          >
            <RefreshCw className="h-4 w-4" />
            <span>リセット</span>
          </button>
          <button
            onClick={handleSave}
            className="flex items-center gap-2 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            <Save className="h-4 w-4" />
            <span>保存</span>
          </button>
        </div>
      </div>

      {/* システム情報 */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center gap-3 mb-6 pb-4 border-b border-gray-200">
          <Sliders className="h-6 w-6 text-purple-500" />
          <h2 className="text-lg font-semibold text-gray-900">
            システム情報
          </h2>
        </div>

        <div className="space-y-3">
          <div className="flex justify-between py-2 border-b border-gray-100">
            <span className="text-gray-600">バージョン</span>
            <span className="text-gray-900 font-mono">1.0.0</span>
          </div>

          <div className="flex justify-between py-2 border-b border-gray-100">
            <span className="text-gray-600">ビルド</span>
            <span className="text-gray-900">Development</span>
          </div>

          <div className="flex justify-between py-2 border-b border-gray-100">
            <span className="text-gray-600">環境</span>
            <span className="text-gray-900">WSL Ubuntu</span>
          </div>

          <div className="flex justify-between py-2">
            <span className="text-gray-600">リポジトリ</span>
            <a
              href="https://github.com/fukukei23/orchestrix"
              target="_blank"
              rel="noopener noreferrer"
              className="text-purple-600 hover:text-purple-700"
            >
              fukukei23/orchestrix
              <X className="inline-block w-4 h-4 ml-1" />
            </a>
          </div>

          <div className="flex justify-between py-2">
            <span className="text-gray-600">ドキュメント</span>
            <a
              href="https://github.com/fukukei23/orchestrix#readme"
              target="_blank"
              rel="noopener noreferrer"
              className="text-purple-600 hover:text-purple-700"
            >
              README.md
              <Download className="inline-block w-4 h-4 ml-1" />
            </a>
          </div>
        </div>
      </div>

      {/* 保存ボタン */}
      <div className="fixed bottom-0 right-0 p-6 bg-white border-t border-gray-200 shadow-lg">
        <div className="flex gap-3">
          <button
            onClick={() => window.history.back()}
            className="px-4 py-2 text-gray-700 hover:bg-gray-100 transition-colors"
          >
            キャンセル
          </button>
          <button
            onClick={handleSave}
            className="flex items-center gap-2 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            <Save className="h-4 w-4" />
            <span>全ての変更を保存</span>
          </button>
        </div>
      </div>
    </div>
  );
}
