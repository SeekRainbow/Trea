from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import config
import re
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY

# 配置Socket.IO
socketio = SocketIO(app, cors_allowed_origins="*")

# 全局变量管理
users = {}  # 存储在线用户 {session_id: username}
room = "general"  # 默认聊天室

# 机器人用户配置
BOT_USERNAME = "川小农"
BOT_SESSION_ID = "bot_chuanxiaonong"  # 特殊的机器人会话ID

# 电影用户配置
MOVIE_USERNAME = "电影"
MOVIE_SESSION_ID = "bot_movie"  # 特殊的电影用户会话ID

# 路由定义
@app.route('/')
def index():
    """登录页面"""
    return render_template('login.html', servers=config.SERVERS)

@app.route('/chat')
def chat():
    """聊天室页面"""
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "用户名不能为空"}), 400
    return render_template('chat.html', username=username)

@app.route('/api/validate_username', methods=['POST'])
def validate_username():
    """验证用户名是否可用"""
    data = request.get_json()
    username = data.get('username')
    
    # 检查是否是机器人用户名
    if username == BOT_USERNAME:
        return jsonify({"valid": False, "message": "该用户名是系统机器人，不可使用"})
    
    # 检查用户名是否已经存在
    if username in users.values():
        return jsonify({"valid": False, "message": "用户名已被使用"})
    
    # 检查用户名长度
    if len(username) < config.USERNAME_MIN_LENGTH or len(username) > config.USERNAME_MAX_LENGTH:
        return jsonify({"valid": False, "message": f"用户名长度应在{config.USERNAME_MIN_LENGTH}-{config.USERNAME_MAX_LENGTH}个字符之间"})
    
    return jsonify({"valid": True})

# Socket.IO事件处理
@socketio.on('connect')
def handle_connect():
    """处理客户端连接"""
    print(f"客户端连接: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """处理客户端断开连接"""
    if request.sid in users and request.sid != BOT_SESSION_ID and request.sid != MOVIE_SESSION_ID:  # 不处理机器人用户和电影用户的断开连接
        username = users[request.sid]
        del users[request.sid]
        # 通知其他用户有用户离开
        emit('user_left', {
            'username': username,
            'timestamp': get_current_timestamp(),
            'online_users': get_online_users()
        }, room=room)
        print(f"用户离开: {username}")

@socketio.on('join')
def handle_join(data):
    """处理用户加入聊天室"""
    username = data.get('username')
    if not username:
        return
    
    # 保存用户信息
    users[request.sid] = username
    join_room(room)
    
    # 通知所有用户有新用户加入
    emit('user_joined', {
        'username': username,
        'timestamp': get_current_timestamp(),
        'online_users': get_online_users()
    }, room=room)
    
    # 发送欢迎消息给新用户
    emit('welcome_message', {
        'message': f"欢迎 {username} 加入聊天室！",
        'timestamp': get_current_timestamp(),
        'online_users': get_online_users()
    }, to=request.sid)
    
    # 机器人自动发送欢迎消息（仅新用户可见）
    socketio.sleep(1)  # 延迟1秒发送
    emit('new_message', {
        'username': BOT_USERNAME,
        'message': f"你好 {username}！我是AI助手川小农，有什么可以帮助你的吗？",
        'timestamp': get_current_timestamp(),
        'is_ai': True
    }, to=request.sid)
    
    print(f"用户加入: {username}, 在线用户: {list(users.values())}")

@socketio.on('send_message')
def handle_message(data):
    """处理用户发送的消息"""
    username = users.get(request.sid)
    if not username:
        return
    
    message = data.get('message', '').strip()
    if not message or len(message) > config.MAX_MESSAGE_LENGTH:
        return
    
    # 处理@用户功能
    mentioned_users = []
    if '@' in message:
        # 简单的@用户检测，查找@后跟非空格字符的模式
        import re
        mentions = re.findall(r'@(\S+)', message)
        mentioned_users = [mention for mention in mentions if mention in get_online_users()]
        
        # 检查是否@了机器人
        if BOT_USERNAME in mentions:
            # 延迟回复@消息
            socketio.sleep(1)
            bot_responses = [
                f"{username}，有什么我可以帮到你的吗？",
                f"你好 {username}，很高兴收到你的消息！",
                f"我是川小农，随时为你服务 {username}！",
                f"收到你的@啦 {username}，需要什么帮助吗？"
            ]
            import random
            bot_response = random.choice(bot_responses)
            
            # 发送机器人回复
            emit('new_message', {
                'username': BOT_USERNAME,
                'message': bot_response,
                'timestamp': get_current_timestamp(),
                'is_ai': True
            }, room=room)
    
    # 检查是否是特殊命令（以@开头的命令）
    if message.startswith('@'):
        handle_special_command(username, message, get_current_timestamp(), room)
    else:
        # 构建消息数据
        message_data = {
            'username': username,
            'message': message,
            'timestamp': get_current_timestamp(),
            'mentioned_users': mentioned_users
        }
        
        # 广播消息给所有用户
        emit('new_message', message_data, room=room)

@socketio.on('leave')
def handle_leave():
    """处理用户主动离开聊天室"""
    if request.sid in users:
        username = users[request.sid]
        del users[request.sid]
        leave_room(room)
        # 通知其他用户有用户离开
        emit('user_left', {
            'username': username,
            'timestamp': get_current_timestamp(),
            'online_users': list(users.values())
        }, room=room)
        print(f"用户主动离开: {username}")

# 特殊命令处理
def handle_special_command(username, message, timestamp, room):
    """处理@xxx特殊命令"""
    # 解析命令格式: @命令名 参数
    match = re.match(r'@(.+?)(\s+.*)?$', message)
    if not match:
        return
    
    command = match.group(1).strip()
    params = match.group(2) if match.group(2) else ''
    params = params.strip()
    # 添加调试日志
    print(f"处理特殊命令: {command}, 参数: {params}")
    # 移除参数中可能包含的反引号
    params = params.replace('`', '')
    print(f"清理后的参数: {params}")
    
    # 根据不同命令进行处理
    if command == '电影':
        handle_movie_command(username, params, timestamp, room)
    elif command == '川小农':
        handle_ai_command(username, params, timestamp)
    else:
        # 检查是否是@用户提醒
        if command in users.values():
            # 发送@提醒消息
            emit('new_message', {
                'username': username,
                'message': message,
                'timestamp': timestamp,
                'is_mention': True,
                'mention_target': command
            }, room=room)
        else:
            # 未知命令，当作普通消息处理
            emit('new_message', {
                'username': username,
                'message': message,
                'timestamp': timestamp
            }, room=room)

def handle_movie_command(username, url, timestamp, room):
    """处理@电影命令，支持解析电影地址并播放"""
    # 添加调试日志
    print(f"处理@电影命令: 用户={username}, URL完整长度={len(url)}, URL内容: '{url}'")
    
    if not url:
        response = "请提供电影链接，格式: @电影 url"
        final_url = ""
    else:
        # 确保URL中没有反引号
        url = url.replace('`', '')
        print(f"清理后的URL完整内容: '{url}'")
        
        # 验证URL格式 - 更宽松的验证，适应各种链接格式
        import re
        url_pattern = r'^(https?://|www\.)\S+$'
        is_valid_url = re.match(url_pattern, url)
        print(f"URL验证结果: {is_valid_url is not None}")
        
        # 使用指定的解析地址模板处理URL
        import urllib.parse
        # 确保完整编码URL，包括查询参数
        parsed_url = urllib.parse.quote(url, safe='')
        # 严格使用要求的解析地址
        parsed_movie_url = f"https://jx.m3u8.tv/jiexi/?url={parsed_url}"
        print(f"解析后的电影URL完整内容: '{parsed_movie_url}'")
        
        # 根据URL验证结果设置不同的响应消息
        if is_valid_url:
            response = f"[{username} 分享了一个电影链接]"
        else:
            response = f"[{username} 分享了一个电影链接(请检查链接格式)]"
        
        # 设置最终的电影URL
        final_url = parsed_movie_url
    
    emit('new_message', {
        'username': '系统',
        'message': response,
        'timestamp': timestamp,
        'is_system': True,
        'is_movie': True,
        'movie_url': final_url if final_url else ''
    }, room=room)

def handle_ai_command(username, question, timestamp):
    """处理@川小农命令"""
    if not question:
        response = "请输入您想咨询的问题，格式: @川小农 问题"
    else:
        # 模拟AI回复 - 实际项目中可以接入真实的AI模型
        # 简单的示例回复
        sample_responses = [
            "您好！我是川小农，很高兴为您服务。",
            "这个问题很有趣，让我思考一下...",
            "感谢您的提问，我会尽力为您解答。",
            "根据我的了解，您可以尝试..."
        ]
        import random
        response = f"[{username} 的AI助手回复] {random.choice(sample_responses)}"
    
    emit('new_message', {
        'username': '川小农',
        'message': response,
        'timestamp': timestamp,
        'is_ai': True
    }, room=room)

def get_current_timestamp():
    """获取当前时间戳，格式为 HH:MM:SS"""
    return time.strftime('%H:%M:%S')

def get_online_users():
    """获取在线用户列表，包含机器人用户和电影用户"""
    # 获取所有真实用户
    real_users = list(users.values())
    # 确保机器人用户始终在列表中
    if BOT_USERNAME not in real_users:
        real_users = [BOT_USERNAME] + real_users
    # 确保电影用户始终在列表中
    if MOVIE_USERNAME not in real_users:
        real_users = [MOVIE_USERNAME] + real_users
    return real_users

# 在应用启动时初始化机器人用户
def initialize_bot():
    """初始化机器人用户和电影用户"""
    global users
    # 添加机器人用户到用户列表
    users[BOT_SESSION_ID] = BOT_USERNAME
    # 添加电影用户到用户列表
    users[MOVIE_SESSION_ID] = MOVIE_USERNAME
    print(f"机器人用户 '{BOT_USERNAME}' 已初始化")
    print(f"电影用户 '{MOVIE_USERNAME}' 已初始化")

if __name__ == '__main__':
    print("Jamp智能聊天室启动中...")
    print("服务器地址:")
    for server in config.SERVERS:
        print(f"- {server['name']}: {server['url']}")
    
    # 初始化机器人用户
    initialize_bot()
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=config.DEBUG)