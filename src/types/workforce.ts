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

// 月份数据 [年, 月]
export type MonthData = [number, number];

// 劳动力计划数据
export interface WorkforcePlan {
  [workType: string]: number[];
}

// 配置模式类型
export type DistributionMode = 'constant' | 'normal';

// 模块配置
export interface ModuleConfig {
  startYear: number;
  startMonth: number;
  endYear: number;
  endMonth: number;
  teamCount: number;
  distributionMode: DistributionMode;
  workforceConfig: {
    [workType: string]: {
      enabled: boolean;
      count: number;
    };
  };
}

// 项目配置
export interface ProjectConfig {
  enabled: boolean;
  modules: {
    [moduleName: string]: ModuleConfig;
  };
  name?: string; // 自定义项目名称（可选）
  type?: string; // 项目类型（可选，用于标识动态创建的项目）
  // 项目级冬休期配置
  hasWinterBreak?: boolean;
  winterBreakStartMonth?: number;  // 冬休期开始月份 (1-12)
  winterBreakEndMonth?: number;    // 冬休期结束月份 (1-12)
}

// 项目状态管理
export interface ProjectState {
  [projectKey: string]: ProjectConfig;
}