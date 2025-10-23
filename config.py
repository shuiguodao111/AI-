############################
TEMPERATURE=0.3
API_URL='https://api.moonshot.cn/v1'
MODEL=[
  'kimi-latest',
  'moonshot-v1-auto',
  'moonshot-v1-8k',
  'moonshot-v1-32k',
  'moonshot-v1-128k'
  ]
MODEL_USE=0

# 交互模式配置
MAX_HISTORY = 10          # 最大对话历史记录数
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB文件大小限制

# 支持的文件类型
SUPPORTED_IMAGE_TYPES = ['.jpg', '.jpeg', '.png', '.gif']
SUPPORTED_AUDIO_TYPES = ['.mp3', '.wav', '.ogg']
SUPPORTED_TEXT_TYPES = ['.txt', '.md', '.py', '.js', '.html', '.css', '.json']
SUPPORTED_DOC_TYPES = ['.pdf', '.docx', '.xlsx', '.pptx']

# 多模态提示模板
IMAGE_PROMPT = "这是一张图片文件 '{file_name}'。请根据图片内容进行分析。"
AUDIO_PROMPT = "这是一个音频文件 '{file_name}'。请根据音频内容进行分析。"
#############################

