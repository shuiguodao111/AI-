import os
from . import f00_prepare as f00

def writeTMP(content):
    try:
        with open(f00.TMP_FILE, 'a+', encoding='utf-8') as file:
            file.write(content + '\n')
        os.chmod(f00.TMP_FILE, 0o600)
    except Exception as e:
        print(f"写入临时文件失败: {e}")

def writeLOG(content):
    if not f00.LOG_USE:
        return
    
    try:
        with open(f00.LOG_FILE, 'a+', encoding='utf-8') as file:
            file.write(content + '\n')
        os.chmod(f00.LOG_FILE, 0o600)
    except Exception as e:
        print(f"写入日志失败: {e}")

def save_history(messages, file_path):
    """保存对话历史到文件"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            for msg in messages:
                role = msg['role']
                content = msg['content'].replace('\n', '\n    ')
                f.write(f"{role.capitalize()}:\n    {content}\n\n")
        print(f"对话已保存到: {file_path}")
        return True
    except Exception as e:
        print(f"保存对话失败: {e}")
        return False
