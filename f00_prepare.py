import os, sys, time
from datetime import datetime
from openai import OpenAI
import config

# 初始化全局变量
def init_globals():
    global KEY_FILE, BKG_USE, BKG_FILE, BKG_SPLIT
    global TMP_USE, TMP_SPLIT, TMP_END, TMP_FILE
    global LOG_USE, LOG_FILE, client, current_user
    
    pyfile_name = os.path.basename(__file__)
    pyfile_path = os.path.dirname(os.path.abspath(__file__))
    
    # 密钥文件
    KEY_FILE = os.path.join(pyfile_path, 'key.txt')
    
    # 背景知识配置
    BKG_USE = True
    BKG_FILE = os.path.join(pyfile_path, 'bkg.txt')
    BKG_SPLIT = '#---FILE_SPLIT---'
    
    # 临时文件配置
    TMP_USE = False
    TMP_SPLIT = '\n_|_SPLIT_|_\n'
    TMP_END = '\n_|_END_|_\n'
    
    # 获取当前用户
    try:
        import getpass
        current_user = getpass.getuser()
    except Exception:
        try:
            current_user = os.getlogin()
        except Exception:
            current_user = str(os.getuid())
    
    TMP_FILE = f'.tmp_ai_{current_user}.txt'
    if os.path.exists(TMP_FILE):
        TMP_USE = True
    
    # 日志配置
    LOG_USE = True
    HOME_PATH = os.path.expanduser('~')
    LOG_FOLDER = HOME_PATH
    if not os.path.exists(LOG_FOLDER) and LOG_USE:
        os.makedirs(LOG_FOLDER, exist_ok=True)
        os.chmod(LOG_FOLDER, 0o700)
    
    LOG_FILE = os.path.join(LOG_FOLDER, f'.log_ai_{current_user}.txt')
    
    # 创建客户端
    try:
        api_key = open(KEY_FILE).readline().rstrip()
        client = OpenAI(api_key=api_key, base_url=config.API_URL)
    except Exception as e:
        print(f"初始化API客户端失败: {e}")
        sys.exit(1)

# 初始化全局变量
init_globals()




