# Jamp智能聊天室配置文件

# 服务器配置列表，用户可以在登录时选择
SERVERS = [
    {"name": "本地服务器", "url": "http://localhost:5000"},
    {"name": "测试服务器", "url": "http://127.0.0.1:5000"},
    {"name": "网络服务器", "url": "http://10.23.103.139:5000"}  # 实际本地网络IP地址
]

# 应用配置
SECRET_KEY = 'dev_key_for_jamp_chatroom'
DEBUG = True

# 聊天室相关配置
MAX_MESSAGE_LENGTH = 500  # 消息最大长度
USERNAME_MIN_LENGTH = 1
USERNAME_MAX_LENGTH = 20