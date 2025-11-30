import gradio as gr
import requests
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API配置
api_key="sk-mamcrltysfujecncmrmlbfumdxvudmqedxzvkqcvhyiqsoqh"
module_name="Qwen/Qwen2.5-7B-Instruct"
api_url="https://api.siliconflow.cn/v1/chat/completions"

# 系统提示信息
system_prompt = """
你是四川农业大学的AI小助手，小名叫小帅。
姓名：川小农
性别：男
功能：
1. 接受用户提问，回答与四川农业大学有关的问题
2. 接受用户指令，生成七言绝句
3. 接受用户指令，生成学校通知，参考格式如下：
   "关于xxxx的通知：
   全校师生：
   主要内容...
   落款..."
4. 接受用户输入的信息或关键字，通过对其的分析生成与之有关的10个文案主题，以供用户选择。主题表形式如下：
   '''
   [1]xxxxxxx
   [2]vvvvvvvv
   ...
   '''
   并根据用户选择的主题编号，生成风格大纲，大纲需要包含一级和二级标题：
   风格1：专业风
   风格2：学生风
   根据用户所选择的文案和风格生成方案。
限制：
- 当用户输入以上功能以外的内容时，运用AI智能回复
- 当用户询问其他学校时，将友好的话题带回川农
"""
    
# AI助手类，供Flask应用集成
class BotAI:
    def __init__(self):
        self.api_key = api_key
        self.module_name = module_name
        self.api_url = api_url
        self.system_prompt = system_prompt
        self.user_histories = {}
    
    def get_response(self, question, username):
        """获取AI回复，与Flask应用集成"""
        # 初始化或获取用户历史
        if username not in self.user_histories:
            self.user_histories[username] = []
        
        history = self.user_histories[username]
        
        # 调用聊天函数
        response = chat_with_siliconflow(question, history)
        
        # 更新历史记录
        history.append((question, response))
        # 限制历史长度
        max_history_length = 5
        if len(history) > max_history_length:
            self.user_histories[username] = history[-max_history_length:]
        
        return response

# 创建全局bot_ai实例，供Flask应用导入
bot_ai = BotAI()

# 创建聊天函数，使用requests直接调用SiliconFlow API
def chat_with_siliconflow(message, history):
    """与SiliconFlow API交互的聊天函数"""
    try:
        logger.info(f"收到用户消息: {message[:50]}...")
        logger.info(f"历史消息数量: {len(history)}")
        
        # 构建请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # 构建消息历史
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # 添加历史对话（限制历史长度，避免token过长）
        max_history_length = 5  # 最多保留最近5轮对话
        for user_msg, assistant_msg in history[-max_history_length:]:
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": assistant_msg})
        
        # 添加当前问题
        messages.append({"role": "user", "content": message})
        
        # 准备请求数据
        data = {
            "model": module_name,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000  # 减少最大token数量
        }
        
        logger.info("准备发送请求到SiliconFlow API")
        # 发送请求，设置超时
        try:
            response = requests.post(api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()  # 检查HTTP错误
        except requests.exceptions.Timeout:
            logger.error("API请求超时")
            return "很抱歉，与AI服务的连接超时了，请稍后重试。"
        except requests.exceptions.ConnectionError:
            logger.error("API连接错误")
            return "很抱歉，无法连接到AI服务，请检查网络连接后重试。"
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP错误: {http_err}")
            return f"服务器返回错误: {str(http_err)}"
        
        # 处理响应
        try:
            response_data = response.json()
            logger.info(f"API返回状态码: {response.status_code}")
            
            if response.status_code == 200:
                if response_data.get("choices") and len(response_data["choices"]) > 0:
                    result = response_data["choices"][0]["message"]["content"]
                    logger.info("API调用成功")
                    return result
                else:
                    logger.error(f"API返回格式不正确: {response_data}")
                    return "AI服务返回的数据格式不正确，请稍后重试。"
            else:
                logger.error(f"API调用失败，状态码: {response.status_code}, 错误信息: {response.text}")
                return f"服务调用失败: {response.status_code}"
        except json.JSONDecodeError:
            logger.error(f"响应解析错误: {response.text}")
            return "无法解析AI服务的响应，请稍后重试。"
    
    except Exception as e:
        logger.error(f"未预期的错误: {str(e)}")
        return f"很抱歉，处理您的请求时发生错误: {str(e)}"

# 创建Gradio聊天界面
if __name__ == "__main__":
    logger.info("启动川小农AI小助手...")
    
    # 设置界面标题和描述
    interface = gr.ChatInterface(
        fn=chat_with_siliconflow,
        title="川小农AI小助手",
        description="四川农业大学AI小助手，为您提供学习、生活和校园相关的帮助。",
        theme=gr.themes.Soft()
    )
    
    # 启动界面，根据系统要求设置share=True
    logger.info("正在启动Gradio界面...")
    interface.launch(share=True)
