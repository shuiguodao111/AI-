import os
import sys
import time
from . import f00_prepare as f00
from .f01_load import loadBKG, loadTMP, loadNEW
from .f02_write import writeTMP, writeLOG, save_history
from .f03_util import print_cn, check_command, getTMP, print_help
from .f04_run import get_result

class InteractiveSession:
    def __init__(self):
        self.history = []
        self.last_response = None
        self.session_messages = []
        
        # 加载背景知识和历史记录
        self.bkg_messages = loadBKG()
        self.tmp_messages = loadTMP()
        
        # 初始化会话消息
        self.reset_session()
    
    def reset_session(self):
        """重置当前会话历史"""
        self.history = []
        self.session_messages = self.bkg_messages + self.tmp_messages
        print("\n对话历史已重置\n")
    
    def add_file(self, file_path):
        """添加文件到会话"""
        if not os.path.isfile(file_path):
            print(f"文件不存在: {file_path}")
            return False
        
        file_messages = loadNEW([file_path])
        if file_messages:
            self.history.extend(file_messages)
            self.session_messages.extend(file_messages)
            print(f"已添加文件: {file_path}")
            return True
        return False
    
    def process_input(self, user_input):
        """处理用户输入"""
        # 处理命令
        if user_input.startswith('!'):
            return self.handle_command(user_input)
        
        # 处理普通输入
        user_message = {'role': 'user', 'content': user_input}
        self.history.append(user_message)
        self.session_messages.append(user_message)
        
        # 获取AI响应
        response = get_result(self.session_messages)
        if not response:
            return True
        
        # 保存响应
        self.last_response = response
        assistant_message = {'role': 'assistant', 'content': response}
        self.history.append(assistant_message)
        self.session_messages.append(assistant_message)
        
        # 写入日志
        tmp_content = getTMP(user_message, assistant_message)
        if f00.LOG_USE:
            writeLOG(tmp_content)
        
        return True
    
    def handle_command(self, command):
        """处理交互命令"""
        cmd = command.strip().lower()
        
        if cmd == '!q':
            print("退出交互模式")
            return False
        
        if cmd == '!r':
            self.reset_session()
            return True
        
        if cmd == '!last':
            if self.last_response:
                print("\n上一条回复:")
                print_cn(self.last_response)
                print("\n")
            else:
                print("暂无历史回复")
            return True
        
        if cmd.startswith('!f '):
            file_path = command[3:].strip()
            if file_path:
                self.add_file(file_path)
            else:
                print("请指定文件路径: !f <文件路径>")
            return True
        
        if cmd.startswith('!save '):
            save_path = command[6:].strip()
            if save_path:
                success = save_history(self.history, save_path)
                if success:
                    print(f"对话已保存到: {save_path}")
            else:
                print("请指定保存路径: !save <文件路径>")
            return True
        
        if cmd == '!help':
            print_help()
            return True
        
        print(f"未知命令: {command}")
        return True
    
    def run(self):
        """运行交互会话"""
        print("\n进入交互模式 (输入 !help 查看帮助)")
        while True:
            try:
                user_input = input("\n> ").strip()
                if not user_input:
                    continue
                
                if not self.process_input(user_input):
                    break
            
            except KeyboardInterrupt:
                print("\n退出交互模式")
                break
            except Exception as e:
                print(f"处理错误: {e}")

def single_run(args):
    """单次运行模式"""
    bkg_messages = loadBKG()
    tmp_messages = loadTMP()
    new_messages = loadNEW(args)
    
    # 检查特殊命令
    if not check_command(new_messages):
        return
    
    # 组合所有消息
    all_messages = bkg_messages + tmp_messages + new_messages
    
    # 获取结果
    result = get_result(all_messages)
    if not result:
        return
    
    # 保存结果
    user_message = new_messages[0]
    assistant_message = {'role': 'assistant', 'content': result}
    tmp_content = getTMP(user_message, assistant_message)
    
    if f00.TMP_USE:
        writeTMP(tmp_content)
    
    if f00.LOG_USE:
        writeLOG(tmp_content)