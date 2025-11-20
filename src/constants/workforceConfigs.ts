/**
 * 标准化工种配置映射
 * 消除代码重复，提高可维护性
 */

export interface WorkforceConfig {
  [workType: string]: {
    enabled: boolean;
    count: number;
  };
}

export interface ModuleWorkforceConfig {
  [moduleName: string]: WorkforceConfig;
}

export interface ProjectWorkforceConfig {
  [projectKey: string]: ModuleWorkforceConfig;
}

/**
 * 标准化项目工种配置映射
 */
export const STANDARD_WORKFORCE_CONFIGS: ProjectWorkforceConfig = {
  // 路基工程配置
  roadbed: {
    '路基填筑开挖阶段': {
      '普工': { enabled: false, count: 12 },
      '司机': { enabled: false, count: 32 }
    },
    '路基防排水阶段': {
      '司机': { enabled: false, count: 10 },
      '普工': { enabled: false, count: 10 },
      '混凝土工': { enabled: false, count: 10 },
      '钢筋工': { enabled: false, count: 4 },
      '模板工': { enabled: false, count: 10 },
      '机械操作手': { enabled: false, count: 4 },
      '电焊工': { enabled: false, count: 2 }
    },
    '涵洞工程': {
      '司机': { enabled: false, count: 8 },
      '钢筋工': { enabled: false, count: 5 },
      '模板工': { enabled: false, count: 5 },
      '混凝土工': { enabled: false, count: 5 }
    }
  },

  // 桥梁工程配置
  bridge: {
    '基础施工阶段': {
      '机械操作手': { enabled: false, count: 2 },
      '司机': { enabled: false, count: 8 },
      '电焊工': { enabled: false, count: 4 },
      '钢筋工': { enabled: false, count: 4 },
      '混凝土工': { enabled: false, count: 4 },
      '模板工': { enabled: false, count: 6 }
    },
    '墩柱施工阶段': {
      '钢筋工': { enabled: false, count: 6 },
      '模板工': { enabled: false, count: 8 },
      '混凝土工': { enabled: false, count: 10 },
      '司机': { enabled: false, count: 8 },
      '电焊工': { enabled: false, count: 4 }
    },
    '梁板预制及安装阶段': {
      '司机': { enabled: false, count: 10 },
      '机械操作手': { enabled: false, count: 7 },
      '电焊工': { enabled: false, count: 4 },
      '钢筋工': { enabled: false, count: 10 },
      '混凝土工': { enabled: false, count: 10 },
      '模板工': { enabled: false, count: 10 },
      '普工': { enabled: false, count: 10 }
    },
    '桥面系及附属施工阶段': {
      '司机': { enabled: false, count: 9 },
      '钢筋工': { enabled: false, count: 5 },
      '混凝土工': { enabled: false, count: 6 },
      '模板工': { enabled: false, count: 6 },
      '电焊工': { enabled: false, count: 2 },
      '普工': { enabled: false, count: 4 }
    }
  },

  // 路面工程配置
  pavement: {
    '路面基层施工阶段': {
      '司机': { enabled: false, count: 20 },
      '模板工': { enabled: false, count: 10 },
      '普工': { enabled: false, count: 16 }
    },
    '路面面层施工阶段': {
      '司机': { enabled: false, count: 20 },
      '模板工': { enabled: false, count: 7 },
      '普工': { enabled: false, count: 17 }
    }
  },

  // 隧道工程配置
  tunnel: {
    '洞口施工阶段': {
      '司机': { enabled: false, count: 4 },
      '机械操作手': { enabled: false, count: 4 },
      '钢筋工': { enabled: false, count: 4 },
      '混凝土工': { enabled: false, count: 4 },
      '模板工': { enabled: false, count: 4 },
      '普工': { enabled: false, count: 6 }
    },
    '洞身施工阶段': {
      '爆破工': { enabled: false, count: 10 },
      '喷砼工': { enabled: false, count: 2 },
      '机械操作手': { enabled: false, count: 4 },
      '司机': { enabled: false, count: 16 }
    },
    '初支施工阶段': {
      '支护工': { enabled: false, count: 12 },
      '钢筋工': { enabled: false, count: 6 },
      '电焊工': { enabled: false, count: 4 }
    },
    '二衬施工阶段': {
      '司机': { enabled: false, count: 4 },
      '防水工': { enabled: false, count: 4 },
      '钢筋工': { enabled: false, count: 10 },
      '混凝土工': { enabled: false, count: 8 }
    },
    '附属施工阶段': {
      '司机': { enabled: false, count: 4 },
      '机械操作手': { enabled: false, count: 2 },
      '钢筋工': { enabled: false, count: 4 },
      '模板工': { enabled: false, count: 2 },
      '普工': { enabled: false, count: 4 },
      '混凝土工': { enabled: false, count: 2 }
    }
  },

  // 房建工程配置
  building: {
    '基础施工阶段': {
      '司机': { enabled: false, count: 10 },
      '机械操作手': { enabled: false, count: 6 },
      '钢筋工': { enabled: false, count: 4 },
      '模板工': { enabled: false, count: 10 },
      '混凝土工': { enabled: false, count: 10 },
      '木工': { enabled: false, count: 20 },
      '防水工': { enabled: false, count: 8 }
    },
    '主体施工阶段': {
      '司机': { enabled: false, count: 6 },
      '机械操作手': { enabled: false, count: 6 },
      '架子工': { enabled: false, count: 15 },
      '电焊工': { enabled: false, count: 6 },
      '钢筋工': { enabled: false, count: 20 },
      '模板工': { enabled: false, count: 20 },
      '混凝土工': { enabled: false, count: 20 }
    },
    '装饰装修施工阶段': {
      '保温工': { enabled: false, count: 18 },
      '涂料工': { enabled: false, count: 10 },
      '普工': { enabled: false, count: 10 },
      '安装工': { enabled: false, count: 12 },
      '泥瓦工': { enabled: false, count: 10 },
      '抹灰工': { enabled: false, count: 12 },
      '防水工': { enabled: false, count: 10 }
    },
    '机电安装工程': {
      '安装工': { enabled: false, count: 10 },
      '普工': { enabled: false, count: 5 }
    }
  }
};

/**
 * 获取标准化工种配置
 */
export function getStandardWorkforceConfig(projectKey: string, moduleName: string): WorkforceConfig | null {
  const projectConfig = STANDARD_WORKFORCE_CONFIGS[projectKey];
  if (!projectConfig) return null;
  
  const moduleConfig = projectConfig[moduleName];
  if (!moduleConfig) return null;
  
  return moduleConfig;
}

/**
 * 检查是否存在标准化配置
 */
export function hasStandardWorkforceConfig(projectKey: string, moduleName: string): boolean {
  return getStandardWorkforceConfig(projectKey, moduleName) !== null;
}

/**
 * 获取默认工种配置（当没有标准化配置时）
 */
export function getDefaultWorkforceConfig(workTypes: string[]): WorkforceConfig {
  const config: WorkforceConfig = {};
  workTypes.forEach(workType => {
    config[workType] = { enabled: false, count: 50 }; // 默认50人
  });
  return config;
}