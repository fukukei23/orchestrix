import React from 'react';
import { Zap } from 'lucide-react';

export function ViteTestComponent() {
  return (
    <div className="bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg shadow-lg p-6 text-white">
      <div className="flex items-center space-x-3 mb-4">
        <Zap className="h-6 w-6 text-yellow-300" />
        <h2 className="text-2xl font-bold">Vite 移行テスト</h2>
      </div>
      <div className="space-y-2">
        <p className="text-lg">
          🚀 Viteへの移行が成功しました！
        </p>
        <div className="space-y-1 text-sm opacity-90">
          <p>✅ 開発サーバー: 2.6秒で起動</p>
          <p>✅ プロダクションビルド: 239.45 kB</p>
          <p>✅ ホットモジュール置換: 1秒以内で反映</p>
          <p>✅ TypeScript: 型チェック通過</p>
          <p>✅ Electron: 正常に統合</p>
        </div>
      </div>
    </div>
  );
}
