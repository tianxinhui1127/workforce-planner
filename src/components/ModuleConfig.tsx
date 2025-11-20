import React from 'react';
import { useWorkforceStore } from '../stores/workforceStore';
import { getDefaultWorkforce } from '../utils/workforceGenerator';

interface ModuleConfigProps {
  projectKey: string;
  moduleName: string;
  config: any;
  workTypes: string[];
}

const ModuleConfig: React.FC<ModuleConfigProps> = ({
  projectKey,
  moduleName,
  config,
  workTypes
}) => {
  const { updateModuleConfig, updateWorkforceConfig } = useWorkforceStore();
  
  const currentYear = new Date().getFullYear();
  const currentMonth = new Date().getMonth() + 1;
  const years = Array.from({ length: 16 }, (_, i) => currentYear - 5 + i);
  const months = Array.from({ length: 12 }, (_, i) => i + 1);
  
  // 验证开始时间不得早于当前年月
  const validateStartDate = (year: number, month: number) => {
    if (year < currentYear || (year === currentYear && month < currentMonth)) {
      return false;
    }
    return true;
  };
  
  // 验证结束时间不得早于开始时间
  const validateEndDate = (endYear: number, endMonth: number, startYear: number, startMonth: number) => {
    if (endYear < startYear || (endYear === startYear && endMonth < startMonth)) {
      return false;
    }
    return true;
  };
  
  return (
    <div className="bg-gray-50 rounded-lg p-6">
      <h4 className="text-md font-semibold text-blue-800 mb-6 bg-blue-50 px-3 py-2 rounded-lg border border-blue-200 shadow-sm inline-block">
        {moduleName}
      </h4>
      
      <div className="flex flex-col md:flex-row gap-8">
        {/* 时间配置 */}
        <div className="flex-1 space-y-4">
          <h5 className="text-sm font-medium text-blue-700 flex items-center gap-2 bg-blue-50 px-2.5 py-1.5 rounded-md border border-blue-100 shadow-sm inline-flex">
            ⏰ 时间范围
          </h5>
          
          <div className="space-y-3">
            <div>
              <label className="block text-xs text-gray-600 mb-1">开始时间</label>
              <div className="flex gap-2">
                <select
                  value={config.startYear}
                  onChange={(e) => {
                    const newYear = parseInt(e.target.value);
                    if (validateStartDate(newYear, config.startMonth)) {
                      updateModuleConfig(projectKey, moduleName, { startYear: newYear });
                    } else {
                      alert('开始时间不得早于当前年月！');
                    }
                  }}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm"
                >
                  {years.map(year => (
                    <option key={year} value={year}>{year}年</option>
                  ))}
                </select>
                <select
                  value={config.startMonth}
                  onChange={(e) => {
                    const newMonth = parseInt(e.target.value);
                    if (validateStartDate(config.startYear, newMonth)) {
                      updateModuleConfig(projectKey, moduleName, { startMonth: newMonth });
                    } else {
                      alert('开始时间不得早于当前年月！');
                    }
                  }}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm"
                >
                  {months.map(month => (
                    <option key={month} value={month}>{month}月</option>
                  ))}
                </select>
              </div>
            </div>
            
            <div>
              <label className="block text-xs text-gray-600 mb-1">结束时间</label>
              <div className="flex gap-2">
                <select
                  value={config.endYear}
                  onChange={(e) => {
                    const newYear = parseInt(e.target.value);
                    if (validateEndDate(newYear, config.endMonth, config.startYear, config.startMonth)) {
                      updateModuleConfig(projectKey, moduleName, { endYear: newYear });
                    } else {
                      alert('结束时间不得早于开始时间！');
                    }
                  }}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm"
                >
                  {years.map(year => (
                    <option key={year} value={year}>{year}年</option>
                  ))}
                </select>
                <select
                  value={config.endMonth}
                  onChange={(e) => {
                    const newMonth = parseInt(e.target.value);
                    if (validateEndDate(config.endYear, newMonth, config.startYear, config.startMonth)) {
                      updateModuleConfig(projectKey, moduleName, { endMonth: newMonth });
                    } else {
                      alert('结束时间不得早于开始时间！');
                    }
                  }}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm"
                >
                  {months.map(month => (
                    <option key={month} value={month}>{month}月</option>
                  ))}
                </select>
              </div>
            </div>
            </div>
          </div>
        
        {/* 分隔线 */}
        <div className="hidden md:block w-px bg-gray-300"></div>
        <div className="md:hidden h-px bg-gray-300 my-4"></div>
        
        {/* 队伍配置 */}
        <div className="flex-1 space-y-4">
          <h5 className="text-sm font-medium text-blue-700 flex items-center gap-2 bg-blue-50 px-3 py-2 rounded-md border border-blue-100 shadow-sm inline-flex">
            👥 队伍配置
          </h5>
          
          <div>
            <label className="block text-xs text-gray-600 mb-1">队伍数量</label>
            <input
              type="number"
              min="1"
              max="100"
              value={config.teamCount}
              onChange={(e) => updateModuleConfig(projectKey, moduleName, { 
                teamCount: parseInt(e.target.value) || 1 
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            />
          </div>
          
          {/* 配置模式 */}
          <div className="space-y-2">
            <h5 className="text-sm font-medium text-blue-700 flex items-center gap-2 bg-blue-50 px-3 py-2 rounded-md border border-blue-100 shadow-sm inline-flex">
              📊 配置模式
            </h5>
            
            <label className="flex items-center gap-2">
              <input
                type="radio"
                name={`config-mode-${projectKey}-${moduleName}`}
                checked={config.distributionMode === 'constant'}
                onChange={() => updateModuleConfig(projectKey, moduleName, { distributionMode: 'constant' })}
                className="text-blue-600"
              />
              <span className="text-sm text-gray-700">⚖️ 数量恒定</span>
            </label>
            
            <label className="flex items-center gap-2">
              <input
                type="radio"
                name={`config-mode-${projectKey}-${moduleName}`}
                checked={config.distributionMode === 'normal'}
                onChange={() => updateModuleConfig(projectKey, moduleName, { distributionMode: 'normal' })}
                className="text-blue-600"
              />
              <span className="text-sm text-gray-700">📈 正态分布</span>
            </label>
          </div>
        </div>
        
        {/* 分隔线 */}
        <div className="hidden md:block w-px bg-gray-300"></div>
        <div className="md:hidden h-px bg-gray-300 my-4"></div>
        
        {/* 工种配置 */}
        <div className="flex-1 space-y-4">
          <div className="flex items-center gap-3">
            <h5 className="text-sm font-medium text-blue-700 flex items-center gap-2 bg-blue-50 px-3 py-2 rounded-md border border-blue-100 shadow-sm inline-flex">
              🔧 工种配置
            </h5>
            {config.distributionMode === 'constant' && (
              <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
                <input
                  type="checkbox"
                  className="text-blue-600"
                  checked={workTypes.every(workType => config.workforceConfig[workType]?.enabled || false)}
                  onChange={(e) => {
                    const shouldSelectAll = e.target.checked;
                    workTypes.forEach(workType => {
                      updateWorkforceConfig(
                        projectKey,
                        moduleName,
                        workType,
                        shouldSelectAll,
                        config.workforceConfig[workType]?.count || getDefaultWorkforce(workType)
                      );
                    });
                  }}
                />
                <span>全选</span>
              </label>
            )}
          </div>
          
          {config.distributionMode === 'constant' && (
            <div className="grid grid-cols-1 gap-2 max-h-48 overflow-y-auto">
              {workTypes.map(workType => (
                <div key={workType} className="flex items-center gap-2">
                  <label className="flex items-center gap-2 flex-1">
                    <input
                      type="checkbox"
                      checked={config.workforceConfig[workType]?.enabled || false}
                      onChange={(e) => updateWorkforceConfig(
                        projectKey,
                        moduleName,
                        workType,
                        e.target.checked,
                        config.workforceConfig[workType]?.count || getDefaultWorkforce(workType)
                      )}
                      className="text-blue-600"
                    />
                    <span className="text-sm text-gray-700">{workType}</span>
                  </label>
                  
                  <input
                    type="number"
                    min="0"
                    max="500"
                    value={config.workforceConfig[workType]?.count || getDefaultWorkforce(workType)}
                    onChange={(e) => updateWorkforceConfig(
                      projectKey,
                      moduleName,
                      workType,
                      config.workforceConfig[workType]?.enabled || false,
                      parseInt(e.target.value) || 0
                    )}
                    disabled={!config.workforceConfig[workType]?.enabled}
                    className="w-16 px-2 py-1 border border-gray-300 rounded text-sm disabled:bg-gray-100"
                  />
                </div>
              ))}
            </div>
          )}
          
          {config.distributionMode === 'normal' && (
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <p className="text-sm font-medium text-gray-600">📈 正态分布模式</p>
                <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
                  <input
                    type="checkbox"
                    className="text-blue-600"
                    checked={workTypes.every(workType => config.workforceConfig[workType]?.enabled || false)}
                    onChange={(e) => {
                      const shouldSelectAll = e.target.checked;
                      workTypes.forEach(workType => {
                        updateWorkforceConfig(
                          projectKey,
                          moduleName,
                          workType,
                          shouldSelectAll,
                          config.workforceConfig[workType]?.count || getDefaultWorkforce(workType)
                        );
                      });
                    }}
                  />
                  <span>全选</span>
                </label>
              </div>
              <div className="space-y-1 max-h-32 overflow-y-auto">
                {workTypes.map(workType => {
                  const isEnabled = config.workforceConfig[workType]?.enabled || false;
                  const count = config.workforceConfig[workType]?.count || getDefaultWorkforce(workType);
                  
                  if (!isEnabled) return null;
                  
                  return (
                    <div key={workType} className="flex justify-between items-center text-xs bg-blue-50 px-2 py-1 rounded">
                      <span className="text-blue-700">{workType}</span>
                      <span className="text-blue-600 font-medium">峰值: {count}人</span>
                    </div>
                  );
                }).filter(Boolean)}
                
                {workTypes.filter(workType => config.workforceConfig[workType]?.enabled).length === 0 && (
                  <p className="text-xs text-gray-500 italic">请选择至少一个工种类型</p>
                )}
              </div>
              <p className="text-xs text-gray-500 italic">
                将以峰值数量为中心，按正态分布曲线调整各月数量
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ModuleConfig;