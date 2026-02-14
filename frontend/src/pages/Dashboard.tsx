import React, { useEffect } from 'react';
import { useStore } from '../state/store';
import { Activity, TrendingUp, Clock, DollarSign, CheckCircle, AlertCircle, FileText } from 'lucide-react';
import { format } from 'date-fns';

export function Dashboard() {
  const tasks = useStore(state => state.tasks);
  const agents = useStore(state => state.agents);
  const executions = useStore(state => state.executions);
  const isLoading = useStore(state => state.isLoading);
  const fetchTasks = useStore(state => state.fetchTasks);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  // 統計計算
  const totalTasks = tasks.length;
  const completedTasks = tasks.filter(t => t.status === 'completed').length;
  const runningTasks = tasks.filter(t => t.status === 'running').length;
  const pendingTasks = tasks.filter(t => t.status === 'pending').length;

  const successRate = totalTasks > 0
    ? ((completedTasks / totalTasks) * 100).toFixed(1)
    : '0.0';

  const totalCost = executions.reduce((sum, e) => sum + (e.cost_usd || 0), 0);

  return (
    <div className="space-y-6">
      {/* ヘッダーセクション */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">
          ダッシュボード
        </h1>
        <p className="text-gray-600 mt-2">
          AIエージェントオーケストレーションの全体状況を確認
        </p>
      </div>

      {/* 統計カード */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* タスク数 */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-600">総タスク数</h3>
            <FileText className="h-5 w-5 text-blue-500" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{totalTasks}</p>
          <div className="mt-4 space-y-2 text-sm">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span className="text-gray-600">完了: {completedTasks}</span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-yellow-500" />
              <span className="text-gray-600">実行中: {runningTasks}</span>
            </div>
            <div className="flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-gray-400" />
              <span className="text-gray-600">待機中: {pendingTasks}</span>
            </div>
          </div>
        </div>

        {/* 成功率 */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-600">成功率</h3>
            <TrendingUp className="h-5 w-5 text-green-500" />
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

        {/* エージェント数 */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-600">エージェント数</h3>
            <Activity className="h-5 w-5 text-purple-500" />
          </div>
          <p className="text-3xl font-bold text-gray-900">{agents.length}</p>
          <div className="mt-4 space-y-1 text-sm">
            {agents.filter(a => a.enabled).map(agent => (
              <div key={agent.id} className="flex items-center gap-2">
                <CheckCircle className="h-3 w-3 text-green-500" />
                <span className="text-gray-600">{agent.name}</span>
              </div>
            ))}
          </div>
        </div>

        {/* 総コスト */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-600">総コスト</h3>
            <DollarSign className="h-5 w-5 text-yellow-500" />
          </div>
          <p className="text-3xl font-bold text-gray-900">
            ${totalCost.toFixed(2)}
          </p>
          <p className="mt-4 text-sm text-gray-600">
            過去7日間
          </p>
        </div>
      </div>

      {/* 最近の実行 */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-bold text-gray-900">最近の実行</h2>
        </div>
        <div className="p-6">
          {isLoading ? (
            <p className="text-center text-gray-600">読み込み中...</p>
          ) : executions.length === 0 ? (
            <p className="text-center text-gray-600">
              実行履歴がありません
            </p>
          ) : (
            <div className="space-y-4">
              {executions.slice(0, 5).map(execution => (
                <div
                  key={execution.id}
                  className="flex items-start justify-between p-4 bg-gray-50 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-gray-900">
                      タスク: {tasks.find(t => t.id === execution.task_id)?.title || 'Unknown'}
                    </p>
                    <p className="text-sm text-gray-600">
                      エージェント: {execution.agent_type || 'Unknown'}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className={`text-sm font-medium ${
                      execution.status === 'completed' ? 'text-green-600' :
                      execution.status === 'failed' ? 'text-red-600' :
                      'text-yellow-600'
                    }`}>
                      {execution.status === 'completed' ? '成功' :
                       execution.status === 'failed' ? '失敗' : '実行中'}
                    </p>
                    <p className="text-xs text-gray-500">
                      {format(new Date(execution.start_time), 'yyyy/MM/dd HH:mm')}
                    </p>
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
