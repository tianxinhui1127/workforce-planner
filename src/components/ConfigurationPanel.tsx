import React, { useState, useEffect, useRef, useLayoutEffect } from 'react';
import { useWorkforceStore } from '../stores/workforceStore';
import { PROJECT_TYPES } from '../constants/workforce';
import ModuleConfig from './ModuleConfig';

const ConfigurationPanel: React.FC = () => {
  const { projects, selectedProject, selectProject, updateProjectWinterBreak } = useWorkforceStore();
  const [activeTab, setActiveTab] = useState<string>('');
  const [sliderStyle, setSliderStyle] = useState({ left: 0, width: 0, top: 0 });
  const tabRefs = useRef<{ [key: string]: HTMLButtonElement | null }>({});
  const navRef = useRef<HTMLDivElement>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);
  
  // 获取启用的项目
  const enabledProjects = Object.keys(projects).filter(key => projects[key]?.enabled);
  
  // 更新滑块位置
  const updateSliderPosition = (projectKey: string) => {
    const tabElement = tabRefs.current[projectKey];
    const navElement = navRef.current;
    const wrapperElement = wrapperRef.current;
    if (tabElement && navElement && wrapperElement) {
      const padding = 2;
      const indicatorHeight = 4;
      const next = {
        left: (tabElement.offsetLeft + navElement.offsetLeft) - wrapperElement.offsetLeft + padding,
        width: tabElement.offsetWidth - padding * 2,
        top: (tabElement.offsetTop + navElement.offsetTop) - wrapperElement.offsetTop + (tabElement.offsetHeight - indicatorHeight)
      };
      setSliderStyle(prev => (prev.left !== next.left || prev.width !== next.width || prev.top !== next.top ? next : prev));
    }
  };
  
  // 更新当前选中标签页时更新滑块位置
  useLayoutEffect(() => {
    if (activeTab && enabledProjects.includes(activeTab)) {
      updateSliderPosition(activeTab);
    }
  }, [activeTab, enabledProjects]);

  useEffect(() => {
    const navEl = navRef.current;
    if (!navEl) return;
    const ro = new ResizeObserver(() => {
      if (activeTab) updateSliderPosition(activeTab);
    });
    ro.observe(navEl);
    return () => ro.disconnect();
  }, [activeTab]);
  
  // 当启用的项目变化时，自动选择第一个项目
  useEffect(() => {
    if (enabledProjects.length > 0) {
      // 如果有选中的项目且该项目已启用，则切换到该项目（允许用户主动导航）
      if (selectedProject && enabledProjects.includes(selectedProject)) {
        setActiveTab(selectedProject);
      } else if (!enabledProjects.includes(activeTab) || !activeTab) {
        // 如果当前选中的标签页不在启用的项目中，或者没有选中任何标签页
        setActiveTab(enabledProjects[0]);
        selectProject(enabledProjects[0]);
      }
      // 如果activeTab已经在enabledProjects中，保持当前选择，允许用户自由导航
    } else {
      setActiveTab('');
    }
  }, [enabledProjects, selectedProject]);
  
  // 如果没有启用的项目，显示提示
  if (enabledProjects.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8">
        <div className="text-center text-gray-500">
          <div className="text-6xl mb-4">📋</div>
          <h3 className="text-xl font-semibold mb-2">请选择工程类型</h3>
          <p>请在左侧选择至少一个工程类型来开始配置</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="bg-white rounded-xl shadow-lg">
      {/* 标签页导航 */}
      <div className="border-b-0 relative" ref={wrapperRef}>
        <nav className="flex space-x-8 px-6" ref={navRef}>
          
          {enabledProjects.map(projectKey => {
            // 获取项目信息 - 动态隧道项目、桥梁项目或固定项目类型
            let project;
            if (projectKey.startsWith('tunnel_')) {
              project = { 
                name: projects[projectKey]?.name || '隧道工程', 
                icon: '🚇',
                modules: PROJECT_TYPES.tunnel.modules,
                workTypes: PROJECT_TYPES.tunnel.workTypes
              };
            } else if (projectKey.startsWith('bridge_')) {
              project = { 
                name: projects[projectKey]?.name || '桥梁工程', 
                icon: '🌉',
                modules: ['基础施工阶段', '墩柱施工阶段', '梁板预制及安装阶段', '桥面系及附属施工阶段'],
                workTypes: PROJECT_TYPES.bridge.workTypes
              };
            } else {
              project = PROJECT_TYPES[projectKey];
            }
            
            if (!project) return null;
            
            const isActive = activeTab === projectKey;
            
            return (
              <button
                key={projectKey}
                ref={(el) => {
                  tabRefs.current[projectKey] = el;
                  if (isActive && el && navRef.current) {
                    updateSliderPosition(projectKey);
                  }
                }}
                onClick={() => {
                  setActiveTab(projectKey);
                  selectProject(projectKey);
                  updateSliderPosition(projectKey);
                }}
                className={`py-4 px-3 inline-flex items-center font-medium text-sm transition-all duration-150 relative z-10 hover:scale-105 rounded-t-lg active:scale-95 select-none ${
                  isActive
                    ? 'text-blue-600 font-semibold bg-blue-50/50 shadow-sm'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                }`}
              >
                <span className="mr-2">{project.icon}</span>
                {project.name}
                {isActive && (
                  <span className="absolute bottom-0 left-[2px] right-[2px] h-[4px] bg-gradient-to-r from-blue-600 to-blue-700 rounded-t-[3px] shadow-[0_2px_4px_rgba(37,99,235,0.45)]" />
                )}
              </button>
            );
          })}
        </nav>
      </div>
      
      {/* 标签页内容 */}
      <div className="p-6">
        {enabledProjects.map(projectKey => {
          if (activeTab !== projectKey) return null;
          
          // 获取项目信息 - 动态隧道项目、桥梁项目或固定项目类型
          let project;
          if (projectKey.startsWith('tunnel_')) {
            project = { 
              name: projects[projectKey]?.name || '隧道工程', 
              icon: '🚇',
              modules: PROJECT_TYPES.tunnel.modules,
              workTypes: PROJECT_TYPES.tunnel.workTypes
            };
          } else if (projectKey.startsWith('bridge_')) {
            project = { 
              name: projects[projectKey]?.name || '桥梁工程', 
              icon: '🌉',
              modules: ['基础施工阶段', '墩柱施工阶段', '梁板预制及安装阶段', '桥面系及附属施工阶段'],
              workTypes: PROJECT_TYPES.bridge.workTypes
            };
          } else {
            project = PROJECT_TYPES[projectKey];
          }
          
          const projectConfig = projects[projectKey];
          
          // 确保项目配置存在
          if (!projectConfig) {
            return (
              <div key={projectKey} className="text-center text-gray-500">
                <p>项目配置加载中...</p>
              </div>
            );
          }
          
          return (
            <div key={projectKey} className="animate-fade-in">
              {/* 项目标题和冬休期配置 */}
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-6 gap-4">
                <h3 className="text-lg font-semibold text-gray-800">
                  {project.icon} {project.name} 配置
                </h3>
                
                {/* 项目级冬休期配置（隧道工程除外） */}
                {!projectKey.startsWith('tunnel') && (
                  <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          id={`winter-break-${projectKey}`}
                          checked={projectConfig.hasWinterBreak || false}
                          onChange={(e) => updateProjectWinterBreak(projectKey, e.target.checked)}
                          className="text-blue-600"
                        />
                        <label htmlFor={`winter-break-${projectKey}`} className="text-sm font-medium text-blue-700">
                          ❄️ 是否有冬休期
                        </label>
                      </div>
                      
                      {projectConfig.hasWinterBreak && (
                        <div className="flex items-center gap-2">
                          <select
                            value={projectConfig.winterBreakStartMonth || 11}
                            onChange={(e) => updateProjectWinterBreak(
                              projectKey, 
                              true, 
                              parseInt(e.target.value), 
                              projectConfig.winterBreakEndMonth || 4
                            )}
                            className="px-2 py-1 border border-blue-200 rounded text-sm bg-white"
                          >
                            {Array.from({ length: 12 }, (_, i) => i + 1).map(month => (
                              <option key={month} value={month}>{month}月</option>
                            ))}
                          </select>
                          <span className="text-blue-600 text-sm">至</span>
                          <select
                            value={projectConfig.winterBreakEndMonth || 4}
                            onChange={(e) => updateProjectWinterBreak(
                              projectKey, 
                              true, 
                              projectConfig.winterBreakStartMonth || 11, 
                              parseInt(e.target.value)
                            )}
                            className="px-2 py-1 border border-blue-200 rounded text-sm bg-white"
                          >
                            {Array.from({ length: 12 }, (_, i) => i + 1).map(month => (
                              <option key={month} value={month}>{month}月</option>
                            ))}
                          </select>
                        </div>
                      )}
                    </div>
                    
                    {projectConfig.hasWinterBreak && (
                      <p className="text-xs text-blue-600 mt-2">
                        📅 冬休期内的工种将不参与计算（人数为0）
                      </p>
                    )}
                  </div>
                )}
              </div>
              
              <div className="space-y-6">
                {project.modules.map(moduleName => {
                  const moduleConfig = projectConfig.modules[moduleName];
                  if (!moduleConfig) {
                    return (
                      <div key={moduleName} className="text-red-500">
                        模块配置缺失: {moduleName}
                      </div>
                    );
                  }
                  
                  return (
                    <ModuleConfig
                      key={moduleName}
                      projectKey={projectKey}
                      moduleName={moduleName}
                      config={moduleConfig}
                      workTypes={Object.keys(moduleConfig.workforceConfig) as string[]}
                    />
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ConfigurationPanel;