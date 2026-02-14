import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  Activity,
  Zap,
  Settings,
  Menu,
  X,
} from 'lucide-react';

export function Layout() {
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = React.useState(true);

  const menuItems = [
    { path: '/', label: 'ダッシュボード', icon: LayoutDashboard },
    { path: '/tasks', label: 'タスク', icon: FileText },
    { path: '/agents', label: 'エージェント', icon: Zap },
    { path: '/analytics', label: '分析', icon: Activity },
    { path: '/settings', label: '設定', icon: Settings },
  ];

  return (
    <div className="flex h-screen bg-gray-100">
      {/* サイドバー */}
      <aside
        className={`${sidebarOpen ? 'w-64' : 'w-20'} transition-all duration-300 bg-gray-900 text-white flex flex-col`}
      >
        {/* ロゴ */}
        <div className="p-4 border-b border-gray-800">
          <div className="flex items-center gap-2">
            <Zap className="h-8 w-8 text-purple-400" />
            {!sidebarOpen && <span className="text-xl font-bold">Orchestrix</span>}
          </div>
        </div>

        {/* メニューアイテム */}
        <nav className="flex-1 p-4 space-y-2">
          {menuItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                location.pathname === item.path
                  ? 'bg-purple-600 text-white'
                  : 'hover:bg-gray-800 text-gray-300'
              }`}
            >
              <item.icon className="h-5 w-5 flex-shrink-0" />
              {sidebarOpen && <span>{item.label}</span>}
            </Link>
          ))}
        </nav>

        {/* サイドバートグル */}
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-4 border-t border-gray-800 hover:bg-gray-800 transition-colors"
        >
          <Menu className="h-6 w-6" />
        </button>
      </aside>

      {/* メインコンテンツ */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* ヘッダー */}
        <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">
              {menuItems.find(item => item.path === location.pathname)?.label || 'Orchestrix'}
            </h1>
          </div>
        </header>

        {/* ページコンテンツ */}
        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
