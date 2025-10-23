import time
from . import f00_prepare as f00
from . import config

def get_result(messages, max_retries=3):
    """获取AI结果，支持重试"""
    for attempt in range(max_retries):
        try:
            stream = f00.client.chat.completions.create(
                model=config.MODEL[config.MODEL_USE],
                messages=messages,
                temperature=config.TEMPERATURE,
                stream=True
            )
            
            result = ''
            print('\n回答:')
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    # 使用工具函数确保中文字符正确显示
                    from .f03_util import print_cn
                    print_cn(content)
                    result += content
            
            print('\n')
            return result
        
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"请求失败，{wait_time}秒后重试... ({e})")
                time.sleep(wait_time)
            else:
                print(f"请求失败: {e}")
                return "抱歉，请求处理失败，请稍后再试。"



