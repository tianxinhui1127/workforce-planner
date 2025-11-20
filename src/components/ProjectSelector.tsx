import React, { useState } from 'react';
import { useWorkforceStore } from '../stores/workforceStore';
import { PROJECT_TYPES } from '../constants/workforce';

const ProjectSelector: React.FC = () => {
  const { projects, toggleProject, selectProject, selectedProject, createTunnelProject, deleteTunnelProject, createBridgeProject, deleteBridgeProject } = useWorkforceStore();
  const [showTunnelForm, setShowTunnelForm] = useState(false);
  const [newTunnelName, setNewTunnelName] = useState('');
  const [showBridgeForm, setShowBridgeForm] = useState(false);
  const [newBridgeName, setNewBridgeName] = useState('');
  
  return (
    <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
      <h2 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-3">
        <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
          📋
        </div>
        选择工程类型
      </h2>
      
      {/* 添加隧道工程表单 */}
      {showTunnelForm && (
        <div className="mb-4 p-4 bg-orange-50 rounded-lg border border-orange-200">
          <h3 className="text-sm font-medium text-orange-800 mb-3">添加新隧道工程</h3>
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="输入隧道工程名称"
              value={newTunnelName}
              onChange={(e) => setNewTunnelName(e.target.value)}
              className="flex-1 px-3 py-2 border border-orange-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
              onKeyPress={(e) => {
                if (e.key === 'Enter' && newTunnelName.trim()) {
                  createTunnelProject(newTunnelName.trim());
                  setNewTunnelName('');
                  setShowTunnelForm(false);
                }
              }}
            />
            <button
              onClick={() => {
                if (newTunnelName.trim()) {
                  createTunnelProject(newTunnelName.trim());
                  setNewTunnelName('');
                  setShowTunnelForm(false);
                }
              }}
              className="px-4 py-2 bg-orange-600 text-white rounded-md text-sm hover:bg-orange-700 transition-colors"
            >
              添加
            </button>
            <button
              onClick={() => {
                setShowTunnelForm(false);
                setNewTunnelName('');
              }}
              className="px-4 py-2 bg-gray-500 text-white rounded-md text-sm hover:bg-gray-600 transition-colors"
            >
              取消
            </button>
          </div>
        </div>
      )}

      {/* 添加桥梁工程表单 */}
      {showBridgeForm && (
        <div className="mb-4 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
          <h3 className="text-sm font-medium text-yellow-800 mb-3">添加新桥梁工程</h3>
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="输入桥梁工程名称"
              value={newBridgeName}
              onChange={(e) => setNewBridgeName(e.target.value)}
              className="flex-1 px-3 py-2 border border-yellow-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-yellow-500"
              onKeyPress={(e) => {
                if (e.key === 'Enter' && newBridgeName.trim()) {
                  createBridgeProject(newBridgeName.trim());
                  setNewBridgeName('');
                  setShowBridgeForm(false);
                }
              }}
            />
            <button
              onClick={() => {
                if (newBridgeName.trim()) {
                  createBridgeProject(newBridgeName.trim());
                  setNewBridgeName('');
                  setShowBridgeForm(false);
                }
              }}
              className="px-4 py-2 bg-yellow-600 text-white rounded-md text-sm hover:bg-yellow-700 transition-colors"
            >
              添加
            </button>
            <button
              onClick={() => {
                setShowBridgeForm(false);
                setNewBridgeName('');
              }}
              className="px-4 py-2 bg-gray-500 text-white rounded-md text-sm hover:bg-gray-600 transition-colors"
            >
              取消
            </button>
          </div>
        </div>
      )}

      <div className="space-y-4">
        {/* 渲染固定项目类型 */}
        {Object.entries(PROJECT_TYPES).map(([key, project]) => {
          const isEnabled = projects[key]?.enabled || false;
          
          return (
            <div
              key={key}
              className={`p-4 rounded-xl border-2 transition-all duration-300 cursor-pointer transform hover:scale-[1.02] ${
                selectedProject === key
                  ? 'border-green-500 bg-gradient-to-r from-green-50 to-emerald-50 shadow-lg'
                  : isEnabled
                  ? 'border-blue-500 bg-gradient-to-r from-blue-50 to-indigo-50 shadow-md'
                  : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'
              }`}
              onClick={() => {
                // 如果项目已启用，只进行导航选择，不切换启用状态
                if (isEnabled) {
                  selectProject(key);
                } else {
                  // 如果项目未启用，则启用并选择
                  toggleProject(key);
                  selectProject(key);
                }
              }}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div 
                    className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl shadow-sm"
                    style={{ 
                      backgroundColor: isEnabled ? `${project.color}20` : '#f8fafc',
                      color: isEnabled ? project.color : '#64748b'
                    }}
                  >
                    {project.icon}
                  </div>
                  <div>
                    <h3 
                      className="font-bold text-gray-800 text-lg"
                      style={{ color: isEnabled ? project.color : undefined }}
                    >
                      {project.name}
                    </h3>
                    <p className="text-sm text-gray-500 mt-1">
                      包含 {project.modules.length} 个施工阶段
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  {isEnabled && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation(); // 防止触发卡片点击事件
                        toggleProject(key);
                        // 如果取消的是当前选中的项目，需要选择其他项目
                        if (selectedProject === key) {
                          const remainingProjects = Object.keys(projects).filter(k => 
                            projects[k]?.enabled && k !== key
                          );
                          if (remainingProjects.length > 0) {
                            selectProject(remainingProjects[0]);
                          }
                        }
                      }}
                      className="text-red-600 hover:text-red-800 text-sm bg-red-100 hover:bg-red-200 px-2 py-1 rounded-full transition-colors"
                      title="取消选择"
                    >
                      ✕
                    </button>
                  )}
                  <div
                    className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all duration-200 ${
                      isEnabled
                        ? 'border-blue-500 bg-blue-500 shadow-md'
                        : 'border-gray-300 bg-white'
                    }`}
                  >
                    {isEnabled && (
                      <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    )}
                  </div>
                </div>
              </div>
              
              {isEnabled && (
                <div className="mt-3 pt-3 border-t border-blue-100">
                  <div className="flex flex-wrap gap-2">
                    {project.modules.slice(0, 2).map((module, index) => (
                      <span key={index} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                        {module}
                      </span>
                    ))}
                    {project.modules.length > 2 && (
                      <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                        +{project.modules.length - 2}
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
        
        {/* 渲染动态隧道工程 */}
        {Object.entries(projects).filter(([key, project]) => 
          key.startsWith('tunnel_') && project
        ).map(([key, project]) => {
          const isEnabled = project.enabled || false;
          
          return (
            <div
              key={key}
              className={`p-4 rounded-xl border-2 transition-all duration-300 cursor-pointer transform hover:scale-[1.02] ${
                selectedProject === key
                  ? 'border-green-500 bg-gradient-to-r from-green-50 to-emerald-50 shadow-lg'
                  : isEnabled
                  ? 'border-orange-500 bg-gradient-to-r from-orange-50 to-amber-50 shadow-md'
                  : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'
              }`}
              onClick={() => {
                if (isEnabled) {
                  selectProject(key);
                } else {
                  toggleProject(key);
                  selectProject(key);
                }
              }}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div 
                    className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl shadow-sm"
                    style={{ 
                      backgroundColor: isEnabled ? '#FFB74D20' : '#f8fafc',
                      color: isEnabled ? '#FF9800' : '#64748b'
                    }}
                  >
                    🚇
                  </div>
                  <div>
                    <h3 
                      className="font-bold text-gray-800 text-lg"
                      style={{ color: isEnabled ? '#FF9800' : undefined }}
                    >
                      {project.name || '隧道工程'}
                    </h3>
                    <p className="text-sm text-gray-500 mt-1">
                      隧道工程 - 4个施工阶段
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteTunnelProject(key);
                    }}
                    className="text-red-600 hover:text-red-800 text-sm bg-red-100 hover:bg-red-200 px-2 py-1 rounded-full transition-colors"
                    title="删除隧道工程"
                  >
                    🗑️
                  </button>
                  {isEnabled && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleProject(key);
                        if (selectedProject === key) {
                          const remainingProjects = Object.keys(projects).filter(k => 
                            projects[k]?.enabled && k !== key
                          );
                          if (remainingProjects.length > 0) {
                            selectProject(remainingProjects[0]);
                          }
                        }
                      }}
                      className="text-red-600 hover:text-red-800 text-sm bg-red-100 hover:bg-red-200 px-2 py-1 rounded-full transition-colors"
                      title="取消选择"
                    >
                      ✕
                    </button>
                  )}
                  <div
                    className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all duration-200 ${
                      isEnabled
                        ? 'border-orange-500 bg-orange-500 shadow-md'
                        : 'border-gray-300 bg-white'
                    }`}
                  >
                    {isEnabled && (
                      <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    )}
                  </div>
                </div>
              </div>
              
              {isEnabled && (
                <div className="mt-3 pt-3 border-t border-orange-100">
                  <div className="flex flex-wrap gap-2">
                    <span className="px-2 py-1 bg-orange-100 text-orange-700 text-xs rounded-full">
                      洞口施工阶段
                    </span>
                    <span className="px-2 py-1 bg-orange-100 text-orange-700 text-xs rounded-full">
                      初支施工阶段
                    </span>
                    <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                      +2
                    </span>
                  </div>
                </div>
              )}
            </div>
          );
        })}
        
        {/* 渲染动态桥梁工程 */}
        {Object.entries(projects).filter(([key, project]) => 
          key.startsWith('bridge_') && project
        ).map(([key, project]) => {
          const isEnabled = project.enabled || false;
          
          return (
            <div
              key={key}
              className={`p-4 rounded-xl border-2 transition-all duration-300 cursor-pointer transform hover:scale-[1.02] ${
                selectedProject === key
                  ? 'border-green-500 bg-gradient-to-r from-green-50 to-emerald-50 shadow-lg'
                  : isEnabled
                  ? 'border-yellow-500 bg-gradient-to-r from-yellow-50 to-amber-50 shadow-md'
                  : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'
              }`}
              onClick={() => {
                if (isEnabled) {
                  selectProject(key);
                } else {
                  toggleProject(key);
                  selectProject(key);
                }
              }}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div 
                    className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl shadow-sm"
                    style={{ 
                      backgroundColor: isEnabled ? '#FFB74D20' : '#f8fafc',
                      color: isEnabled ? '#FFB74D' : '#64748b'
                    }}
                  >
                    🌉
                  </div>
                  <div>
                    <h3 
                      className="font-bold text-gray-800 text-lg"
                      style={{ color: isEnabled ? '#FFB74D' : undefined }}
                    >
                      {project.name || '桥梁工程'}
                    </h3>
                    <p className="text-sm text-gray-500 mt-1">
                      桥梁工程 - 4个施工阶段
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteBridgeProject(key);
                    }}
                    className="text-red-600 hover:text-red-800 text-sm bg-red-100 hover:bg-red-200 px-2 py-1 rounded-full transition-colors"
                    title="删除桥梁工程"
                  >
                    🗑️
                  </button>
                  {isEnabled && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleProject(key);
                        if (selectedProject === key) {
                          const remainingProjects = Object.keys(projects).filter(k => 
                            projects[k]?.enabled && k !== key
                          );
                          if (remainingProjects.length > 0) {
                            selectProject(remainingProjects[0]);
                          }
                        }
                      }}
                      className="text-red-600 hover:text-red-800 text-sm bg-red-100 hover:bg-red-200 px-2 py-1 rounded-full transition-colors"
                      title="取消选择"
                    >
                      ✕
                    </button>
                  )}
                  <div
                    className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all duration-200 ${
                      isEnabled
                        ? 'border-yellow-500 bg-yellow-500 shadow-md'
                        : 'border-gray-300 bg-white'
                    }`}
                  >
                    {isEnabled && (
                      <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    )}
                  </div>
                </div>
              </div>
              
              {isEnabled && (
                <div className="mt-3 pt-3 border-t border-yellow-100">
                  <div className="flex flex-wrap gap-2">
                    <span className="px-2 py-1 bg-yellow-100 text-yellow-700 text-xs rounded-full">
                      基础施工
                    </span>
                    <span className="px-2 py-1 bg-yellow-100 text-yellow-700 text-xs rounded-full">
                      墩柱施工
                    </span>
                    <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                      +2
                    </span>
                  </div>
                </div>
              )}
            </div>
          );
        })}
        
        {/* 添加桥梁工程按钮 */}
        <div
          onClick={() => setShowBridgeForm(true)}
          className="p-4 rounded-xl border-2 border-dashed border-yellow-300 bg-gradient-to-r from-yellow-50 to-amber-50 cursor-pointer transform hover:scale-[1.02] transition-all duration-300 hover:border-yellow-400 hover:shadow-sm"
        >
          <div className="flex items-center justify-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-yellow-100 flex items-center justify-center text-2xl">
              ➕
            </div>
            <div>
              <h3 className="font-bold text-yellow-800 text-lg">
                添加桥梁工程
              </h3>
              <p className="text-sm text-yellow-600 mt-1">
                创建新的桥梁工程项目
              </p>
            </div>
          </div>
        </div>
        
        {/* 添加隧道工程按钮 */}
        <div
          onClick={() => setShowTunnelForm(true)}
          className="p-4 rounded-xl border-2 border-dashed border-orange-300 bg-gradient-to-r from-orange-50 to-amber-50 cursor-pointer transform hover:scale-[1.02] transition-all duration-300 hover:border-orange-400 hover:shadow-sm"
        >
          <div className="flex items-center justify-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-orange-100 flex items-center justify-center text-2xl">
              ➕
            </div>
            <div>
              <h3 className="font-bold text-orange-800 text-lg">
                添加隧道工程
              </h3>
              <p className="text-sm text-orange-600 mt-1">
                创建新的隧道工程项目
              </p>
            </div>
          </div>
        </div>
      </div>
      
      <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
        <div className="flex items-center gap-2 text-blue-700">
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <span className="text-sm font-medium">使用提示</span>
        </div>
        <p className="text-sm text-blue-600 mt-2">
          点击上方卡片选择要配置的工程类型，然后在右侧配置各阶段的施工参数
        </p>
      </div>
    </div>
  );
};

export default ProjectSelector;