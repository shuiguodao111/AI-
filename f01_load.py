import os
import mimetypes
from . import f00_prepare as f00
from . import config
from pathlib import Path
import base64

def loadBKG():
    bkg_messages = []
    if f00.BKG_USE:
        try:
            if os.path.exists(f00.BKG_FILE):
                with open(f00.BKG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                    bkg_contents = f.read().split(f00.BKG_SPLIT)
                
                for content in bkg_contents:
                    if content.strip():
                        bkg_messages.append({'role': 'system', 'content': content})
        except Exception as e:
            print(f"加载背景知识失败: {e}")
    return bkg_messages

def loadTMP():
    tmp_messages = []
    if f00.TMP_USE and os.path.isfile(f00.TMP_FILE):
        try:
            with open(f00.TMP_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                all_tmp = f.read()
            
            for line in all_tmp.rstrip().split(f00.TMP_END):
                parts = line.strip().split(f00.TMP_SPLIT)
                if len(parts) >= 2:
                    user_msg = {'role': 'user', 'content': parts[-2]}
                    assistant_msg = {'role': 'assistant', 'content': parts[-1]}
                    tmp_messages.append(user_msg)
                    tmp_messages.append(assistant_msg)
        except Exception as e:
            print(f"加载临时文件失败: {e}")
    return tmp_messages

def process_file(file_path):
    """处理单个文件并返回消息内容"""
    if not os.path.isfile(file_path):
        return f"文件不存在: {file_path}"
    
    # 检查文件大小
    file_size = os.path.getsize(file_path)
    if file_size > config.MAX_FILE_SIZE:
        return f"文件过大 ({file_size/1024/1024:.2f}MB > {config.MAX_FILE_SIZE/1024/1024}MB)，跳过处理"
    
    # 获取文件扩展名
    ext = os.path.splitext(file_path)[1].lower()
    
    # 图片处理
    if ext in config.SUPPORTED_IMAGE_TYPES:
        return config.IMAGE_PROMPT.format(file_name=os.path.basename(file_path))
    
    # 音频处理
    elif ext in config.SUPPORTED_AUDIO_TYPES:
        return config.AUDIO_PROMPT.format(file_name=os.path.basename(file_path))
    
    # PDF处理（使用Moonshot API）
    elif ext == '.pdf':
        return process_pdf(file_path)
    
    # 文本文件处理
    elif ext in config.SUPPORTED_TEXT_TYPES + config.SUPPORTED_DOC_TYPES:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return (f"文件 '{os.path.basename(file_path)}' 内容:\n"
                    f"{content}\n"
                    f"# 文件内容结束")
        except Exception as e:
            return f"读取文件失败: {e}"
    
    else:
        return f"不支持的文件类型: {ext}"

def process_pdf(file_path):
    """使用API处理PDF文件"""
    try:
        file_object = f00.client.files.create(
            file=Path(file_path), 
            purpose="file-extract"
        )
        
        try:
            file_content = f00.client.files.retrieve_content(file_id=file_object.id)
        except:
            file_content = f00.client.files.content(file_id=file_object.id).text
        
        f00.client.files.delete(file_id=file_object.id)
        
        # 保存提取内容（可选）
        try:
            with open(f"{file_path}.content.txt", 'w') as f:
                f.write(file_content)
        except:
            pass
        
        return (f"PDF文件 '{os.path.basename(file_path)}' 提取内容:\n"
                f"{file_content}\n"
                f"# PDF内容结束")
    except Exception as e:
        return f"处理PDF失败: {e}"

def loadNEW(args):
    """处理新的用户输入"""
    new_messages = []
    
    for arg in args:
        # 处理文件
        if os.path.isfile(arg):
            file_content = process_file(arg)
            new_messages.append({'role': 'user', 'content': file_content})
        # 处理文本输入
        else:
            new_messages.append({'role': 'user', 'content': arg})
    
    return new_messages



