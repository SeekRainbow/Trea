# Jamp智能聊天室

一个基于Python+Flask+Socket.IO开发的局域网多人聊天应用，支持文字消息、Emoji表情和特殊命令功能。

## 功能特性

### 基本功能
- 🔐 用户登录系统，支持昵称唯一性验证
- 💬 实时文本聊天和Emoji表情支持
- 📋 在线用户列表显示
- 🚪 优雅的登录和退出机制

### 特殊命令功能
- **@用户名** - 提醒特定用户
- **@电影 url** - 分享电影链接
- **@川小农 问题** - 与AI助手对话

### 技术特点
- 🎯 B/S架构，浏览器直接访问
- 🔧 使用Python虚拟环境开发
- 📱 响应式设计，支持移动设备
- 🎨 简约现代的UI界面
- 🌐 支持多服务器配置

## 技术栈

- **后端**: Python 3 + Flask + Flask-SocketIO
- **前端**: HTML5 + CSS3 + JavaScript + Font Awesome
- **通信**: WebSocket (Socket.IO)

## 快速开始

### 1. 安装依赖

确保已创建Python虚拟环境：

```bash
# 激活虚拟环境
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# 安装依赖
pip install flask flask-socketio eventlet
```

### 2. 配置服务器

编辑 `config.py` 文件，修改服务器配置列表：

```python
SERVERS = [
    {"name": "本地服务器", "url": "http://localhost:5000"},
    {"name": "测试服务器", "url": "http://127.0.0.1:5000"},
    # 可以添加更多服务器配置
]
```

### 3. 启动服务器

```bash
# 激活虚拟环境
venv\Scripts\activate  # Windows

# 运行应用
python app.py
```

服务器将在 http://localhost:5000 启动。

### 4. 访问应用

打开浏览器，访问以下地址：
- http://localhost:5000
- 或者从配置的服务器列表中选择相应地址

## 使用指南

### 登录流程
1. 输入唯一的昵称
2. 选择服务器地址
3. 点击"加入聊天室"

### 聊天功能
- **发送普通消息**：在输入框中输入文本并按Enter发送
- **使用Emoji**：点击😊按钮选择表情
- **@提醒**：输入 @用户名 提醒特定用户
- **分享电影**：输入 @电影 视频链接
- **AI对话**：输入 @川小农 你的问题

### 退出聊天室
- 点击右上角的"退出"按钮
- 或者直接关闭浏览器标签页

## 项目结构

```
Trae/
├── app.py              # 主应用文件
├── config.py           # 配置文件
├── README.md           # 项目说明
├── templates/          # HTML模板目录
│   ├── login.html      # 登录页面
│   └── chat.html       # 聊天室页面
├── static/             # 静态资源目录
│   └── css/            # CSS样式目录
│       └── style.css   # 主样式文件
└── venv/               # Python虚拟环境
```

## 开发说明

### 创建虚拟环境

```bash
python -m venv venv
```

### 安装开发依赖

```bash
venv\Scripts\activate
pip install flask flask-socketio eventlet
```

### 配置修改

- 服务器配置：在 `config.py` 中修改 `SERVERS` 列表
- 应用配置：可调整消息长度限制、用户名规则等参数

## 注意事项

1. 确保所有用户在同一个局域网内
2. 用户名必须唯一，不能重复
3. 消息长度限制为500字符
4. 服务器默认监听0.0.0.0，可在局域网内访问
5. 电影播放功能和AI对话功能可根据需要进一步扩展

## 版本信息

- 版本: 1.0.0
- 开发环境: Python 3.8+
- 兼容性: 主流现代浏览器

## License

MIT