#!/usr/bin/env python3
import os
import sys
import time
import argparse
import textwrap
from datetime import datetime

# 全局配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 在项目根目录下创建 ai_data 文件夹
DATA_FOLDER = os.path.join(SCRIPT_DIR, 'ai_data')
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER, exist_ok=True)

# 更新文件路径
TMP_FILE = os.path.join(DATA_FOLDER, 'chat_history.txt')  # 普通文件名，非隐藏
LOG_FILE = os.path.join(DATA_FOLDER, 'chat_log.txt')      # 普通文件名，非隐藏
MODELS = ['kimi-latest', 'moonshot-v1-128k']
MODEL_INDEX = 0  # 当前使用的模型索引
TEMPERATURE = 0.3
API_URL = 'https://api.moonshot.cn/v1'
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
TERMINAL_WIDTH = 80  # 默认终端宽度

def get_terminal_width():
    """获取终端宽度"""
    try:
        import shutil
        return shutil.get_terminal_size().columns
    except:
        return TERMINAL_WIDTH

def init_openai_client():
    """初始化OpenAI客户端 - 更健壮的密钥处理"""
    try:
        # 1. 尝试从环境变量获取
        api_key = os.getenv('MOONSHOT_API_KEY')
        
        # 2. 尝试从key.txt文件获取
        if not api_key:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            key_path = os.path.join(script_dir, 'key.txt')
            if os.path.exists(key_path):
                try:
                    with open(key_path, 'r') as f:
                        api_key = f.readline().strip()
                except Exception as e:
                    print(f"读取密钥文件失败: {e}")
                    pass
        
        # 3. 如果都没有找到，提示用户
        if not api_key:
            print("错误: 未找到API密钥")
            print("请执行以下操作之一:")
            print("1. 创建key.txt文件并写入您的API密钥")
            print("2. 设置环境变量: export MOONSHOT_API_KEY='您的密钥'")
            print("3. 直接在提示符下输入您的API密钥")
            
            api_key = input("请输入API密钥: ").strip()
            if not api_key:
                print("必须提供API密钥才能继续")
                sys.exit(1)
        
        from openai import OpenAI
        return OpenAI(api_key=api_key, base_url=API_URL)
    except Exception as e:
        print(f"初始化API客户端失败: {e}")
        sys.exit(1)

def print_formatted(text, prefix="", width=None):
    """格式化输出文本，自动换行"""
    if width is None:
        width = get_terminal_width() - len(prefix)
    
    # 将文本分割成段落
    paragraphs = text.split('\n\n')
    
    for para in paragraphs:
        # 处理每个段落内的换行
        lines = []
        for line in para.split('\n'):
            if line.strip():
                wrapped = textwrap.wrap(line, width=width)
                lines.extend(wrapped)
            else:
                lines.append("")
        
        # 打印带前缀的段落
        for i, line in enumerate(lines):
            if i == 0:
                print(f"{prefix}{line}")
            else:
                print(f"{' ' * len(prefix)}{line}")
        
        # 段落间空行
        print()

def process_file(file_path, client):
    """处理文件内容 - 更友好的错误处理"""
    try:
        if not os.path.isfile(file_path):
            return f"文件不存在: {file_path}"
        
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            return f"文件过大 ({file_size/1024/1024:.2f}MB)，最大支持{MAX_FILE_SIZE/1024/1024}MB"
        
        ext = os.path.splitext(file_path)[1].lower()
        
        # PDF处理
        if ext == '.pdf':
            from pathlib import Path
            file_obj = client.files.create(file=Path(file_path), purpose="file-extract")
            try:
                content = client.files.retrieve_content(file_id=file_obj.id)
            except:
                content = client.files.content(file_id=file_obj.id).text
            client.files.delete(file_id=file_obj.id)
            return f"PDF文件内容: {content}"
        
        # 文本文件处理
        elif ext in ['.txt', '.py', '.md', '.json', '.html', '.csv']:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return f"文件内容:\n{content}"
        
        # 图片和音频处理
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.mp3', '.wav', '.ogg']:
            return f"已添加{ext.upper()[1:]}文件: {os.path.basename(file_path)}"
        
        else:
            return f"不支持的文件类型: {ext}"
    except Exception as e:
        return f"处理文件时出错: {str(e)}"

def get_chat_response(client, messages):
    """获取AI响应 - 添加重试机制"""
    global MODEL_INDEX  # 声明使用全局变量
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            stream = client.chat.completions.create(
                model=MODELS[MODEL_INDEX],
                messages=messages,
                temperature=TEMPERATURE,
                stream=True
            )
            
            full_response = ""
            print("\n" + "=" * get_terminal_width())
            print("AI 回答:")
            print("=" * get_terminal_width())
            
            # 流式接收响应
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end='', flush=True)
                    full_response += content
            
            print("\n" + "=" * get_terminal_width())
            return full_response
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"\n请求失败，{wait_time}秒后重试... ({str(e)})")
                time.sleep(wait_time)
            else:
                print(f"\n最终请求失败: {str(e)}")
                return "抱歉，处理您的请求时出现问题。"

def save_history(messages, file_path):
    """保存对话历史 - 添加错误处理"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            for msg in messages:
                role = msg['role'].upper()
                content = msg['content']
                f.write(f"{role}:\n")
                # 使用textwrap.fill处理内容
                wrapped_content = textwrap.fill(content, width=80)
                f.write(wrapped_content)
                f.write("\n\n")  # 注意这里：两个换行符，表示段落结束
        print(f"对话已保存到: {file_path}")
        return True
    except Exception as e:
        print(f"保存失败: {e}")
        return False

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
    print("  stoptmp/rmtmp - 删除临时文件 (位于 ai_data/ 文件夹)")
    print("  usetmp/tmp    - 创建临时文件 (位于 ai_data/ 文件夹)")
    print("  cleantmp      - 清理并重建临时文件 (位于 ai_data/ 文件夹)")
    
    
    print("=" * terminal_width + "\n")

def interactive_mode(client):
    """交互模式主函数 - 优化输出格式"""
    global MODEL_INDEX  # 声明使用全局变量
    
    messages = []
    
    # 加载背景知识
    script_dir = os.path.dirname(os.path.abspath(__file__))
    bkg_path = os.path.join(script_dir, 'bkg.txt')
    if os.path.exists(bkg_path):
        try:
            with open(bkg_path, 'r', encoding='utf-8') as f:
                bkg_content = f.read()
            messages.append({"role": "system", "content": bkg_content})
            print("已加载背景知识")
        except Exception as e:
            print(f"加载背景知识失败: {e}")
    
    # 加载历史记录
    if os.path.exists(TMP_FILE):
        try:
            with open(TMP_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        parts = line.split('|')
                        if len(parts) >= 2:
                            role = parts[0].strip()
                            content = parts[1].strip()
                            messages.append({"role": role, "content": content})
            print(f"已加载{len(messages)}条历史记录")
        except Exception as e:
            print(f"加载历史记录失败: {e}")
    
    terminal_width = get_terminal_width()
    print("\n" + "=" * terminal_width)
    print("AI 助手交互模式")
    print("输入 '!help' 查看帮助, '!exit' 退出")
    print("=" * terminal_width + "\n")
    
    last_response = None
    
    while True:
        try:
            user_input = input("> ").strip()
           
            # 添加特殊命令处理 (stoptmp, usetmp, cleantmp)
            if user_input.lower() in ['stoptmp', 'rmtmp']:
                if os.path.exists(TMP_FILE):
                    os.remove(TMP_FILE)
                    print(f"临时文件已删除: {os.path.abspath(TMP_FILE)}")
                else:
                    print(f"临时文件不存在: {os.path.abspath(TMP_FILE)}")
                continue

            if user_input.lower() in ['usetmp', 'tmp']:
                try:
                    # 确保目录存在
                    os.makedirs(os.path.dirname(TMP_FILE), exist_ok=True)
                    with open(TMP_FILE, 'a+', encoding='utf-8') as file:
                        file.write('\n')
                    print(f"临时文件已创建在: {os.path.abspath(TMP_FILE)}")
                except Exception as e:
                    print(f"创建失败: {e}")
                continue

            if user_input.lower() == 'cleantmp': # type: ignore
                try:
                    if os.path.exists(TMP_FILE):
                        os.remove(TMP_FILE)
                     # 确保目录存在
                    os.makedirs(os.path.dirname(TMP_FILE), exist_ok=True)
                    with open(TMP_FILE, 'a+', encoding='utf-8') as file:
                        file.write('\n')
                    print(f"临时文件已清理并重新创建: {os.path.abspath(TMP_FILE)}")
                except Exception as e:
                    print(f"清理失败: {e}")
                continue
            
            # 处理空输入
            if not user_input:
                continue
                
            # 退出命令
            if user_input.lower() in ['!exit', '!quit', '!q']:
                print("退出交互模式")
                break
                
            # 帮助命令
            if user_input.lower() == '!help':
                print_help()
                continue
                
            # 模型切换
            if user_input.lower() == '!model':
                print("\n可用模型:")
                for i, model in enumerate(MODELS):
                    prefix = "→ " if i == MODEL_INDEX else "  "
                    print(f"{prefix}{i+1}. {model}")
                
                try:
                    choice = input("\n输入模型编号切换 (按Enter取消): ").strip()
                    if choice:
                        new_index = int(choice) - 1
                        if 0 <= new_index < len(MODELS):
                            MODEL_INDEX = new_index
                            print(f"已切换到模型: {MODELS[MODEL_INDEX]}")
                        else:
                            print("无效的模型编号")
                except:
                    print("无效输入")
                continue
                
            # 重置对话
            if user_input.lower() == '!reset':
                messages = []
                print("\n对话已重置\n")
                continue
                
            # 保存对话
            if user_input.lower().startswith('!save'):
                parts = user_input.split(maxsplit=1)
                save_path = parts[1] if len(parts) > 1 else "ai_chat_history.txt"
                if save_history(messages, save_path):
                    # 同时更新历史文件
                    with open(TMP_FILE, 'w', encoding='utf-8') as f:
                        for msg in messages:
                            f.write(f"{msg['role']}|{msg['content']}\n")
                continue
                
            # 添加文件
            if user_input.lower().startswith('!file'):
                parts = user_input.split(maxsplit=1)
                if len(parts) < 2:
                    print("请指定文件路径: !file [文件路径]")
                    continue
                    
                file_path = parts[1].strip()
                file_content = process_file(file_path, client)
                
                # 格式化文件内容提示
                file_prompt = f"请分析以下内容: {file_content}"
                messages.append({"role": "user", "content": file_prompt})
                print(f"\n已添加文件: {file_path}")
                
                # 获取AI响应
                response = get_chat_response(client, messages)
                if response:
                    messages.append({"role": "assistant", "content": response})
                    last_response = response
                
                # 保存到历史
                with open(TMP_FILE, 'a', encoding='utf-8') as f:
                    f.write(f"user|分析文件: {file_path}\n")
                    if response:
                        f.write(f"assistant|{response}\n")
                continue
                
            # 显示上一条回复
            if user_input.lower() == '!last':
                if last_response:
                    print("\n" + "=" * terminal_width)
                    print("上一条AI回复:")
                    print("=" * terminal_width)
                    print_formatted(last_response, prefix="  ")
                    print("=" * terminal_width + "\n")
                else:
                    print("没有上一条回复")
                continue
                
            # 清屏
            if user_input.lower() == '!clear':
                os.system('clear' if os.name == 'posix' else 'cls')
                continue
                
            # 普通用户输入
            user_message = {"role": "user", "content": user_input}
            messages.append(user_message)
            
            # 获取AI响应
            response = get_chat_response(client, messages)
            if response:
                messages.append({"role": "assistant", "content": response})
                last_response = response
            
            # 保存到历史
            with open(TMP_FILE, 'a', encoding='utf-8') as f:
                f.write(f"user|{user_input}\n")
                if response:
                    f.write(f"assistant|{response}\n")
                    
        except KeyboardInterrupt:
            print("\n输入 '!exit' 退出")
        except Exception as e:
            print(f"\n处理错误: {e}")

def main():
    """主函数 - 添加参数处理"""
    global MODEL_INDEX  # 声明使用全局变量
    
    parser = argparse.ArgumentParser(description='AI命令行助手', 
                                    formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-i', '--interactive', action='store_true', help='进入交互模式')
    parser.add_argument('input', nargs='*', help='输入内容或文件路径')
    
    help_text = """
使用示例:
  单次查询: 
    python3 ai.py "你的问题"
    python3 ai.py document.pdf
  
  交互模式:
    python3 ai.py -i
    
  交互模式命令:
    !help    - 显示帮助信息
    !file    - 添加文件分析
    !save    - 保存对话
    !exit    - 退出交互模式
    """
    parser.epilog = help_text
    
    args = parser.parse_args()
    
    client = init_openai_client()
    
    if args.interactive:
        interactive_mode(client)
    else:
        if not args.input:
            print("请提供输入内容或文件路径")
            parser.print_help()
            return
            
        # 处理输入
        user_input = " ".join(args.input)
        
        # 如果是文件
        if os.path.isfile(user_input):
            file_content = process_file(user_input, client)
            user_message = {"role": "user", "content": f"请分析以下内容: {file_content}"}
        else:
            user_message = {"role": "user", "content": user_input}
        
        # 获取响应
        response = get_chat_response(client, [user_message])
        
        # 保存到日志
        if response:
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"[{timestamp}] USER: {user_message['content']}\n")
                f.write(f"[{timestamp}] AI: {response}\n\n")

if __name__ == "__main__":
    # 确保全局变量在函数中可修改
    MODEL_INDEX = 0
    main()