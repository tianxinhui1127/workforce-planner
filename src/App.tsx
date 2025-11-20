import React, { useEffect } from 'react';
import { useWorkforceStore } from './stores/workforceStore';
import ProjectSelector from './components/ProjectSelector';
import ConfigurationPanel from './components/ConfigurationPanel';
import ActionPanel from './components/ActionPanel';

function App() {
  const { initializeProjects } = useWorkforceStore();
  
  useEffect(() => {
    // 确保只初始化一次
    initializeProjects();
  }, []); // 空依赖数组，确保只执行一次
  
  return (
    <div className="min-h-screen" style={{ backgroundColor: '#f0f9ff' }}>
      {/* 顶部标题区域 */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold mb-2 flex items-center justify-center gap-3">
              🚧 工程劳动力计划生成器
            </h1>
            <p className="text-blue-100 text-lg">智能生成各类工程劳动力配置计划</p>
          </div>
        </div>
      </div>
      
      {/* 主要内容区域 */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* 左侧项目选择区 */}
          <div className="lg:col-span-1">
            <div className="sticky top-8">
              <ProjectSelector />
            </div>
          </div>
          
          {/* 右侧配置区 */}
          <div className="lg:col-span-3 space-y-8">
            <ConfigurationPanel />
            <ActionPanel />
          </div>
        </div>
      </div>
      
      {/* 底部信息 */}
      <footer className="bg-white border-t border-gray-200 py-6 mt-12">
        <div className="container mx-auto px-4 text-center text-gray-600">
          <p className="text-sm">
            💡 提示：选择工程类型 → 配置各阶段参数 → 生成劳动力计划
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
