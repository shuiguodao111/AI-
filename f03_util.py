import os
import sys
import time
from datetime import datetime
from . import f00_prepare as f00
from . import config

def print_cn(text, chunk_size=5, delay=0.05):
    """流式输出中文字符"""
    for i in range(0, len(text), chunk_size):
        out_text = text[i:i + chunk_size]
        sys.stdout.buffer.write(out_text.encode('utf-8'))
        sys.stdout.buffer.flush()
        time.sleep(delay)
    sys.stdout.buffer.flush()

def clean_content(text):
    """清理内容中的特殊标记"""
    return text.replace(f00.TMP_SPLIT, ' ').replace(f00.TMP_END, ' ')

def check_command(new_messages):
    """检查特殊命令"""
    if not new_messages:
        print('错误: 输入内容为空!')
        return False
    
    content = new_messages[0]['content'].strip().lower()
    
    if content in ['stoptmp', 'rmtmp']:
        if os.path.exists(f00.TMP_FILE):
            os.remove(f00.TMP_FILE)
            print(f"'{f00.TMP_FILE}' 已删除")
        return False
    
    if content in ['usetmp', 'tmp']:
        with open(f00.TMP_FILE, 'a+', encoding='utf-8') as file:
            file.write('\n')
        print(f"'{f00.TMP_FILE}' 已创建")
        os.chmod(f00.TMP_FILE, 0o600)
        return False
    
    if content == 'cleantmp':
        if os.path.exists(f00.TMP_FILE):
            os.remove(f00.TMP_FILE)
        with open(f00.TMP_FILE, 'a+', encoding='utf-8') as file:
            file.write('\n')
        print(f"'{f00.TMP_FILE}' 已清理并重新创建")
        os.chmod(f00.TMP_FILE, 0o600)
        return False
    
    return True

def getTMP(user_message, assistant_message):
    """生成临时文件内容"""
    timestamp = time.time()
    human_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    current_path = os.getcwd()
    current_model = config.MODEL[config.MODEL_USE]
    
    user_content = clean_content(user_message['content'])
    assistant_content = clean_content(assistant_message['content'])
    
    return f00.TMP_SPLIT.join([
        human_time, current_path, f00.current_user,
        __file__, current_model, user_content, assistant_content
    ]) + f00.TMP_END

def print_help():
    """打印格式化的帮助信息"""
    terminal_width = get_terminal_width()
    
    print("\n" + "=" * terminal_width)
    print("AI 助手交互模式 - 帮助")
    print("=" * terminal_width)
    
    commands = [
        ("!help", "显示帮助信息"),
        ("!exit, !quit, !q", "退出交互模式"),
        ("!reset", "重置对话历史"),
        ("!save [路径]", "保存对话到文件"),
        ("!file [文件路径]", "添加文件进行分析"),
        ("!last", "显示上一条AI回复"),
        ("!clear", "清空屏幕"),
        ("!model", "显示/切换AI模型")
    ]
    
    for cmd, desc in commands:
        print(f"  {cmd.ljust(20)} {desc}")
    
    print("\n特殊命令:")
    print("  stoptmp/rmtmp - 删除临时文件")
    print("  usetmp/tmp    - 创建临时文件")
    print("  cleantmp      - 清理并重建临时文件")
    
    print("=" * terminal_width + "\n")