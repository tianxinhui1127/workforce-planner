import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os

# 配色常量
MODERN_COLORS = {
    'background': '#DCEAF7',
    'card_bg': '#FFFFFF',
    'text_primary': '#2C3E50',
    'text_secondary': '#7F8C8D',
    'border': '#ECEFF1',
    'primary': '#1E88E5',
    'accent': '#FFB74D',
    'success': '#4CAF50',
    'warning': '#FF9800',
    'error': '#F44336',
}

# 工程类型配置
PROJECT_TYPES = {
    'roadbed': {'name': '路基工程', 'icon': '🛣️', 'modules': ['路基填筑开挖阶段', '路基防排水阶段'], 'color': '#1E88E5'},
    'bridge': {'name': '桥梁工程', 'icon': '🌉', 'modules': ['基础施工阶段', '墩柱施工阶段', '梁板预制及安装阶段', '桥面系及附属施工阶段'], 'color': '#FFB74D'},
    'pavement': {'name': '路面工程', 'icon': '🏗️', 'modules': ['路面基层施工阶段', '路面面层施工阶段'], 'color': '#4CAF50'},
    'tunnel': {'name': '隧道工程', 'icon': '🚇', 'modules': ['洞口工程', '初支工程', '二衬工程', '附属工程'], 'color': '#FF9800'},
    'building': {'name': '房建工程', 'icon': '🏢', 'modules': ['基础施工阶段', '主体施工阶段', '装饰装修施工阶段', '机电安装工程'], 'color': '#F44336'},
}

class ModernCard(ttk.Frame):
    def __init__(self, parent, title="", icon="", bg_color=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.bg_color = bg_color or MODERN_COLORS['card_bg']
        self.title = title
        self.icon = icon
        self._setup_style()
        self._create_widgets()
    
    def _setup_style(self):
        style = ttk.Style()
        style.configure('ModernCard.TFrame', background=self.bg_color, relief='flat', borderwidth=0)
        style.configure('CardTitle.TLabel', background=self.bg_color, foreground=MODERN_COLORS['text_primary'], font=('Microsoft YaHei', 12, 'bold'))
        style.configure('CardContent.TFrame', background=self.bg_color)
        self.configure(style='ModernCard.TFrame')
    
    def _create_widgets(self):
        title_frame = ttk.Frame(self, style='CardContent.TFrame')
        title_frame.pack(fill='x', padx=20, pady=(15, 10))
        
        if self.icon:
            icon_label = ttk.Label(title_frame, text=self.icon, font=('Arial', 16), style='CardTitle.TLabel')
            icon_label.pack(side='left', padx=(0, 10))
        
        if self.title:
            title_label = ttk.Label(title_frame, text=self.title, style='CardTitle.TLabel')
            title_label.pack(side='left')
        
        self.content_frame = ttk.Frame(self, style='CardContent.TFrame')
        self.content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 15))
    
    def get_content_frame(self):
        return self.content_frame

class ModernToggle(ttk.Checkbutton):
    def __init__(self, parent, text="", variable=None, command=None, **kwargs):
        self.var = variable or tk.BooleanVar()
        self.command = command
        super().__init__(parent, text=text, variable=self.var, style='Modern.TCheckbutton', command=self._on_toggle, **kwargs)
    
    def _on_toggle(self):
        if self.command:
            self.command()

class ModernButton(ttk.Button):
    def __init__(self, parent, text="", command=None, style_type='primary', **kwargs):
        self.style_type = style_type
        self._setup_style()
        super().__init__(parent, text=text, command=command, style=f'Modern{style_type.capitalize()}.TButton', **kwargs)
    
    def _setup_style(self):
        style = ttk.Style()
        if self.style_type == 'primary':
            bg, fg, hover = MODERN_COLORS['primary'], 'white', MODERN_COLORS['primary']
        else:
            bg, fg, hover = MODERN_COLORS['border'], MODERN_COLORS['text_primary'], MODERN_COLORS['border']
        style.configure(f'Modern{self.style_type.capitalize()}.TButton', background=bg, foreground=fg, font=('Microsoft YaHei', 10, 'bold'), padding=10, borderwidth=0, relief='flat')
        style.map(f'Modern{self.style_type.capitalize()}.TButton', background=[('active', hover)], foreground=[('active', fg)])

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("🚧 工程劳动力计划生成器")
        self.root.geometry("1200x800")
        self.root.configure(bg=MODERN_COLORS['background'])
        
        self._setup_styles()
        self._init_variables()
        self._create_ui()
    
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Main.TFrame', background=MODERN_COLORS['background'])
        style.configure('Header.TLabel', background=MODERN_COLORS['background'], foreground=MODERN_COLORS['text_primary'], font=('Microsoft YaHei', 16, 'bold'))
        style.configure('SubHeader.TLabel', background=MODERN_COLORS['background'], foreground=MODERN_COLORS['text_secondary'], font=('Microsoft YaHei', 12))
        style.configure('Modern.TLabelframe', background=MODERN_COLORS['card_bg'], relief='flat', borderwidth=0)
        style.configure('Modern.TLabelframe.Label', background=MODERN_COLORS['card_bg'], foreground=MODERN_COLORS['text_primary'], font=('Microsoft YaHei', 11, 'bold'))
        style.configure('Modern.TRadiobutton', background=MODERN_COLORS['card_bg'], foreground=MODERN_COLORS['text_primary'], font=('Microsoft YaHei', 10))
        style.configure('Modern.TCheckbutton', background=MODERN_COLORS['card_bg'], foreground=MODERN_COLORS['text_primary'], font=('Microsoft YaHei', 10))
        style.configure('Modern.TEntry', fieldbackground=MODERN_COLORS['card_bg'], background=MODERN_COLORS['card_bg'], foreground=MODERN_COLORS['text_primary'], borderwidth=1, relief='solid')
        style.configure('Modern.TCombobox', fieldbackground=MODERN_COLORS['card_bg'], background=MODERN_COLORS['card_bg'], foreground=MODERN_COLORS['text_primary'], arrowcolor=MODERN_COLORS['text_secondary'])
        style.configure('Modern.TSpinbox', fieldbackground=MODERN_COLORS['card_bg'], background=MODERN_COLORS['card_bg'], foreground=MODERN_COLORS['text_primary'], arrowcolor=MODERN_COLORS['text_secondary'])
    
    def _init_variables(self):
        self.project_vars = {}
        for key in PROJECT_TYPES:
            self.project_vars[key] = {'enabled': tk.BooleanVar(value=False)}
        self.output_path = tk.StringVar(value=r"E:\python代码\工程劳动力计划.xlsx")
    
    def _create_ui(self):
        main = ttk.Frame(self.root, style='Main.TFrame')
        main.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 标题
        header = ttk.Frame(main, style='Main.TFrame')
        header.pack(fill='x', pady=(0, 20))
        ttk.Label(header, text="🚧 工程劳动力计划生成器", style='Header.TLabel').pack(side='left')
        ttk.Label(header, text="智能生成各类工程劳动力配置计划", style='SubHeader.TLabel').pack(side='left', padx=(20, 0))
        
        # 内容区
        content = ttk.Frame(main, style='Main.TFrame')
        content.pack(fill='both', expand=True)
        
        # 左栏
        left = ttk.Frame(content, style='Main.TFrame', width=280)
        left.pack(side='left', fill='y', padx=(0, 20))
        left.pack_propagate(False)
        self._build_left(left)
        
        # 右栏
        right = ttk.Frame(content, style='Main.TFrame')
        right.pack(side='left', fill='both', expand=True)
        self._build_right(right)
        
        # 底部（放在右栏内）
        self._build_bottom(right)
    
    def _build_left(self, parent):
        card = ModernCard(parent, title="📋 选择工程类型", bg_color=MODERN_COLORS['card_bg'])
        card.pack(fill='x', padx=(0, 10))
        
        for key, cfg in PROJECT_TYPES.items():
            row = ttk.Frame(card.get_content_frame(), style='CardContent.TFrame')
            row.pack(fill='x', pady=8)
            row.columnconfigure(1, weight=1)
            
            icon = ttk.Label(row, text=cfg['icon'], font=('Arial', 20), background=MODERN_COLORS['card_bg'])
            icon.grid(row=0, column=0, padx=(0, 15), sticky='nsw')
            
            info = ttk.Frame(row, style='CardContent.TFrame')
            info.grid(row=0, column=1, sticky='nsw')
            name = ttk.Label(info, text=cfg['name'], font=('Microsoft YaHei', 11, 'bold'), background=MODERN_COLORS['card_bg'], foreground=cfg['color'])
            name.grid(row=0, column=0, sticky='w')
            desc = ttk.Label(info, text=f"包含 {len(cfg['modules'])} 个阶段", font=('Microsoft YaHei', 9), background=MODERN_COLORS['card_bg'], foreground=MODERN_COLORS['text_secondary'])
            desc.grid(row=1, column=0, sticky='w')
            
            toggle = ModernToggle(row, text="启用", variable=self.project_vars[key]['enabled'],
                                  command=self._refresh_tabs)
            toggle.grid(row=0, column=2, sticky='nse')
    
    def _build_right(self, parent):
        self.nb = ttk.Notebook(parent)
        self.nb.pack(fill='both', expand=True)
        self._refresh_tabs()
    
    def _refresh_tabs(self):
        # 先清空所有标签
        for tab_id in self.nb.tabs():
            self.nb.forget(tab_id)
        # 只添加已启用的工程
        for key, cfg in PROJECT_TYPES.items():
            if self.project_vars[key]['enabled'].get():
                tab = ttk.Frame(self.nb, style='Main.TFrame')
                self.nb.add(tab, text=f"{cfg['icon']} {cfg['name']}")
                # 示例：默认把隧道工程内容放进去，可扩展
                if key == 'tunnel':
                    self._build_tunnel_tab(tab)
    
    def _build_tunnel_tab(self, parent):
        # 时间范围
        time_frame = ttk.LabelFrame(parent, text="⏰ 时间范围", style='Modern.TLabelframe')
        time_frame.pack(fill='x', pady=10)
        
        start_row = ttk.Frame(time_frame, style='CardContent.TFrame')
        start_row.pack(fill='x', padx=15, pady=8)
        ttk.Label(start_row, text="开始时间:", style='CardTitle.TLabel').pack(side='left', padx=(0, 15))
        ttk.Combobox(start_row, values=[2024, 2025], width=8, state="readonly", style='Modern.TCombobox').pack(side='left', padx=5)
        ttk.Label(start_row, text="年", background=MODERN_COLORS['card_bg']).pack(side='left', padx=5)
        ttk.Combobox(start_row, values=list(range(1, 13)), width=5, state="readonly", style='Modern.TCombobox').pack(side='left', padx=5)
        ttk.Label(start_row, text="月", background=MODERN_COLORS['card_bg']).pack(side='left', padx=5)
        
        end_row = ttk.Frame(time_frame, style='CardContent.TFrame')
        end_row.pack(fill='x', padx=15, pady=8)
        ttk.Label(end_row, text="结束时间:", style='CardTitle.TLabel').pack(side='left', padx=(0, 15))
        ttk.Combobox(end_row, values=[2024, 2025], width=8, state="readonly", style='Modern.TCombobox').pack(side='left', padx=5)
        ttk.Label(end_row, text="年", background=MODERN_COLORS['card_bg']).pack(side='left', padx=5)
        ttk.Combobox(end_row, values=list(range(1, 13)), width=5, state="readonly", style='Modern.TCombobox').pack(side='left', padx=5)
        ttk.Label(end_row, text="月", background=MODERN_COLORS['card_bg']).pack(side='left', padx=5)
        
        # 队伍配置
        team_frame = ttk.LabelFrame(parent, text="👥 队伍配置", style='Modern.TLabelframe')
        team_frame.pack(fill='x', pady=10)
        team_row = ttk.Frame(team_frame, style='CardContent.TFrame')
        team_row.pack(fill='x', padx=15, pady=8)
        ttk.Label(team_row, text="队伍数量:", style='CardTitle.TLabel').pack(side='left', padx=(0, 15))
        ttk.Spinbox(team_row, from_=1, to=100, width=8, style='Modern.TSpinbox').pack(side='left')
        
        # 配置模式
        mode_frame = ttk.LabelFrame(parent, text="⚙️ 配置模式", style='Modern.TLabelframe')
        mode_frame.pack(fill='x', pady=10)
        mode_row = ttk.Frame(mode_frame, style='CardContent.TFrame')
        mode_row.pack(fill='x', padx=15, pady=8)
        ttk.Radiobutton(mode_row, text="● 智能生成 (推荐)", value=True, style='Modern.TRadiobutton').pack(anchor='w', pady=5)
        ttk.Radiobutton(mode_row, text="○ 手动配置", value=False, style='Modern.TRadiobutton').pack(anchor='w', pady=5)
        
        # 工种配置
        work_frame = ttk.LabelFrame(parent, text="🔧 工种配置", style='Modern.TLabelframe')
        work_frame.pack(fill='x', pady=10)
        # 这里仅示意，可展开具体内容
    
    def _build_bottom(self, parent):
        card = ModernCard(parent, title="💾 导出设置", bg_color=MODERN_COLORS['card_bg'])
        card.pack(fill='x', pady=(10, 0))
        
        output_row = ttk.Frame(card.get_content_frame(), style='CardContent.TFrame')
        output_row.pack(fill='x', pady=10)
        ttk.Label(output_row, text="输出文件:", style='CardTitle.TLabel').pack(side='left', padx=(0, 15))
        ttk.Entry(output_row, textvariable=self.output_path, width=60, style='Modern.TEntry').pack(side='left', fill='x', expand=True)
        ModernButton(output_row, text="📁 浏览", command=lambda: None, style_type='secondary').pack(side='left', padx=(15, 0))
        
        btn_row = ttk.Frame(card.get_content_frame(), style='CardContent.TFrame')
        btn_row.pack(fill='x', pady=15)
        ModernButton(btn_row, text="🚀 生成计划", command=lambda: None, style_type='primary').pack(side='left')
        ModernButton(btn_row, text="📊 快速测试", command=lambda: None, style_type='secondary').pack(side='right', padx=(0, 10))
        ModernButton(btn_row, text="❌ 退出", command=self.root.quit, style_type='secondary').pack(side='right')

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()