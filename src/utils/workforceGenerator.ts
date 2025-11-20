import { MonthData, WorkforcePlan, WorkType, TunnelWorkType, WORK_TYPES, TUNNEL_WORK_TYPES } from '../types/workforce';

/**
 * 生成从开始日期到结束日期之间的所有月份序列
 */
export function generateMonthSequence(startDate: Date, endDate: Date): MonthData[] {
  const months: MonthData[] = [];
  const currentDate = new Date(startDate.getFullYear(), startDate.getMonth(), 1);
  
  while (currentDate <= endDate) {
    months.push([currentDate.getFullYear(), currentDate.getMonth() + 1]);
    
    // 计算下一个月
    if (currentDate.getMonth() === 11) {
      currentDate.setFullYear(currentDate.getFullYear() + 1);
      currentDate.setMonth(0);
    } else {
      currentDate.setMonth(currentDate.getMonth() + 1);
    }
  }
  
  return months;
}

/**
 * 根据工程进度自动生成各工种的投入计划 - 与Python版本完全一致
 */
export function generateDefaultWorkforcePlan(months: MonthData[], workTypes?: AllWorkType[]): WorkforcePlan {
  const types = workTypes || WORK_TYPES;
  const totalMonths = months.length;
  const workforcePlan: WorkforcePlan = {};
  
  // 初始化各工种数组
  for (const workType of types) {
    workforcePlan[workType] = [];
  }
  
  // 为每个月生成各工种人数 - 与Python版本相同的算法
  for (let monthIdx = 0; monthIdx < totalMonths; monthIdx++) {
    // 计算当前进度百分比
    const progress = totalMonths > 1 ? monthIdx / (totalMonths - 1) : 1.0;
    
    // 模板工：前期和中期需求较高
    const templateFactor = progress < 0.7 ? Math.min(progress * 2, 1.0) : (1.0 - (progress - 0.7) * 3.33);
    if ("模板工" in workforcePlan) {
      workforcePlan["模板工"].push(Math.floor(80 * templateFactor));
    }
    
    // 混凝土工：中期需求最高
    const concreteFactor = progress < 0.3 ? Math.min(progress * 3, 1.0) : 
                          progress < 0.8 ? Math.min(2 - progress * 2, 1.0) : 
                          (1.0 - (progress - 0.8) * 5);
    if ("混凝土工" in workforcePlan) {
      workforcePlan["混凝土工"].push(Math.floor(90 * concreteFactor));
    }
    
    // 钢筋工：前期和中期需求较高
    const steelFactor = progress < 0.6 ? Math.min(progress * 2.5, 1.0) : (1.0 - (progress - 0.6) * 2.5);
    if ("钢筋工" in workforcePlan) {
      workforcePlan["钢筋工"].push(Math.floor(100 * steelFactor));
    }
    
    // 支架工：前期和中期需求较高
    const scaffoldFactor = progress < 0.5 ? Math.min(progress * 2, 1.0) : (1.0 - (progress - 0.5) * 2);
    if ("支架工" in workforcePlan) {
      workforcePlan["支架工"].push(Math.floor(40 * scaffoldFactor));
    }
    
    // 测量工：前期和后期需求较高
    const surveyFactor = 0.6 + 0.4 * (1.0 - Math.abs(progress - 0.2) * 2.5) * (1.0 - Math.abs(progress - 0.8) * 2.5);
    if ("测量工" in workforcePlan) {
      workforcePlan["测量工"].push(Math.floor(10 * surveyFactor));
    }
    
    // 电焊工：中期需求较高
    const weldingFactor = progress < 0.4 ? Math.min(progress * 3, 1.0) : Math.min(1.5 - progress * 1.5, 1.0);
    if ("电焊工" in workforcePlan) {
      workforcePlan["电焊工"].push(Math.floor(35 * weldingFactor));
    }
    
    // 泥瓦工：后期需求较高
    const masonFactor = progress < 0.2 ? Math.min(progress * 5, 1.0) : 
                        progress < 0.8 ? 1.0 : 
                        (1.0 - (progress - 0.8) * 5);
    if ("泥瓦工" in workforcePlan) {
      workforcePlan["泥瓦工"].push(Math.floor(25 * masonFactor));
    }
    
    // 电工：均匀分布，略中后期增加
    const electricianFactor = 0.5 + 0.5 * progress;
    if ("电工" in workforcePlan) {
      workforcePlan["电工"].push(Math.floor(5 * electricianFactor));
    }
    
    // 普工：全程都需要，中期需求最高
    const laborerFactor = 0.7 + 0.3 * (1.0 - Math.abs(progress - 0.5) * 2);
    if ("普工" in workforcePlan) {
      workforcePlan["普工"].push(Math.floor(50 * laborerFactor));
    }
    
    // 隧道工程特殊工种
    // 出渣工
    const slagFactor = progress < 0.3 ? Math.min(progress * 3, 1.0) : Math.min(1.5 - progress * 1.5, 1.0);
    if ("出渣工" in workforcePlan) {
      workforcePlan["出渣工"].push(Math.floor(60 * slagFactor));
    }
    
    // 防水工
    const waterproofFactor = progress < 0.4 ? Math.min(progress * 2, 1.0) : 
                            progress < 0.7 ? 1.0 : 
                            (1.0 - (progress - 0.7) * 3.33);
    if ("防水工" in workforcePlan) {
      workforcePlan["防水工"].push(Math.floor(30 * waterproofFactor));
    }
    
    // 开挖工
    const excavationFactor = progress < 0.2 ? Math.min(progress * 4, 1.0) : 
                             progress < 0.6 ? 1.0 : 
                             (1.0 - (progress - 0.6) * 2.5);
    if ("开挖工" in workforcePlan) {
      workforcePlan["开挖工"].push(Math.floor(100 * excavationFactor));
    }
    
    // 喷砼工
    const shotcreteFactor = progress < 0.3 ? Math.min(progress * 3, 1.0) : 
                           progress < 0.7 ? 1.0 : 
                           (1.0 - (progress - 0.7) * 3.33);
    if ("喷砼工" in workforcePlan) {
      workforcePlan["喷砼工"].push(Math.floor(90 * shotcreteFactor));
    }
    
    // 普通工
    const generalLaborFactor = 0.6 + 0.4 * (1.0 - Math.abs(progress - 0.4) * 2);
    if ("普通工" in workforcePlan) {
      workforcePlan["普通工"].push(Math.floor(70 * generalLaborFactor));
    }
    
    // 司机
    const driverFactor = progress < 0.5 ? Math.min(progress * 2, 1.0) : (1.0 - (progress - 0.5) * 2);
    if ("司机" in workforcePlan) {
      workforcePlan["司机"].push(Math.floor(30 * driverFactor));
    }
    
    // 支护工
    const supportFactor = progress < 0.4 ? Math.min(progress * 2.5, 1.0) : 
                         progress < 0.8 ? 1.0 : 
                         (1.0 - (progress - 0.8) * 5);
    if ("支护工" in workforcePlan) {
      workforcePlan["支护工"].push(Math.floor(30 * supportFactor));
    }
  }
  
  return workforcePlan;
}

/**
 * 根据用户输入的最大配置数量生成各工种的投入计划 - 与Python版本一致，考虑冬休期
 */
export function generateCustomWorkforcePlan(months: MonthData[], workforceConfig: Record<string, number>): WorkforcePlan {
  const totalMonths = months.length;
  const workforcePlan: WorkforcePlan = {};
  
  // 为每个工种生成投入计划 - 每个月人数恒定为输入值
  for (const [workType, maxCount] of Object.entries(workforceConfig)) {
    workforcePlan[workType] = Array(totalMonths).fill(Math.floor(maxCount));
  }
  
  return workforcePlan;
}

/**
 * 根据用户输入的最大配置数量生成各工种的投入计划 - 考虑冬休期（按月份循环）
 */
export function generateCustomWorkforcePlanWithWinterBreak(
  months: MonthData[], 
  workforceConfig: Record<string, number>,
  hasWinterBreak: boolean = false,
  winterBreakStartMonth?: number,
  winterBreakEndMonth?: number
): WorkforcePlan {
  const workforcePlan: WorkforcePlan = {};
  
  // 为每个工种生成投入计划
  for (const [workType, maxCount] of Object.entries(workforceConfig)) {
    const monthlyPlan: number[] = [];
    
    for (let i = 0; i < months.length; i++) {
      const currentMonth = months[i];
      
      // 检查是否在冬休期内（按月份循环判断）
      if (hasWinterBreak && winterBreakStartMonth && winterBreakEndMonth && 
          isInWinterBreak(currentMonth, winterBreakStartMonth, winterBreakEndMonth)) {
        monthlyPlan.push(0); // 冬休期为0人
      } else {
        monthlyPlan.push(Math.floor(maxCount));
      }
    }
    
    workforcePlan[workType] = monthlyPlan;
  }
  
  return workforcePlan;
}

/**
 * 检查月份是否在冬休期内 - 按月份循环判断（支持跨年度，如11月-4月）
 */
export function isInWinterBreak(month: MonthData, winterBreakStartMonth: number, winterBreakEndMonth: number): boolean {
  const [year, monthNum] = month;
  
  // 处理跨年度的情况（如11月-4月）
  if (winterBreakStartMonth > winterBreakEndMonth) {
    // 跨年度：从startMonth到12月，以及从1月到endMonth
    return monthNum >= winterBreakStartMonth || monthNum <= winterBreakEndMonth;
  } else {
    // 同年度：从startMonth到endMonth
    return monthNum >= winterBreakStartMonth && monthNum <= winterBreakEndMonth;
  }
}

/**
 * 生成劳动力计划 - 支持数量恒定和正态分布模式，考虑冬休期
 */
export function generateWorkforcePlan(
  months: MonthData[], 
  workforceConfig?: Record<string, number>,
  distributionMode: 'constant' | 'normal' = 'normal',
  hasWinterBreak: boolean = false,
  winterBreakStartMonth?: number,
  winterBreakEndMonth?: number
): WorkforcePlan {
  if (!workforceConfig) {
    return generateDefaultWorkforcePlan(months);
  } else if (distributionMode === 'constant') {
    // 数量恒定模式 - 每个月数量相同，但考虑冬休期
    return generateCustomWorkforcePlanWithWinterBreak(months, workforceConfig, hasWinterBreak, winterBreakStartMonth, winterBreakEndMonth);
  } else {
    // 正态分布模式 - 按正态分布调整数量，考虑冬休期
    const workforcePlan: WorkforcePlan = {};
    
    for (const [workType, baseCount] of Object.entries(workforceConfig)) {
      workforcePlan[workType] = generateNormalDistributionPlanWithWinterBreak(months, baseCount, hasWinterBreak, winterBreakStartMonth, winterBreakEndMonth);
    }
    
    return workforcePlan;
  }
}

/**
 * 正态分布函数 - 生成钟形曲线分布
 */
function normalDistribution(x: number, mean: number, stdDev: number): number {
  const coefficient = 1 / (stdDev * Math.sqrt(2 * Math.PI));
  const exponent = -Math.pow(x - mean, 2) / (2 * Math.pow(stdDev, 2));
  return coefficient * Math.exp(exponent);
}

/**
 * 生成正态分布的劳动力计划 - 使用用户配置的数量作为峰值
 */
export function generateNormalDistributionPlan(
  months: MonthData[], 
  peakCount: number, 
  minFactor: number = 0.3,
  stdDevFactor: number = 0.3
): number[] {
  const totalMonths = months.length;
  const plan: number[] = [];
  
  // 计算均值和标准差
  const mean = (totalMonths - 1) / 2; // 中间月份
  const stdDev = totalMonths * stdDevFactor; // 标准差
  
  // 生成正态分布数据
  const distributionValues: number[] = [];
  let maxValue = 0;
  
  for (let i = 0; i < totalMonths; i++) {
    const value = normalDistribution(i, mean, stdDev);
    distributionValues.push(value);
    maxValue = Math.max(maxValue, value);
  }
  
  // 归一化并应用到峰值数量
  // 峰值在中间月份，两端递减到最小值
  for (let i = 0; i < totalMonths; i++) {
    const normalizedValue = distributionValues[i] / maxValue;
    const scaledCount = peakCount * (minFactor + normalizedValue * (1 - minFactor));
    plan.push(Math.floor(scaledCount));
  }
  
  return plan;
}

/**
 * 生成正态分布的劳动力计划 - 考虑冬休期（按月份循环）
 */
export function generateNormalDistributionPlanWithWinterBreak(
  months: MonthData[], 
  peakCount: number, 
  hasWinterBreak: boolean = false,
  winterBreakStartMonth?: number,
  winterBreakEndMonth?: number,
  minFactor: number = 0.3,
  stdDevFactor: number = 0.3
): number[] {
  const plan: number[] = [];
  
  // 计算均值和标准差
  const mean = (months.length - 1) / 2; // 中间月份
  const stdDev = months.length * stdDevFactor; // 标准差
  
  // 生成正态分布数据
  const distributionValues: number[] = [];
  let maxValue = 0;
  
  for (let i = 0; i < months.length; i++) {
    const value = normalDistribution(i, mean, stdDev);
    distributionValues.push(value);
    maxValue = Math.max(maxValue, value);
  }
  
  // 归一化并应用到峰值数量，考虑冬休期
  for (let i = 0; i < months.length; i++) {
    const currentMonth = months[i];
    
    // 检查是否在冬休期内（按月份循环判断）
    if (hasWinterBreak && winterBreakStartMonth && winterBreakEndMonth && 
        isInWinterBreak(currentMonth, winterBreakStartMonth, winterBreakEndMonth)) {
      plan.push(0); // 冬休期为0人
    } else {
      const normalizedValue = distributionValues[i] / maxValue;
      const scaledCount = peakCount * (minFactor + normalizedValue * (1 - minFactor));
      plan.push(Math.floor(scaledCount));
    }
  }
  
  return plan;
}

/**
 * 获取默认劳动力配置
 */
export function getDefaultWorkforce(workType: string): number {
  const defaults: Record<string, number> = {
    "模板工": 80, "混凝土工": 90, "钢筋工": 100, "支架工": 40,
    "测量工": 10, "电焊工": 35, "泥瓦工": 25, "电工": 5, "普工": 50,
    "出渣工": 60, "防水工": 30, "开挖工": 100, "喷砼工": 90,
    "普通工": 70, "司机": 30, "支护工": 30
  };
  return defaults[workType] || 50;
}

type AllWorkType = WorkType | TunnelWorkType;