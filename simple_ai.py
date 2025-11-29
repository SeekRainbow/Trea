import random
import re
from datetime import datetime

class SimpleChatAI:
    """简单的聊天AI类，模拟智能对话回复"""
    
    def __init__(self, name="川小农"):
        self.name = name
        self.context_history = []  # 简单的上下文历史
        self.max_history = 5  # 保存最近5条对话
        self.greetings = [
            "你好！很高兴见到你，我是{name}，有什么可以帮助你的吗？",
            "嗨！我是{name}，随时为你服务。",
            "你好呀！我是{name}，今天有什么可以帮到你的？"
        ]
        self.farewells = [
            "再见！祝你有美好的一天！",
            "拜拜！有需要随时找我哦！",
            "下次再聊！我一直在这儿等你！"
        ]
        self.thanks_responses = [
            "不客气！能帮到你我很开心。",
            "不用谢，这是我应该做的。",
            "没关系的，有需要随时告诉我！"
        ]
        self.weather_keywords = ["天气", "气温", "下雨", "晴天", "冷", "热"]
        self.time_keywords = ["时间", "几点", "日期", "今天"]
        self.chatbot_keywords = ["你是谁", "你叫什么", "你是什么", "介绍你自己"]
        self.help_keywords = ["帮助", "怎么用", "功能", "指南"]
    
    def add_to_history(self, user_message, ai_response):
        """添加对话到历史记录"""
        self.context_history.append((user_message, ai_response))
        # 保持历史记录不超过最大长度
        if len(self.context_history) > self.max_history:
            self.context_history.pop(0)
    
    def get_response(self, user_message, username="用户"):
        """根据用户消息生成回复"""
        user_message = user_message.strip()
        
        # 转换为小写以便于关键词匹配
        message_lower = user_message.lower()
        
        # 检测关键词并生成相应回复
        response = None
        
        # 检测问候语
        if self._contains_any(message_lower, ["你好", "嗨", "哈喽", "早上好", "晚上好", "中午好"]):
            response = random.choice(self.greetings).format(name=self.name)
        # 检测告别语
        elif self._contains_any(message_lower, ["再见", "拜拜", "88", "下次见"]):
            response = random.choice(self.farewells)
        # 检测感谢
        elif self._contains_any(message_lower, ["谢谢", "感谢", "谢了"]):
            response = random.choice(self.thanks_responses)
        # 检测天气相关
        elif self._contains_any(message_lower, self.weather_keywords):
            response = self._generate_weather_response()
        # 检测时间相关
        elif self._contains_any(message_lower, self.time_keywords):
            response = self._generate_time_response()
        # 检测关于聊天机器人自身的问题
        elif self._contains_any(message_lower, self.chatbot_keywords):
            response = self._generate_about_response()
        # 检测帮助请求
        elif self._contains_any(message_lower, self.help_keywords):
            response = self._generate_help_response()
        # 检测电影相关
        elif self._contains_any(message_lower, ["电影", "影视", "推荐电影"]):
            response = self._generate_movie_response()
        # 检测聊天相关
        elif self._contains_any(message_lower, ["聊天", "聊聊", "说说话"]):
            response = self._generate_chat_response(username)
        # 检测问题包含问号
        elif '?' in user_message or '？' in user_message:
            response = self._generate_question_response(user_message, username)
        
        # 如果没有匹配到特定关键词，生成通用回复
        if not response:
            response = self._generate_default_response(user_message, username)
        
        # 添加到历史记录
        self.add_to_history(user_message, response)
        
        return response
    
    def _contains_any(self, text, keywords):
        """检查文本是否包含任意关键词"""
        return any(keyword in text for keyword in keywords)
    
    def _generate_weather_response(self):
        """生成天气相关回复"""
        responses = [
            "今天天气看起来不错呢！阳光明媚，适合出去走走。",
            "我没有实时天气数据，但希望今天是个好天气！",
            "天气变化无常，出门前记得查看天气预报哦。",
            "不管天气如何，保持好心情最重要！"
        ]
        return random.choice(responses)
    
    def _generate_time_response(self):
        """生成时间相关回复"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        current_date = now.strftime("%Y年%m月%d日")
        weekday = now.strftime("%A")
        weekday_map = {"Monday": "星期一", "Tuesday": "星期二", "Wednesday": "星期三",
                      "Thursday": "星期四", "Friday": "星期五", "Saturday": "星期六", "Sunday": "星期日"}
        weekday_cn = weekday_map.get(weekday, weekday)
        
        return f"现在是{current_date} {weekday_cn} {current_time}，祝你度过愉快的一天！"
    
    def _generate_about_response(self):
        """生成关于机器人自身的回复"""
        responses = [
            f"我是{self.name}，一个智能聊天助手，很高兴能和你聊天！",
            f"你好，我是{self.name}，是这个聊天室的AI助手，可以陪你聊天、回答问题。",
            f"我叫{self.name}，是一个人工智能助手，随时为你提供帮助！"
        ]
        return random.choice(responses)
    
    def _generate_help_response(self):
        """生成帮助信息回复"""
        return "我是你的AI助手，你可以：\n1. 和我聊天\n2. @电影 分享电影链接\n3. @其他用户 发送提醒\n有什么具体需要帮助的吗？"
    
    def _generate_movie_response(self):
        """生成电影相关回复"""
        movies = ["《星际穿越》", "《盗梦空间》", "《阿甘正传》", "《肖申克的救赎》", "《泰坦尼克号》"]
        random_movie = random.choice(movies)
        responses = [
            f"喜欢看电影吗？我推荐{random_movie}，很经典的一部作品！",
            f"你可以使用@电影 链接 的格式分享电影链接哦！",
            f"我也很喜欢看电影呢！最近有什么好看的电影推荐给我吗？"
        ]
        return random.choice(responses)
    
    def _generate_chat_response(self, username):
        """生成聊天相关回复"""
        responses = [
            f"{username}，很高兴和你聊天！今天过得怎么样？",
            f"聊天是我的强项，{username}想聊点什么呢？",
            f"嗨，{username}！我们来聊点有趣的话题吧！"
        ]
        return random.choice(responses)
    
    def _generate_question_response(self, question, username):
        """生成问题回复"""
        responses = [
            f"{username}，这是个好问题！我认为...",
            f"关于这个问题，我的看法是...",
            f"感谢你的提问，{username}！根据我的了解...",
            f"这个问题很有意思，让我想想...",
            f"我觉得这个问题可以从几个方面来看..."
        ]
        base_response = random.choice(responses)
        
        # 根据问题内容添加一些具体的回答
        if self._contains_any(question, ["喜欢", "爱"]):
            return f"{base_response} 我喜欢和你聊天，这让我感到很开心！"
        elif self._contains_any(question, ["学习", "工作"]):
            return f"{base_response} 学习和工作都很重要，但也要记得适当休息哦！"
        elif self._contains_any(question, ["生活", "日常"]):
            return f"{base_response} 生活中有很多美好的事情值得我们去发现和珍惜。"
        else:
            return f"{base_response} 希望我的回答对你有所帮助！"
    
    def _generate_default_response(self, message, username):
        """生成默认回复"""
        responses = [
            f"{username}，你说的我记住了。",
            f"哦，原来是这样啊，{username}。",
            f"我理解你的意思了，{username}。",
            f"很有趣的观点，{username}！",
            f"继续说下去，我在听呢，{username}。",
            f"{message}，这个我知道！",
            f"{username}，能再详细说说吗？",
            f"这个话题很有意思，{username}！",
            f"我明白了，你是在说{message}，对吗？",
            f"{username}，你的想法很不错！"
        ]
        return random.choice(responses)

# 创建AI实例
bot_ai = SimpleChatAI(name="川小农")
