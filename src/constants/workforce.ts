// 现代化配色方案 - 天气应用风格
export const MODERN_COLORS = {
  // 主色调 - 天空蓝渐变
  primary: '#1E88E5',      // 主蓝色
  primaryLight: '#42A5F5', // 浅蓝色
  primaryDark: '#1565C0',  // 深蓝色
  
  // 辅助色 - 云朵白和阳光黄
  background: '#DCEAF7',    // 浅灰背景
  cardBg: '#FFFFFF',       // 纯白卡片
  accent: '#FFB74D',        // 阳光橙色
  accentLight: '#FFF3E0',  // 浅橙色背景
  
  // 文字颜色
  textPrimary: '#2C3E50',  // 深灰文字
  textSecondary: '#7F8C8D', // 浅灰文字
  textLight: '#BDC3C7',    // 最浅文字
  
  // 状态颜色
  success: '#4CAF50',       // 成功绿
  warning: '#FF9800',       // 警告橙
  error: '#F44336',         // 错误红
  
  // 边框和分隔线
  border: '#ECEFF1',        // 浅灰边框
  divider: '#F5F7FA',       // 分隔线
} as const;

// 工种类型定义
export const WORK_TYPES = ["模板工", "混凝土工", "钢筋工", "支架工", "测量工", "电焊工", "泥瓦工", "电工", "普工"] as const;
export const TUNNEL_WORK_TYPES = ["出渣工", "防水工", "钢筋工", "混凝土工", "开挖工", "模板工", "喷砼工", "普通工", "司机", "支护工", "电焊工"] as const;

export type WorkType = typeof WORK_TYPES[number];
export type TunnelWorkType = typeof TUNNEL_WORK_TYPES[number];
export type AllWorkType = WorkType | TunnelWorkType;

// 工程类型配置
export interface ProjectType {
  key: string;
  name: string;
  icon: string;
  modules: string[];
  color: string;
  workTypes: AllWorkType[];
}

// 工程类型配置
export const PROJECT_TYPES: Record<string, ProjectType> = {
  roadbed: {
    key: 'roadbed',
    name: '路基工程',
    icon: '⛰️',
    modules: ['路基填筑开挖阶段', '路基防排水阶段', '涵洞工程'],
    color: MODERN_COLORS.primary,
    workTypes: [...WORK_TYPES]
  },
  bridge: {
    key: 'bridge',
    name: '桥梁工程',
    icon: '🌉',
    modules: ['基础施工阶段', '墩柱施工阶段', '梁板预制及安装阶段', '桥面系及附属施工阶段'],
    color: MODERN_COLORS.accent,
    workTypes: [...WORK_TYPES]
  },
  pavement: {
    key: 'pavement',
    name: '路面工程',
    icon: '🛣️',
    modules: ['路面基层施工阶段', '路面面层施工阶段'],
    color: MODERN_COLORS.success,
    workTypes: [...WORK_TYPES]
  },
  tunnel: {
    key: 'tunnel',
    name: '隧道工程',
    icon: '🚇',
    modules: ['洞口施工阶段', '洞身施工阶段', '初支施工阶段', '二衬施工阶段', '附属施工阶段'],
    color: MODERN_COLORS.warning,
    workTypes: [...TUNNEL_WORK_TYPES]
  },
  building: {
    key: 'building',
    name: '房建工程',
    icon: '🏢',
    modules: ['基础施工阶段', '主体施工阶段', '装饰装修施工阶段', '机电安装工程'],
    color: MODERN_COLORS.error,
    workTypes: [...WORK_TYPES]
  }
};