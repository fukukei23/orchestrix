import React, { useEffect, useState } from 'react';
import { useStore } from '../state/store';
import { Plus, Play, Trash2, Filter } from 'lucide-react';
import { format } from 'date-fns';

export function Tasks() {
  const tasks = useStore(state => state.tasks);
  const isLoading = useStore(state => state.isLoading);
  const fetchTasks = useStore(state => state.fetchTasks);
  const createTask = useStore(state => state.createTask);
  const executeTask = useStore(state => state.executeTask);

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    goal: '',
    complexity_score: 0.5,
    priority: 0,
  });

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const handleCreateTask = async () => {
    try {
      await createTask(newTask);
      setShowCreateModal(false);
      setNewTask({
        title: '',
        description: '',
        goal: '',
        complexity_score: 0.5,
        priority: 0,
      });
    } catch (error) {
      alert('タスクの作成に失敗しました');
    }
  };

  const handleExecuteTask = async (taskId: string) => {
    try {
      await executeTask(taskId);
    } catch (error) {
      alert('タスクの実行に失敗しました');
    }
  };

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">タスク</h1>
          <p className="text-gray-600 mt-1">
            タスクの作成・管理・実行
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
        >
          <Plus className="h-5 w-5" />
          <span>新規タスク</span>
        </button>
      </div>

      {/* タスクリスト */}
      <div className="bg-white rounded-lg shadow">
        {isLoading ? (
          <div className="p-12 text-center text-gray-600">
            読み込み中...
          </div>
        ) : tasks.length === 0 ? (
          <div className="p-12 text-center text-gray-600">
            タスクがありません
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {tasks.map(task => (
              <div key={task.id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {task.title}
                      </h3>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        task.status === 'completed' ? 'bg-green-100 text-green-800' :
                        task.status === 'running' ? 'bg-yellow-100 text-yellow-800' :
                        task.status === 'failed' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {task.status === 'completed' ? '完了' :
                         task.status === 'running' ? '実行中' :
                         task.status === 'failed' ? '失敗' : '待機中'}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {task.status === 'pending' && (
                      <button
                        onClick={() => handleExecuteTask(task.id)}
                        className="flex items-center gap-2 px-3 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                      >
                        <Play className="h-4 w-4" />
                        <span>実行</span>
                      </button>
                    )}
                  </div>
                </div>

                {/* タスク詳細 */}
                <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-600 mb-1">説明</p>
                    <p className="text-gray-900">
                      {task.description || '説明なし'}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-600 mb-1">ゴール</p>
                    <p className="text-gray-900">
                      {task.goal || 'ゴールなし'}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-600 mb-1">複雑度</p>
                    <p className="text-gray-900">
                      {task.complexity_score?.toFixed(2) || 'N/A'}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-600 mb-1">優先度</p>
                    <p className="text-gray-900">
                      {task.priority}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-600 mb-1">作成日時</p>
                    <p className="text-gray-900">
                      {format(new Date(task.created_at), 'yyyy/MM/dd HH:mm')}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 新規タスクモーダル */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">
                新規タスクの作成
              </h2>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <Trash2 className="h-6 w-6" />
              </button>
            </div>

            <form onSubmit={(e) => { e.preventDefault(); handleCreateTask(); }} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  タイトル *
                </label>
                <input
                  type="text"
                  required
                  value={newTask.title}
                  onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
                  placeholder="例: ユーザー認証機能の実装"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  説明
                </label>
                <textarea
                  value={newTask.description}
                  onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
                  placeholder="詳細な説明を入力してください"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  ゴール *
                </label>
                <textarea
                  required
                  value={newTask.goal}
                  onChange={(e) => setNewTask({ ...newTask, goal: e.target.value })}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
                  placeholder="例: ログイン機能を有効にする"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    複雑度 (0.0-1.0)
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.1"
                    value={newTask.complexity_score}
                    onChange={(e) => setNewTask({ ...newTask, complexity_score: parseFloat(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    優先度 (0-10)
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="10"
                    value={newTask.priority}
                    onChange={(e) => setNewTask({ ...newTask, priority: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-purple-500 focus:border-purple-500"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 transition-colors"
                >
                  キャンセル
                </button>
                <button
                  type="submit"
                  className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                >
                  作成
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
