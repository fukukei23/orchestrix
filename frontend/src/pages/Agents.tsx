import React, { useState, useEffect } from 'react';
import { useStore } from '../state/store';
import { Settings, Zap, ToggleLeft, ToggleRight, Trash2 } from 'lucide-react';
import { format } from 'date-fns';

export function Agents() {
  const agents = useStore(state => state.agents);
  const fetchAgents = useStore(state => state.fetchAgents);
  const toggleAgent = useStore(state => state.toggleAgent);
  const isLoading = useStore(state => state.isLoading);

  const [filterStatus, setFilterStatus] = useState<'all' | 'enabled' | 'disabled'>('all');

  useEffect(() => {
    fetchAgents();
  }, [fetchAgents]);

  const enabledAgents = agents.filter(a => a.enabled);
  const disabledAgents = agents.filter(a => !a.enabled);

  const filteredAgents = () => {
    switch (filterStatus) {
      case 'all': return agents;
      case 'enabled': return enabledAgents;
      case 'disabled': return disabledAgents;
    }
  };

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">
          エージェント管理
        </h1>
        <p className="text-gray-600 mt-2">
          AIエージェントの設定と有効/無効を管理
        </p>
      </div>

      {/* フィルター */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setFilterStatus('all')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filterStatus === 'all'
              ? 'bg-purple-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          全て ({agents.length})
        </button>
        <button
          onClick={() => setFilterStatus('enabled')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filterStatus === 'enabled'
              ? 'bg-green-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          有効 ({enabledAgents.length})
        </button>
        <button
          onClick={() => setFilterStatus('disabled')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filterStatus === 'disabled'
              ? 'bg-red-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          無効 ({disabledAgents.length})
        </button>
      </div>

      {/* エージェント一覧 */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center text-gray-600">
            読み込み中...
          </div>
        ) : filteredAgents().length === 0 ? (
          <div className="p-12 text-center text-gray-600">
            {filterStatus === 'all' && 'エージェントがありません'}
            {filterStatus === 'enabled' && '有効なエージェントがありません'}
            {filterStatus === 'disabled' && '無効なエージェントがありません'}
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {filteredAgents().map(agent => (
              <div
                key={agent.id}
                className={`p-6 transition-colors ${
                  agent.enabled ? 'hover:bg-green-50' : 'hover:bg-red-50'
                }`}
              >
                {/* ステータス */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <Settings className="h-6 w-6 text-purple-500" />
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">
                        {agent.name}
                      </h3>
                      <p className="text-sm text-gray-600">
                        CLIコマンド: <code className="bg-gray-100 px-2 py-1 rounded text-purple-600">{agent.cli_command}</code>
                      </p>
                    </div>
                  </div>
                  {/* トグルボタン */}
                  <button
                    onClick={() => toggleAgent(agent.id, !agent.enabled)}
                    className={`p-2 rounded-lg transition-colors ${
                      agent.enabled
                        ? 'bg-red-100 text-red-700 hover:bg-red-200'
                        : 'bg-green-100 text-green-700 hover:bg-green-200'
                    }`}
                  >
                    {agent.enabled ? (
                      <>
                        <ToggleRight className="h-5 w-5" />
                        <span className="ml-2">無効にする</span>
                      </>
                    ) : (
                      <>
                        <ToggleLeft className="h-5 w-5" />
                        <span className="ml-2">有効にする</span>
                      </>
                    )}
                  </button>
                </div>

                {/* 詳細情報 */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-1">
                      デフォルトモデル
                    </p>
                    <p className="text-gray-900 font-mono">
                      {agent.default_model || 'N/A'}
                    </p>
                  </div>

                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-1">
                      サポート機能
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {agent.supports_features.length === 0 ? (
                        <span className="text-gray-500">なし</span>
                      ) : (
                        agent.supports_features.map((feature, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-sm"
                          >
                            {feature}
                          </span>
                        ))
                      )}
                    </div>
                  </div>

                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-1">
                      入力コスト
                    </p>
                    <p className="text-gray-900 font-mono">
                      ${agent.cost_per_1k_input?.toFixed(4) || 'N/A'} / 1k tokens
                    </p>
                  </div>

                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-1">
                      出力コスト
                    </p>
                    <p className="text-gray-900 font-mono">
                      ${agent.cost_per_1k_output?.toFixed(4) || 'N/A'} / 1k tokens
                    </p>
                  </div>

                  {/* 合計コスト見積もり */}
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <p className="text-sm font-medium text-gray-600">
                      合計コスト見積もり（1k入力+1k出力）
                    </p>
                    <p className="text-lg font-bold text-gray-900">
                      ${(agent.cost_per_1k_input + agent.cost_per_1k_output).toFixed(4)}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 統計情報 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          統計
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-purple-50 rounded-lg p-4">
            <p className="text-2xl font-bold text-purple-900">
              {agents.length}
            </p>
            <p className="text-sm text-gray-600 mt-1">
              総エージェント数
            </p>
          </div>

          <div className="bg-green-50 rounded-lg p-4">
            <p className="text-2xl font-bold text-green-900">
              {enabledAgents.length}
            </p>
            <p className="text-sm text-gray-600 mt-1">
              有効なエージェント
            </p>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-2xl font-bold text-gray-900">
              {disabledAgents.length}
            </p>
            <p className="text-sm text-gray-600 mt-1">
              無効なエージェント
            </p>
          </div>
        </div>

        {/* コスト比較 */}
        <div className="mt-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">
            コスト効率比較
          </h3>
          <div className="space-y-2">
            {agents
              .filter(a => a.enabled)
              .sort((a, b) => a.cost_per_1k_input + a.cost_per_1k_output - (b.cost_per_1k_input + b.cost_per_1k_output))
              .slice(0, 3)
              .map((agent, index) => (
                <div key={agent.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                  <div>
                    <p className="font-medium text-gray-900">
                      #{index + 1} {agent.name}
                    </p>
                    <p className="text-sm text-gray-600">
                      ${(agent.cost_per_1k_input + agent.cost_per_1k_output).toFixed(2)} / 1k tokens
                    </p>
                  </div>
                  <div className="text-green-600 font-semibold">
                    最もコスト効率
                  </div>
                </div>
              ))}
          </div>
        </div>
      </div>
    </div>
  );
}
