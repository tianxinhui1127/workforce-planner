import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import calendar
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, List, Tuple, Optional

# =============================================================================
# 配置常量 - 现代化配色方案 (灵感来自天气应用)
# =============================================================================

# 工种定义
WORK_TYPES = ["模板工", "混凝土工", "钢筋工", "支架工", "测量工", "电焊工", "泥瓦工", "电工", "普工"]
TUNNEL_WORK_TYPES = ["出渣工", "防水工", "钢筋工", "混凝土工", "开挖工", "模板工", "喷砼工", "普通工", "司机", "支护工", "电焊工"]

# 现代化配色方案 - 天气应用风格
MODERN_COLORS = {
    # 主色调 - 天空蓝渐变
    'primary': '#1E88E5',      # 主蓝色
    'primary_light': '#42A5F5', # 浅蓝色
    'primary_dark': '#1565C0',  # 深蓝色
    
    # 辅助色 - 云朵白和阳光黄
    'background': '#DCEAF7',    # 浅灰背景
    'card_bg': '#FFFFFF',       # 纯白卡片
    'accent': '#FFB74D',        # 阳光橙色
    'accent_light': '#FFF3E0',  # 浅橙色背景
    
    # 文字颜色
    'text_primary': '#2C3E50',  # 深灰文字
    'text_secondary': '#7F8C8D', # 浅灰文字
    'text_light': '#BDC3C7',    # 最浅文字
    
    # 状态颜色
    'success': '#4CAF50',       # 成功绿
    'warning': '#FF9800',       # 警告橙
    'error': '#F44336',         # 错误红
    
    # 边框和分隔线
    'border': '#ECEFF1',        # 浅灰边框
    'divider': '#F5F7FA',       # 分隔线
}

# 工程类型配置
PROJECT_TYPES = {
    'roadbed': {
        'name': '路基工程',
        'icon': '🛣️',
        'modules': ['路基填筑开挖阶段', '路基防排水阶段'],
        'color': MODERN_COLORS['primary']
    },
    'bridge': {
        'name': '桥梁工程', 
        'icon': '🌉',
        'modules': ['基础施工阶段', '墩柱施工阶段', '梁板预制及安装阶段', '桥面系及附属施工阶段'],
        'color': MODERN_COLORS['accent']
    },
    'pavement': {
        'name': '路面工程',
        'icon': '🏗️',
        'modules': ['路面基层施工阶段', '路面面层施工阶段'],
        'color': MODERN_COLORS['success']
    },
    'tunnel': {
        'name': '隧道工程',
        'icon': '🚇',
        'modules': ['洞口工程', '初支工程', '二衬工程', '附属工程'],
        'color': MODERN_COLORS['warning']
    },
    'building': {
        'name': '房建工程',
        'icon': '🏢',
        'modules': ['基础施工阶段', '主体施工阶段', '装饰装修施工阶段', '机电安装工程'],
        'color': MODERN_COLORS['error']
    }
}

# =============================================================================
# 核心功能函数
# =============================================================================

def generate_month_sequence(start_date: datetime, end_date: datetime) -> List[Tuple[int, int]]:
    """生成从开始日期到结束日期之间的所有月份序列"""
    months = []
    current_date = start_date.replace(day=1)
    
    while current_date <= end_date:
        months.append((current_date.year, current_date.month))
        
        # 计算下一个月
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    return months

def get_month_columns(months: List[Tuple[int, int]]) -> Tuple[List[str], List[str]]:
    """生成月份列的层级结构，用于DataFrame的MultiIndex"""
    years = [str(year) for year, _ in months]
    month_numbers = [str(month) for _, month in months]
    return years, month_numbers

def generate_default_workforce_plan(months: List[Tuple[int, int]], work_types: List[str] = None) -> Dict[str, List[int]]:
    """根据工程进度自动生成各工种的投入计划 - 与原版逻辑完全一致"""
    if work_types is None:
        work_types = WORK_TYPES
    
    total_months = len(months)
    workforce_plan = {}
    
    # 定义各工种的投入曲线（按百分比）- 与原版相同
    for work_type in work_types:
        workforce_plan[work_type] = []
    
    # 为每个月生成各工种人数 - 与原版相同的算法
    for month_idx in range(total_months):
        # 计算当前进度百分比
        progress = month_idx / (total_months - 1) if total_months > 1 else 1.0
        
        # 模板工：前期和中期需求较高
        template_factor = min(progress * 2, 1.0) if progress < 0.7 else (1.0 - (progress - 0.7) * 3.33)
        if "模板工" in workforce_plan:
            workforce_plan["模板工"].append(int(80 * template_factor))
        
        # 混凝土工：中期需求最高
        concrete_factor = min(progress * 3, 1.0) if progress < 0.3 else min(2 - progress * 2, 1.0) if progress < 0.8 else (1.0 - (progress - 0.8) * 5)
        if "混凝土工" in workforce_plan:
            workforce_plan["混凝土工"].append(int(90 * concrete_factor))
        
        # 钢筋工：前期和中期需求较高
        steel_factor = min(progress * 2.5, 1.0) if progress < 0.6 else (1.0 - (progress - 0.6) * 2.5)
        if "钢筋工" in workforce_plan:
            workforce_plan["钢筋工"].append(int(100 * steel_factor))
        
        # 支架工：前期和中期需求较高
        scaffold_factor = min(progress * 2, 1.0) if progress < 0.5 else (1.0 - (progress - 0.5) * 2)
        if "支架工" in workforce_plan:
            workforce_plan["支架工"].append(int(40 * scaffold_factor))
        
        # 测量工：前期和后期需求较高
        survey_factor = 0.6 + 0.4 * (1.0 - abs(progress - 0.2) * 2.5) * (1.0 - abs(progress - 0.8) * 2.5)
        if "测量工" in workforce_plan:
            workforce_plan["测量工"].append(int(10 * survey_factor))
        
        # 电焊工：中期需求较高
        welding_factor = min(progress * 3, 1.0) if progress < 0.4 else min(1.5 - progress * 1.5, 1.0)
        if "电焊工" in workforce_plan:
            workforce_plan["电焊工"].append(int(35 * welding_factor))
        
        # 泥瓦工：后期需求较高
        mason_factor = min(progress * 5, 1.0) if progress < 0.2 else 1.0 if progress < 0.8 else (1.0 - (progress - 0.8) * 5)
        if "泥瓦工" in workforce_plan:
            workforce_plan["泥瓦工"].append(int(25 * mason_factor))
        
        # 电工：均匀分布，略中后期增加
        electrician_factor = 0.5 + 0.5 * progress
        if "电工" in workforce_plan:
            workforce_plan["电工"].append(int(5 * electrician_factor))
        
        # 普工：全程都需要，中期需求最高
        laborer_factor = 0.7 + 0.3 * (1.0 - abs(progress - 0.5) * 2)
        if "普工" in workforce_plan:
            workforce_plan["普工"].append(int(50 * laborer_factor))
    
    return workforce_plan

def generate_custom_workforce_plan(months: List[Tuple[int, int]], workforce_config: Dict[str, int]) -> Dict[str, List[int]]:
    """根据用户输入的最大配置数量生成各工种的投入计划 - 与原版逻辑一致"""
    total_months = len(months)
    workforce_plan = {}
    
    # 为每个工种生成投入计划 - 与原版相同：每个月人数恒定为输入值
    for work_type, max_count in workforce_config.items():
        workforce_plan[work_type] = [int(max_count) for _ in range(total_months)]
    
    return workforce_plan

def generate_workforce_plan(months: List[Tuple[int, int]], workforce_config: Dict[str, int] = None) -> Dict[str, List[int]]:
    """生成劳动力计划 - 与原版完全一致"""
    if workforce_config is None:
        return generate_default_workforce_plan(months)
    else:
        return generate_custom_workforce_plan(months, workforce_config)

def export_to_excel(months: List[Tuple[int, int]], workforce_plan: Dict[str, List[int]], 
                   output_file: str = "路基工程劳动力计划.xlsx") -> str:
    """将劳动力计划数据导出为Excel表格"""
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
        df.to_excel(writer, sheet_name='劳动力计划', index_label='工种')
        
        # 获取工作表并进行格式化
        worksheet = writer.sheets['劳动力计划']
        worksheet.column_dimensions['A'].width = 15
        
        # 设置数据列的宽度
        import openpyxl.utils as xlutils
        max_column = worksheet.max_column
        
        for col_idx in range(2, max_column + 1):
            column_letter = xlutils.get_column_letter(col_idx)
            worksheet.column_dimensions[column_letter].width = 12
    
    return output_file

# =============================================================================
# 现代化UI组件
# =============================================================================

class ModernCard(ttk.Frame):
    """现代化卡片组件"""
    
    def __init__(self, parent, title: str = "", icon: str = "", bg_color: str = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.bg_color = bg_color or MODERN_COLORS['card_bg']
        self.title = title
        self.icon = icon
        self._radius = 12
        self._margin = 12
        self._setup_style()
        self._create_widgets()
    
    def _setup_style(self):
        """设置卡片样式"""
        style = ttk.Style()
        style.configure('ModernCard.TFrame', 
                       background=MODERN_COLORS['background'],
                       relief='flat',
                       borderwidth=0)
        style.configure('CardTitle.TLabel',
                       background=self.bg_color,
                       foreground=MODERN_COLORS['text_primary'],
                       font=('Microsoft YaHei', 12, 'bold'))
        style.configure('CardContent.TFrame',
                       background=self.bg_color)
        
        self.configure(style='ModernCard.TFrame')
    
    def _create_widgets(self):
        """创建卡片组件"""
        self.card_canvas = tk.Canvas(self, highlightthickness=0, bd=0, background=MODERN_COLORS['background'])
        self.card_canvas.pack(fill='both', expand=True)
        self.inner_frame = ttk.Frame(self, style='CardContent.TFrame')
        self.card_window = self.card_canvas.create_window(self._margin, self._margin, anchor='nw', window=self.inner_frame)
        self.inner_frame.bind("<Configure>", self._on_inner_configure)
        title_frame = ttk.Frame(self.inner_frame, style='CardContent.TFrame')
        title_frame.pack(fill='x', padx=20, pady=(15, 10))
        
        if self.icon:
            icon_label = ttk.Label(title_frame, text=self.icon, 
                                 font=('Arial', 16),
                                 style='CardTitle.TLabel')
            icon_label.pack(side='left', padx=(0, 10))
        
        if self.title:
            title_label = ttk.Label(title_frame, text=self.title,
                                  style='CardTitle.TLabel')
            title_label.pack(side='left')
        
        self.content_frame = ttk.Frame(self.inner_frame, style='CardContent.TFrame')
        self.content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 15))
        
    def get_content_frame(self):
        """获取内容框架"""
        return self.content_frame

    def _on_inner_configure(self, event):
        w = event.width
        h = event.height
        cw = w + self._margin * 2
        ch = h + self._margin * 2
        self.card_canvas.configure(width=cw, height=ch)
        self.card_canvas.coords(self.card_window, self._margin, self._margin)
        self._draw_rounded_card(cw, ch, self._radius, self.bg_color)

    def _draw_rounded_card(self, width, height, r, fill):
        self.card_canvas.delete('card')
        w = width
        h = height
        x1 = 0
        y1 = 0
        x2 = w
        y2 = h
        self.card_canvas.create_rectangle(r, y1, x2 - r, y2, fill=fill, outline=fill, tags='card')
        self.card_canvas.create_rectangle(x1, r, x2, y2 - r, fill=fill, outline=fill, tags='card')
        self.card_canvas.create_arc(x1, y1, x1 + 2*r, y1 + 2*r, start=90, extent=90, style='pieslice', fill=fill, outline=fill, tags='card')
        self.card_canvas.create_arc(x2 - 2*r, y1, x2, y1 + 2*r, start=0, extent=90, style='pieslice', fill=fill, outline=fill, tags='card')
        self.card_canvas.create_arc(x2 - 2*r, y2 - 2*r, x2, y2, start=270, extent=90, style='pieslice', fill=fill, outline=fill, tags='card')
        self.card_canvas.create_arc(x1, y2 - 2*r, x1 + 2*r, y2, start=180, extent=90, style='pieslice', fill=fill, outline=fill, tags='card')

class ModernToggle(ttk.Checkbutton):
    """现代化切换按钮"""
    
    def __init__(self, parent, text: str = "", variable=None, command=None, **kwargs):
        self.var = variable or tk.BooleanVar()
        self.command = command
        
        super().__init__(parent, text=text, variable=self.var,
                        style='Modern.TCheckbutton',
                        command=self._on_toggle, **kwargs)
    
    def _on_toggle(self):
        """切换事件处理"""
        if self.command:
            self.command()

class ModernButton(ttk.Button):
    """现代化按钮"""
    
    def __init__(self, parent, text: str = "", command=None, 
                 style_type: str = 'primary', **kwargs):
        self.style_type = style_type
        self._setup_style()
        
        super().__init__(parent, text=text, command=command, 
                        style=f'Modern{style_type.capitalize()}.TButton', **kwargs)
    
    def _setup_style(self):
        """设置按钮样式"""
        style = ttk.Style()
        
        if self.style_type == 'primary':
            bg_color = MODERN_COLORS['primary']
            fg_color = 'white'
            hover_bg = MODERN_COLORS['primary_light']
        elif self.style_type == 'secondary':
            bg_color = MODERN_COLORS['background']
            fg_color = MODERN_COLORS['text_primary']
            hover_bg = MODERN_COLORS['border']
        else:
            bg_color = MODERN_COLORS['success']
            fg_color = 'white'
            hover_bg = '#66BB6A'
        
        style.configure(f'Modern{self.style_type.capitalize()}.TButton',
                     background=bg_color,
                     foreground=fg_color,
                     font=('Microsoft YaHei', 10, 'bold'),
                     padding=10,
                     borderwidth=0,
                     focusthickness=0,
                     relief='flat')
        
        style.map(f'Modern{self.style_type.capitalize()}.TButton',
                 background=[('active', hover_bg), ('disabled', MODERN_COLORS['text_light'])],
                 foreground=[('active', fg_color), ('disabled', 'white')])

# =============================================================================
# 主要应用类
# =============================================================================

class ModernPlanGeneratorApp:
    """现代化劳动力计划生成器应用"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🚧 工程劳动力计划生成器")
        self.root.geometry("1200x800")
        self.root.configure(bg=MODERN_COLORS['background'])
        
        # 设置全局样式
        self._setup_global_styles()
        
        # 初始化变量
        self._init_variables()
        
        # 创建UI
        self._create_ui()
        
        # 初始化数据
        self._init_data()
    
    def _setup_global_styles(self):
        """设置全局样式"""
        style = ttk.Style()
        
        # 配置主题
        style.theme_use('clam')
        
        # 主框架样式
        style.configure('Main.TFrame', background=MODERN_COLORS['background'])
        
        # 标题样式
        style.configure('Header.TLabel',
                       background=MODERN_COLORS['background'],
                       foreground=MODERN_COLORS['text_primary'],
                       font=('Microsoft YaHei', 16, 'bold'))
        
        style.configure('SubHeader.TLabel',
                       background=MODERN_COLORS['background'],
                       foreground=MODERN_COLORS['text_secondary'],
                       font=('Microsoft YaHei', 12))
        
        # 标签框架样式
        style.configure('Modern.TLabelframe',
                       background=MODERN_COLORS['card_bg'],
                       relief='flat',
                       borderwidth=0)
        
        style.configure('Modern.TLabelframe.Label',
                       background=MODERN_COLORS['card_bg'],
                       foreground=MODERN_COLORS['text_primary'],
                       font=('Microsoft YaHei', 11, 'bold'))
        
        # 复选框和单选按钮样式
        style.configure('Modern.TRadiobutton',
                       background=MODERN_COLORS['card_bg'],
                       foreground=MODERN_COLORS['text_primary'],
                       font=('Microsoft YaHei', 10))
        
        style.configure('Modern.TCheckbutton',
                       background=MODERN_COLORS['card_bg'],
                       foreground=MODERN_COLORS['text_primary'],
                       font=('Microsoft YaHei', 10))
        
        # 输入控件样式
        style.configure('Modern.TEntry',
                       fieldbackground=MODERN_COLORS['card_bg'],
                       background=MODERN_COLORS['card_bg'],
                       foreground=MODERN_COLORS['text_primary'],
                       borderwidth=1,
                       relief='solid')
        
        style.configure('Modern.TCombobox',
                       fieldbackground=MODERN_COLORS['card_bg'],
                       background=MODERN_COLORS['card_bg'],
                       foreground=MODERN_COLORS['text_primary'],
                       arrowcolor=MODERN_COLORS['text_secondary'])
        
        style.configure('Modern.TSpinbox',
                       fieldbackground=MODERN_COLORS['card_bg'],
                       background=MODERN_COLORS['card_bg'],
                       foreground=MODERN_COLORS['text_primary'],
                       arrowcolor=MODERN_COLORS['text_secondary'])
    
    def _init_variables(self):
        """初始化变量"""
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        # 时间范围变量
        self.year_options = list(range(current_year - 5, current_year + 11))
        self.month_options = list(range(1, 13))
        
        # 项目配置变量
        self.project_vars = {}
        for project_key, project_config in PROJECT_TYPES.items():
            self.project_vars[project_key] = {
                'enabled': tk.BooleanVar(value=False),
                'modules': {}
            }
            
            for module in project_config['modules']:
                self.project_vars[project_key]['modules'][module] = {
                    'start_year': tk.IntVar(value=current_year),
                    'start_month': tk.IntVar(value=current_month),
                    'end_year': tk.IntVar(value=current_year),
                    'end_month': tk.IntVar(value=current_month),
                    'team_count': tk.IntVar(value=1),
                    'use_default': tk.BooleanVar(value=True),
                    'workforce_config': {}
                }
                
                # 为每个工种创建变量
                work_types = TUNNEL_WORK_TYPES if project_key == 'tunnel' else WORK_TYPES
                for work_type in work_types:
                    self.project_vars[project_key]['modules'][module]['workforce_config'][work_type] = {
                        'enabled': tk.BooleanVar(value=False),
                        'count': tk.IntVar(value=self._get_default_workforce(work_type))
                    }
        
        # 输出设置
        self.output_path = tk.StringVar(
            value=os.path.join(os.getcwd(), "工程劳动力计划.xlsx")
        )
    
    def _get_default_workforce(self, work_type: str) -> int:
        """获取默认劳动力配置"""
        defaults = {
            "模板工": 80, "混凝土工": 90, "钢筋工": 100, "支架工": 40,
            "测量工": 10, "电焊工": 35, "泥瓦工": 25, "电工": 5, "普工": 50,
            "出渣工": 60, "防水工": 30, "开挖工": 100, "喷砼工": 90,
            "普通工": 70, "司机": 30, "支护工": 30
        }
        return defaults.get(work_type, 50)
    
    def _create_ui(self):
        """创建用户界面"""
        # 主容器
        main_frame = ttk.Frame(self.root, style='Main.TFrame')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 标题区域
        self._create_header(main_frame)
        
        # 内容区域
        content_frame = ttk.Frame(main_frame, style='Main.TFrame')
        content_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        # 左侧项目选择区
        left_frame = ttk.Frame(content_frame, style='Main.TFrame')
        left_frame.pack(side='left', fill='y', padx=(0, 20))
        left_frame.configure(width=280)
        left_frame.pack_propagate(False)
        self._create_project_selector(left_frame)
        
        # 右侧配置区
        right_frame = ttk.Frame(content_frame, style='Main.TFrame')
        right_frame.pack(side='left', fill='both', expand=True)
        self._create_configuration_area(right_frame)
        
        # 底部操作区（与右侧配置区对齐）
        self._create_action_area(right_frame)
    
    def _create_header(self, parent):
        """创建标题区域"""
        header_frame = ttk.Frame(parent, style='Main.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # 主标题
        title_label = ttk.Label(header_frame, text="🚧 工程劳动力计划生成器",
                               style='Header.TLabel')
        title_label.pack(side='left')
        
        # 副标题
        subtitle_label = ttk.Label(header_frame, 
                                   text="智能生成各类工程劳动力配置计划",
                                   style='SubHeader.TLabel')
        subtitle_label.pack(side='left', padx=(20, 0))
    
    def _create_project_selector(self, parent):
        """创建项目选择器"""
        # 项目选择卡片
        selector_card = ModernCard(parent, title="📋 选择工程类型", 
                                 bg_color=MODERN_COLORS['card_bg'])
        selector_card.pack(fill='x')
        
        content_frame = selector_card.get_content_frame()
        
        # 为每种工程类型创建选择器
        for project_key, project_config in PROJECT_TYPES.items():
            project_frame = ttk.Frame(content_frame, style='CardContent.TFrame')
            project_frame.pack(fill='x', pady=8)

            project_frame.columnconfigure(1, weight=1)
            project_frame.rowconfigure(0, weight=1)

            icon_label = ttk.Label(project_frame, text=project_config['icon'],
                                 font=('Arial', 20),
                                 background=MODERN_COLORS['card_bg'])
            icon_label.grid(row=0, column=0, padx=(0, 15), sticky='nsw')

            info_frame = ttk.Frame(project_frame, style='CardContent.TFrame')
            info_frame.grid(row=0, column=1, sticky='nsw')
            info_frame.rowconfigure(0, weight=1)
            info_frame.rowconfigure(1, weight=1)

            name_label = ttk.Label(info_frame, text=project_config['name'],
                                   font=('Microsoft YaHei', 11, 'bold'),
                                   background=MODERN_COLORS['card_bg'],
                                   foreground=project_config['color'])
            name_label.grid(row=0, column=0, sticky='w')

            desc_label = ttk.Label(info_frame, 
                                 text=f"包含 {len(project_config['modules'])} 个阶段",
                                 font=('Microsoft YaHei', 9),
                                 background=MODERN_COLORS['card_bg'],
                                 foreground=MODERN_COLORS['text_secondary'])
            desc_label.grid(row=1, column=0, sticky='w')

            toggle = ModernToggle(project_frame, text="启用",
                                variable=self.project_vars[project_key]['enabled'],
                                command=lambda k=project_key: self._on_project_toggle(k))
            toggle.grid(row=0, column=2, sticky='nse')
    
    def _create_configuration_area(self, parent):
        """创建配置区域"""
        # 创建Notebook用于不同阶段
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill='both', expand=True)
        
        # 为每个项目创建配置页面
        self.config_frames = {}
        for project_key, project_config in PROJECT_TYPES.items():
            frame = ttk.Frame(self.notebook, style='Main.TFrame')
            self.config_frames[project_key] = frame
            
            # 根据项目启用状态设置标签页状态
            initial_state = 'normal' if self.project_vars[project_key]['enabled'].get() else 'disabled'
            self.notebook.add(frame, text=f"{project_config['icon']} {project_config['name']}")
            
            # 如果项目未启用，禁用标签页
            if initial_state == 'disabled':
                tab_index = len(self.notebook.tabs()) - 1
                self.notebook.tab(tab_index, state='disabled')
            
            self._create_module_config(frame, project_key, project_config)
    
    def _create_module_config(self, parent, project_key: str, project_config: dict):
        """创建模块配置"""
        # 创建滚动区域
        canvas = tk.Canvas(parent, bg=MODERN_COLORS['background'], 
                          highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Main.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 添加鼠标滚轮事件绑定
        def _on_mousewheel(event):
            """鼠标滚轮事件处理"""
            # Windows系统使用delta，Linux使用num
            if event.delta:
                # Windows: delta通常为±120，需要除以120得到滚动单位
                # 向上滚动为正值，向下滚动为负值，需要反转方向
                if event.delta > 0:
                    canvas.yview_scroll(-1, "units")  # 向上滚动
                else:
                    canvas.yview_scroll(1, "units")   # 向下滚动
            else:
                # Linux系统
                if event.num == 4:  # Linux向上滚动
                    canvas.yview_scroll(-1, "units")
                elif event.num == 5:  # Linux向下滚动
                    canvas.yview_scroll(1, "units")
            return "break"  # 阻止事件冒泡
        
        # 绑定鼠标滚轮事件到canvas和scrollable_frame
        canvas.bind("<MouseWheel>", _on_mousewheel)
        canvas.bind("<Button-4>", _on_mousewheel)
        canvas.bind("<Button-5>", _on_mousewheel)
        
        # 也绑定到可滚动框架，确保鼠标在内容上时也能滚动
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<Button-4>", _on_mousewheel)
        scrollable_frame.bind("<Button-5>", _on_mousewheel)
        
        # 为所有子控件绑定鼠标滚轮事件
        def bind_scroll_to_children(widget):
            """递归地为所有子控件绑定滚动事件"""
            widget.bind("<MouseWheel>", _on_mousewheel)
            widget.bind("<Button-4>", _on_mousewheel)
            widget.bind("<Button-5>", _on_mousewheel)
            
            # 递归处理子控件
            for child in widget.winfo_children():
                bind_scroll_to_children(child)
        
        # 立即为scrollable_frame的所有子控件绑定事件
        bind_scroll_to_children(scrollable_frame)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 为每个模块创建配置卡片
        for module in project_config['modules']:
            module_card = ModernCard(scrollable_frame, title=module,
                                     bg_color=MODERN_COLORS['card_bg'])
            module_card.pack(fill='x', pady=10)
            
            self._create_module_details(module_card.get_content_frame(), 
                                      project_key, module)
    
    def _create_module_details(self, parent, project_key: str, module: str):
        """创建模块详细配置"""
        module_vars = self.project_vars[project_key]['modules'][module]
        work_types = TUNNEL_WORK_TYPES if project_key == 'tunnel' else WORK_TYPES
        
        # 时间配置
        time_frame = ttk.LabelFrame(parent, text="⏰ 时间范围", 
                                   style='Modern.TLabelframe')
        time_frame.pack(fill='x', pady=10)
        
        # 开始时间
        start_frame = ttk.Frame(time_frame, style='CardContent.TFrame')
        start_frame.pack(fill='x', padx=15, pady=8)
        
        ttk.Label(start_frame, text="开始时间:", 
                 style='CardTitle.TLabel').pack(side='left', padx=(0, 15))
        
        ttk.Combobox(start_frame, values=self.year_options,
                    textvariable=module_vars['start_year'],
                    width=8, state="readonly",
                    style='Modern.TCombobox').pack(side='left', padx=5)
        
        ttk.Label(start_frame, text="年", 
                 background=MODERN_COLORS['card_bg']).pack(side='left', padx=5)
        
        ttk.Combobox(start_frame, values=self.month_options,
                    textvariable=module_vars['start_month'],
                    width=5, state="readonly",
                    style='Modern.TCombobox').pack(side='left', padx=5)
        
        ttk.Label(start_frame, text="月", 
                 background=MODERN_COLORS['card_bg']).pack(side='left', padx=5)
        
        # 结束时间
        end_frame = ttk.Frame(time_frame, style='CardContent.TFrame')
        end_frame.pack(fill='x', padx=15, pady=8)
        
        ttk.Label(end_frame, text="结束时间:", 
                 style='CardTitle.TLabel').pack(side='left', padx=(0, 15))
        
        ttk.Combobox(end_frame, values=self.year_options,
                    textvariable=module_vars['end_year'],
                    width=8, state="readonly",
                    style='Modern.TCombobox').pack(side='left', padx=5)
        
        ttk.Label(end_frame, text="年", 
                 background=MODERN_COLORS['card_bg']).pack(side='left', padx=5)
        
        ttk.Combobox(end_frame, values=self.month_options,
                    textvariable=module_vars['end_month'],
                    width=5, state="readonly",
                    style='Modern.TCombobox').pack(side='left', padx=5)
        
        ttk.Label(end_frame, text="月", 
                 background=MODERN_COLORS['card_bg']).pack(side='left', padx=5)
        
        # 队伍配置
        team_frame = ttk.LabelFrame(parent, text="👥 队伍配置", 
                                   style='Modern.TLabelframe')
        team_frame.pack(fill='x', pady=10)
        
        team_content = ttk.Frame(team_frame, style='CardContent.TFrame')
        team_content.pack(fill='x', padx=15, pady=8)
        
        ttk.Label(team_content, text="队伍数量:", 
                 style='CardTitle.TLabel').pack(side='left', padx=(0, 15))
        
        ttk.Spinbox(team_content, from_=1, to=100,
                   textvariable=module_vars['team_count'],
                   width=8, style='Modern.TSpinbox').pack(side='left')
        
        # 配置模式
        config_frame = ttk.LabelFrame(parent, text="⚙️ 配置模式", 
                                     style='Modern.TLabelframe')
        config_frame.pack(fill='x', pady=10)
        
        config_content = ttk.Frame(config_frame, style='CardContent.TFrame')
        config_content.pack(fill='x', padx=15, pady=8)
        
        ttk.Radiobutton(config_content, 
                       text="🤖 智能生成 (推荐)",
                       variable=module_vars['use_default'],
                       value=True,
                       command=lambda: self._on_config_mode_change(project_key, module, True),
                       style='Modern.TRadiobutton').pack(anchor='w', pady=5)
        
        ttk.Radiobutton(config_content,
                       text="📝 手动配置",
                       variable=module_vars['use_default'],
                       value=False,
                       command=lambda: self._on_config_mode_change(project_key, module, False),
                       style='Modern.TRadiobutton').pack(anchor='w', pady=5)
        
        # 手动配置区域
        manual_frame = ttk.LabelFrame(parent, text="🔧 工种配置", 
                                      style='Modern.TLabelframe')
        manual_frame.pack(fill='x', pady=10)
        
        # 存储手动配置区域的引用，用于后续状态控制
        if not hasattr(self, 'manual_frames'):
            self.manual_frames = {}
        self.manual_frames[f"{project_key}_{module}"] = manual_frame
        
        # 创建工种配置网格
        manual_content = ttk.Frame(manual_frame, style='CardContent.TFrame')
        manual_content.pack(fill='x', padx=15, pady=8)
        
        for i, work_type in enumerate(work_types):
            row = i // 3
            col = (i % 3) * 2
            
            # 工种复选框
            toggle = ModernToggle(manual_content, text=work_type,
                                variable=module_vars['workforce_config'][work_type]['enabled'],
                                command=lambda wt=work_type: self._update_workforce_input(
                                    project_key, module, wt))
            toggle.grid(row=row, column=col, padx=5, pady=5, sticky='w')
            
            # 数量输入
            spin = ttk.Spinbox(manual_content, from_=0, to=500,
                             textvariable=module_vars['workforce_config'][work_type]['count'],
                             width=6, style='Modern.TSpinbox')
            spin.grid(row=row, column=col + 1, padx=5, pady=5, sticky='w')

        is_default_mode = module_vars['use_default'].get()
        self._on_config_mode_change(project_key, module, is_default_mode)
    
    def _create_action_area(self, parent):
        """创建操作区域"""
        action_card = ModernCard(parent, title="💾 导出设置", 
                               bg_color=MODERN_COLORS['card_bg'])
        action_card.pack(fill='x')
        
        content_frame = action_card.get_content_frame()
        
        # 输出文件设置
        output_frame = ttk.Frame(content_frame, style='CardContent.TFrame')
        output_frame.pack(fill='x', pady=10)
        
        ttk.Label(output_frame, text="输出文件:", 
                 style='CardTitle.TLabel').pack(side='left', padx=(0, 15))
        
        ttk.Entry(output_frame, textvariable=self.output_path,
                 width=60, style='Modern.TEntry').pack(side='left', fill='x', expand=True)
        
        ModernButton(output_frame, text="📁 浏览",
                    command=self._choose_output_file,
                    style_type='secondary').pack(side='left', padx=(15, 0))
        
        # 操作按钮
        button_frame = ttk.Frame(content_frame, style='CardContent.TFrame')
        button_frame.pack(fill='x', pady=15)
        
        ModernButton(button_frame, text="🚀 生成计划",
                    command=self._generate_plan,
                    style_type='primary').pack(side='left')
        
        ModernButton(button_frame, text="❌ 退出",
                    command=self.root.quit,
                    style_type='secondary').pack(side='right')
        
        ModernButton(button_frame, text="📊 快速测试",
                    command=self._quick_test,
                    style_type='secondary').pack(side='right', padx=(0, 10))
    
    def _on_project_toggle(self, project_key: str):
        """项目切换事件 - 控制右侧配置区域的启用/禁用状态，并跳转到对应工作区"""
        try:
            enabled = self.project_vars[project_key]['enabled'].get()
            
            # 找到对应的配置页面
            for i, frame in enumerate(self.notebook.tabs()):
                tab_text = self.notebook.tab(i, 'text')
                project_config = PROJECT_TYPES[project_key]
                expected_text = f"{project_config['icon']} {project_config['name']}"
                
                if tab_text == expected_text:
                    # 获取对应的frame
                    tab_frame = self.notebook.nametowidget(frame)
                    
                    if enabled:
                        # 启用状态 - 正常显示
                        self._set_frame_state(tab_frame, 'normal')
                        # 更新标签页状态为正常
                        self.notebook.tab(i, state='normal')
                        # 自动跳转到对应的工作区
                        self.notebook.select(i)
                        print(f"[OK] 已启用 {project_config['name']} 配置区域，并自动跳转")
                    else:
                        # 禁用状态 - 禁用所有控件并灰化标签页
                        self._set_frame_state(tab_frame, 'disabled')
                        # 更新标签页状态为禁用
                        self.notebook.tab(i, state='disabled')
                        print(f"[DISABLED] 已禁用 {project_config['name']} 配置区域")
                    break
            
            # 检查是否至少有一个项目被启用
            any_enabled = any(data['enabled'].get() for data in self.project_vars.values())
            if not any_enabled:
                print("⚠️ 警告：未启用任何工程项目")
                
        except Exception as e:
            print(f"❌ 切换项目状态时出错: {e}")
    
    def _set_frame_state(self, frame, state):
        """递归设置frame及其所有子组件的状态"""
        try:
            # 尝试直接设置frame的状态
            frame.configure(state=state)
        except tk.TclError:
            # 某些frame可能不支持state属性，忽略
            pass
        
        # 递归处理所有子组件
        for child in frame.winfo_children():
            # 特殊处理Notebook和Canvas
            if isinstance(child, ttk.Notebook):
                continue
            elif isinstance(child, tk.Canvas):
                # 处理Canvas的子组件
                for canvas_child in child.winfo_children():
                    self._set_widget_state(canvas_child, state)
            else:
                self._set_widget_state(child, state)
    
    def _set_widget_state(self, widget, state):
        """设置单个组件的状态 - 支持更多组件类型"""
        # 定义支持state属性的组件类型
        state_supported_widgets = (
            ttk.Button, ttk.Entry, ttk.Combobox, ttk.Spinbox, 
            ttk.Checkbutton, ttk.Radiobutton, tk.Button, 
            tk.Entry, tk.Spinbox, tk.Checkbutton, tk.Radiobutton
        )
        
        # 如果是指定类型的组件，设置其状态
        if isinstance(widget, state_supported_widgets):
            try:
                widget.configure(state=state)
            except tk.TclError:
                pass  # 忽略不支持state属性的组件
        
        # 处理LabelFrame的特殊情况
        if isinstance(widget, ttk.LabelFrame):
            # LabelFrame本身不支持state，但我们需要处理其内容
            for child in widget.winfo_children():
                self._set_widget_state(child, state)
        # 处理Frame的特殊情况
        elif isinstance(widget, (ttk.Frame, tk.Frame)):
            # Frame本身不支持state，但我们需要处理其内容
            for child in widget.winfo_children():
                self._set_widget_state(child, state)
        # 处理其他容器的子组件
        else:
            for child in widget.winfo_children():
                self._set_widget_state(child, state)
    
    def _on_config_mode_change(self, project_key: str, module: str, is_default: bool):
        """配置模式变更事件 - 控制工种配置区域的启用/禁用状态"""
        try:
            # 获取手动配置区域的frame键
            frame_key = f"{project_key}_{module}"
            
            if hasattr(self, 'manual_frames') and frame_key in self.manual_frames:
                manual_frame = self.manual_frames[frame_key]
                
                if is_default:
                    # 智能生成模式 - 禁用工种配置
                    self._set_frame_state(manual_frame, 'disabled')
                    print(f"[CONFIG] {PROJECT_TYPES[project_key]['name']}-{module}: Smart mode, manual config disabled")
                else:
                    # 手动配置模式 - 启用工种配置
                    self._set_frame_state(manual_frame, 'normal')
                    print(f"[CONFIG] {PROJECT_TYPES[project_key]['name']}-{module}: Manual mode, manual config enabled")
            else:
                print(f"[WARNING] Manual config frame not found: {frame_key}")
                
        except Exception as e:
            print(f"[ERROR] Config mode change error: {e}")
    
    def _update_workforce_input(self, project_key: str, module: str, work_type: str):
        """更新工种输入状态 - 处理自定义配置的启用/禁用"""
        # 获取工种配置
        workforce_config = self.project_vars[project_key]['modules'][module]['workforce_config'][work_type]
        enabled = workforce_config['enabled'].get()
        
        # 这里可以添加额外的逻辑，比如根据项目状态更新工种可用性
        # 目前主要功能由默认配置/自定义配置单选按钮控制
        pass
    
    def _choose_output_file(self):
        """选择输出文件"""
        filename = filedialog.asksaveasfilename(
            title="选择输出文件",
            defaultextension=".xlsx",
            initialfile="工程劳动力计划.xlsx",
            filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        if filename:
            self.output_path.set(filename)
    
    def _init_data(self):
        """初始化数据"""
        # 默认不启用任何项目，需要用户手动启用
        for project_data in self.project_vars.values():
            project_data['enabled'].set(False)
        
        # 初始化所有配置区域为禁用状态
        self._update_all_project_states()
        
        # 初始化所有配置模式（默认智能生成模式）
        self._init_all_config_modes()
    
    def _update_all_project_states(self):
        """更新所有项目的状态"""
        for project_key in PROJECT_TYPES:
            self._on_project_toggle(project_key)
    
    def _init_all_config_modes(self):
        """初始化所有配置模式（默认智能生成，禁用手动配置）"""
        for project_key in PROJECT_TYPES:
            for module in PROJECT_TYPES[project_key]['modules']:
                # 默认设置为智能生成模式
                self.project_vars[project_key]['modules'][module]['use_default'].set(True)
                # 禁用手动配置区域
                self._on_config_mode_change(project_key, module, True)
    
    def _generate_plan(self):
        """生成劳动力计划 - 与原版逻辑完全一致"""
        try:
            # 按项目类型分别收集数据 - 与原版相同
            months_rb_map = {}
            plan_rb_map = {}
            months_br_map = {}
            plan_br_map = {}
            months_pv_map = {}
            plan_pv_map = {}
            months_tunnel_map = {}
            plan_tunnel_map = {}
            months_hs_map = {}
            plan_house_map = {}
            
            # 路基工程处理 - 与原版相同
            if self.project_vars['roadbed']['enabled'].get():
                for module in PROJECT_TYPES['roadbed']['modules']:
                    module_vars = self.project_vars['roadbed']['modules'][module]
                    
                    # 获取时间范围
                    start_date = datetime(
                        module_vars['start_year'].get(),
                        module_vars['start_month'].get(),
                        1
                    )
                    
                    end_date = datetime(
                        module_vars['end_year'].get(),
                        module_vars['end_month'].get(),
                        calendar.monthrange(module_vars['end_year'].get(), 
                                          module_vars['end_month'].get())[1]
                    )
                    
                    if start_date >= end_date:
                        messagebox.showerror("输入错误", f"路基工程-{module}开始时间必须早于结束时间！")
                        return
                    
                    months_list = generate_month_sequence(start_date, end_date)
                    months_rb_map[module] = months_list
                    
                    # 生成模块计划 - 与原版相同
                    plan_mod = {}
                    for work_type in WORK_TYPES:
                        if module_vars['use_default'].get():
                            # 使用默认配置生成曲线
                            temp_plan = generate_default_workforce_plan(months_list, WORK_TYPES)
                            plan_mod[work_type] = temp_plan[work_type]
                        else:
                            # 使用自定义配置
                            if module_vars['workforce_config'][work_type]['enabled'].get():
                                val = module_vars['workforce_config'][work_type]['count'].get()
                                plan_mod[work_type] = [val for _ in range(len(months_list))]
                            else:
                                plan_mod[work_type] = [0 for _ in range(len(months_list))]
                    
                    # 应用班组系数 - 与原版相同
                    team_count = max(1, module_vars['team_count'].get())
                    for work_type in plan_mod:
                        plan_mod[work_type] = [int(count * team_count) for count in plan_mod[work_type]]
                    
                    plan_rb_map[module] = plan_mod
            
            # 桥梁工程处理 - 与原版相同
            if self.project_vars['bridge']['enabled'].get():
                for module in PROJECT_TYPES['bridge']['modules']:
                    module_vars = self.project_vars['bridge']['modules'][module]
                    
                    start_date = datetime(
                        module_vars['start_year'].get(),
                        module_vars['start_month'].get(),
                        1
                    )
                    
                    end_date = datetime(
                        module_vars['end_year'].get(),
                        module_vars['end_month'].get(),
                        calendar.monthrange(module_vars['end_year'].get(), 
                                          module_vars['end_month'].get())[1]
                    )
                    
                    if start_date >= end_date:
                        messagebox.showerror("输入错误", f"桥梁工程-{module}开始时间必须早于结束时间！")
                        return
                    
                    months_list = generate_month_sequence(start_date, end_date)
                    months_br_map[module] = months_list
                    
                    plan_mod = {}
                    for work_type in WORK_TYPES:
                        if module_vars['use_default'].get():
                            temp_plan = generate_default_workforce_plan(months_list, WORK_TYPES)
                            plan_mod[work_type] = temp_plan[work_type]
                        else:
                            if module_vars['workforce_config'][work_type]['enabled'].get():
                                val = module_vars['workforce_config'][work_type]['count'].get()
                                plan_mod[work_type] = [val for _ in range(len(months_list))]
                            else:
                                plan_mod[work_type] = [0 for _ in range(len(months_list))]
                    
                    team_count = max(1, module_vars['team_count'].get())
                    for work_type in plan_mod:
                        plan_mod[work_type] = [int(count * team_count) for count in plan_mod[work_type]]
                    
                    plan_br_map[module] = plan_mod
            
            # 路面工程处理 - 与原版相同
            if self.project_vars['pavement']['enabled'].get():
                for module in PROJECT_TYPES['pavement']['modules']:
                    module_vars = self.project_vars['pavement']['modules'][module]
                    
                    start_date = datetime(
                        module_vars['start_year'].get(),
                        module_vars['start_month'].get(),
                        1
                    )
                    
                    end_date = datetime(
                        module_vars['end_year'].get(),
                        module_vars['end_month'].get(),
                        calendar.monthrange(module_vars['end_year'].get(), 
                                          module_vars['end_month'].get())[1]
                    )
                    
                    if start_date >= end_date:
                        messagebox.showerror("输入错误", f"路面工程-{module}开始时间必须早于结束时间！")
                        return
                    
                    months_list = generate_month_sequence(start_date, end_date)
                    months_pv_map[module] = months_list
                    
                    plan_mod = {}
                    for work_type in WORK_TYPES:
                        if module_vars['use_default'].get():
                            temp_plan = generate_default_workforce_plan(months_list, WORK_TYPES)
                            plan_mod[work_type] = temp_plan[work_type]
                        else:
                            if module_vars['workforce_config'][work_type]['enabled'].get():
                                val = module_vars['workforce_config'][work_type]['count'].get()
                                plan_mod[work_type] = [val for _ in range(len(months_list))]
                            else:
                                plan_mod[work_type] = [0 for _ in range(len(months_list))]
                    
                    team_count = max(1, module_vars['team_count'].get())
                    for work_type in plan_mod:
                        plan_mod[work_type] = [int(count * team_count) for count in plan_mod[work_type]]
                    
                    plan_pv_map[module] = plan_mod
            
            # 隧道工程处理 - 与原版相同
            if self.project_vars['tunnel']['enabled'].get():
                for module in PROJECT_TYPES['tunnel']['modules']:
                    module_vars = self.project_vars['tunnel']['modules'][module]
                    
                    start_date = datetime(
                        module_vars['start_year'].get(),
                        module_vars['start_month'].get(),
                        1
                    )
                    
                    end_date = datetime(
                        module_vars['end_year'].get(),
                        module_vars['end_month'].get(),
                        calendar.monthrange(module_vars['end_year'].get(), 
                                          module_vars['end_month'].get())[1]
                    )
                    
                    if start_date >= end_date:
                        messagebox.showerror("输入错误", f"隧道工程-{module}开始时间必须早于结束时间！")
                        return
                    
                    months_list = generate_month_sequence(start_date, end_date)
                    months_tunnel_map[module] = months_list
                    
                    plan_mod = {}
                    for work_type in TUNNEL_WORK_TYPES:
                        if module_vars['use_default'].get():
                            temp_plan = generate_default_workforce_plan(months_list, TUNNEL_WORK_TYPES)
                            plan_mod[work_type] = temp_plan[work_type]
                        else:
                            if module_vars['workforce_config'][work_type]['enabled'].get():
                                val = module_vars['workforce_config'][work_type]['count'].get()
                                plan_mod[work_type] = [val for _ in range(len(months_list))]
                            else:
                                plan_mod[work_type] = [0 for _ in range(len(months_list))]
                    
                    team_count = max(1, module_vars['team_count'].get())
                    for work_type in plan_mod:
                        plan_mod[work_type] = [int(count * team_count) for count in plan_mod[work_type]]
                    
                    plan_tunnel_map[module] = plan_mod
            
            # 房建工程处理 - 与原版相同
            if self.project_vars['building']['enabled'].get():
                for module in PROJECT_TYPES['building']['modules']:
                    module_vars = self.project_vars['building']['modules'][module]
                    
                    start_date = datetime(
                        module_vars['start_year'].get(),
                        module_vars['start_month'].get(),
                        1
                    )
                    
                    end_date = datetime(
                        module_vars['end_year'].get(),
                        module_vars['end_month'].get(),
                        calendar.monthrange(module_vars['end_year'].get(), 
                                          module_vars['end_month'].get())[1]
                    )
                    
                    if start_date >= end_date:
                        messagebox.showerror("输入错误", f"房建工程-{module}开始时间必须早于结束时间！")
                        return
                    
                    months_list = generate_month_sequence(start_date, end_date)
                    months_hs_map[module] = months_list
                    
                    plan_mod = {}
                    for work_type in WORK_TYPES:
                        if module_vars['use_default'].get():
                            temp_plan = generate_default_workforce_plan(months_list, WORK_TYPES)
                            plan_mod[work_type] = temp_plan[work_type]
                        else:
                            if module_vars['workforce_config'][work_type]['enabled'].get():
                                val = module_vars['workforce_config'][work_type]['count'].get()
                                plan_mod[work_type] = [val for _ in range(len(months_list))]
                            else:
                                plan_mod[work_type] = [0 for _ in range(len(months_list))]
                    
                    team_count = max(1, module_vars['team_count'].get())
                    for work_type in plan_mod:
                        plan_mod[work_type] = [int(count * team_count) for count in plan_mod[work_type]]
                    
                    plan_house_map[module] = plan_mod
            
            # 汇总：月份并集，缺失月份按0相加 - 与原版完全相同
            rb_union = set()
            for module in PROJECT_TYPES['roadbed']['modules']:
                if module in months_rb_map:
                    rb_union |= {m for m in months_rb_map[module]}
            
            br_union = set()
            for module in PROJECT_TYPES['bridge']['modules']:
                if module in months_br_map:
                    br_union |= {m for m in months_br_map[module]}
            
            pv_union = set()
            for module in PROJECT_TYPES['pavement']['modules']:
                if module in months_pv_map:
                    pv_union |= {m for m in months_pv_map[module]}
            
            tunnel_union = set()
            for module in PROJECT_TYPES['tunnel']['modules']:
                if module in months_tunnel_map:
                    tunnel_union |= {m for m in months_tunnel_map[module]}
            
            hs_union = set()
            for module in PROJECT_TYPES['building']['modules']:
                if module in months_hs_map:
                    hs_union |= {m for m in months_hs_map[module]}
            
            months_union = list(rb_union | br_union | pv_union | tunnel_union | hs_union)
            months_union.sort(key=lambda x: (x[0], x[1]))
            if not months_union:
                messagebox.showerror("提示", "未启用任何项目或时间范围无效，无法生成计划")
                return
            
            aggregated_plan = {}
            aggregated_types = list(dict.fromkeys(WORK_TYPES + TUNNEL_WORK_TYPES))
            
            for wt in aggregated_types:
                # 收集各项目类型的数据映射 - 与原版相同
                rb_maps = []
                for module in PROJECT_TYPES['roadbed']['modules']:
                    if module in months_rb_map:
                        mod_months_rb = months_rb_map[module]
                        mod_plan_rb = plan_rb_map.get(module, {})
                        if wt in mod_plan_rb:
                            rb_maps.append({m: v for m, v in zip(mod_months_rb, mod_plan_rb[wt])})
                
                br_maps = []
                for module in PROJECT_TYPES['bridge']['modules']:
                    if module in months_br_map:
                        mod_months_br = months_br_map[module]
                        mod_plan_br = plan_br_map.get(module, {})
                        if wt in mod_plan_br:
                            br_maps.append({m: v for m, v in zip(mod_months_br, mod_plan_br[wt])})
                
                pv_maps = []
                for module in PROJECT_TYPES['pavement']['modules']:
                    if module in months_pv_map:
                        mod_months_pv = months_pv_map[module]
                        mod_plan_pv = plan_pv_map.get(module, {})
                        if wt in mod_plan_pv:
                            pv_maps.append({m: v for m, v in zip(mod_months_pv, mod_plan_pv[wt])})
                
                tunnel_maps = []
                for module in PROJECT_TYPES['tunnel']['modules']:
                    if module in months_tunnel_map:
                        mod_months_tunnel = months_tunnel_map[module]
                        mod_plan_tunnel = plan_tunnel_map.get(module, {})
                        if wt in mod_plan_tunnel:
                            tunnel_maps.append({m: v for m, v in zip(mod_months_tunnel, mod_plan_tunnel[wt])})
                
                hs_maps = []
                for module in PROJECT_TYPES['building']['modules']:
                    if module in months_hs_map:
                        mod_months_hs = months_hs_map[module]
                        mod_plan_hs = plan_house_map.get(module, {})
                        if wt in mod_plan_hs:
                            hs_maps.append({m: v for m, v in zip(mod_months_hs, mod_plan_hs[wt])})
                
                # 聚合计算 - 与原版完全相同
                aggregated_plan[wt] = [sum(rb.get(m, 0) for rb in rb_maps) + 
                                     sum(br.get(m, 0) for br in br_maps) + 
                                     sum(pv.get(m, 0) for pv in pv_maps) + 
                                     sum(hs.get(m, 0) for hs in hs_maps) + 
                                     sum(tunnel.get(m, 0) for tunnel in tunnel_maps) for m in months_union]
            
            # 导出到Excel
            output_file = self.output_path.get()
            export_to_excel(months_union, aggregated_plan, output_file)
            
            # 显示成功消息
            if messagebox.askyesno("成功", 
                                 f"劳动力计划已成功生成！\n\n"
                                 f"文件保存位置：\n{output_file}\n\n"
                                 f"是否立即打开文件？"):
                try:
                    os.startfile(output_file)
                except Exception as e:
                    messagebox.showwarning("提示", f"无法自动打开文件：{e}")
            
        except Exception as e:
            messagebox.showerror("错误", f"生成计划时发生错误：\n{str(e)}")
    
    def _quick_test(self):
        """快速测试功能"""
        try:
            # 使用示例数据
            start_date = datetime(2025, 1, 1)
            end_date = datetime(2025, 12, 31)
            months = generate_month_sequence(start_date, end_date)
            workforce_plan = generate_default_workforce_plan(months, WORK_TYPES)
            
            test_file = "测试_劳动力计划.xlsx"
            export_to_excel(months, workforce_plan, test_file)
            
            messagebox.showinfo("测试完成", 
                              f"测试文件已生成：{test_file}\n\n"
                              f"此文件展示了智能生成的劳动力配置曲线。")
            
            try:
                os.startfile(test_file)
            except:
                pass
                
        except Exception as e:
            messagebox.showerror("测试失败", f"快速测试失败：{str(e)}")

# =============================================================================
# 主程序入口
# =============================================================================

def main():
    """主函数"""
    root = tk.Tk()
    app = ModernPlanGeneratorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()