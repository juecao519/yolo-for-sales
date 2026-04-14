#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能饮料贩卖机GUI启动器
废弃了，我用的final
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

class GUILauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("智能饮料贩卖机 - GUI启动器")
        self.root.geometry("500x400")
        self.root.configure(bg='#f0f0f0')
        self.root.resizable(False, False)
        
        # 创建界面
        self.create_widgets()
    
    def create_widgets(self):
        """创建界面组件"""
        # 主标题
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        title_frame.pack(fill='x', padx=20, pady=20)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="🤖 智能饮料贩卖机系统", 
                              font=('Arial', 18, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(expand=True)
        
        subtitle_label = tk.Label(title_frame, text="请选择要启动的界面", 
                                 font=('Arial', 12), fg='#ecf0f1', bg='#2c3e50')
        subtitle_label.pack()
        
        # 主容器
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 界面选择区域
        selection_frame = tk.LabelFrame(main_frame, text="界面选择", 
                                       font=('Arial', 12, 'bold'), 
                                       bg='white', padx=20, pady=20)
        selection_frame.pack(fill='both', expand=True)
        
        # 完整版GUI选项
        full_gui_frame = tk.Frame(selection_frame, bg='white')
        full_gui_frame.pack(fill='x', pady=10)
        
        full_gui_label = tk.Label(full_gui_frame, 
                                 text="📱 完整版GUI界面", 
                                 font=('Arial', 14, 'bold'), 
                                 bg='white', fg='#2c3e50')
        full_gui_label.pack(anchor='w')
        
        full_gui_desc = tk.Label(full_gui_frame, 
                                text="• 包含图片预览功能\n• 需要PIL库支持\n• 界面更美观", 
                                font=('Arial', 10), 
                                bg='white', fg='#7f8c8d', 
                                justify='left')
        full_gui_desc.pack(anchor='w', pady=(5, 10))
        
        full_gui_btn = tk.Button(full_gui_frame, 
                                text="启动完整版GUI", 
                                command=self.start_full_gui,
                                bg='#3498db', fg='white', 
                                font=('Arial', 12, 'bold'),
                                relief='flat', padx=30, pady=10)
        full_gui_btn.pack(anchor='w')
        
        # 分隔线
        separator = tk.Frame(selection_frame, height=2, bg='#ecf0f1')
        separator.pack(fill='x', pady=20)
        
        # 简化版GUI选项
        simple_gui_frame = tk.Frame(selection_frame, bg='white')
        simple_gui_frame.pack(fill='x', pady=10)
        
        simple_gui_label = tk.Label(simple_gui_frame, 
                                   text="💻 简化版GUI界面", 
                                   font=('Arial', 14, 'bold'), 
                                   bg='white', fg='#2c3e50')
        simple_gui_label.pack(anchor='w')
        
        simple_gui_desc = tk.Label(simple_gui_frame, 
                                  text="• 基础功能完整\n• 无需额外依赖\n• 兼容性更好", 
                                  font=('Arial', 10), 
                                  bg='white', fg='#7f8c8d', 
                                  justify='left')
        simple_gui_desc.pack(anchor='w', pady=(5, 10))
        
        simple_gui_btn = tk.Button(simple_gui_frame, 
                                  text="启动简化版GUI", 
                                  command=self.start_simple_gui,
                                  bg='#27ae60', fg='white', 
                                  font=('Arial', 12, 'bold'),
                                  relief='flat', padx=30, pady=10)
        simple_gui_btn.pack(anchor='w')
        
        # 底部按钮
        bottom_frame = tk.Frame(main_frame, bg='#f0f0f0')
        bottom_frame.pack(fill='x', pady=(20, 0))
        
        exit_btn = tk.Button(bottom_frame, 
                            text="退出", 
                            command=self.root.quit,
                            bg='#e74c3c', fg='white', 
                            font=('Arial', 10),
                            relief='flat', padx=20, pady=5)
        exit_btn.pack(side='right')
    
    def start_full_gui(self):
        """启动完整版GUI"""
        try:
            # 检查PIL库
            try:
                import PIL
                print("✅ PIL库已安装")
            except ImportError:
                result = messagebox.askyesno("依赖缺失", 
                                           "完整版GUI需要PIL库，是否现在安装？\n\n"
                                           "点击'是'将尝试安装PIL库\n"
                                           "点击'否'将启动简化版GUI")
                if result:
                    self.install_pil()
                    return
                else:
                    self.start_simple_gui()
                    return
            
            # 检查文件是否存在
            if not os.path.exists("gui_vending_machine.py"):
                messagebox.showerror("错误", "找不到完整版GUI文件: gui_vending_machine.py")
                return
            
            # 启动完整版GUI
            self.root.withdraw()  # 隐藏启动器窗口
            subprocess.run([sys.executable, "gui_vending_machine.py"])
            self.root.deiconify()  # 显示启动器窗口
            
        except Exception as e:
            messagebox.showerror("错误", f"启动完整版GUI失败: {str(e)}")
    
    def start_simple_gui(self):
        """启动简化版GUI"""
        try:
            # 检查文件是否存在
            if not os.path.exists("simple_gui_vending_machine.py"):
                messagebox.showerror("错误", "找不到简化版GUI文件: simple_gui_vending_machine.py")
                return
            
            # 启动简化版GUI
            self.root.withdraw()  # 隐藏启动器窗口
            subprocess.run([sys.executable, "simple_gui_vending_machine.py"])
            self.root.deiconify()  # 显示启动器窗口
            
        except Exception as e:
            messagebox.showerror("错误", f"启动简化版GUI失败: {str(e)}")
    
    def install_pil(self):
        """安装PIL库"""
        try:
            messagebox.showinfo("安装", "正在安装PIL库，请稍候...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
            messagebox.showinfo("成功", "PIL库安装成功！现在可以启动完整版GUI了。")
        except Exception as e:
            messagebox.showerror("安装失败", f"PIL库安装失败: {str(e)}\n\n请手动运行: pip install pillow")

def main():
    """主函数"""
    root = tk.Tk()
    app = GUILauncher(root)
    root.mainloop()

if __name__ == "__main__":
    main() 