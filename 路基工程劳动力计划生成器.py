import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import calendar
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# 定义所有工种
WORK_TYPES = ["模板工", "混凝土工", "钢筋工", "支架工", "测量工", "电焊工", "泥瓦工", "电工", "普工"]

# 隧道工程专用工种类型
TUNNEL_WORK_TYPES = [
    "出渣工",
    "防水工",
    "钢筋工",
    "混凝土工",
    "开挖工",
    "模板工",
    "喷砼工",
    "普通工",
    "司机",
    "支护工",
    "电焊工"
]

# 生成月份序列
def generate_month_sequence(start_date, end_date):
    """
    生成从开始日期到结束日期之间的所有月份的序列
    返回格式: [(年份, 月份), ...]
    """
    months = []
    # 从开始日期的月份开始
    current_date = start_date.replace(day=1)
    
    # 生成所有月份直到结束日期的月份
    while current_date <= end_date:
        months.append((current_date.year, current_date.month))
        
        # 计算下一个月
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    return months

# 获取月份列的层级结构
def get_month_columns(months):
    """
    生成月份列的层级结构，用于DataFrame的MultiIndex
    返回格式: (年列表, 月列表)
    """
    years = []
    month_numbers = []
    
    for year, month in months:
        years.append(str(year))
        month_numbers.append(str(month))
    
    return years, month_numbers

# 默认工种配置模式 - 模拟路基工程各阶段的劳动力需求
def generate_default_workforce_plan(months):
    """
    根据工程进度自动生成各工种的投入计划
    模拟一个合理的路基工程劳动力配置曲线
    """
    total_months = len(months)
    workforce_plan = {}
    
    # 定义各工种的投入曲线（按百分比）
    for work_type in WORK_TYPES:
        workforce_plan[work_type] = []
    
    # 为每个月生成各工种人数
    for month_idx in range(total_months):
        # 计算当前进度百分比
        progress = month_idx / (total_months - 1) if total_months > 1 else 1.0
        
        # 模板工：前期和中期需求较高
        template_factor = min(progress * 2, 1.0) if progress < 0.7 else (1.0 - (progress - 0.7) * 3.33)
        workforce_plan["模板工"].append(int(80 * template_factor))
        
        # 混凝土工：中期需求最高
        concrete_factor = min(progress * 3, 1.0) if progress < 0.3 else min(2 - progress * 2, 1.0) if progress < 0.8 else (1.0 - (progress - 0.8) * 5)
        workforce_plan["混凝土工"].append(int(90 * concrete_factor))
        
        # 钢筋工：前期和中期需求较高
        steel_factor = min(progress * 2.5, 1.0) if progress < 0.6 else (1.0 - (progress - 0.6) * 2.5)
        workforce_plan["钢筋工"].append(int(100 * steel_factor))
        
        # 支架工：前期和中期需求较高
        scaffold_factor = min(progress * 2, 1.0) if progress < 0.5 else (1.0 - (progress - 0.5) * 2)
        workforce_plan["支架工"].append(int(40 * scaffold_factor))
        
        # 测量工：前期和后期需求较高
        survey_factor = 0.6 + 0.4 * (1.0 - abs(progress - 0.2) * 2.5) * (1.0 - abs(progress - 0.8) * 2.5)
        workforce_plan["测量工"].append(int(10 * survey_factor))
        
        # 电焊工：中期需求较高
        welding_factor = min(progress * 3, 1.0) if progress < 0.4 else min(1.5 - progress * 1.5, 1.0)
        workforce_plan["电焊工"].append(int(35 * welding_factor))
        
        # 泥瓦工：后期需求较高
        mason_factor = min(progress * 5, 1.0) if progress < 0.2 else 1.0 if progress < 0.8 else (1.0 - (progress - 0.8) * 5)
        workforce_plan["泥瓦工"].append(int(25 * mason_factor))
        
        # 电工：均匀分布，略中后期增加
        electrician_factor = 0.5 + 0.5 * progress
        workforce_plan["电工"].append(int(5 * electrician_factor))
        
        # 普工：全程都需要，中期需求最高
        laborer_factor = 0.7 + 0.3 * (1.0 - abs(progress - 0.5) * 2)
        workforce_plan["普工"].append(int(50 * laborer_factor))
    
    return workforce_plan

# 用户自定义配置模式
def generate_custom_workforce_plan(months, workforce_config):
    """
    根据用户输入的最大配置数量生成各工种的投入计划
    可以根据需要调整这里的生成逻辑
    """
    total_months = len(months)
    workforce_plan = {}
    
    # 为每个工种生成投入计划
    for work_type, max_count in workforce_config.items():
        # 新逻辑：每个月人数恒定为输入值（与输入一致）
        workforce_plan[work_type] = [int(max_count) for _ in range(total_months)]
    
    return workforce_plan

# 主函数：生成劳动力计划
def generate_workforce_plan(months, workforce_config=None):
    """
    生成劳动力计划
    如果workforce_config为None，则使用默认配置模式
    否则使用用户自定义配置
    """
    if workforce_config is None:
        return generate_default_workforce_plan(months)
    else:
        return generate_custom_workforce_plan(months, workforce_config)

# 输入工程时间范围
def get_project_dates():
    """获取用户输入的工程开始和结束日期"""
    print("请输入工程时间范围：")
    while True:
        try:
            start_date_str = input("开始日期 (格式: YYYY-MM-DD): ")
            end_date_str = input("结束日期 (格式: YYYY-MM-DD): ")
            
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            
            if start_date >= end_date:
                print("错误：开始日期必须早于结束日期！")
                continue
            
            return start_date, end_date
        except ValueError:
            print("错误：日期格式不正确，请使用YYYY-MM-DD格式！")

# 输入各工种配置数量
def get_workforce_configuration():
    """获取用户输入的各工种配置数量"""
    print("\n请输入各工种配置数量 (输入-1表示使用默认配置模式):")
    print("注：输入-1将自动生成符合工程进度的劳动力配置计划")
    
    workforce_config = {}
    use_default_config = False
    
    # 询问是否使用默认配置
    while True:
        choice = input("是否使用默认配置? (y/n): ")
        if choice.lower() == 'y':
            use_default_config = True
            break
        elif choice.lower() == 'n':
            break
        else:
            print("请输入 y 或 n")
    
    if use_default_config:
        print("将使用默认配置模式生成劳动力计划")
        return None  # 返回None表示使用默认配置
    
    # 逐个工种输入配置
    for work_type in WORK_TYPES:
        while True:
            try:
                max_count = input(f"{work_type} 最大配置数量: ")
                workforce_config[work_type] = int(max_count)
                break
            except ValueError:
                print("请输入有效的数字!")
    
    return workforce_config

# 创建Excel表格并导出数据
def export_to_excel(months, workforce_plan, output_file="路基工程劳动力计划.xlsx"):
    """
    将劳动力计划数据导出为Excel表格
    使用MultiIndex创建年份和月份的层级结构
    """
    # 获取月份列的层级结构
    years, month_numbers = get_month_columns(months)
    
    # 创建多级列索引
    columns = pd.MultiIndex.from_tuples(
        list(zip(years, month_numbers)),
        names=['年份', '月份']
    )
    
    # 创建数据
    data = []
    index = []
    
    for work_type, values in workforce_plan.items():
        index.append(work_type)
        data.append(values)
    
    # 创建DataFrame
    df = pd.DataFrame(data, index=index, columns=columns)
    
    # 创建ExcelWriter对象以进行格式化
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # 将DataFrame写入Excel
        df.to_excel(writer, sheet_name='劳动力计划', index_label='工种')
        
        # 获取工作表
        worksheet = writer.sheets['劳动力计划']
        
        # 设置列宽，使内容更好地显示
        worksheet.column_dimensions['A'].width = 12  # 工种列
        
        # 设置数据列的宽度为统一值（简化处理，避免合并单元格问题）
        # 获取最大列字母
        max_column = worksheet.max_column
        import openpyxl.utils as xlutils
        
        # 从B列开始设置所有数据列的宽度
        for col_idx in range(2, max_column + 1):
            column_letter = xlutils.get_column_letter(col_idx)
            worksheet.column_dimensions[column_letter].width = 10  # 统一设置列宽
    
    print(f"\nExcel表格已成功导出到: {output_file}")
    return output_file

# 图形界面应用
class PlanGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("路基工程劳动力计划生成器")
        try:
            # 在部分环境中设置几何可能失败，保持稳健
            self.root.geometry("800x600")
        except Exception:
            pass

        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass
        try:
            self.root.configure(bg='#F5FAFF')
        except Exception:
            pass
        self.colors = {
            'primary': '#1F5DA8',
            'accent': '#88C7E6',
            'card_bg': '#CFE5FF',
            'card_hover': '#B9DBFF',
            'root_bg': '#F5FAFF',
            'text_primary': '#1F5DA8'
        }
        style.configure('.', font=('Microsoft YaHei', 10))
        style.configure('TLabelframe', padding=8, borderwidth=1, background=self.colors['root_bg'])
        style.configure('TLabelframe.Label', font=('Microsoft YaHei', 10, 'bold'), foreground=self.colors['text_primary'], background=self.colors['root_bg'])
        style.configure('SectionHeader.TLabel', font=('Microsoft YaHei', 11, 'bold'), foreground=self.colors['text_primary'], padding=(4, 6))
        style.configure('TFrame', background=self.colors['root_bg'])
        style.configure('TNotebook', background=self.colors['root_bg'])
        style.configure('TNotebook.Tab', padding=(10,6), background=self.colors['root_bg'])
        style.configure('TButton', padding=6, background=self.colors['primary'], foreground='#FFFFFF')
        try:
            style.map('TButton', background=[('active', self.colors['primary'])], foreground=[('active', '#FFFFFF')])
        except Exception:
            pass
        try:
            style.layout('NoInd.TCheckbutton', [('Checkbutton.padding', {'children': [('Checkbutton.label', {'side': 'left', 'expand': 1})]})])
        except Exception:
            pass
        try:
            style.layout('ToggleButton.TCheckbutton', [('Checkbutton.padding', {'children': [('Checkbutton.label', {'side': 'left', 'expand': 1})]})])
            style.configure('ToggleButton.TCheckbutton', background=self.colors['card_bg'], foreground=self.colors['primary'], padding=(14, 6))
            style.map('ToggleButton.TCheckbutton', background=[('selected', self.colors['primary']), ('active', self.colors['card_hover'])], foreground=[('selected', '#FFFFFF'), ('!selected', self.colors['primary'])])
        except Exception:
            pass
        try:
            style.configure('ToggleOn.TButton', padding=6, background=self.colors['primary'], foreground='#FFFFFF')
            style.map('ToggleOn.TButton', background=[('active', self.colors['primary'])], foreground=[('active', '#FFFFFF')])
            style.configure('ToggleOff.TButton', padding=6, background=self.colors['card_bg'], foreground=self.colors['primary'])
            style.map('ToggleOff.TButton', background=[('active', self.colors['card_hover'])], foreground=[('active', self.colors['primary'])])
        except Exception:
            pass
        try:
            style.configure('Enabled.TNotebook', background=self.colors['root_bg'])
            style.configure('Enabled.TNotebook.Tab', padding=(10,6), background=self.colors['root_bg'], foreground=self.colors['text_primary'])
            style.map('Enabled.TNotebook.Tab', background=[('selected', self.colors['primary'])], foreground=[('selected', '#FFFFFF')])
            style.configure('Disabled.TNotebook', background=self.colors['root_bg'])
            style.configure('Disabled.TNotebook.Tab', padding=(10,6), background=self.colors['root_bg'], foreground=self.colors['text_primary'])
            style.map('Disabled.TNotebook.Tab', background=[('selected', self.colors['card_bg'])], foreground=[('selected', self.colors['text_primary'])])
            style.layout('TNotebook.Tab', [])
            style.configure('TNotebook.Tab', padding=0)
        except Exception:
            pass
        try:
            style.configure('NavItem.TFrame', background=self.colors['card_bg'], padding=4)
            style.configure('NavItemSelected.TFrame', background=self.colors['card_hover'], padding=4)
            style.configure('Card.TFrame', background=self.colors['root_bg'], padding=4)
        except Exception:
            pass

        # 年月选择范围
        current_year = datetime.now().year
        self.year_options = [y for y in range(current_year - 5, current_year + 11)]
        self.month_options = [m for m in range(1, 13)]

        # 变量
        self.start_year_var = tk.IntVar(value=current_year)
        self.start_month_var = tk.IntVar(value=datetime.now().month)
        self.end_year_var = tk.IntVar(value=current_year)
        self.end_month_var = tk.IntVar(value=datetime.now().month)
        self.use_default_var = tk.BooleanVar(value=True)
        self.enable_rb = tk.BooleanVar(value=False)
        self.output_path_var = tk.StringVar(value=os.path.join(os.getcwd(), "路基工程劳动力计划.xlsx"))
        self.team_count_var = tk.IntVar(value=1)
        # 路基工程时间范围变量
        self.start_year_var_rb = tk.IntVar(value=current_year)
        self.start_month_var_rb = tk.IntVar(value=datetime.now().month)
        self.end_year_var_rb = tk.IntVar(value=current_year)
        self.end_month_var_rb = tk.IntVar(value=datetime.now().month)

        # 路基工程阶段（路基填筑开挖阶段、路基防排水阶段）
        self.rb_modules = ["路基填筑开挖阶段", "路基防排水阶段"]
        self.use_default_rb_vars = {}
        self.team_count_rb_vars = {}
        self.start_year_var_rb_m = {}
        self.start_month_var_rb_m = {}
        self.end_year_var_rb_m = {}
        self.end_month_var_rb_m = {}
        self.config_vars_rb_modules = {}
        self.enabled_rb_modules = {}
        self.spin_widgets_rb_modules = {}
        self.custom_rb_frames = {}
        self.rb_mod_frames = {}
        rb_defaults = {
            "模板工": 80,
            "混凝土工": 90,
            "钢筋工": 100,
            "支架工": 40,
            "测量工": 10,
            "电焊工": 35,
            "泥瓦工": 25,
            "电工": 5,
            "普工": 50
        }
        for module in self.rb_modules:
            self.use_default_rb_vars[module] = tk.BooleanVar(value=True)
            self.team_count_rb_vars[module] = tk.IntVar(value=1)
            self.start_year_var_rb_m[module] = tk.IntVar(value=current_year)
            self.start_month_var_rb_m[module] = tk.IntVar(value=datetime.now().month)
            self.end_year_var_rb_m[module] = tk.IntVar(value=current_year)
            self.end_month_var_rb_m[module] = tk.IntVar(value=datetime.now().month)
            self.config_vars_rb_modules[module] = {wt: tk.IntVar(value=val) for wt, val in rb_defaults.items()}
            self.enabled_rb_modules[module] = {wt: tk.BooleanVar(value=True) for wt in WORK_TYPES}
            self.spin_widgets_rb_modules[module] = {}

        # 桥梁工程相关变量
        self.use_default_bridge_var = tk.BooleanVar(value=True)
        self.enable_br = tk.BooleanVar(value=False)
        self.team_count_bridge_var = tk.IntVar(value=1)
        # 桥梁工程时间范围变量
        self.start_year_var_br = tk.IntVar(value=current_year)
        self.start_month_var_br = tk.IntVar(value=datetime.now().month)
        self.end_year_var_br = tk.IntVar(value=current_year)
        self.end_month_var_br = tk.IntVar(value=datetime.now().month)
        self.br_modules = ["基础施工阶段", "墩柱施工阶段", "梁板预制及安装阶段", "桥面系及附属施工阶段"]
        self.use_default_br_vars = {}
        self.team_count_br_vars = {}
        self.start_year_var_br_m = {}
        self.start_month_var_br_m = {}
        self.end_year_var_br_m = {}
        self.end_month_var_br_m = {}
        self.config_vars_br_modules = {}
        self.enabled_br_modules = {}
        self.spin_widgets_br_modules = {}
        self.custom_br_frames = {}
        self.br_mod_frames = {}
        br_defaults = {
            "模板工": 80,
            "混凝土工": 90,
            "钢筋工": 100,
            "支架工": 40,
            "测量工": 10,
            "电焊工": 35,
            "泥瓦工": 25,
            "电工": 5,
            "普工": 50
        }
        for module in self.br_modules:
            self.use_default_br_vars[module] = tk.BooleanVar(value=True)
            self.team_count_br_vars[module] = tk.IntVar(value=1)
            self.start_year_var_br_m[module] = tk.IntVar(value=current_year)
            self.start_month_var_br_m[module] = tk.IntVar(value=datetime.now().month)
            self.end_year_var_br_m[module] = tk.IntVar(value=current_year)
            self.end_month_var_br_m[module] = tk.IntVar(value=datetime.now().month)
            self.config_vars_br_modules[module] = {wt: tk.IntVar(value=val) for wt, val in br_defaults.items()}
            self.enabled_br_modules[module] = {wt: tk.BooleanVar(value=True) for wt in WORK_TYPES}
            self.spin_widgets_br_modules[module] = {}

        # 路面工程相关变量
        self.use_default_pave_var = tk.BooleanVar(value=True)
        self.enable_pv = tk.BooleanVar(value=False)
        self.team_count_pave_var = tk.IntVar(value=1)
        # 路面工程时间范围变量
        self.start_year_var_pv = tk.IntVar(value=current_year)
        self.start_month_var_pv = tk.IntVar(value=datetime.now().month)
        self.end_year_var_pv = tk.IntVar(value=current_year)
        self.end_month_var_pv = tk.IntVar(value=datetime.now().month)
        # 路面工程阶段（路面基层施工阶段、路面路面施工阶段）
        self.pv_modules = ["路面基层施工阶段", "路面路面施工阶段"]
        self.use_default_pv_vars = {}
        self.team_count_pv_vars = {}
        self.start_year_var_pv_m = {}
        self.start_month_var_pv_m = {}
        self.end_year_var_pv_m = {}
        self.end_month_var_pv_m = {}
        self.config_vars_pv_modules = {}
        self.enabled_pv_modules = {}
        self.spin_widgets_pv_modules = {}
        self.custom_pv_frames = {}
        self.pv_mod_frames = {}
        pv_defaults = {
            "模板工": 80,
            "混凝土工": 90,
            "钢筋工": 100,
            "支架工": 40,
            "测量工": 10,
            "电焊工": 35,
            "泥瓦工": 25,
            "电工": 5,
            "普工": 50
        }
        for module in self.pv_modules:
            self.use_default_pv_vars[module] = tk.BooleanVar(value=True)
            self.team_count_pv_vars[module] = tk.IntVar(value=1)
            self.start_year_var_pv_m[module] = tk.IntVar(value=current_year)
            self.start_month_var_pv_m[module] = tk.IntVar(value=datetime.now().month)
            self.end_year_var_pv_m[module] = tk.IntVar(value=current_year)
            self.end_month_var_pv_m[module] = tk.IntVar(value=datetime.now().month)
            self.config_vars_pv_modules[module] = {wt: tk.IntVar(value=val) for wt, val in pv_defaults.items()}
            self.enabled_pv_modules[module] = {wt: tk.BooleanVar(value=True) for wt in WORK_TYPES}
            self.spin_widgets_pv_modules[module] = {}
        
        # 隧道工程相关变量
        self.use_default_tunnel_var = tk.BooleanVar(value=True)
        self.enable_tu = tk.BooleanVar(value=False)
        self.team_count_tunnel_var = tk.IntVar(value=1)
        # 隧道工程时间范围变量
        self.start_year_var_tu = tk.IntVar(value=current_year)
        self.start_month_var_tu = tk.IntVar(value=datetime.now().month)
        self.end_year_var_tu = tk.IntVar(value=current_year)
        self.end_month_var_tu = tk.IntVar(value=datetime.now().month)

        self.use_default_house_var = tk.BooleanVar(value=True)
        self.enable_house = tk.BooleanVar(value=False)
        self.team_count_house_var = tk.IntVar(value=1)
        self.start_year_var_h = tk.IntVar(value=current_year)
        self.start_month_var_h = tk.IntVar(value=datetime.now().month)
        self.end_year_var_h = tk.IntVar(value=current_year)
        self.end_month_var_h = tk.IntVar(value=datetime.now().month)

        # 自定义配置变量（默认设为各工种建议最大值）
        self.config_vars = {wt: tk.IntVar(value=val) for wt, val in {
            "模板工": 80,
            "混凝土工": 90,
            "钢筋工": 100,
            "支架工": 40,
            "测量工": 10,
            "电焊工": 35,
            "泥瓦工": 25,
            "电工": 5,
            "普工": 50
        }.items()}
        self.enabled_vars = {wt: tk.BooleanVar(value=True) for wt in WORK_TYPES}
        self.spin_widgets_rb = {}

        # 桥梁工程自定义配置变量
        self.config_vars_bridge = {wt: tk.IntVar(value=val) for wt, val in {
            "模板工": 80,
            "混凝土工": 90,
            "钢筋工": 100,
            "支架工": 40,
            "测量工": 10,
            "电焊工": 35,
            "泥瓦工": 25,
            "电工": 5,
            "普工": 50
        }.items()}
        self.enabled_bridge_vars = {wt: tk.BooleanVar(value=True) for wt in WORK_TYPES}
        self.spin_widgets_bridge = {}

        # 路面工程自定义配置变量
        self.config_vars_pave = {wt: tk.IntVar(value=val) for wt, val in {
            "模板工": 80,
            "混凝土工": 90,
            "钢筋工": 100,
            "支架工": 40,
            "测量工": 10,
            "电焊工": 35,
            "泥瓦工": 25,
            "电工": 5,
            "普工": 50
        }.items()}
        self.enabled_pave_vars = {wt: tk.BooleanVar(value=True) for wt in WORK_TYPES}
        self.spin_widgets_pave = {}
        
        # 隧道工程自定义配置变量
        self.config_vars_tunnel = {wt: tk.IntVar(value=val) for wt, val in {
            "模板工": 100,
            "混凝土工": 80,
            "钢筋工": 120,
            "支架工": 60,
            "测量工": 15,
            "电焊工": 50,
            "泥瓦工": 30,
            "电工": 8,
            "普工": 70
        }.items()}

        self.config_vars_house = {wt: tk.IntVar(value=val) for wt, val in {
            "模板工": 80,
            "混凝土工": 90,
            "钢筋工": 100,
            "支架工": 40,
            "测量工": 10,
            "电焊工": 35,
            "泥瓦工": 25,
            "电工": 5,
            "普工": 50
        }.items()}
        self.enabled_house_vars = {wt: tk.BooleanVar(value=True) for wt in WORK_TYPES}
        self.spin_widgets_house = {}
        self.custom_house_frame = None
        # 房建工程阶段化变量
        self.hs_modules = ["基础施工阶段", "主体施工阶段", "装饰装修施工阶段", "机电安装工程"]
        self.use_default_house_vars = {}
        self.team_count_house_vars = {}
        self.start_year_var_h_m = {}
        self.start_month_var_h_m = {}
        self.end_year_var_h_m = {}
        self.end_month_var_h_m = {}
        self.config_vars_house_modules = {}
        self.enabled_house_modules = {}
        self.spin_widgets_house_modules = {}
        self.custom_house_frames = {}
        self.house_mod_frames = {}
        house_defaults = {
            "模板工": 80,
            "混凝土工": 90,
            "钢筋工": 100,
            "支架工": 40,
            "测量工": 10,
            "电焊工": 35,
            "泥瓦工": 25,
            "电工": 5,
            "普工": 50
        }
        for module in self.hs_modules:
            self.use_default_house_vars[module] = tk.BooleanVar(value=True)
            self.team_count_house_vars[module] = tk.IntVar(value=1)
            self.start_year_var_h_m[module] = tk.IntVar(value=current_year)
            self.start_month_var_h_m[module] = tk.IntVar(value=datetime.now().month)
            self.end_year_var_h_m[module] = tk.IntVar(value=current_year)
            self.end_month_var_h_m[module] = tk.IntVar(value=datetime.now().month)
            self.config_vars_house_modules[module] = {wt: tk.IntVar(value=val) for wt, val in house_defaults.items()}
            self.enabled_house_modules[module] = {wt: tk.BooleanVar(value=True) for wt in WORK_TYPES}
            self.spin_widgets_house_modules[module] = {}

        self.tunnel_modules = ["洞口工程", "初支工程", "二衬工程", "附属工程"]
        self.tunnel_names = [f"隧道{i}" for i in range(1, 7)]
        self.enable_tunnel = {name: tk.BooleanVar(value=False) for name in self.tunnel_names}
        self.use_default_tunnel_vars = {}
        self.team_count_tunnel_vars = {}
        self.start_year_var_tm = {}
        self.start_month_var_tm = {}
        self.end_year_var_tm = {}
        self.end_month_var_tm = {}
        self.config_vars_tunnel_modules = {}
        self.custom_tunnel_frames = {}
        self.enabled_tunnel_modules = {}
        self.spin_widgets_tunnel = {}
        self.tunnel_mod_frames = {}
        self.tunnel_root_frames = {}
        tunnel_defaults = {
            "出渣工": 60,
            "防水工": 30,
            "钢筋工": 120,
            "混凝土工": 80,
            "开挖工": 100,
            "模板工": 100,
            "喷砼工": 90,
            "普通工": 70,
            "司机": 30,
            "支护工": 30,
            "电焊工": 50
        }
        for tunnel in self.tunnel_names:
            self.use_default_tunnel_vars[tunnel] = {}
            self.team_count_tunnel_vars[tunnel] = {}
            self.start_year_var_tm[tunnel] = {}
            self.start_month_var_tm[tunnel] = {}
            self.end_year_var_tm[tunnel] = {}
            self.end_month_var_tm[tunnel] = {}
            self.config_vars_tunnel_modules[tunnel] = {}
            self.custom_tunnel_frames[tunnel] = {}
            self.enabled_tunnel_modules[tunnel] = {}
            self.spin_widgets_tunnel[tunnel] = {}
            for module in self.tunnel_modules:
                self.use_default_tunnel_vars[tunnel][module] = tk.BooleanVar(value=True)
                self.team_count_tunnel_vars[tunnel][module] = tk.IntVar(value=1)
                self.start_year_var_tm[tunnel][module] = tk.IntVar(value=current_year)
                self.start_month_var_tm[tunnel][module] = tk.IntVar(value=datetime.now().month)
                self.end_year_var_tm[tunnel][module] = tk.IntVar(value=current_year)
                self.end_month_var_tm[tunnel][module] = tk.IntVar(value=datetime.now().month)
                self.config_vars_tunnel_modules[tunnel][module] = {wt: tk.IntVar(value=val) for wt, val in tunnel_defaults.items()}
                self.enabled_tunnel_modules[tunnel][module] = {wt: tk.BooleanVar(value=True) for wt in TUNNEL_WORK_TYPES}
                self.spin_widgets_tunnel[tunnel][module] = {}

        self._build_ui()

    def _build_ui(self):
        # 右侧垂直滚动区域
        outer_scroll = ttk.Frame(self.root)
        outer_scroll.pack(fill="both", expand=True)
        self.scroll_canvas = tk.Canvas(outer_scroll, highlightthickness=0)
        vbar = ttk.Scrollbar(outer_scroll, orient="vertical", command=self.scroll_canvas.yview)
        self.scroll_canvas.configure(yscrollcommand=vbar.set)
        self.scroll_canvas.pack(side="left", fill="both", expand=True)
        vbar.pack(side="right", fill="y")
        self.scroll_content = ttk.Frame(self.scroll_canvas)
        self._scroll_window_id = self.scroll_canvas.create_window((0, 0), window=self.scroll_content, anchor="nw")
        self.scroll_content.bind("<Configure>", lambda e: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all")))
        self.scroll_canvas.bind("<Configure>", lambda e: self.scroll_canvas.itemconfig(self._scroll_window_id, width=e.width))
        try:
            self.scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
            self.scroll_canvas.bind_all("<Button-4>", lambda e: self.scroll_canvas.yview_scroll(-1, "units"))
            self.scroll_canvas.bind_all("<Button-5>", lambda e: self.scroll_canvas.yview_scroll(1, "units"))
        except Exception:
            pass

        # 使用 Notebook 分多个界面（置于滚动内容中）
        notebook = ttk.Notebook(self.scroll_content)
        tabs_header = ttk.Frame(self.scroll_content)
        tabs_header.pack(fill="x", padx=10, pady=(4,0))
        tab_rb = ttk.Frame(notebook)
        tab_br = ttk.Frame(notebook)
        tab_pv = ttk.Frame(notebook)
        tab_tu = ttk.Frame(notebook)  # 隧道工程标签页
        tab_hs = ttk.Frame(notebook)
        notebook.add(tab_rb, text="路基工程")
        notebook.add(tab_br, text="桥梁工程")
        notebook.add(tab_pv, text="路面工程")
        notebook.add(tab_tu, text="隧道工程")
        notebook.add(tab_hs, text="房建工程")
        notebook.pack(fill="both", expand=True, padx=10, pady=8)
        self.notebook = notebook
        self._tab_map = {str(tab_rb): 'rb', str(tab_br): 'br', str(tab_pv): 'pv', str(tab_tu): 'tu', str(tab_hs): 'hs'}
        self.header_tab_buttons = {}
        for tab_ref, key, title in [(tab_rb, 'rb', '路基工程'), (tab_br, 'br', '桥梁工程'), (tab_pv, 'pv', '路面工程'), (tab_tu, 'tu', '隧道工程'), (tab_hs, 'hs', '房建工程')]:
            btn = ttk.Button(tabs_header, text=title, command=lambda t=tab_ref: notebook.select(t), style='ToggleOff.TButton')
            btn.configure(width=12)
            btn.pack(side="left", padx=(0,8), pady=0)
            self.header_tab_buttons[key] = btn
        try:
            notebook.bind('<<NotebookTabChanged>>', lambda _e: self._update_notebook_style_by_selected())
        except Exception:
            pass
        try:
            self._update_notebook_style_by_selected()
        except Exception:
            pass

        if 'card_bg_canvases' not in self.__dict__:
            self.card_bg_canvases = {}
        if 'card_labels' not in self.__dict__:
            self.card_labels = {}
        if 'card_circle_canvases' not in self.__dict__:
            self.card_circle_canvases = {}
        if 'card_circle_items' not in self.__dict__:
            self.card_circle_items = {}

        rb_card = ttk.Frame(tab_rb, style='Card.TFrame')
        rb_card.pack(padx=12, pady=(8,0), anchor="w")
        rb_bg = tk.Canvas(rb_card, highlightthickness=0, bd=0)
        rb_bg.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.card_bg_canvases['rb'] = rb_bg
        rb_card.bind("<Configure>", lambda e: self._draw_round_rect(rb_bg, radius=10, fill=self.colors['card_bg']))
        self.root.after(0, lambda cv=rb_bg: self._draw_round_rect(cv, radius=10, fill=self.colors['card_bg']))
        rb_row = ttk.Frame(rb_card, style='Card.TFrame')
        rb_row.pack(anchor="w")
        rb_row.configure(height=37)
        rb_row.pack_propagate(False)
        rb_row.grid_columnconfigure(0, weight=0)
        rb_row.grid_rowconfigure(0, weight=1)
        rb_toggle = ttk.Button(rb_row, text="参与计算", command=lambda: (self.enable_rb.set(not self.enable_rb.get()), self._toggle_enable_rb()), style='ToggleOff.TButton')
        rb_toggle.configure(width=12)
        rb_toggle.grid(row=0, column=0, padx=8, pady=0, sticky="w")
        rb_card.configure(cursor='hand2')
        rb_toggle.configure(cursor='hand2')
        rb_row.configure(cursor='hand2')
        rb_card.bind("<Button-1>", lambda _e: (self.enable_rb.set(not self.enable_rb.get()), self._toggle_enable_rb(), self._update_toggle_button('rb')))
        rb_card.bind("<Enter>", lambda _e: self._set_card_hover('rb', True))
        rb_card.bind("<Leave>", lambda _e: self._set_card_hover('rb', False))
        if 'card_toggle_buttons' not in self.__dict__:
            self.card_toggle_buttons = {}
        self.card_toggle_buttons['rb'] = rb_toggle
        try:
            self.enable_rb.trace_add('write', lambda *_: self._update_toggle_button('rb'))
        except Exception:
            pass
        
        
        self._update_card_toggle('rb')
        rb_container = ttk.Frame(tab_rb)
        rb_container.pack(fill="x", expand=False, padx=10, pady=8)
        rb_container.columnconfigure(0, weight=1)
        rb_container.columnconfigure(1, weight=1)
        for i, module in enumerate(self.rb_modules):
            r = 0
            c = i % 2
            mod_frame = ttk.Frame(rb_container)
            mod_frame.grid(row=r, column=c, padx=10, pady=8, sticky="nsew")
            self.rb_mod_frames[module] = mod_frame
            ttk.Label(mod_frame, text=f"{module}", style="SectionHeader.TLabel").pack(fill="x", padx=4, pady=(0,6))
            team_frame = ttk.LabelFrame(mod_frame, text="队伍设置")
            team_frame.pack(fill="x", padx=12, pady=8)
            ttk.Label(team_frame, text="队伍个数").grid(row=0, column=0, padx=6, pady=6, sticky="w")
            tk.Spinbox(team_frame, from_=1, to=100, textvariable=self.team_count_rb_vars[module], width=6).grid(row=0, column=1, padx=6, pady=6, sticky="w")

            date_frame = ttk.LabelFrame(mod_frame, text="时间范围（选择到月份）")
            date_frame.pack(fill="x", padx=12, pady=8)
            ttk.Label(date_frame, text="开始年份").grid(row=0, column=0, padx=6, pady=6, sticky="w")
            ttk.Combobox(date_frame, values=self.year_options, textvariable=self.start_year_var_rb_m[module], width=8, state="readonly").grid(row=0, column=1, padx=6, pady=6)
            ttk.Label(date_frame, text="开始月份").grid(row=0, column=2, padx=6, pady=6, sticky="w")
            ttk.Combobox(date_frame, values=self.month_options, textvariable=self.start_month_var_rb_m[module], width=6, state="readonly").grid(row=0, column=3, padx=6, pady=6)
            ttk.Label(date_frame, text="结束年份").grid(row=1, column=0, padx=6, pady=6, sticky="w")
            ttk.Combobox(date_frame, values=self.year_options, textvariable=self.end_year_var_rb_m[module], width=8, state="readonly").grid(row=1, column=1, padx=6, pady=6)
            ttk.Label(date_frame, text="结束月份").grid(row=1, column=2, padx=6, pady=6, sticky="w")
            ttk.Combobox(date_frame, values=self.month_options, textvariable=self.end_month_var_rb_m[module], width=6, state="readonly").grid(row=1, column=3, padx=6, pady=6)

            mode_frame = ttk.LabelFrame(mod_frame, text="配置模式")
            mode_frame.pack(fill="x", padx=12, pady=8)
            ttk.Radiobutton(mode_frame, text="使用默认配置（自动生成曲线）", variable=self.use_default_rb_vars[module], value=True, command=lambda m=module: self._toggle_rb_module_config_frame(m)).grid(row=0, column=0, padx=6, pady=6, sticky="w")
            ttk.Radiobutton(mode_frame, text="自定义各工种最大配置数量", variable=self.use_default_rb_vars[module], value=False, command=lambda m=module: self._toggle_rb_module_config_frame(m)).grid(row=0, column=1, padx=6, pady=6, sticky="w")

            custom_frame = ttk.LabelFrame(mod_frame, text="自定义工种最大配置数量")
            self.custom_rb_frames[module] = custom_frame
            custom_frame.pack(fill="x", padx=12, pady=8)
            for idx, wt in enumerate(WORK_TYPES):
                rr = idx // 3
                cc = (idx % 3) * 2
                if 'label_rb_modules' not in self.__dict__:
                    self.label_rb_modules = {}
                self.label_rb_modules.setdefault(module, {})
                lvr = tk.StringVar()
                lvr.set(("√ " if self.enabled_rb_modules[module][wt].get() else "× ") + wt)
                try:
                    self.enabled_rb_modules[module][wt].trace_add('write', lambda *_x, v=self.enabled_rb_modules[module][wt], s=lvr, name=wt: s.set(("√ " if v.get() else "× ") + name))
                except Exception:
                    pass
                self.label_rb_modules[module][wt] = lvr
                chkr = ttk.Checkbutton(custom_frame, textvariable=lvr, variable=self.enabled_rb_modules[module][wt], command=lambda m=module, w=wt: self._update_spin_state_rb_module(m, w), style='NoInd.TCheckbutton')
                chkr.grid(row=rr, column=cc, padx=6, pady=6, sticky="e")
                spinr = tk.Spinbox(custom_frame, from_=0, to=500, textvariable=self.config_vars_rb_modules[module][wt], width=6)
                spinr.grid(row=rr, column=cc+1, padx=6, pady=6, sticky="w")
                self.spin_widgets_rb_modules[module][wt] = spinr
                self._update_spin_state_rb_module(module, wt)

        

        br_card = ttk.Frame(tab_br, style='Card.TFrame')
        br_card.pack(padx=12, pady=(8,0), anchor="w")
        br_bg = tk.Canvas(br_card, highlightthickness=0, bd=0)
        br_bg.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.card_bg_canvases['br'] = br_bg
        br_card.bind("<Configure>", lambda e: self._draw_round_rect(br_bg, radius=10, fill=self.colors['card_bg']))
        self.root.after(0, lambda cv=br_bg: self._draw_round_rect(cv, radius=10, fill=self.colors['card_bg']))
        br_row = ttk.Frame(br_card, style='Card.TFrame')
        br_row.pack(anchor="w")
        br_row.configure(height=37)
        br_row.pack_propagate(False)
        br_row.grid_columnconfigure(0, weight=0)
        br_row.grid_rowconfigure(0, weight=1)
        br_toggle = ttk.Button(br_row, text="参与计算", command=lambda: (self.enable_br.set(not self.enable_br.get()), self._toggle_enable_br(), self._update_toggle_button('br')), style='ToggleOff.TButton')
        br_toggle.configure(width=12)
        br_toggle.grid(row=0, column=0, padx=8, pady=0, sticky="w")
        br_card.configure(cursor='hand2')
        br_toggle.configure(cursor='hand2')
        br_row.configure(cursor='hand2')
        br_card.bind("<Button-1>", lambda _e: (self.enable_br.set(not self.enable_br.get()), self._toggle_enable_br(), self._update_toggle_button('br')))
        br_card.bind("<Enter>", lambda _e: self._set_card_hover('br', True))
        br_card.bind("<Leave>", lambda _e: self._set_card_hover('br', False))
        self.card_toggle_buttons['br'] = br_toggle
        try:
            self.enable_br.trace_add('write', lambda *_: self._update_toggle_button('br'))
        except Exception:
            pass
        self._update_toggle_button('br')
        
        
        br_container = ttk.Frame(tab_br)
        br_container.pack(fill="both", expand=True, padx=10, pady=8)
        br_container.columnconfigure(0, weight=1)
        br_container.columnconfigure(1, weight=1)
        br_container.rowconfigure(0, weight=1)
        br_container.rowconfigure(1, weight=1)
        for i, module in enumerate(self.br_modules):
            r = 0 if i < 2 else 1
            c = i % 2
            mod_frame = ttk.Frame(br_container)
            mod_frame.grid(row=r, column=c, padx=10, pady=8, sticky="nsew")
            self.br_mod_frames[module] = mod_frame
            ttk.Label(mod_frame, text=f"{module}", style="SectionHeader.TLabel").pack(fill="x", padx=4, pady=(0,6))
            team_frame = ttk.LabelFrame(mod_frame, text="队伍设置")
            team_frame.pack(fill="x", padx=12, pady=8)
            ttk.Label(team_frame, text="队伍个数").grid(row=0, column=0, padx=6, pady=6, sticky="w")
            tk.Spinbox(team_frame, from_=1, to=100, textvariable=self.team_count_br_vars[module], width=6).grid(row=0, column=1, padx=6, pady=6, sticky="w")

            date_frame = ttk.LabelFrame(mod_frame, text="时间范围（选择到月份）")
            date_frame.pack(fill="x", padx=12, pady=8)
            ttk.Label(date_frame, text="开始年份").grid(row=0, column=0, padx=6, pady=6, sticky="w")
            ttk.Combobox(date_frame, values=self.year_options, textvariable=self.start_year_var_br_m[module], width=8, state="readonly").grid(row=0, column=1, padx=6, pady=6)
            ttk.Label(date_frame, text="开始月份").grid(row=0, column=2, padx=6, pady=6, sticky="w")
            ttk.Combobox(date_frame, values=self.month_options, textvariable=self.start_month_var_br_m[module], width=6, state="readonly").grid(row=0, column=3, padx=6, pady=6)
            ttk.Label(date_frame, text="结束年份").grid(row=1, column=0, padx=6, pady=6, sticky="w")
            ttk.Combobox(date_frame, values=self.year_options, textvariable=self.end_year_var_br_m[module], width=8, state="readonly").grid(row=1, column=1, padx=6, pady=6)
            ttk.Label(date_frame, text="结束月份").grid(row=1, column=2, padx=6, pady=6, sticky="w")
            ttk.Combobox(date_frame, values=self.month_options, textvariable=self.end_month_var_br_m[module], width=6, state="readonly").grid(row=1, column=3, padx=6, pady=6)

            bridge_mode_frame = ttk.LabelFrame(mod_frame, text="配置模式")
            bridge_mode_frame.pack(fill="x", padx=12, pady=8)
            ttk.Radiobutton(bridge_mode_frame, text="使用默认配置（自动生成曲线）", variable=self.use_default_br_vars[module], value=True, command=lambda m=module: self._toggle_bridge_module_config_frame(m)).grid(row=0, column=0, padx=6, pady=6, sticky="w")
            ttk.Radiobutton(bridge_mode_frame, text="自定义各工种最大配置数量", variable=self.use_default_br_vars[module], value=False, command=lambda m=module: self._toggle_bridge_module_config_frame(m)).grid(row=0, column=1, padx=6, pady=6, sticky="w")

            custom_frame = ttk.LabelFrame(mod_frame, text="自定义工种最大配置数量")
            self.custom_br_frames[module] = custom_frame
            custom_frame.pack(fill="both", padx=12, pady=8)
            for idx, wt in enumerate(WORK_TYPES):
                rr = idx // 3
                cc = (idx % 3) * 2
                if 'label_br_modules' not in self.__dict__:
                    self.label_br_modules = {}
                self.label_br_modules.setdefault(module, {})
                lvb = tk.StringVar()
                lvb.set(("√ " if self.enabled_br_modules[module][wt].get() else "× ") + wt)
                try:
                    self.enabled_br_modules[module][wt].trace_add('write', lambda *_x, v=self.enabled_br_modules[module][wt], s=lvb, name=wt: s.set(("√ " if v.get() else "× ") + name))
                except Exception:
                    pass
                self.label_br_modules[module][wt] = lvb
                chkb = ttk.Checkbutton(custom_frame, textvariable=lvb, variable=self.enabled_br_modules[module][wt], command=lambda m=module, w=wt: self._update_spin_state_bridge_module(m, w), style='NoInd.TCheckbutton')
                chkb.grid(row=rr, column=cc, padx=6, pady=6, sticky="e")
                spinb = tk.Spinbox(custom_frame, from_=0, to=500, textvariable=self.config_vars_br_modules[module][wt], width=6)
                spinb.grid(row=rr, column=cc+1, padx=6, pady=6, sticky="w")
                self.spin_widgets_br_modules[module][wt] = spinb
                self._update_spin_state_bridge_module(module, wt)

        # 桥梁工程：导出设置与操作按钮（靠近自定义模块）
        out_frame_br = ttk.LabelFrame(tab_br, text="导出设置")
        out_frame_br.pack(fill="x", padx=12, pady=4)
        ttk.Label(out_frame_br, text="输出文件").grid(row=0, column=0, padx=6, pady=4, sticky="w")
        out_entry_br = ttk.Entry(out_frame_br, textvariable=self.output_path_var, width=60)
        out_entry_br.grid(row=0, column=1, padx=6, pady=4, sticky="w")
        ttk.Button(out_frame_br, text="选择...", command=self._choose_output_file).grid(row=0, column=2, padx=6, pady=4)

        btn_frame_br = ttk.Frame(tab_br)
        btn_frame_br.pack(fill="x", padx=12, pady=6)
        ttk.Button(btn_frame_br, text="生成 Excel", command=self._generate).pack(side="left", padx=6)
        ttk.Button(btn_frame_br, text="退出", command=self.root.quit).pack(side="right", padx=6)

        pv_card = ttk.Frame(tab_pv, style='Card.TFrame')
        pv_card.pack(padx=12, pady=(8,0), anchor="w")
        pv_bg = tk.Canvas(pv_card, highlightthickness=0, bd=0)
        pv_bg.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.card_bg_canvases['pv'] = pv_bg
        pv_card.bind("<Configure>", lambda e: self._draw_round_rect(pv_bg, radius=10, fill=self.colors['card_bg']))
        self.root.after(0, lambda cv=pv_bg: self._draw_round_rect(cv, radius=10, fill=self.colors['card_bg']))
        pv_row = ttk.Frame(pv_card, style='Card.TFrame')
        pv_row.pack(anchor="w")
        pv_row.configure(height=37)
        pv_row.pack_propagate(False)
        pv_row.grid_columnconfigure(0, weight=0)
        pv_row.grid_rowconfigure(0, weight=1)
        pv_toggle = ttk.Button(pv_row, text="参与计算", command=lambda: (self.enable_pv.set(not self.enable_pv.get()), self._toggle_enable_pv(), self._update_toggle_button('pv')), style='ToggleOff.TButton')
        pv_toggle.configure(width=12)
        pv_toggle.grid(row=0, column=0, padx=8, pady=0, sticky="w")
        pv_card.configure(cursor='hand2')
        pv_toggle.configure(cursor='hand2')
        pv_row.configure(cursor='hand2')
        pv_card.bind("<Button-1>", lambda _e: (self.enable_pv.set(not self.enable_pv.get()), self._toggle_enable_pv(), self._update_toggle_button('pv')))
        self.card_toggle_buttons['pv'] = pv_toggle
        try:
            self.enable_pv.trace_add('write', lambda *_: self._update_toggle_button('pv'))
        except Exception:
            pass
        self._update_toggle_button('pv')
        pv_card.bind("<Enter>", lambda _e: self._set_card_hover('pv', True))
        pv_card.bind("<Leave>", lambda _e: self._set_card_hover('pv', False))
        
        
        pv_container = ttk.Frame(tab_pv)
        pv_container.pack(fill="x", expand=False, padx=10, pady=8)
        pv_container.columnconfigure(0, weight=1)
        pv_container.columnconfigure(1, weight=1)
        for i, module in enumerate(self.pv_modules):
            r = 0
            c = i % 2
            mod_frame = ttk.Frame(pv_container)
            mod_frame.grid(row=r, column=c, padx=10, pady=8, sticky="nsew")
            self.pv_mod_frames[module] = mod_frame
            ttk.Label(mod_frame, text=f"{module}", style="SectionHeader.TLabel").pack(fill="x", padx=4, pady=(0,6))
            team_frame = ttk.LabelFrame(mod_frame, text="队伍设置")
            team_frame.pack(fill="x", padx=12, pady=8)
            ttk.Label(team_frame, text="队伍个数").grid(row=0, column=0, padx=6, pady=6, sticky="w")
            tk.Spinbox(team_frame, from_=1, to=100, textvariable=self.team_count_pv_vars[module], width=6).grid(row=0, column=1, padx=6, pady=6, sticky="w")

            pv_date_frame = ttk.LabelFrame(mod_frame, text="时间范围（选择到月份）")
            pv_date_frame.pack(fill="x", padx=12, pady=8)
            ttk.Label(pv_date_frame, text="开始年份").grid(row=0, column=0, padx=6, pady=6, sticky="w")
            ttk.Combobox(pv_date_frame, values=self.year_options, textvariable=self.start_year_var_pv_m[module], width=8, state="readonly").grid(row=0, column=1, padx=6, pady=6)
            ttk.Label(pv_date_frame, text="开始月份").grid(row=0, column=2, padx=6, pady=6, sticky="w")
            ttk.Combobox(pv_date_frame, values=self.month_options, textvariable=self.start_month_var_pv_m[module], width=6, state="readonly").grid(row=0, column=3, padx=6, pady=6)
            ttk.Label(pv_date_frame, text="结束年份").grid(row=1, column=0, padx=6, pady=6, sticky="w")
            ttk.Combobox(pv_date_frame, values=self.year_options, textvariable=self.end_year_var_pv_m[module], width=8, state="readonly").grid(row=1, column=1, padx=6, pady=6)
            ttk.Label(pv_date_frame, text="结束月份").grid(row=1, column=2, padx=6, pady=6, sticky="w")
            ttk.Combobox(pv_date_frame, values=self.month_options, textvariable=self.end_month_var_pv_m[module], width=6, state="readonly").grid(row=1, column=3, padx=6, pady=6)

            pave_mode_frame = ttk.LabelFrame(mod_frame, text="配置模式")
            pave_mode_frame.pack(fill="x", padx=12, pady=8)
            ttk.Radiobutton(pave_mode_frame, text="使用默认配置（自动生成曲线）", variable=self.use_default_pv_vars[module], value=True, command=lambda m=module: self._toggle_pv_module_config_frame(m)).grid(row=0, column=0, padx=6, pady=6, sticky="w")
            ttk.Radiobutton(pave_mode_frame, text="自定义各工种最大配置数量", variable=self.use_default_pv_vars[module], value=False, command=lambda m=module: self._toggle_pv_module_config_frame(m)).grid(row=0, column=1, padx=6, pady=6, sticky="w")

            self.custom_pv_frames[module] = ttk.LabelFrame(mod_frame, text="自定义工种最大配置数量")
            self.custom_pv_frames[module].pack(fill="x", padx=12, pady=8)
            for idx, wt in enumerate(WORK_TYPES):
                rr = idx // 3
                cc = (idx % 3) * 2
                if 'label_pv_modules' not in self.__dict__:
                    self.label_pv_modules = {}
                self.label_pv_modules.setdefault(module, {})
                lvp = tk.StringVar()
                lvp.set(("√ " if self.enabled_pv_modules[module][wt].get() else "× ") + wt)
                try:
                    self.enabled_pv_modules[module][wt].trace_add('write', lambda *_x, v=self.enabled_pv_modules[module][wt], s=lvp, name=wt: s.set(("√ " if v.get() else "× ") + name))
                except Exception:
                    pass
                self.label_pv_modules[module][wt] = lvp
                chkp = ttk.Checkbutton(self.custom_pv_frames[module], textvariable=lvp, variable=self.enabled_pv_modules[module][wt], command=lambda m=module, w=wt: self._update_spin_state_pv_module(m, w), style='NoInd.TCheckbutton')
                chkp.grid(row=rr, column=cc, padx=6, pady=6, sticky="e")
                spinp = tk.Spinbox(self.custom_pv_frames[module], from_=0, to=500, textvariable=self.config_vars_pv_modules[module][wt], width=6)
                spinp.grid(row=rr, column=cc+1, padx=6, pady=6, sticky="w")
                self.spin_widgets_pv_modules[module][wt] = spinp
                self._update_spin_state_pv_module(module, wt)

        
        
        tu_card = ttk.Frame(tab_tu, style='Card.TFrame')
        tu_card.pack(padx=12, pady=(8,0), anchor="w")
        tu_bg = tk.Canvas(tu_card, highlightthickness=0, bd=0)
        tu_bg.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.card_bg_canvases['tu'] = tu_bg
        tu_card.bind("<Configure>", lambda e: self._draw_round_rect(tu_bg, radius=10, fill=self.colors['card_bg']))
        self.root.after(0, lambda cv=tu_bg: self._draw_round_rect(cv, radius=10, fill=self.colors['card_bg']))
        tu_row = ttk.Frame(tu_card, style='Card.TFrame')
        tu_row.pack(anchor="w")
        tu_row.configure(height=37)
        tu_row.pack_propagate(False)
        tu_row.grid_columnconfigure(0, weight=0)
        tu_row.grid_rowconfigure(0, weight=1)
        tu_toggle = ttk.Button(tu_row, text="参与计算", command=lambda: (self.enable_tu.set(not self.enable_tu.get()), self._toggle_enable_tu(), self._update_toggle_button('tu')), style='ToggleOff.TButton')
        tu_toggle.configure(width=12)
        tu_toggle.grid(row=0, column=0, padx=8, pady=0, sticky="w")
        tu_card.configure(cursor='hand2')
        tu_toggle.configure(cursor='hand2')
        tu_row.configure(cursor='hand2')
        tu_card.bind("<Button-1>", lambda _e: (self.enable_tu.set(not self.enable_tu.get()), self._toggle_enable_tu(), self._update_toggle_button('tu')))
        self.card_toggle_buttons['tu'] = tu_toggle
        try:
            self.enable_tu.trace_add('write', lambda *_: self._update_toggle_button('tu'))
        except Exception:
            pass
        self._update_toggle_button('tu')
        tu_card.bind("<Enter>", lambda _e: self._set_card_hover('tu', True))
        tu_card.bind("<Leave>", lambda _e: self._set_card_hover('tu', False))
        
        
        style = ttk.Style()
        try:
            style.configure('lefttab.TNotebook', tabposition='wn')
        except Exception:
            pass
        try:
            style.layout('NavNoInd.TCheckbutton', [('Checkbutton.padding', {'children': [('Checkbutton.label', {'side': 'left', 'expand': 1})]})])
            style.layout('NavNoIndSelected.TCheckbutton', [('Checkbutton.padding', {'children': [('Checkbutton.label', {'side': 'left', 'expand': 1})]})])
            style.configure('NavNoInd.TCheckbutton', background=self.colors['card_bg'], foreground=self.colors['primary'], font=('KaiTi', 11))
            style.configure('NavNoIndSelected.TCheckbutton', background=self.colors['card_bg'], foreground=self.colors['primary'], font=('KaiTi', 11))
            try:
                style.map('NavNoInd.TCheckbutton', foreground=[('disabled', '#9AAEC7'), ('!disabled', self.colors['primary'])])
                style.map('NavNoIndSelected.TCheckbutton', foreground=[('disabled', '#9AAEC7'), ('!disabled', self.colors['primary'])])
            except Exception:
                pass
        except Exception:
            pass
        tu_outer = ttk.Frame(tab_tu)
        tu_outer.pack(fill="both", expand=True, padx=10, pady=8)
        left_select = ttk.Frame(tu_outer)
        left_select.pack(side="left", fill="y", padx=10, pady=(20,8))
        self.tu_left_select = left_select
        self.show_tunnel = {}
        self.nav_item_frames = {}
        self.nav_item_buttons = {}
        for i, tunnel in enumerate(self.tunnel_names):
            var = tk.BooleanVar(value=(i == 0))
            self.show_tunnel[tunnel] = var
            sv = tk.StringVar()
            sv.set(f"{tunnel}")
            item_frame = ttk.Frame(left_select, style='Card.TFrame')
            item_frame.pack(anchor="w", fill="x", padx=4, pady=(0 if i == 0 else 4))
            self.nav_item_frames[tunnel] = item_frame
            btn = ttk.Button(item_frame, textvariable=sv, command=lambda t=tunnel: (self.show_tunnel[t].set(not self.show_tunnel[t].get()), self._toggle_tunnel_show(t), self._update_tunnel_nav_button(t)), style=('ToggleOn.TButton' if var.get() else 'ToggleOff.TButton'))
            btn.configure(width=10)
            btn.pack(anchor="w")
            self.nav_item_buttons[tunnel] = btn
            def _on_nav_change(*_args, v=var, s=sv, name=tunnel):
                s.set(f"{name}")
                try:
                    self._update_tunnel_nav_button(name)
                except Exception:
                    pass
            try:
                var.trace_add('write', _on_nav_change)
            except Exception:
                pass
        right_content = ttk.Frame(tu_outer)
        right_content.pack(side="left", fill="both", expand=True)
        self.tu_right_content = right_content
        for tunnel in self.tunnel_names:
            tu_frame = ttk.Frame(right_content)
            self.tunnel_root_frames[tunnel] = tu_frame
            container_tu = ttk.Frame(tu_frame)
            container_tu.pack(fill="both", expand=True, padx=6, pady=6)
            container_tu.columnconfigure(0, weight=1)
            container_tu.columnconfigure(1, weight=1)
            container_tu.rowconfigure(0, weight=1)
            container_tu.rowconfigure(1, weight=1)
            for i, module in enumerate(self.tunnel_modules):
                r = 0 if i < 2 else 1
                c = i % 2
                mod_frame = ttk.Frame(container_tu)
                mod_frame.grid(row=r, column=c, padx=10, pady=8, sticky="nsew")
                self.tunnel_mod_frames.setdefault(tunnel, {})[module] = mod_frame
                ttk.Label(mod_frame, text=f"{module}阶段", style="SectionHeader.TLabel").pack(fill="x", padx=4, pady=(0,6))
                team_frame = ttk.LabelFrame(mod_frame, text="队伍设置")
                team_frame.pack(fill="x", padx=12, pady=8)
                ttk.Label(team_frame, text="队伍个数").grid(row=0, column=0, padx=6, pady=6, sticky="w")
                tk.Spinbox(team_frame, from_=1, to=100, textvariable=self.team_count_tunnel_vars[tunnel][module], width=6).grid(row=0, column=1, padx=6, pady=6, sticky="w")

                date_frame = ttk.LabelFrame(mod_frame, text="时间范围（选择到月份）")
                date_frame.pack(fill="x", padx=12, pady=8)
                ttk.Label(date_frame, text="开始年份").grid(row=0, column=0, padx=6, pady=6, sticky="w")
                ttk.Combobox(date_frame, values=self.year_options, textvariable=self.start_year_var_tm[tunnel][module], width=8, state="readonly").grid(row=0, column=1, padx=6, pady=6)
                ttk.Label(date_frame, text="开始月份").grid(row=0, column=2, padx=6, pady=6, sticky="w")
                ttk.Combobox(date_frame, values=self.month_options, textvariable=self.start_month_var_tm[tunnel][module], width=6, state="readonly").grid(row=0, column=3, padx=6, pady=6)
                ttk.Label(date_frame, text="结束年份").grid(row=1, column=0, padx=6, pady=6, sticky="w")
                ttk.Combobox(date_frame, values=self.year_options, textvariable=self.end_year_var_tm[tunnel][module], width=8, state="readonly").grid(row=1, column=1, padx=6, pady=6)
                ttk.Label(date_frame, text="结束月份").grid(row=1, column=2, padx=6, pady=6, sticky="w")
                ttk.Combobox(date_frame, values=self.month_options, textvariable=self.end_month_var_tm[tunnel][module], width=6, state="readonly").grid(row=1, column=3, padx=6, pady=6)
                mode_frame = ttk.LabelFrame(mod_frame, text="配置模式")
                mode_frame.pack(fill="x", padx=12, pady=8)
                ttk.Radiobutton(mode_frame, text="使用默认配置（自动生成曲线）", variable=self.use_default_tunnel_vars[tunnel][module], value=True, command=lambda t=tunnel, m=module: self._toggle_tunnel_module_config_frame(t, m)).grid(row=0, column=0, padx=6, pady=6, sticky="w")
                ttk.Radiobutton(mode_frame, text="自定义各工种最大配置数量", variable=self.use_default_tunnel_vars[tunnel][module], value=False, command=lambda t=tunnel, m=module: self._toggle_tunnel_module_config_frame(t, m)).grid(row=0, column=1, padx=6, pady=6, sticky="w")
                custom_frame = ttk.LabelFrame(mod_frame, text="自定义工种最大配置数量")
                self.custom_tunnel_frames[tunnel][module] = custom_frame
                custom_frame.pack(fill="both", padx=12, pady=8)
                for idx, wt in enumerate(TUNNEL_WORK_TYPES):
                    rr = idx // 3
                    cc = (idx % 3) * 2
                    if 'label_tunnel_modules' not in self.__dict__:
                        self.label_tunnel_modules = {}
                    self.label_tunnel_modules.setdefault(tunnel, {}).setdefault(module, {})
                    lvt = tk.StringVar()
                    lvt.set(("√ " if self.enabled_tunnel_modules[tunnel][module][wt].get() else "× ") + wt)
                    try:
                        self.enabled_tunnel_modules[tunnel][module][wt].trace_add('write', lambda *_x, v=self.enabled_tunnel_modules[tunnel][module][wt], s=lvt, name=wt: s.set(("√ " if v.get() else "× ") + name))
                    except Exception:
                        pass
                    self.label_tunnel_modules[tunnel][module][wt] = lvt
                    chk = ttk.Checkbutton(custom_frame, textvariable=lvt, variable=self.enabled_tunnel_modules[tunnel][module][wt], command=lambda t=tunnel, m=module, w=wt: self._update_spin_state_tunnel(t, m, w), style='NoInd.TCheckbutton')
                    chk.grid(row=rr, column=cc, padx=6, pady=6, sticky="e")
                    sp = tk.Spinbox(custom_frame, from_=0, to=500, textvariable=self.config_vars_tunnel_modules[tunnel][module][wt], width=6)
                    sp.grid(row=rr, column=cc+1, padx=6, pady=6, sticky="w")
                    self.spin_widgets_tunnel[tunnel][module][wt] = sp
                    self._update_spin_state_tunnel(tunnel, module, wt)
                
        # 隧道工程：导出设置与操作按钮（靠近自定义模块）
        out_frame_tu = ttk.LabelFrame(tab_tu, text="导出设置")
        out_frame_tu.pack(fill="x", padx=12, pady=4)
        ttk.Label(out_frame_tu, text="输出文件").grid(row=0, column=0, padx=6, pady=4, sticky="w")
        out_entry_tu = ttk.Entry(out_frame_tu, textvariable=self.output_path_var, width=60)
        out_entry_tu.grid(row=0, column=1, padx=6, pady=4, sticky="w")
        ttk.Button(out_frame_tu, text="选择...", command=self._choose_output_file).grid(row=0, column=2, padx=6, pady=4)

        btn_frame_tu = ttk.Frame(tab_tu)
        btn_frame_tu.pack(fill="x", padx=12, pady=6)
        ttk.Button(btn_frame_tu, text="生成 Excel", command=self._generate).pack(side="left", padx=6)
        ttk.Button(btn_frame_tu, text="退出", command=self.root.quit).pack(side="right", padx=6)
        hs_card = ttk.Frame(tab_hs, style='Card.TFrame')
        hs_card.pack(padx=12, pady=(8,0), anchor="w")
        hs_bg = tk.Canvas(hs_card, highlightthickness=0, bd=0)
        hs_bg.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.card_bg_canvases['hs'] = hs_bg
        hs_card.bind("<Configure>", lambda e: self._draw_round_rect(hs_bg, radius=10, fill=self.colors['card_bg']))
        self.root.after(0, lambda cv=hs_bg: self._draw_round_rect(cv, radius=10, fill=self.colors['card_bg']))
        hs_row = ttk.Frame(hs_card, style='Card.TFrame')
        hs_row.pack(anchor="w")
        hs_row.configure(height=37)
        hs_row.pack_propagate(False)
        hs_row.grid_columnconfigure(0, weight=0)
        hs_row.grid_rowconfigure(0, weight=1)
        hs_toggle = ttk.Button(hs_row, text="参与计算", command=lambda: (self.enable_house.set(not self.enable_house.get()), self._toggle_enable_house(), self._update_toggle_button('hs')), style='ToggleOff.TButton')
        hs_toggle.configure(width=12)
        hs_toggle.grid(row=0, column=0, padx=8, pady=0, sticky="w")
        hs_card.configure(cursor='hand2')
        hs_toggle.configure(cursor='hand2')
        hs_row.configure(cursor='hand2')
        hs_card.bind("<Button-1>", lambda _e: (self.enable_house.set(not self.enable_house.get()), self._toggle_enable_house(), self._update_toggle_button('hs')))
        self.card_toggle_buttons['hs'] = hs_toggle
        try:
            self.enable_house.trace_add('write', lambda *_: self._update_toggle_button('hs'))
        except Exception:
            pass
        self._update_toggle_button('hs')
        hs_card.bind("<Enter>", lambda _e: self._set_card_hover('hs', True))
        hs_card.bind("<Leave>", lambda _e: self._set_card_hover('hs', False))
        
        
        hs_container = ttk.Frame(tab_hs)
        hs_container.pack(fill="both", expand=True, padx=10, pady=4)
        hs_container.columnconfigure(0, weight=1)
        hs_container.columnconfigure(1, weight=1)
        hs_container.rowconfigure(0, weight=1)
        hs_container.rowconfigure(1, weight=1)
        for i, module in enumerate(self.hs_modules):
            r = 0 if i < 2 else 1
            c = i % 2
            mod_frame = ttk.Frame(hs_container)
            mod_frame.grid(row=r, column=c, padx=10, pady=4, sticky="nsew")
            self.house_mod_frames[module] = mod_frame
            ttk.Label(mod_frame, text=f"{module}", style="SectionHeader.TLabel").pack(fill="x", padx=4, pady=(0,6))
            team_frame = ttk.LabelFrame(mod_frame, text="队伍设置")
            team_frame.pack(fill="x", padx=12, pady=4)
            ttk.Label(team_frame, text="队伍个数").grid(row=0, column=0, padx=6, pady=6, sticky="w")
            tk.Spinbox(team_frame, from_=1, to=100, textvariable=self.team_count_house_vars[module], width=6).grid(row=0, column=1, padx=6, pady=6, sticky="w")

            hs_date_frame = ttk.LabelFrame(mod_frame, text="时间范围（选择到月份）")
            hs_date_frame.pack(fill="x", padx=12, pady=4)
            ttk.Label(hs_date_frame, text="开始年份").grid(row=0, column=0, padx=6, pady=6, sticky="w")
            ttk.Combobox(hs_date_frame, values=self.year_options, textvariable=self.start_year_var_h_m[module], width=8, state="readonly").grid(row=0, column=1, padx=6, pady=6)
            ttk.Label(hs_date_frame, text="开始月份").grid(row=0, column=2, padx=6, pady=6, sticky="w")
            ttk.Combobox(hs_date_frame, values=self.month_options, textvariable=self.start_month_var_h_m[module], width=6, state="readonly").grid(row=0, column=3, padx=6, pady=6)
            ttk.Label(hs_date_frame, text="结束年份").grid(row=1, column=0, padx=6, pady=6, sticky="w")
            ttk.Combobox(hs_date_frame, values=self.year_options, textvariable=self.end_year_var_h_m[module], width=8, state="readonly").grid(row=1, column=1, padx=6, pady=6)
            ttk.Label(hs_date_frame, text="结束月份").grid(row=1, column=2, padx=6, pady=6, sticky="w")
            ttk.Combobox(hs_date_frame, values=self.month_options, textvariable=self.end_month_var_h_m[module], width=6, state="readonly").grid(row=1, column=3, padx=6, pady=6)

            house_mode_frame = ttk.LabelFrame(mod_frame, text="配置模式")
            house_mode_frame.pack(fill="x", padx=12, pady=4)
            ttk.Radiobutton(house_mode_frame, text="使用默认配置（自动生成曲线）", variable=self.use_default_house_vars[module], value=True, command=lambda m=module: self._toggle_house_module_config_frame(m)).grid(row=0, column=0, padx=6, pady=6, sticky="w")
            ttk.Radiobutton(house_mode_frame, text="自定义各工种最大配置数量", variable=self.use_default_house_vars[module], value=False, command=lambda m=module: self._toggle_house_module_config_frame(m)).grid(row=0, column=1, padx=6, pady=6, sticky="w")

            custom_hs_frame = ttk.LabelFrame(mod_frame, text="自定义工种最大配置数量")
            self.custom_house_frames[module] = custom_hs_frame
            custom_hs_frame.pack(fill="both", padx=12, pady=4)
            for idx, wt in enumerate(WORK_TYPES):
                rr = idx // 3
                cc = (idx % 3) * 2
                if 'label_house_modules' not in self.__dict__:
                    self.label_house_modules = {}
                self.label_house_modules.setdefault(module, {})
                lvh = tk.StringVar()
                lvh.set(("√ " if self.enabled_house_modules[module][wt].get() else "× ") + wt)
                try:
                    self.enabled_house_modules[module][wt].trace_add('write', lambda *_x, v=self.enabled_house_modules[module][wt], s=lvh, name=wt: s.set(("√ " if v.get() else "× ") + name))
                except Exception:
                    pass
                self.label_house_modules[module][wt] = lvh
                chkh = ttk.Checkbutton(custom_hs_frame, textvariable=lvh, variable=self.enabled_house_modules[module][wt], command=lambda m=module, w=wt: self._update_spin_state_house_module(m, w), style='NoInd.TCheckbutton')
                chkh.grid(row=rr, column=cc, padx=6, pady=6, sticky="e")
                spinh = tk.Spinbox(custom_hs_frame, from_=0, to=500, textvariable=self.config_vars_house_modules[module][wt], width=6)
                spinh.grid(row=rr, column=cc+1, padx=6, pady=6, sticky="w")
                self.spin_widgets_house_modules[module][wt] = spinh
                self._update_spin_state_house_module(module, wt)

        # 路基工程：导出设置与操作按钮（靠近自定义模块）
        out_frame_rb = ttk.LabelFrame(tab_rb, text="导出设置")
        out_frame_rb.pack(fill="x", padx=12, pady=4)
        ttk.Label(out_frame_rb, text="输出文件").grid(row=0, column=0, padx=6, pady=4, sticky="w")
        out_entry_rb = ttk.Entry(out_frame_rb, textvariable=self.output_path_var, width=60)
        out_entry_rb.grid(row=0, column=1, padx=6, pady=4, sticky="w")
        ttk.Button(out_frame_rb, text="选择...", command=self._choose_output_file).grid(row=0, column=2, padx=6, pady=4)

        btn_frame_rb = ttk.Frame(tab_rb)
        btn_frame_rb.pack(fill="x", padx=12, pady=6)
        ttk.Button(btn_frame_rb, text="生成 Excel", command=self._generate).pack(side="left", padx=6)
        ttk.Button(btn_frame_rb, text="退出", command=self.root.quit).pack(side="right", padx=6)

        # 路面工程：导出设置与操作按钮（靠近自定义模块）
        out_frame_pv = ttk.LabelFrame(tab_pv, text="导出设置")
        out_frame_pv.pack(fill="x", padx=12, pady=4)
        ttk.Label(out_frame_pv, text="输出文件").grid(row=0, column=0, padx=6, pady=4, sticky="w")
        out_entry_pv = ttk.Entry(out_frame_pv, textvariable=self.output_path_var, width=60)
        out_entry_pv.grid(row=0, column=1, padx=6, pady=4, sticky="w")
        ttk.Button(out_frame_pv, text="选择...", command=self._choose_output_file).grid(row=0, column=2, padx=6, pady=4)

        btn_frame_pv = ttk.Frame(tab_pv)
        btn_frame_pv.pack(fill="x", padx=12, pady=6)
        ttk.Button(btn_frame_pv, text="生成 Excel", command=self._generate).pack(side="left", padx=6)
        ttk.Button(btn_frame_pv, text="退出", command=self.root.quit).pack(side="right", padx=6)

        # 房建工程：导出设置与操作按钮（靠近自定义模块）
        out_frame_hs = ttk.LabelFrame(tab_hs, text="导出设置")
        out_frame_hs.pack(fill="x", padx=12, pady=4)
        ttk.Label(out_frame_hs, text="输出文件").grid(row=0, column=0, padx=6, pady=4, sticky="w")
        out_entry_hs = ttk.Entry(out_frame_hs, textvariable=self.output_path_var, width=60)
        out_entry_hs.grid(row=0, column=1, padx=6, pady=4, sticky="w")
        ttk.Button(out_frame_hs, text="选择...", command=self._choose_output_file).grid(row=0, column=2, padx=6, pady=4)

        btn_frame_hs = ttk.Frame(tab_hs)
        btn_frame_hs.pack(fill="x", padx=12, pady=4)
        ttk.Button(btn_frame_hs, text="生成 Excel", command=self._generate).pack(side="left", padx=6)
        ttk.Button(btn_frame_hs, text="退出", command=self.root.quit).pack(side="right", padx=6)

        # 初始隐藏/显示自定义区
        for module in self.rb_modules:
            self._toggle_rb_module_config_frame(module)
        for module in self.br_modules:
            self._toggle_bridge_module_config_frame(module)
        for module in self.pv_modules:
            self._toggle_pv_module_config_frame(module)
        self._toggle_enable_rb()
        self._toggle_enable_br()
        self._toggle_enable_pv()
        self._toggle_enable_tu()
        for tunnel in self.tunnel_names:
            for module in self.tunnel_modules:
                self._toggle_tunnel_module_config_frame(tunnel, module)
        for tunnel in self.tunnel_names:
            self._toggle_tunnel_show(tunnel)
            self._update_tunnel_nav_style(tunnel)
        for tunnel in self.tunnel_names:
            self._toggle_tunnel_enable(tunnel)
        for module in self.hs_modules:
            self._toggle_house_module_config_frame(module)
        self._toggle_enable_house()

    def _toggle_config_frame(self):
        disable = self.use_default_var.get()
        for child in self.custom_frame.winfo_children():
            try:
                child.configure(state="disabled" if disable else "normal")
            except tk.TclError:
                # 部分控件可能不支持state属性，忽略这些控件
                pass
        for wt in WORK_TYPES:
            self._update_spin_state_rb(wt)

    def _toggle_bridge_config_frame(self):
        disable = self.use_default_bridge_var.get()
        for child in self.custom_bridge_frame.winfo_children():
            try:
                child.configure(state="disabled" if disable else "normal")
            except tk.TclError:
                pass
        for wt in WORK_TYPES:
            self._update_spin_state_bridge(wt)

    def _toggle_pv_module_config_frame(self, module):
        disable = self.use_default_pv_vars[module].get()
        for child in self.custom_pv_frames[module].winfo_children():
            try:
                child.configure(state="disabled" if disable else "normal")
            except tk.TclError:
                pass
        for wt in WORK_TYPES:
            self._update_spin_state_pv_module(module, wt)
                
    def _toggle_rb_module_config_frame(self, module):
        disable = self.use_default_rb_vars[module].get()
        for child in self.custom_rb_frames[module].winfo_children():
            try:
                child.configure(state="disabled" if disable else "normal")
            except tk.TclError:
                pass
        for wt in WORK_TYPES:
            self._update_spin_state_rb_module(module, wt)

    def _toggle_bridge_module_config_frame(self, module):
        disable = self.use_default_br_vars[module].get()
        for child in self.custom_br_frames[module].winfo_children():
            try:
                child.configure(state="disabled" if disable else "normal")
            except tk.TclError:
                pass
        for wt in WORK_TYPES:
            self._update_spin_state_bridge_module(module, wt)

    def _toggle_tunnel_module_config_frame(self, tunnel, module):
        disable = self.use_default_tunnel_vars[tunnel][module].get()
        for child in self.custom_tunnel_frames[tunnel][module].winfo_children():
            try:
                child.configure(state="disabled" if disable else "normal")
            except tk.TclError:
                pass
        for wt in TUNNEL_WORK_TYPES:
            self._update_spin_state_tunnel(tunnel, module, wt)
        self._toggle_tunnel_enable(tunnel)

    def _toggle_tunnel_enable(self, tunnel):
        enable = self.show_tunnel[tunnel].get()
        frames = self.tunnel_mod_frames.get(tunnel, {})
        for module, frame in frames.items():
            state = "normal" if enable else "disabled"
            for child in frame.winfo_children():
                try:
                    child.configure(state=state)
                except tk.TclError:
                    pass

    def _select_tunnel(self, tunnel):
        for name, root in self.tunnel_root_frames.items():
            try:
                if name == tunnel:
                    if not root.winfo_ismapped():
                        root.pack(fill="both", expand=True, pady=6)
                else:
                    if root.winfo_ismapped():
                        root.pack_forget()
            except Exception:
                pass

    def _toggle_tunnel_show(self, tunnel):
        show = self.show_tunnel[tunnel].get()
        root = self.tunnel_root_frames.get(tunnel)
        if root:
            try:
                if show and not root.winfo_ismapped():
                    root.pack(fill="both", expand=True, pady=6)
                elif not show and root.winfo_ismapped():
                    root.pack_forget()
            except Exception:
                pass
        # 更新左侧导航项的样式以反映选中状态
        try:
            self._update_tunnel_nav_style(tunnel)
            self._update_tunnel_nav_dot(tunnel)
        except Exception:
            pass

    def _update_tunnel_nav_style(self, tunnel):
        fr = getattr(self, 'nav_item_frames', {}).get(tunnel)
        if not fr:
            return
        try:
            fr.configure(style='NavItemSelected.TFrame')
        except Exception:
            pass

    def _update_tunnel_nav_button(self, tunnel):
        btn = getattr(self, 'nav_item_buttons', {}).get(tunnel)
        if not btn:
            return
        try:
            btn.configure(style=('ToggleOn.TButton' if self.show_tunnel[tunnel].get() else 'ToggleOff.TButton'))
        except Exception:
            pass


    def _set_frame_children_state(self, frame, state):
        for child in frame.winfo_children():
            try:
                child.configure(state=state)
            except tk.TclError:
                pass
            try:
                if child.winfo_children():
                    self._set_frame_children_state(child, state)
            except Exception:
                pass

    def _toggle_enable_rb(self):
        st = "normal" if self.enable_rb.get() else "disabled"
        for module, frame in self.rb_mod_frames.items():
            self._set_frame_children_state(frame, st)

    def _toggle_enable_br(self):
        st = "normal" if self.enable_br.get() else "disabled"
        for module, frame in self.br_mod_frames.items():
            self._set_frame_children_state(frame, st)

    def _toggle_enable_pv(self):
        st = "normal" if self.enable_pv.get() else "disabled"
        for module, frame in self.pv_mod_frames.items():
            self._set_frame_children_state(frame, st)

    def _toggle_enable_tu(self):
        st = "normal" if self.enable_tu.get() else "disabled"
        for tunnel in self.tunnel_names:
            for module, frame in self.tunnel_mod_frames.get(tunnel, {}).items():
                self._set_frame_children_state(frame, st)

    def _toggle_enable_house(self):
        st = "normal" if self.enable_house.get() else "disabled"
        for module, frame in self.house_mod_frames.items():
            self._set_frame_children_state(frame, st)

    def _draw_round_rect(self, canvas, radius=10, fill='#CFE5FF', tag='card_bg'):
        try:
            w = canvas.winfo_width()
            h = canvas.winfo_height()
        except Exception:
            return
        if w <= 0 or h <= 0:
            return
        r = max(1, min(radius, int(min(w, h) // 2)))
        canvas.delete(tag)
        try:
            canvas.create_arc(0, 0, 2*r, 2*r, start=90, extent=90, fill=fill, outline='', tags=tag)
            canvas.create_arc(w-2*r, 0, w, 2*r, start=0, extent=90, fill=fill, outline='', tags=tag)
            canvas.create_arc(0, h-2*r, 2*r, h, start=180, extent=90, fill=fill, outline='', tags=tag)
            canvas.create_arc(w-2*r, h-2*r, w, h, start=270, extent=90, fill=fill, outline='', tags=tag)
            canvas.create_rectangle(r, 0, w-r, h, fill=fill, outline='', tags=tag)
            canvas.create_rectangle(0, r, w, h-r, fill=fill, outline='', tags=tag)
        except Exception:
            pass

    def _set_card_hover(self, name, on):
        bg_cv = getattr(self, 'card_bg_canvases', {}).get(name)
        if not bg_cv:
            return
        fill = '#B9DBFF' if on else '#CFE5FF'
        self._draw_round_rect(bg_cv, radius=10, fill=fill)
        lbl = getattr(self, 'card_labels', {}).get(name)
        circ = getattr(self, 'card_circle_canvases', {}).get(name)
        try:
            if lbl:
                lbl.configure(bg=fill)
            if circ:
                circ.configure(background=fill)
        except Exception:
            pass

    def _update_card_toggle(self, name):
        try:
            var_map = {
                'rb': self.enable_rb,
                'br': self.enable_br,
                'pv': self.enable_pv,
                'tu': self.enable_tu,
                'hs': self.enable_house,
            }
            selected = bool(var_map[name].get())
            items = getattr(self, 'card_circle_items', {}).get(name, {})
            cv = getattr(self, 'card_circle_canvases', {}).get(name)
            if cv and items.get('circle') is not None:
                cv.itemconfigure(items['circle'], fill=self.colors['primary'] if selected else '#FFFFFF')
            if cv and items.get('shadow') is not None:
                cv.itemconfigure(items['shadow'], fill=self.colors['accent'])
        except Exception:
            pass

    def _update_toggle_button(self, name):
        try:
            btn = getattr(self, 'card_toggle_buttons', {}).get(name)
            if not btn:
                return
            var_map = {
                'rb': self.enable_rb,
                'br': self.enable_br,
                'pv': self.enable_pv,
                'tu': self.enable_tu,
                'hs': self.enable_house,
            }
            selected = bool(var_map[name].get())
            btn.configure(style=('ToggleOn.TButton' if selected else 'ToggleOff.TButton'))
            bg_cv = getattr(self, 'card_bg_canvases', {}).get(name)
            fill = (self.colors['primary'] if selected else self.colors['card_bg'])
            if bg_cv:
                self._draw_round_rect(bg_cv, radius=10, fill=fill)
            lbl = getattr(self, 'card_labels', {}).get(name)
            circ = getattr(self, 'card_circle_canvases', {}).get(name)
            try:
                if lbl:
                    lbl.configure(bg=fill, fg=('#FFFFFF' if selected else self.colors['text_primary']))
                if circ:
                    circ.configure(background=fill)
            except Exception:
                pass
            try:
                nb = getattr(self, 'notebook', None)
                if nb:
                    sel = nb.select()
                    if self._tab_map.get(sel) == name:
                        nb.configure(style=('Enabled.TNotebook' if selected else 'Disabled.TNotebook'))
                for key, hb in getattr(self, 'header_tab_buttons', {}).items():
                    var_map2 = {'rb': self.enable_rb, 'br': self.enable_br, 'pv': self.enable_pv, 'tu': self.enable_tu, 'hs': self.enable_house}
                    sel2 = bool(var_map2[key].get())
                    hb.configure(style=('ToggleOn.TButton' if sel2 else 'ToggleOff.TButton'))
            except Exception:
                pass
        except Exception:
            pass

    def _update_notebook_style_by_selected(self):
        try:
            nb = getattr(self, 'notebook', None)
            if not nb:
                return
            sel = nb.select()
            name = getattr(self, '_tab_map', {}).get(sel)
            if not name:
                return
            var_map = {'rb': self.enable_rb, 'br': self.enable_br, 'pv': self.enable_pv, 'tu': self.enable_tu, 'hs': self.enable_house}
            selected = bool(var_map[name].get())
            nb.configure(style=('Enabled.TNotebook' if selected else 'Disabled.TNotebook'))
            for key, hb in getattr(self, 'header_tab_buttons', {}).items():
                var_map2 = {'rb': self.enable_rb, 'br': self.enable_br, 'pv': self.enable_pv, 'tu': self.enable_tu, 'hs': self.enable_house}
                sel2 = bool(var_map2[key].get())
                hb.configure(style=('ToggleOn.TButton' if sel2 else 'ToggleOff.TButton'))
        except Exception:
            pass

    def _on_mousewheel(self, e):
        try:
            delta = e.delta
        except Exception:
            delta = 0
        if delta == 0:
            return
        step = -1 if delta > 0 else 1
        try:
            self.scroll_canvas.yview_scroll(step, "units")
        except Exception:
            pass

    def _toggle_house_module_config_frame(self, module):
        disable = self.use_default_house_vars[module].get()
        for child in self.custom_house_frames[module].winfo_children():
            try:
                child.configure(state="disabled" if disable else "normal")
            except tk.TclError:
                pass
        for wt in WORK_TYPES:
            self._update_spin_state_house_module(module, wt)

    def _update_spin_state_rb_module(self, module, wt):
        st = "normal" if self.enabled_rb_modules[module][wt].get() and not self.use_default_rb_vars[module].get() else "disabled"
        sp = self.spin_widgets_rb_modules[module].get(wt)
        if sp:
            try:
                sp.configure(state=st)
            except tk.TclError:
                pass

    def _update_spin_state_bridge_module(self, module, wt):
        st = "normal" if self.enabled_br_modules[module][wt].get() and not self.use_default_br_vars[module].get() else "disabled"
        sp = self.spin_widgets_br_modules[module].get(wt)
        if sp:
            try:
                sp.configure(state=st)
            except tk.TclError:
                pass

    def _update_spin_state_bridge(self, wt):
        st = "normal" if self.enabled_bridge_vars[wt].get() and not self.use_default_bridge_var.get() else "disabled"
        if wt in self.spin_widgets_bridge:
            try:
                self.spin_widgets_bridge[wt].configure(state=st)
            except tk.TclError:
                pass

    def _update_spin_state_pv_module(self, module, wt):
        st = "normal" if self.enabled_pv_modules[module][wt].get() and not self.use_default_pv_vars[module].get() else "disabled"
        sp = self.spin_widgets_pv_modules[module].get(wt)
        if sp:
            try:
                sp.configure(state=st)
            except tk.TclError:
                pass

    def _update_spin_state_tunnel(self, tunnel, module, wt):
        st = "normal" if self.enabled_tunnel_modules[tunnel][module][wt].get() and not self.use_default_tunnel_vars[tunnel][module].get() else "disabled"
        sp = self.spin_widgets_tunnel[tunnel][module].get(wt)
        if sp:
            try:
                sp.configure(state=st)
            except tk.TclError:
                pass

    def _update_spin_state_house_module(self, module, wt):
        st = "normal" if self.enabled_house_modules[module][wt].get() and not self.use_default_house_vars[module].get() else "disabled"
        sp = self.spin_widgets_house_modules[module].get(wt)
        if sp:
            try:
                sp.configure(state=st)
            except tk.TclError:
                pass

    def _choose_output_file(self):
        path = filedialog.asksaveasfilename(
            title="选择导出文件",
            defaultextension=".xlsx",
            initialfile="路基工程劳动力计划.xlsx",
            filetypes=[("Excel 文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        if path:
            self.output_path_var.set(path)

    def _generate(self):
        try:
            # 路基工程时间范围（分阶段）
            months_rb_map = {}
            plan_rb_map = {}
            if self.enable_rb.get():
                for module in self.rb_modules:
                    sy_rb, sm_rb = int(self.start_year_var_rb_m[module].get()), int(self.start_month_var_rb_m[module].get())
                    ey_rb, em_rb = int(self.end_year_var_rb_m[module].get()), int(self.end_month_var_rb_m[module].get())
                    start_rb = datetime(sy_rb, sm_rb, 1)
                    last_rb = calendar.monthrange(ey_rb, em_rb)[1]
                    end_rb = datetime(ey_rb, em_rb, last_rb)
                    if start_rb >= end_rb:
                        messagebox.showerror("输入错误", f"路基工程-{module}开始时间必须早于结束时间！")
                        return
                    months_list = generate_month_sequence(start_rb, end_rb)
                    months_rb_map[module] = months_list
                    plan_mod = {}
                    for wt in WORK_TYPES:
                        enabled = self.enabled_rb_modules[module][wt].get()
                        valr = int(self.config_vars_rb_modules[module][wt].get()) if enabled else 0
                        plan_mod[wt] = [valr for _ in range(len(months_list))]
                    team_count_r = max(1, int(self.team_count_rb_vars[module].get()))
                    for wt in plan_mod:
                        plan_mod[wt] = [int(count * team_count_r) for count in plan_mod[wt]]
                    plan_rb_map[module] = plan_mod

            months_br_map = {}
            plan_br_map = {}
            if self.enable_br.get():
                for module in self.br_modules:
                    sy_br, sm_br = int(self.start_year_var_br_m[module].get()), int(self.start_month_var_br_m[module].get())
                    ey_br, em_br = int(self.end_year_var_br_m[module].get()), int(self.end_month_var_br_m[module].get())
                    start_br = datetime(sy_br, sm_br, 1)
                    last_br = calendar.monthrange(ey_br, em_br)[1]
                    end_br = datetime(ey_br, em_br, last_br)
                    if start_br >= end_br:
                        messagebox.showerror("输入错误", f"桥梁工程-{module}开始时间必须早于结束时间！")
                        return
                    months_list = generate_month_sequence(start_br, end_br)
                    months_br_map[module] = months_list
                    plan_mod = {}
                    for wt in WORK_TYPES:
                        enabled = self.enabled_br_modules[module][wt].get()
                        valb = int(self.config_vars_br_modules[module][wt].get()) if enabled else 0
                        plan_mod[wt] = [valb for _ in range(len(months_list))]
                    team_count_b = max(1, int(self.team_count_br_vars[module].get()))
                    for wt in plan_mod:
                        plan_mod[wt] = [int(count * team_count_b) for count in plan_mod[wt]]
                    plan_br_map[module] = plan_mod

            months_pv_map = {}
            plan_pv_map = {}
            if self.enable_pv.get():
                for module in self.pv_modules:
                    sy_pv, sm_pv = int(self.start_year_var_pv_m[module].get()), int(self.start_month_var_pv_m[module].get())
                    ey_pv, em_pv = int(self.end_year_var_pv_m[module].get()), int(self.end_month_var_pv_m[module].get())
                    start_pv = datetime(sy_pv, sm_pv, 1)
                    last_pv = calendar.monthrange(ey_pv, em_pv)[1]
                    end_pv = datetime(ey_pv, em_pv, last_pv)
                    if start_pv >= end_pv:
                        messagebox.showerror("输入错误", f"路面工程-{module}开始时间必须早于结束时间！")
                        return
                    months_list = generate_month_sequence(start_pv, end_pv)
                    months_pv_map[module] = months_list
                    plan_mod = {}
                    for wt in WORK_TYPES:
                        enabled = self.enabled_pv_modules[module][wt].get()
                        valp = int(self.config_vars_pv_modules[module][wt].get()) if enabled else 0
                        plan_mod[wt] = [valp for _ in range(len(months_list))]
                    team_count_p = max(1, int(self.team_count_pv_vars[module].get()))
                    for wt in plan_mod:
                        plan_mod[wt] = [int(count * team_count_p) for count in plan_mod[wt]]
                    plan_pv_map[module] = plan_mod
            
            months_tunnel_map = {}
            plan_tunnel_map = {}
            if self.enable_tu.get():
                for tunnel in self.tunnel_names:
                    if not self.show_tunnel[tunnel].get():
                        continue
                    months_tunnel_map[tunnel] = {}
                    plan_tunnel_map[tunnel] = {}
                    for module in self.tunnel_modules:
                        sy_tu, sm_tu = int(self.start_year_var_tm[tunnel][module].get()), int(self.start_month_var_tm[tunnel][module].get())
                        ey_tu, em_tu = int(self.end_year_var_tm[tunnel][module].get()), int(self.end_month_var_tm[tunnel][module].get())
                        start_tu = datetime(sy_tu, sm_tu, 1)
                        last_tu = calendar.monthrange(ey_tu, em_tu)[1]
                        end_tu = datetime(ey_tu, em_tu, last_tu)
                        if start_tu >= end_tu:
                            messagebox.showerror("输入错误", f"{tunnel}-{module}开始时间必须早于结束时间！")
                            return
                        months_list = generate_month_sequence(start_tu, end_tu)
                        months_tunnel_map[tunnel][module] = months_list
                        plan_mod = {}
                        for wt in TUNNEL_WORK_TYPES:
                            enabled = self.enabled_tunnel_modules[tunnel][module][wt].get()
                            valt = int(self.config_vars_tunnel_modules[tunnel][module][wt].get()) if enabled else 0
                            plan_mod[wt] = [valt for _ in range(len(months_list))]
                        team_count_t = max(1, int(self.team_count_tunnel_vars[tunnel][module].get()))
                        for wt in plan_mod:
                            plan_mod[wt] = [int(count * team_count_t) for count in plan_mod[wt]]
                        plan_tunnel_map[tunnel][module] = plan_mod

            # 路基工程计划已在上面按阶段生成

            # 桥梁工程计划（每月恒定为界面输入）
            plan_bridge = {}
            if self.enable_br.get():
                for wt in WORK_TYPES:
                    valb = int(self.config_vars_bridge[wt].get()) if self.enabled_bridge_vars[wt].get() else 0
                    plan_bridge[wt] = [valb for _ in range(len(months_br))]
                team_count_b = max(1, int(self.team_count_bridge_var.get()))
                for wt in plan_bridge:
                    plan_bridge[wt] = [int(count * team_count_b) for count in plan_bridge[wt]]
            plan_pave = {}

            months_hs_map = {}
            plan_house_map = {}
            if self.enable_house.get():
                for module in self.hs_modules:
                    sy_h, sm_h = int(self.start_year_var_h_m[module].get()), int(self.start_month_var_h_m[module].get())
                    ey_h, em_h = int(self.end_year_var_h_m[module].get()), int(self.end_month_var_h_m[module].get())
                    start_h = datetime(sy_h, sm_h, 1)
                    last_h = calendar.monthrange(ey_h, em_h)[1]
                    end_h = datetime(ey_h, em_h, last_h)
                    if start_h >= end_h:
                        messagebox.showerror("输入错误", f"房建工程-{module}开始时间必须早于结束时间！")
                        return
                    months_list = generate_month_sequence(start_h, end_h)
                    months_hs_map[module] = months_list
                    plan_mod = {}
                    for wt in WORK_TYPES:
                        enabled = self.enabled_house_modules[module][wt].get()
                        valh = int(self.config_vars_house_modules[module][wt].get()) if enabled else 0
                        plan_mod[wt] = [valh for _ in range(len(months_list))]
                    team_count_h = max(1, int(self.team_count_house_vars[module].get()))
                    for wt in plan_mod:
                        plan_mod[wt] = [int(count * team_count_h) for count in plan_mod[wt]]
                    plan_house_map[module] = plan_mod
                
            

            # 汇总：月份并集，缺失月份按0相加（路基+桥梁+路面+隧道）
            rb_union = set()
            for module in self.rb_modules:
                if module in months_rb_map:
                    rb_union |= {m for m in months_rb_map[module]}
            tunnel_union = set()
            for tunnel in self.tunnel_names:
                for module in self.tunnel_modules:
                    if tunnel in months_tunnel_map and module in months_tunnel_map[tunnel]:
                        tunnel_union |= {m for m in months_tunnel_map[tunnel][module]}
            br_union = set()
            for module in self.br_modules:
                if module in months_br_map:
                    br_union |= {m for m in months_br_map[module]}
            pv_union = set()
            for module in self.pv_modules:
                if module in months_pv_map:
                    pv_union |= {m for m in months_pv_map[module]}
            hs_union = set()
            for module in self.hs_modules:
                if module in months_hs_map:
                    hs_union |= {m for m in months_hs_map[module]}
            months_union = list(rb_union | br_union | pv_union | hs_union | tunnel_union)
            months_union.sort(key=lambda x: (x[0], x[1]))
            aggregated_plan = {}
            aggregated_types = list(dict.fromkeys(WORK_TYPES + TUNNEL_WORK_TYPES))
            for wt in aggregated_types:
                rb_maps = []
                for module in self.rb_modules:
                    if module in months_rb_map:
                        mod_months_rb = months_rb_map[module]
                        mod_plan_rb = plan_rb_map.get(module, {})
                        if wt in mod_plan_rb:
                            rb_maps.append({mod_months_rb[i]: mod_plan_rb[wt][i] for i in range(len(mod_months_rb))})
                br_maps = []
                for module in self.br_modules:
                    if module in months_br_map:
                        mod_months_br = months_br_map[module]
                        mod_plan_br = plan_br_map.get(module, {})
                        if wt in mod_plan_br:
                            br_maps.append({mod_months_br[i]: mod_plan_br[wt][i] for i in range(len(mod_months_br))})
                pv_maps = []
                for module in self.pv_modules:
                    if module in months_pv_map:
                        mod_months_pv = months_pv_map[module]
                        mod_plan_pv = plan_pv_map.get(module, {})
                        if wt in mod_plan_pv:
                            pv_maps.append({mod_months_pv[i]: mod_plan_pv[wt][i] for i in range(len(mod_months_pv))})
                hs_maps = []
                for module in self.hs_modules:
                    if module in months_hs_map:
                        mod_months_hs = months_hs_map[module]
                        mod_plan_hs = plan_house_map.get(module, {})
                        if wt in mod_plan_hs:
                            hs_maps.append({mod_months_hs[i]: mod_plan_hs[wt][i] for i in range(len(mod_months_hs))})
                tu_maps = []
                for tunnel in self.tunnel_names:
                    for module in self.tunnel_modules:
                        if tunnel in months_tunnel_map and module in months_tunnel_map[tunnel]:
                            mod_months = months_tunnel_map[tunnel][module]
                            mod_plan = plan_tunnel_map[tunnel][module]
                            if wt in mod_plan:
                                tu_maps.append({mod_months[i]: mod_plan[wt][i] for i in range(len(mod_months))})
                aggregated_plan[wt] = [sum(rb.get(m, 0) for rb in rb_maps) + sum(br.get(m, 0) for br in br_maps) + sum(pv.get(m, 0) for pv in pv_maps) + sum(hs.get(m, 0) for hs in hs_maps) + sum(tu.get(m, 0) for tu in tu_maps) for m in months_union]

            output_file = self.output_path_var.get().strip() or os.path.join(os.getcwd(), "路基工程劳动力计划.xlsx")
            export_to_excel(months_union, aggregated_plan, output_file)

            if messagebox.askyesno("导出成功", f"Excel 已导出到:\n{output_file}\n\n是否立即打开？"):
                try:
                    os.startfile(output_file)
                except Exception as e:
                    messagebox.showwarning("打开失败", f"无法打开文件：{e}")

        except Exception as e:
            messagebox.showerror("生成失败", f"发生错误：\n{e}")

# 主函数
def main():
    """主函数，整合所有功能"""
    print("===== 路基工程劳动力计划生成器 =====")
    
    # 1. 获取工程时间范围
    start_date, end_date = get_project_dates()
    
    # 2. 获取工种配置
    workforce_config = get_workforce_configuration()
    
    # 3. 生成月份序列
    months = generate_month_sequence(start_date, end_date)
    
    # 4. 生成劳动力计划
    workforce_plan = generate_workforce_plan(months, workforce_config)
    
    # 5. 导出到Excel
    export_to_excel(months, workforce_plan)
    
    print("\n劳动力计划生成完成！")

# 测试功能：提供一个快速测试的示例
def test_generation():
    """测试函数，用于验证程序功能"""
    # 使用示例日期范围：2025年10月1日至2028年12月1日
    start_date = datetime(2025, 10, 1)
    end_date = datetime(2028, 12, 1)
    
    # 生成月份序列
    months = generate_month_sequence(start_date, end_date)
    
    # 使用默认配置生成劳动力计划
    workforce_plan = generate_default_workforce_plan(months)
    
    # 导出到测试Excel文件
    test_file = "测试_路基工程劳动力计划.xlsx"
    export_to_excel(months, workforce_plan, test_file)
    
    print(f"\n测试完成！测试文件已保存为: {test_file}")

# 运行程序
if __name__ == "__main__":
    root = tk.Tk()
    app = PlanGeneratorApp(root)
    root.mainloop()
    def _update_tunnel_nav_check_style(self, tunnel):
        chk = getattr(self, 'nav_item_checks', {}).get(tunnel)
        if not chk:
            return
        try:
            chk.configure(style='NavNoIndSelected.TCheckbutton' if self.show_tunnel[tunnel].get() else 'NavNoInd.TCheckbutton')
        except Exception:
            pass
        if 'card_toggle_buttons' not in self.__dict__:
            self.card_toggle_buttons = {}
        self.card_toggle_buttons['br'] = br_toggle
        try:
            self.enable_br.trace_add('write', lambda *_: self._update_toggle_button('br'))
        except Exception:
            pass
        if 'card_toggle_buttons' not in self.__dict__:
            self.card_toggle_buttons = {}
        self.card_toggle_buttons['pv'] = pv_toggle
        try:
            self.enable_pv.trace_add('write', lambda *_: self._update_toggle_button('pv'))
        except Exception:
            pass
        if 'card_toggle_buttons' not in self.__dict__:
            self.card_toggle_buttons = {}
        self.card_toggle_buttons['tu'] = tu_toggle
        try:
            self.enable_tu.trace_add('write', lambda *_: self._update_toggle_button('tu'))
        except Exception:
            pass
        if 'card_toggle_buttons' not in self.__dict__:
            self.card_toggle_buttons = {}
        self.card_toggle_buttons['hs'] = hs_toggle
        try:
            self.enable_house.trace_add('write', lambda *_: self._update_toggle_button('hs'))
        except Exception:
            pass