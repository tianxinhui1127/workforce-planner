import React, { useState } from 'react';
import { useWorkforceStore } from '../stores/workforceStore';
import { generateWorkforcePlan, generateMonthSequence, generateDefaultWorkforcePlan } from '../utils/workforceGenerator';
import { PROJECT_TYPES } from '../constants/workforce';

const ActionPanel: React.FC = () => {
  const { projects, outputPath, setOutputPath, conversionFactor, setConversionFactor } = useWorkforceStore();
  const [isGenerating, setIsGenerating] = useState(false);
  
  // 简化的CSV导出功能
  const exportToCSV = (data: string[][], filename: string) => {
    const csvContent = data.map(row => row.join(',')).join('\n');
    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };
  
  const handleGeneratePlan = async () => {
    setIsGenerating(true);
    
    // 月份排序函数 - 按照年份和月份进行时间排序
    const sortMonthsByTime = (months: string[]): string[] => {
      return months.sort((a, b) => {
        const [yearA, monthA] = a.split('-').map(Number);
        const [yearB, monthB] = b.split('-').map(Number);
        
        // 先按年份排序，同年份按月份排序
        return yearA !== yearB ? yearA - yearB : monthA - monthB;
      });
    };
    
    try {
      // 收集所有启用的项目数据
      const allMonths = new Set<string>();
      const allWorkforceData: Record<string, number[]> = {};
      
      // 处理每个启用的项目
      Object.keys(projects).forEach(projectKey => {
        const project = projects[projectKey];
        if (!project.enabled) return;
        
        const resolvedTypeKey = project.type
          ? project.type
          : projectKey.startsWith('bridge_')
            ? 'bridge'
            : projectKey.startsWith('tunnel_')
              ? 'tunnel'
              : projectKey;
        const projectType = PROJECT_TYPES[resolvedTypeKey];
        
        Object.keys(project.modules).forEach(moduleName => {
          const module = project.modules[moduleName];
          
          // 检查该阶段是否有启用的工种类型
          const hasEnabledWorkTypes = Object.keys(module.workforceConfig).some(
            workType => module.workforceConfig[workType].enabled
          );
          
          // 如果没有启用的工种类型，跳过该阶段的计算
          if (!hasEnabledWorkTypes) {
            return;
          }
          
          // 生成月份序列
          const startDate = new Date(module.startYear, module.startMonth - 1, 1);
          const endDate = new Date(module.endYear, module.endMonth - 1, 
            new Date(module.endYear, module.endMonth, 0).getDate());
          
          const months = generateMonthSequence(startDate, endDate);
          
          // 生成劳动力计划
          let workforcePlan;
          if (module.distributionMode === 'normal') {
            // 正态分布模式 - 使用用户配置的数量作为峰值
            const normalConfig: Record<string, number> = {};
            Object.keys(module.workforceConfig).forEach(workType => {
              if (module.workforceConfig[workType].enabled) {
                normalConfig[workType] = module.workforceConfig[workType].count;
              }
            });
            
            if (Object.keys(normalConfig).length > 0) {
              // 使用用户配置的数量生成正态分布，考虑项目级冬休期（月份循环）
              workforcePlan = generateWorkforcePlan(months, normalConfig, 'normal', project.hasWinterBreak, project.winterBreakStartMonth, project.winterBreakEndMonth);
            } else {
              // 如果没有启用任何工种，使用默认算法
              workforcePlan = generateDefaultWorkforcePlan(months, projectType.workTypes);
            }
          } else {
            // 数量恒定模式 - 使用用户配置的数量
            const customConfig: Record<string, number> = {};
            Object.keys(module.workforceConfig).forEach(workType => {
              if (module.workforceConfig[workType].enabled) {
                customConfig[workType] = module.workforceConfig[workType].count;
              }
            });
            
            // 考虑项目级冬休期（月份循环）
            workforcePlan = generateWorkforcePlan(months, customConfig, 'constant', project.hasWinterBreak, project.winterBreakStartMonth, project.winterBreakEndMonth);
          }
          
          // 应用队伍系数
          const teamCount = Math.max(1, module.teamCount);
          Object.keys(workforcePlan).forEach(workType => {
            workforcePlan[workType] = workforcePlan[workType].map(count => 
              Math.floor(count * teamCount)
            );
          });
          
          // 添加到总数据中
          months.forEach((month, index) => {
            const monthKey = `${month[0]}-${month[1]}`;
            allMonths.add(monthKey);
          });
          
          Object.keys(workforcePlan).forEach(workType => {
            if (!allWorkforceData[workType]) {
              allWorkforceData[workType] = [];
            }
            
            months.forEach((month, index) => {
              const monthKey = `${month[0]}-${month[1]}`;
              const sortedMonths = sortMonthsByTime(Array.from(allMonths));
              const monthIndex = sortedMonths.indexOf(monthKey);
              
              if (!allWorkforceData[workType][monthIndex]) {
                allWorkforceData[workType][monthIndex] = 0;
              }
              
              allWorkforceData[workType][monthIndex] += workforcePlan[workType][index];
            });
          });
        });
      });
      
      if (allMonths.size === 0) {
        alert('请至少启用一个工程项目');
        return;
      }
      
      // 创建CSV数据
      const sortedMonths = sortMonthsByTime(Array.from(allMonths));
      const headers = ['工种', ...sortedMonths.map(month => {
        const [year, monthNum] = month.split('-');
        return `${year}年${monthNum}月`;
      })];
      
      const data = [headers];
      
      Object.keys(allWorkforceData).forEach(workType => {
        const row = [workType];
        sortedMonths.forEach((_, index) => {
          // 应用折算系数并四舍五入为整数
          const originalCount = allWorkforceData[workType][index] || 0;
          const convertedCount = Math.round(originalCount * conversionFactor);
          row.push(String(convertedCount));
        });
        data.push(row);
      });
      
      // 导出CSV文件
      exportToCSV(data, outputPath.replace('.xlsx', '.csv'));
      
      alert(`劳动力计划已成功生成！\n文件保存位置：${outputPath.replace('.xlsx', '.csv')}`);
      
    } catch (error) {
      console.error('生成计划失败:', error);
      alert('生成计划失败，请检查配置是否正确');
    } finally {
      setIsGenerating(false);
    }
  };
  
  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h2 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
        💾 导出设置
      </h2>
      
      <div className="space-y-4">
        {/* 折算系数和输出文件并列布局 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* 折算系数设置 - 在前 */}
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <label className="block text-sm font-medium text-blue-800 mb-2">
              📊 折算系数
            </label>
            <div className="flex gap-2">
              <input
                type="number"
                value={conversionFactor}
                onChange={(e) => setConversionFactor(parseFloat(e.target.value) || 1.0)}
                step="0.1"
                min="0.1"
                max="5.0"
                className="flex-1 px-3 py-2 border border-blue-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                placeholder="1.0"
              />
              <button
                onClick={() => setConversionFactor(1.0)}
                className="px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm"
              >
                重置
              </button>
            </div>
            <p className="text-xs text-blue-600 mt-2">
              将所有劳动力数据乘以该系数 (0.1-5.0，当前: {conversionFactor})
            </p>
          </div>
          
          {/* 输出文件设置 - 在后 */}
          <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              📁 输出文件
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={outputPath}
                onChange={(e) => setOutputPath(e.target.value)}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
                placeholder="输入文件名"
              />
              <button
                onClick={() => {
                  const fileName = prompt('请输入文件名:', outputPath);
                  if (fileName) setOutputPath(fileName);
                }}
                className="px-3 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors text-sm"
              >
                修改
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-2">支持CSV格式，可在Excel中打开</p>
          </div>
        </div>
        
        {/* 操作按钮 */}
        <div className="pt-4">
          <button
            onClick={handleGeneratePlan}
            disabled={isGenerating}
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 disabled:bg-blue-400 transition-colors font-medium shadow-lg hover:shadow-xl transform hover:scale-[1.02]"
          >
            {isGenerating ? '🔄 生成中...' : '🚀 生成计划'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ActionPanel;