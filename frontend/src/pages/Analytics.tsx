import React, { useState, useEffect } from 'react';
import { useStore } from '../state/store';
import { BarChart, TrendingUp, DollarSign, Activity, Clock, AlertCircle, PieChart } from 'lucide-react';
import { format } from 'date-fns';

export function Analytics() {
  const executions = useStore(state => state.executions);
  const tasks = useStore(state => state.tasks);
  const isLoading = useStore(state => state.isLoading);

  const [timeRange, setTimeRange] = useState(7);
  const [selectedTab, setSelectedTab] = useState<'executions' | 'agents' | 'cost' | 'trends'>('executions');

  useEffect(() => {
    // TODO: 実際にAPIからデータを取得
    // const fetchExecutions = useStore(state => state.fetchExecutions);
  }, []);

  const recentExecutions = executions.slice(0, 10);
  const successCount = executions.filter(e => e.status === 'success').length;
  const failedCount = executions.filter(e => e.status === 'failed').length;
  const successRate = executions.length > 0 ? (successCount / executions.length * 100).toFixed(1) : '0.0';

  const totalCost = executions.reduce((sum, e) => sum + (e.cost_usd || 0), 0);
  const avgCost = executions.length > 0 ? totalCost / executions.length : 0;

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">
          分析
        </h1>
        <p className="text-gray-600 mt-2">
          実行履歴とパフォーマンスの分析
        </p>
      </div>

      {/* タブ選択 */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setSelectedTab('executions')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            selectedTab === 'executions'
              ? 'bg-purple-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          <Activity className="h-5 w-5" />
          <span>実行履歴</span>
        </button>
        <button
          onClick={() => setSelectedTab('agents')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            selectedTab === 'agents'
              ? 'bg-purple-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          <Zap className="h-5 w-5" />
          <span>エージェント</span>
        </button>
        <button
          onClick={() => setSelectedTab('cost')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            selectedTab === 'cost'
              ? 'bg-purple-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          <DollarSign className="h-5 w-5" />
          <span>コスト</span>
        </button>
        <button
          onClick={() => setSelectedTab('trends')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            selectedTab === 'trends'
              ? 'bg-purple-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          <TrendingUp className="h-5 w-5" />
          <span>トレンド</span>
        </button>
      </div>

      {/* サマリーカード */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* 実行数カード */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">総実行数</h3>
            <BarChart className="h-8 w-8 text-blue-500" />
          </div>
          <p className="text-3xl font-bold text-gray-900">
            {executions.length}
          </p>
          <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span className="text-gray-600">成功: {successCount}</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <span className="text-gray-600">失敗: {failedCount}</span>
            </div>
          </div>
        </div>

        {/* 成功率カード */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">成功率</h3>
            <TrendingUp className="h-8 w-8 text-green-500" />
          </div>
          <p className="text-3xl font-bold text-gray-900">
            {successRate}%
          </p>
          <div className="mt-4">
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-green-500 transition-all"
                style={{ width: `${successRate}%` }}
              />
            </div>
          </div>
        </div>

        {/* コストカード */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">総コスト</h3>
            <DollarSign className="h-8 w-8 text-yellow-500" />
          </div>
          <p className="text-3xl font-bold text-gray-900">
            ${totalCost.toFixed(2)}
          </p>
          <div className="mt-4 space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">平均コスト</span>
              <span className="text-gray-900 font-mono">
                ${avgCost.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">期間</span>
              <span className="text-gray-900">
                過去 {timeRange} 日
              </span>
            </div>
          </div>
        </div>

        {/* タスク数カード */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">タスク数</h3>
            <PieChart className="h-8 w-8 text-purple-500" />
          </div>
          <p className="text-3xl font-bold text-gray-900">
            {tasks.length}
          </p>
          <div className="mt-4 space-y-2 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span className="text-gray-600">完了</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
              <span className="text-gray-600">実行中</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-gray-400"></div>
              <span className="text-gray-600">待機中</span>
            </div>
          </div>
        </div>
      </div>

      {/* 最近の実行履歴 */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            最近の実行
          </h2>
        </div>
        <div className="p-6">
          {isLoading ? (
            <div className="text-center text-gray-600">
              読み込み中...
            </div>
          ) : recentExecutions.length === 0 ? (
            <div className="text-center text-gray-600">
              実行履歴がありません
            </div>
          ) : (
            <div className="space-y-4">
              {recentExecutions.map(execution => (
                <div
                  key={execution.id}
                  className="flex items-start justify-between p-4 bg-gray-50 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-gray-900 mb-1">
                      {tasks.find(t => t.id === execution.task_id)?.title || 'Unknown Task'}
                    </p>
                    <p className="text-sm text-gray-600">
                      エージェント: {execution.agent_type || 'Unknown'}
                    </p>
                    <p className="text-sm text-gray-600">
                      モデル: {execution.model_used || 'Unknown'}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className={`text-sm font-medium ${
                      execution.status === 'success' ? 'text-green-600' :
                      execution.status === 'failed' ? 'text-red-600' :
                      'text-yellow-600'
                    }`}>
                      {execution.status === 'success' ? '成功' :
                       execution.status === 'failed' ? '失敗' : '実行中'}
                    </p>
                    {execution.status !== 'success' && execution.start_time && (
                      <p className="text-xs text-gray-500 mt-1">
                        {format(new Date(execution.start_time), 'yyyy/MM/dd HH:mm')}
                      </p>
                    )}
                    {execution.cost_usd && execution.status === 'success' && (
                      <p className="text-sm font-medium text-gray-900">
                        ${execution.cost_usd.toFixed(4)}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
