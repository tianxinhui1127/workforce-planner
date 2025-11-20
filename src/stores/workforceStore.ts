import { create } from 'zustand';
import { ProjectState, ModuleConfig, MonthData } from '../types/workforce';
import { PROJECT_TYPES } from '../constants/workforce';
import { generateMonthSequence } from '../utils/workforceGenerator';
import { 
  getStandardWorkforceConfig, 
  hasStandardWorkforceConfig, 
  getDefaultWorkforceConfig 
} from '../constants/workforceConfigs';

interface WorkforceStore {
  // 项目状态
  projects: ProjectState;
  
  // 输出路径
  outputPath: string;
  
  // 折算系数
  conversionFactor: number;
  
  // 加载状态
  isInitialized: boolean;
  
  // 当前选中的项目
  selectedProject: string;
  
  // 操作方法
  toggleProject: (projectKey: string) => void;
  updateModuleConfig: (projectKey: string, moduleName: string, config: Partial<ModuleConfig>) => void;
  updateWorkforceConfig: (projectKey: string, moduleName: string, workType: string, enabled: boolean, count: number) => void;
  updateProjectWinterBreak: (projectKey: string, hasWinterBreak: boolean, winterBreakStartMonth?: number, winterBreakEndMonth?: number) => void;
  setOutputPath: (path: string) => void;
  setConversionFactor: (factor: number) => void;
  selectProject: (projectKey: string) => void;
  
  // 动态创建隧道工程
  createTunnelProject: (projectName: string) => string;
  
  // 删除隧道工程
  deleteTunnelProject: (projectKey: string) => void;
  
  // 动态创建桥梁工程
  createBridgeProject: (projectName: string) => string;
  
  // 删除桥梁工程
  deleteBridgeProject: (projectKey: string) => void;
  
  // 获取当前启用的项目
  getEnabledProjects: () => string[];
  
  // 获取项目的月份序列
  getProjectMonths: (projectKey: string, moduleName: string) => MonthData[];
  
  // 初始化函数
  initializeProjects: () => void;
}

const currentYear = new Date().getFullYear();
const currentMonth = new Date().getMonth() + 1;

export const useWorkforceStore = create<WorkforceStore>((set, get) => ({
  projects: {},
  outputPath: '工程劳动力计划.csv',
  conversionFactor: 1.0,
  isInitialized: false,
  selectedProject: '',
  
  initializeProjects: () => {
    try {
      const initialProjects: ProjectState = {};
      
      // 为每个项目类型创建初始配置
      Object.keys(PROJECT_TYPES).forEach(projectKey => {
        const project = PROJECT_TYPES[projectKey];
        const modules: Record<string, ModuleConfig> = {};
        
        project.modules.forEach(moduleName => {
          // 使用标准化工种配置系统
          let workforceConfig: Record<string, { enabled: boolean; count: number }>;
          
          // 检查是否存在标准化配置
          if (hasStandardWorkforceConfig(projectKey, moduleName)) {
            // 使用预定义的标准化配置
            workforceConfig = getStandardWorkforceConfig(projectKey, moduleName)!;
          } else {
            // 使用默认配置（所有工种都包含，默认50人）
            workforceConfig = getDefaultWorkforceConfig(project.workTypes);
          }
          
          modules[moduleName] = {
            startYear: currentYear,
            startMonth: currentMonth,
            endYear: currentYear,
            endMonth: currentMonth,
            teamCount: 1,
            distributionMode: 'normal',
            workforceConfig
          };
        });
        
        initialProjects[projectKey] = {
          enabled: false,
          modules,
          // 项目级冬休期默认取消勾选（所有类型默认无冬休期）
          hasWinterBreak: false,
          winterBreakStartMonth: 11,
          winterBreakEndMonth: 4
        };
      });
      
      set({ projects: initialProjects, isInitialized: true });
    } catch (error) {
      console.error('初始化项目失败:', error);
      set({ isInitialized: true }); // 即使失败也标记为已初始化
    }
  },
  
  updateProjectWinterBreak: (projectKey: string, hasWinterBreak: boolean, winterBreakStartMonth?: number, winterBreakEndMonth?: number) => {
    set(state => {
      const project = state.projects[projectKey];
      if (!project) {
        console.warn(`项目 ${projectKey} 不存在`);
        return state;
      }
      
      // 隧道工程不允许设置冬休期
      if (projectKey.startsWith('tunnel')) {
        console.warn('隧道工程不支持冬休期设置');
        return state;
      }
      
      return {
        projects: {
          ...state.projects,
          [projectKey]: {
            ...project,
            hasWinterBreak,
            winterBreakStartMonth: winterBreakStartMonth ?? project.winterBreakStartMonth ?? 11,
            winterBreakEndMonth: winterBreakEndMonth ?? project.winterBreakEndMonth ?? 4
          }
        }
      };
    });
  },
  
  toggleProject: (projectKey: string) => {
    set(state => {
      const currentProject = state.projects[projectKey];
      if (!currentProject) {
        console.warn(`项目 ${projectKey} 不存在`);
        return state;
      }
      
      return {
        projects: {
          ...state.projects,
          [projectKey]: {
            ...currentProject,
            enabled: !currentProject.enabled
          }
        }
      };
    });
  },
  
  updateModuleConfig: (projectKey: string, moduleName: string, config: Partial<ModuleConfig>) => {
    set(state => {
      const project = state.projects[projectKey];
      if (!project) {
        console.warn(`项目 ${projectKey} 不存在`);
        return state;
      }
      
      const module = project.modules[moduleName];
      if (!module) {
        console.warn(`模块 ${moduleName} 不存在`);
        return state;
      }
      
      return {
        projects: {
          ...state.projects,
          [projectKey]: {
            ...project,
            modules: {
              ...project.modules,
              [moduleName]: {
                ...module,
                ...config
              }
            }
          }
        }
      };
    });
  },
  
  updateWorkforceConfig: (projectKey: string, moduleName: string, workType: string, enabled: boolean, count: number) => {
    set(state => {
      const project = state.projects[projectKey];
      if (!project) {
        console.warn(`项目 ${projectKey} 不存在`);
        return state;
      }
      
      const module = project.modules[moduleName];
      if (!module) {
        console.warn(`模块 ${moduleName} 不存在`);
        return state;
      }
      
      return {
        projects: {
          ...state.projects,
          [projectKey]: {
            ...project,
            modules: {
              ...project.modules,
              [moduleName]: {
                ...module,
                workforceConfig: {
                  ...module.workforceConfig,
                  [workType]: {
                    enabled,
                    count
                  }
                }
              }
            }
          }
        }
      };
    });
  },
  
  setOutputPath: (path: string) => {
    set({ outputPath: path });
  },
  
  setConversionFactor: (factor: number) => {
    // 确保折算系数在合理范围内 (0.1 - 5.0)
    const clampedFactor = Math.max(0.1, Math.min(5.0, factor));
    set({ conversionFactor: clampedFactor });
  },
  
  selectProject: (projectKey: string) => {
    set({ selectedProject: projectKey });
  },
  
  getEnabledProjects: () => {
    const state = get();
    return Object.keys(state.projects).filter(key => state.projects[key]?.enabled);
  },
  
  getProjectMonths: (projectKey: string, moduleName: string) => {
    const state = get();
    const module = state.projects[projectKey]?.modules[moduleName];
    
    if (!module) return [];
    
    const startDate = new Date(module.startYear, module.startMonth - 1, 1);
    const endDate = new Date(module.endYear, module.endMonth - 1, 
      new Date(module.endYear, module.endMonth, 0).getDate());
    
    return generateMonthSequence(startDate, endDate);
  },
  
  createTunnelProject: (projectName: string) => {
    const state = get();
    const tunnelKey = `tunnel_${Date.now()}`;
    
    // 创建隧道工程配置
    const modules: Record<string, ModuleConfig> = {};
    const tunnelModules = ['洞口施工阶段', '洞身施工阶段', '初支施工阶段', '二衬施工阶段', '附属施工阶段'];
    
    tunnelModules.forEach(moduleName => {
      // 使用标准化工种配置系统
      let workforceConfig: Record<string, { enabled: boolean; count: number }>;
      
      // 检查是否存在标准化配置
      if (hasStandardWorkforceConfig('tunnel', moduleName)) {
        // 使用预定义的标准化配置
        workforceConfig = getStandardWorkforceConfig('tunnel', moduleName)!;
      } else {
        // 使用默认配置（所有工种都包含，默认50人）
        workforceConfig = getDefaultWorkforceConfig(PROJECT_TYPES.tunnel.workTypes);
      }
      
      modules[moduleName] = {
        startYear: currentYear,
        startMonth: currentMonth,
        endYear: currentYear,
        endMonth: currentMonth,
        teamCount: 1,
        distributionMode: 'normal',
        workforceConfig
      };
    });
    
    const newProject = {
      enabled: true,
      modules,
      name: projectName, // 自定义名称
      type: 'tunnel', // 标记为隧道类型
      // 隧道工程不启用冬休期
      hasWinterBreak: false
    };
    
    set({
      projects: {
        ...state.projects,
        [tunnelKey]: newProject
      },
      selectedProject: tunnelKey
    });
    
    return tunnelKey;
  },
  
  deleteTunnelProject: (projectKey: string) => {
    const state = get();
    
    // 只允许删除动态创建的隧道工程
    if (!projectKey.startsWith('tunnel_')) {
      console.warn('只能删除动态创建的隧道工程');
      return;
    }
    
    const newProjects = { ...state.projects };
    delete newProjects[projectKey];
    
    // 如果删除的是当前选中的项目，选择其他项目
    let newSelectedProject = state.selectedProject;
    if (state.selectedProject === projectKey) {
      const remainingProjects = Object.keys(newProjects).filter(key => 
        newProjects[key]?.enabled
      );
      newSelectedProject = remainingProjects.length > 0 ? remainingProjects[0] : '';
    }
    
    set({
      projects: newProjects,
      selectedProject: newSelectedProject
    });
  },
  
  createBridgeProject: (projectName: string) => {
    const state = get();
    const bridgeKey = `bridge_${Date.now()}`;
    
    // 创建桥梁工程配置
    const modules: Record<string, ModuleConfig> = {};
    const bridgeModules = ['基础施工阶段', '墩柱施工阶段', '梁板预制及安装阶段', '桥面系及附属施工阶段'];
    
    bridgeModules.forEach(moduleName => {
      // 使用标准化工种配置系统
      let workforceConfig: Record<string, { enabled: boolean; count: number }>;
      
      // 检查是否存在标准化配置
      if (hasStandardWorkforceConfig('bridge', moduleName)) {
        // 使用预定义的标准化配置
        workforceConfig = getStandardWorkforceConfig('bridge', moduleName)!;
      } else {
        // 使用默认配置（所有工种都包含，默认50人）
        workforceConfig = getDefaultWorkforceConfig(PROJECT_TYPES.bridge.workTypes);
      }
      
      modules[moduleName] = {
        startYear: currentYear,
        startMonth: currentMonth,
        endYear: currentYear,
        endMonth: currentMonth,
        teamCount: 1,
        distributionMode: 'normal',
        workforceConfig
      };
    });
    
    const newProject = {
      enabled: true,
      modules,
      name: projectName, // 自定义名称
      type: 'bridge', // 标记为桥梁类型
      // 桥梁工程默认不启用冬休期
      hasWinterBreak: false,
      winterBreakStartMonth: 11,
      winterBreakEndMonth: 4
    };
    
    set({
      projects: {
        ...state.projects,
        [bridgeKey]: newProject
      },
      selectedProject: bridgeKey
    });
    
    return bridgeKey;
  },
  
  deleteBridgeProject: (projectKey: string) => {
    const state = get();
    
    // 只允许删除动态创建的桥梁工程
    if (!projectKey.startsWith('bridge_')) {
      console.warn('只能删除动态创建的桥梁工程');
      return;
    }
    
    const newProjects = { ...state.projects };
    delete newProjects[projectKey];
    
    // 如果删除的是当前选中的项目，选择其他项目
    let newSelectedProject = state.selectedProject;
    if (state.selectedProject === projectKey) {
      const remainingProjects = Object.keys(newProjects).filter(key => 
        newProjects[key]?.enabled
      );
      newSelectedProject = remainingProjects.length > 0 ? remainingProjects[0] : '';
    }
    
    set({
      projects: newProjects,
      selectedProject: newSelectedProject
    });
  }
}));