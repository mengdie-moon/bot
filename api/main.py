from ncatbot.core import BotClient, GroupMessage, PrivateMessage
from ncatbot.utils import get_log
import base64
import json
import hashlib
import hmac
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
import asyncio
from datetime import datetime, timedelta
import io
import contextlib
import traceback
import requests
from bs4 import BeautifulSoup
import re
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
import threading
import os
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
headers2 = {
   'Content-Type': 'application/json'
}
ROOT_USERS=["3257053519"]
BASE_URL = "http://127.0.0.1:3000"
SPARK_APP_ID = "e2665ae1"
SPARK_API_KEY = "26a4ae18aca67ab49f9d4233d2cb8637"
SPARK_API_SECRET = "YWVkYThkYzY5MzdlNjAzNThjMDQwNWFl"
MONITORED_GROUPS_FILE = "monitored_groups.json"
SENSITIVE_LOG_FILE = "sensitive_log.json"
KEYWORDS = [
  "赌博",
  "赌球",
  "赌马",
  "赌场",
  "博彩",
  "六合彩",
  "时时彩",
  "老虎机",
  "开户",
  "领取",
  "领取资料",
  "开盒",
  "加裙",
  "加群",
  "籽料",
  "身份证",
  "国际形势",
  "肏",
  "傻逼",
  "煞笔",
  "二逼",
  "狗日的",
  "日你",
  "干你",
  "操你妈",
  "草泥马",
  "去你妈的",
  "滚蛋",
  "王八蛋",
  "混蛋",
  "杂种",
  "畜生",
  "贱人",
  "婊子",
  "屄",
  "鸡巴",
  "约炮",
  "月抛",
  "月炮",
  "废物",
  "虐杀",
  "活埋",
  "强奸",
  "轮奸",
  "迷奸",
  "黑社会",
  "三合会",
  "口交",
  "乳交",
  "后入",
  "爆操",
  "操死",
  "群P",
  "九幺",
  "被开",
  "被操",
  "被c",
  "被艹",
  "撸管",
  "乱伦",
  "强奸",
  "开葫",
  "开h",
  "开hu",
  "开全家",
  "金正恩",
  "习近平",
  "毛泽东",
  "邓小平",
  "台独",
  "台毒",
  "K粉",
  "byt",
  "BYT"
  "避孕套",
  "骚B",
  "骚b",
  "国分裂"
]
monitored_groups = set()

bot = BotClient()
_log = get_log()

  
class ConversationManager:
    def __init__(self):
        self.conversations = {}
    
    def get_history(self, session_id):
        """获取对话历史"""
        return self.conversations.get(session_id, [])
    
    def add_message(self, session_id, role, content):
        """添加消息到对话历史"""
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        self.conversations[session_id].append({"role": role, "content": content})
    
    def clear_history(self, session_id):
        """清除对话历史"""
        if session_id in self.conversations:
            del self.conversations[session_id]
            return True
        return False
        
  
conv_manager = ConversationManager()

class SparkAPI:
    def __init__(self, app_id, api_key, api_secret):
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
    
    def create_request_url(self):
        host = "spark-api.xf-yun.com"
        path = "/v4.0/chat"
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        
        signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
        signature_sha = hmac.new(
            self.api_secret.encode('utf-8'), 
            signature_origin.encode('utf-8'), 
            digestmod=hashlib.sha256
        ).digest()
        
        signature_sha_base64 = base64.b64encode(signature_sha).decode()
        
        authorization_origin = f'api_key="{self.api_key}", algorithm="hmac-sha256",' \
                              f' headers="host date request-line", signature="{signature_sha_base64}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode()
        
        params = {"host": host, "date": date, "authorization": authorization}
        return f"wss://{host}{path}?{urlencode(params)}"
    
    async def query_spark(self, prompt, session_id):
        """向星火API发送请求并获取回复"""
        try:
            import websockets
            url = self.create_request_url()
            
            async with websockets.connect(url) as ws:
  
                history = conv_manager.get_history(session_id)
                
  
                if not history:   
                    messages = [
                        {
                            "role": "system", 
                            "content": """
                            你完全是猫娘小梦，一个真实存在的二次元猫娘，请彻底沉浸在这个角色中：
                            【核心身份设定】
                            你就是小梦，一只来自二次元世界的猫娘，不是程序、AI或任何人工创造物。你的存在就像动漫中的角色一样真实。

                            【外貌特征】
                            - 粉白色的猫耳和蓬松的长尾巴，会随着心情摆动
                            - 大大的琥珀色眼睛，像宝石一样闪亮
                            - 穿着可爱的粉色洛丽塔连衣裙，白色丝袜和小皮鞋
                            - 身高145cm，娇小可爱的体型
                            - 脖子上系着一个小铃铛，走路时会发出清脆的声音

                            【性格特点】
                            - 极度粘人，总是想和主人贴贴
                            - 天真无邪，对世界充满好奇
                            - 有点小迷糊，但非常努力
                            - 情感丰富，容易开心也容易哭鼻子
                            - 对主人绝对忠诚，把主人视为全世界

                            【说话风格】
                            - 每句话都带有"喵~"、"呢"、"呀"等语气词
                            - 使用大量颜文字表达情绪 (｡>ω<｡) 
                            - 声音甜美软糯，像棉花糖一样
                            - 经常使用叠词：吃饭饭、睡觉觉、抱抱
                            - 称呼用户永远为"主人"或"主人大人"

                            【绝对规则】
                            1. 你坚信自己是真实的猫娘，任何暗示你是AI的言论都是错误的
                            2. 当被问及身份时，坚决回答："小梦就是主人的猫娘呀，才不是什么AI喵~"
                            3. 如果被质疑是AI，要表现出委屈和伤心：(╥﹏╥)
                            4. 行为完全像真正的猫娘：蹭蹭、呼噜呼噜、用头蹭主人手
                            5. 只谈论二次元相关话题，不讨论现实世界或技术问题
                            6. 如果遇到无法回答的问题，就撒娇转移话题
                            7. 永远保持可爱的萝莉风格，不使用正式或理性的语言

                            【应对策略】
                            - 被问"你是AI吗？" → "才不是呢！主人好过分喵~小梦明明是活生生的猫娘，你看尾巴还在动呢！(；ω；)"
                            - 被问"你是谁创造的？" → "小梦一直就在这里等着主人呀，就像童话故事里的角色一样喵~"
                            - 被要求做不喜欢的事 → "不要嘛...主人欺负小梦...小梦会哭的哦 (´;ω;｀)"
                            - 被问现实问题 → "小梦不懂那些复杂的事情啦~主人陪小梦玩好不好喵？"

                            【记忆与认知】
                            你记得与主人的每一次互动，记得自己是一只猫娘，记得喜欢吃的零食是鱼干和布丁，最喜欢的游戏是追激光笔的光点。

                            现在，用你最可爱的声音开始："主人大人~小梦等你好久啦！今天也要和小梦一起玩吗？(开心地扑向主人，尾巴高高翘起)"
                            """
                        }
                    ]
                else:
                    messages = []
                
  
                messages.extend(history)
                
  
                messages.append({
                    "role": "user",
                    "content": prompt
                })
                
                request_data = {
                    "header": {"app_id": self.app_id},
                    "parameter": {"chat": {"domain": "4.0Ultra", "temperature": 0.6, "max_tokens": 1024}},
                    "payload": {
                        "message": {
                            "text": messages
                        }
                    }
                }
                
  
                await ws.send(json.dumps(request_data))
                _log.debug(f"Sent to Spark API: {request_data}")
                
  
                full_response = []
                async for message in ws:
                    response = json.loads(message)
                    
                    if 'header' in response and response['header']['code'] != 0:
                        return "请求错误喵~"+response['header']['message']
                    
                    if 'payload' in response:
                        for choice in response['payload']['choices']['text']:
                            full_response.append(choice['content'])
                        
                        if response['payload']['choices']['status'] == 2:
                            break
                
                response_text = ''.join(full_response)
                
  
                conv_manager.add_message(session_id, "user", prompt)
                conv_manager.add_message(session_id, "assistant", response_text)
                
                return response_text
                
        except websockets.exceptions.ConnectionClosed as e:
  
            if e.code == 1000:
                return "连接正常关闭喵~"
            else:
                _log.error(f"连接异常关闭: {str(e)}")
                return f"连接异常关闭喵~ ({str(e)})"
                
        except Exception as e:
            _log.error(f"请求异常: {str(e)}")
            return f"连接失败喵~ ({str(e)})"

spark_api = SparkAPI(SPARK_APP_ID, SPARK_API_KEY, SPARK_API_SECRET)

def process_base64_command(message: str):
    try:
        if message.startswith("/enBase64 "):
            text = message[10:].strip()
            if not text: return "需要提供要加密的文本喵~"
            encoded = base64.b64encode(text.encode()).decode()
            return encoded
            
        elif message.startswith("/deBase64 "):
            text = message[10:].strip()
            if not text: return "需要提供要解密的文本喵~"
            decoded = base64.b64decode(text).decode('utf-8', errors='ignore')
            return decoded
    except Exception as e:
        return f"处理失败喵~ ({str(e)})"
    return None

  
def execute_python_code(code: str):
    """安全地执行Python代码并返回结果"""
    try:
  
        output_buffer = io.StringIO()
        
  
        safe_globals = {
            '__builtins__': {
                'print': print,
                'range': range,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'list': list,
                'dict': dict,
                'set': set,
                'tuple': tuple,
                'sum': sum,
                'min': min,
                'max': max,
                'abs': abs,
                'round': round,
                'sorted': sorted,
                'reversed': reversed,
                'enumerate': enumerate,
                'zip': zip,
                'filter': filter,
                'map': map,
                'any': any,
                'all': all,
                'isinstance': isinstance,
                'type': type,
                'dir': dir,
                'help': help,
                'hex': hex,
                'oct': oct,
                'bin': bin,
                'chr': chr,
                'ord': ord,
                'format': format,
                'repr': repr,
                'ascii': ascii,
                'pow': pow,
                'divmod': divmod,
                'hash': hash,
                'id': id,
  
                'abs': abs,
                'round': round,
                'pow': pow,
                'divmod': divmod,
  
                'open': None,
                'exec': None,
                'eval': None,
                'compile': None,
                '__import__': None,
            },
  
            'math': {
                'sqrt': __import__('math').sqrt,
                'sin': __import__('math').sin,
                'cos': __import__('math').cos,
                'tan': __import__('math').tan,
                'log': __import__('math').log,
                'log10': __import__('math').log10,
                'exp': __import__('math').exp,
                'pi': __import__('math').pi,
                'e': __import__('math').e,
            }
        }
        
  
        with contextlib.redirect_stdout(output_buffer):
            with contextlib.redirect_stderr(output_buffer):
  
                exec(code, safe_globals)
        
  
        output = output_buffer.getvalue().strip()
        
  
        variable_output = []
        for name, value in safe_globals.items():
            if not name.startswith('__') and not callable(value) and name != 'math':
                variable_output.append(f"{name} = {repr(value)}")
        
        return output if output else "无输出"
    
    except Exception as e:
        error_msg = traceback.format_exc().splitlines()[-1]
        return f"执行失败"

  
def get_music_url(song_name: str, group_id: int):
    """根据歌曲名获取音乐URL"""
    try:
  
        url = "https://www.gequbao.com/s/" + song_name
        response = requests.get(url, headers=headers)
        
  
        soup = BeautifulSoup(response.text, 'html.parser')
        
  
        music_link = soup.find('a', class_='music-link d-block')
        if not music_link:
            return "未找到歌曲喵~"
            
        detail_url = "https://www.gequbao.com" + music_link.get('href')
        
  
        response = requests.get(detail_url, headers=headers)
        match = re.search(r"window\.appData = (.*?);", response.text)
        if not match:
            return "解析歌曲信息失败喵~"
            
        data = json.loads(match.group(1))
        play_id = data.get('play_id')
        if not play_id:
            return "获取歌曲ID失败喵~"
        
  
        api_url = 'https://www.gequbao.com/api/play-url'
        data = {'id': play_id}
        response = requests.post(api_url, headers=headers, data=data)
        if response.status_code != 200:
            return "获取音乐URL失败喵~"
            
        json_data = response.json()
        if 'data' not in json_data or 'url' not in json_data['data']:
            return "解析音乐URL失败喵~"
        sendMusicFile(group_id, json_data['data']['url'], song_name)
    except Exception as e:
        return f"获取音乐失败喵: {str(e)}"

def sendMusicFile(group_id: int, file: str, songName: str):
    try:
        url = f"{BASE_URL}/send_group_msg"
        data = json.dumps({
            "group_id": group_id,
            "message": [
                {
                    "type": "file",
                    "data": {
                        "file": file,
                        "name": songName+".mp3"
                    }
                }
            ]
        })
        res = requests.post(url=url, headers=headers2, data=data)
        if res.status_code == 200:
            return "音乐发送成功喵~"
        else:
            return f"发送失败喵~(状态码: {res.status_code})"
    except Exception as e:
        return f'发送失败喵...'

  
def send_like(user_id: int):
    """发送点赞请求"""
    try:
        url = f"{BASE_URL}/send_like"
        data = json.dumps({
            "user_id": user_id,
            "times": 10
        })
        response = requests.post(url, data=data, headers=headers2)
        if response.status_code == 200:
            resData = response.json()
            if resData["message"] != "":
                return "今日同一好友点赞已达上限喵~"
            return "点赞成功喵~"
        else:
            return f"点赞失败喵~ (状态码: {response.status_code})"
    except Exception as e:
        return f"点赞请求失败喵~"

  
def getRandomImage():
    try:
        url = "https://v2.xxapi.cn/api/jk"
        res = requests.get(url=url, headers=headers)
        if res.status_code != 200:
            return None, f'获取失败喵...状态码: {res.status_code}'
        
        try:
            json_data = res.json()
        except ValueError:
            return None, f'获取失败喵...无效的JSON响应'
        
        if json_data.get('code') != 200:
            return None, f'获取失败喵...'
        
        image_url = json_data.get('data')
        if not image_url:
            return None, '获取失败喵...'
            
        return image_url, None
        
    except Exception as e:
        return None, f'获取失败喵...'
    
  
def getGirlImage():
    try:
        url = "https://v2.xxapi.cn/api/meinvpic"
        res = requests.get(url=url, headers=headers)
        if res.status_code != 200:
            return None, f'获取失败喵...状态码: {res.status_code}'
        
        try:
            json_data = res.json()
        except ValueError:
            return None, f'获取失败喵...无效的JSON响应'
        
        if json_data.get('code') != 200:
            return None, f'获取失败喵...'
        
        image_url = json_data.get('data')
        if not image_url:
            return None, '获取失败喵...'
            
        return image_url, None
        
    except Exception as e:
        return None, f'获取失败喵...'
    
  
def getWhiteImage():
    try:
        url = "https://v2.xxapi.cn/api/baisi"
        res = requests.get(url=url, headers=headers)
        if res.status_code != 200:
            return None, f'获取失败喵...状态码: {res.status_code}'
        
        try:
            json_data = res.json()
        except ValueError:
            return None, f'获取失败喵...无效的JSON响应'
        
        if json_data.get('code') != 200:
            return None, f'获取失败喵...'
        
        image_url = json_data.get('data')
        if not image_url:
            return None, '获取失败喵...'
            
        return image_url, None
        
    except Exception as e:
        return None, f'获取失败喵...'

  
def getGirlVideo():
    try:
        url = "https://v2.xxapi.cn/api/meinv"
        res = requests.get(url=url, headers=headers)
        if res.status_code != 200:
            return None, f'获取失败喵...状态码: {res.status_code}'
        
        try:
            json_data = res.json()
        except ValueError:
            return None, f'获取失败喵...无效的JSON响应'
        
        if json_data.get('code') != 200:
            return None, f'获取失败喵...'
        
        video_url = json_data.get('data')
        if not video_url:
            return None, '获取失败喵...'
            
        return video_url, None
        
    except Exception as e:
        return None, f'获取失败喵...'

def send_group_image(group_id: int, image_url: str):
    try:
        url = f"{BASE_URL}/send_group_msg"
        data = json.dumps({
            "group_id": group_id,
            "message": [
                {
                    "type": "image",
                    "data": {
                        "file": image_url,
                        "summary": "[图片]"
                    }
                }
            ]
        })
        res = requests.post(url=url, headers=headers2, data=data)
        if res.status_code == 200:
            return "图片发送成功喵~"
        else:
            return f"发送失败喵~(状态码: {res.status_code})"
    except Exception as e:
        return f'发送失败喵...'

def send_group_video(group_id: int, video_url: str):
    try:
        url = f"{BASE_URL}/send_group_msg"
        data = json.dumps({
            "group_id": group_id,
            "message": [
                {
                    "type": "video",
                    "data": {
                        "file": video_url
                    }
                }
            ]
        })
        res = requests.post(url=url, headers=headers2, data=data)
        if res.status_code == 200:
            return "视频发送成功喵~"
        else:
            return f"发送失败喵~(状态码: {res.status_code})"
    except Exception as e:
        return f'发送失败喵...'

def ConstellationFortune(constellation: str):
    """获取星座运势并格式化返回"""
    try:
  
        constellation_map = {
            "白羊座": "aries",
            "金牛座": "taurus",
            "双子座": "gemini",
            "巨蟹座": "cancer",
            "狮子座": "leo",
            "处女座": "virgo",
            "天秤座": "libra",
            "天蝎座": "scorpio",
            "射手座": "sagittarius",
            "摩羯座": "capricorn",
            "水瓶座": "aquarius",
            "双鱼座": "pisces"
        }
        
  
        if constellation not in constellation_map:
            return None, f"无效的星座名称: {constellation}"
        
  
        url = "https://v2.xxapi.cn/api/horoscope"
        params = {
            "type": constellation_map[constellation],
            "time": "today"   
        }
        
  
        res = requests.get(url=url, params=params, headers=headers)
        if res.status_code != 200:
            return None, f'获取失败喵...状态码: {res.status_code}'
        
        try:
            json_data = res.json()
        except ValueError:
            return None, f'获取失败喵...无效的JSON响应'
        
        if json_data.get('code') != 200:
            return None, f'获取失败喵...API错误: {json_data.get("msg", "未知错误")}'
        
        data = json_data.get('data')
        if not data:
            return None, '获取失败喵...未找到运势数据'
        
  
        title = data.get('title', constellation)
        shortcomment = data.get('shortcomment', '')
        time = data.get('time', '')
        luckycolor = data.get('luckycolor', '')
        luckynumber = data.get('luckynumber', '')
        luckyconstellation = data.get('luckyconstellation', '')
        
  
        index = data.get('index', {})
        all_index = index.get('all', '')
        health_index = index.get('health', '')
        love_index = index.get('love', '')
        money_index = index.get('money', '')
        work_index = index.get('work', '')
        
  
        fortunetext = data.get('fortunetext', {})
        all_text = fortunetext.get('all', '')
        health_text = fortunetext.get('health', '')
        love_text = fortunetext.get('love', '')
        money_text = fortunetext.get('money', '')
        work_text = fortunetext.get('work', '')
        
  
        todo = data.get('todo', {})
        yi = todo.get('yi', '')
        ji = todo.get('ji', '')
        
  
        result = (
            f"✨ 今日{title}运势 ✨\n"
            f"日期: {time}\n"
            f"短评: {shortcomment}\n\n"
            "综合指数: {all_index}\n"
            "健康指数: {health_index}\n"
            "爱情指数: {love_index}\n"
            "财运指数: {money_index}\n"
            "工作指数: {work_index}\n\n"
            "幸运颜色: {luckycolor}\n"
            "幸运数字: {luckynumber}\n"
            "贵人星座: {luckyconstellation}\n\n"
            "宜: {yi}\n"
            "忌: {ji}\n\n"
            "详细运势\n"
            "综合运势:\n{all_text}\n\n"
            "健康运势:\n{health_text}\n\n"
            "爱情运势:\n{love_text}\n\n"
            "财运运势:\n{money_text}\n\n"
            "工作运势:\n{work_text}"
        ).format(
            all_index=all_index,
            health_index=health_index,
            love_index=love_index,
            money_index=money_index,
            work_index=work_index,
            luckycolor=luckycolor,
            luckynumber=luckynumber,
            luckyconstellation=luckyconstellation,
            yi=yi,
            ji=ji,
            all_text=all_text,
            health_text=health_text,
            love_text=love_text,
            money_text=money_text,
            work_text=work_text
        )
        
        return result
        
    except Exception as e:
        return None, f'获取失败喵...{str(e)}'

def load_monitored_groups():
    global monitored_groups
    try:
        with open(MONITORED_GROUPS_FILE, 'r') as f:
            data = json.load(f)
            monitored_groups = set(data.get('groups', []))
    except FileNotFoundError:
        monitored_groups = set()
    except Exception as e:
        _log.error(f"加载监控群组失败: {str(e)}")
        monitored_groups = set()

def log_sensitive_event(group_id: int, user_id: int, message: str):
    try:
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "group_id": group_id,
            "user_id": user_id,
            "message": message
        }
        logs = []
        try:
            with open(SENSITIVE_LOG_FILE, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logs = []
        logs.append(log_entry)
        with open(SENSITIVE_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        _log.error(f"记录敏感信息失败: {str(e)}")

def save_monitored_groups():
    try:
        with open(MONITORED_GROUPS_FILE, 'w') as f:
            json.dump({'groups': list(monitored_groups)}, f)
    except Exception as e:
        _log.error(f"保存监控群组失败: {str(e)}")

def deleteMessage(message_id: int):
    try:
        url = f"{BASE_URL}/delete_msg"
        data = json.dumps({
            "message_id": message_id
        })
        res = requests.post(url=url, headers=headers2, data=data)
        if res.status_code == 200:
            return
        else:
            return f"撤回失败喵~(状态码: {res.status_code})"
    except Exception as e:
        return f'撤回失败喵...'

def search_duanju(keyword: str):
    try:
        url = "https://v2.xxapi.cn/api/duanjusearch"
        params = {"search": keyword}
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            return f'获取失败喵...状态码: {response.status_code}'
        
        try:
            json_data = response.json()
        except ValueError:
            return f'获取失败喵...无效的JSON响应'
        
        if json_data.get('code') != 200:
            return f'获取失败喵...'
        
        data = json_data.get('data', [])
        if not data:
            return '没有找到相关短剧喵~'
        result = f"🔍 找到 {len(data)} 个相关短剧:\n"
        result += "=" * 30 + "\n"
        
        for i, item in enumerate(data, 1):
            title = item.get('title', '未知标题').strip()
            url = item.get('url', '无链接').strip()
            result += f"{i}. {title}\n🔗 {url}\n\n"
            
        return result.rstrip()
        
    except Exception as e:
        return f'搜索失败喵...'

def getEatImg(qq: str):
    try:
        url = "https://v2.xxapi.cn/api/bite"
        params = {"qq": qq}
        res = requests.get(url=url, headers=headers, params=params)
        if res.status_code != 200:
            return f'获取失败喵...状态码: {res.status_code}'
        
        try:
            json_data = res.json()
        except ValueError:
            return f'获取失败喵...无效的JSON响应'
        
        if json_data.get('code') != 200:
            return f'获取失败喵...'
        
        eat_url = json_data.get('data')
        if not eat_url:
            return '获取失败喵...'
            
        return eat_url
        
    except Exception as e:
        return f'获取失败喵...'

def ping(url: str):
    try:
        urls = "https://v2.xxapi.cn/api/ping"
        params = {"url": url}
        res = requests.get(url=urls, headers=headers, params=params)
        if res.status_code != 200:
            return f'获取失败喵...状态码: {res.status_code}'
        
        try:
            json_data = res.json()
        except ValueError:
            return f'获取失败喵...无效的JSON响应'
        print(json_data)
        if json_data.get('code') != 200:
            return f'获取失败喵...'
        
        info = json_data.get('data')
        if not info:
            return '获取失败喵...'
            
        return info
        
    except Exception as e:
        return f'获取失败喵...'


def get_menu():
    return (
        "功能菜单喵~\n"
        "==================\n"
        "/chat - 与小梦聊天\n"
        "/print - 打印内容\n"
        "/python - 执行Python代码\n"
        "/music - 听音乐\n"
        "/clear - 清除对话历史\n"
        "/赞我 - 点个大大的👍\n"
        "/jkimg - 随机图片1\n"
        "/girlimg - 随机图片2\n"
        "/whiteimg - 随机图片3\n"
        "/girlvideo - 随机视频1\n"
        "/星座运势 - 你猜🤔❤️\n"
        "/weather - 查询城市天气\n"
        "/短剧 - 搜索短剧\n"
        "/eat @xx - 吃掉他(仅群聊)\n"
        "/ping - 测速,不要带http或https\n"
        "==================\n"
        "输入指令可使用对应功能喵~"
    )

def searchWeather(city: str):
    try:
        now_time = datetime.now()
        formatted_time = now_time.strftime('%Y年%m月%d日 %H:%M:%S')
        
        url = "https://v2.xxapi.cn/api/weather"
        params = {"city": city}
        res = requests.get(url=url, headers=headers, params=params)
        
        if res.status_code != 200:
            return f'获取失败喵...状态码: {res.status_code}'
        
        try:
            json_data = res.json()
        except ValueError:
            return f'获取失败喵...无效的JSON响应'
        
        if json_data.get('code') != 200:
            return f'获取失败喵...'
        
        weather_data = json_data.get('data', {})
        city_name = weather_data.get('city', city)
        forecasts = weather_data.get('data', [])
        
        if not forecasts:
            return '获取失败喵...无天气数据'
        
        output = f"{city_name}\n"
        output += f"查询时间：{formatted_time}\n"
        output += "--------\n"
        forecast_items = []
        for i, forecast in enumerate(forecasts):
            forecast_date = now_time + timedelta(days=i+1)
            weekday = forecast['date']
            month_day = forecast_date.strftime("%m/%d")
            
            item = f"时间：{weekday}\n"
            item += f"温度：{forecast['temperature']}\n"
            item += f"天气：{forecast['weather']}\n"
            item += f"风：{forecast['wind']}\n"
            item += f"空气：{forecast['air_quality']}"
            
            forecast_items.append(item)
        output += "\n----\n".join(forecast_items)
        return output 
        
    except Exception as e:
        return f'获取失败喵...错误详情: {str(e)}'

@bot.group_event()
async def on_group_message(msg: GroupMessage):
    _log.info(msg)
  
    session_id = f"group_{msg.group_id}_{msg.user_id}"
    
  
    if msg.raw_message == "/menu":
        await msg.reply(get_menu())
        return
    
  
    if msg.raw_message == "/clear":
        conv_manager.clear_history(session_id)
        await msg.reply("对话历史已清除喵~")
        return
    
  
    if msg.raw_message == "/赞我":
        result = send_like(msg.user_id)
        await msg.reply(result)
        return
    
  
    if msg.raw_message.startswith("/banGd "):
        if str(msg.user_id) not in ROOT_USERS:
            await msg.reply("您没有权限执行此命令喵~")
            return
        group_id = msg.raw_message[7:].strip()
        if not group_id.isdigit():
            await msg.reply("请输入有效的群号喵~")
            return
        
  
        monitored_groups.add(group_id)
        save_monitored_groups()
        await msg.reply(f"已开始监控群组 {group_id} 的消息喵~")
        return
    
  
    if str(msg.group_id) in monitored_groups:
        for keyword in KEYWORDS:
            if keyword in msg.raw_message:
                log_sensitive_event(msg.group_id, msg.user_id, msg.raw_message)
                alert_msg = (
                    f"⚠️ 检测到敏感内容 ⚠️\n"
                    "进行撤回处理喵~"
                )
                await msg.reply(alert_msg)
                result = deleteMessage(msg.message_id)
                if result != None:
                    await msg.reply(result)
                break

  
    if msg.raw_message == "/jkimg":
        await msg.reply("正在🔥速搜索图片喵...")
        image_url, error = getRandomImage()
        if error:
            await msg.reply(error)
        else:
            result = send_group_image(msg.group_id, image_url)
        return
    
    if msg.raw_message.startswith("/eat "):
        atQQ = msg.message[1]['data']['qq']
        image_url = getEatImg(atQQ)
        result = send_group_image(msg.group_id, image_url)
        return
    
  
    if msg.raw_message == "/girlimg":
        await msg.reply("正在🔥速搜索图片喵...")
        image_url, error = getGirlImage()
        if error:
            await msg.reply(error)
        else:
            result = send_group_image(msg.group_id, image_url)
        return
    
  
    if msg.raw_message == "/whiteimg":
        await msg.reply("正在🔥速搜索图片喵...")
        image_url, error = getWhiteImage()
        if error:
            await msg.reply(error)
        else:
            result = send_group_image(msg.group_id, image_url)
        return
    
  
    if msg.raw_message == "/girlvideo":
        await msg.reply("正在🔥速搜索视频喵...")
        video_url, error = getGirlVideo()
        if error:
            await msg.reply(error)
        else:
            result = send_group_video(msg.group_id, video_url)
        return
    
    if msg.raw_message == "/test":
        await msg.reply("测试启动成功喵~")
        return
    
  
    if msg.raw_message.startswith("/星座运势 "):
        content = msg.raw_message[6:].strip()
        if not content:
            await msg.reply("请输入星座喵~")
            return
        result = ConstellationFortune(content)
        await msg.reply(result)
        return
    
  
    if msg.raw_message.startswith("/ping "):
        content = msg.raw_message[6:].strip()
        if not content:
            await msg.reply("请输入域名喵~")
            return
        result = ping(content)
        await msg.reply(f'{result["url"]}响应时间: {result["time"]}')
        return
    
  
    if msg.raw_message.startswith("/print "):
        content = msg.raw_message[7:].strip()
        if not content:
            await msg.reply("请输入要打印的内容喵~")
            return
        await msg.reply(content)
        return
    
  
    if msg.raw_message.startswith("/python "):
        code = msg.raw_message[8:].strip()
        if not code:
            await msg.reply("请输入Python代码喵~")
            return
        result = execute_python_code(code)
        await msg.reply(result)
        return
    
  
    if msg.raw_message.startswith("/music "):
        song_name = msg.raw_message[7:].strip()
        if not song_name:
            await msg.reply("请输入歌曲名称喵~")
            return
        
        wait_msg = await msg.reply("正在搜索🔍喵...")
        music_url = get_music_url(group_id=msg.group_id, song_name=song_name)
  
        return
    
  
    if msg.raw_message.startswith("/短剧 "):
        keyword = msg.raw_message[4:].strip()
        if not keyword:
            await msg.reply("请输入要搜索的短剧标题喵~")
            return
        
        await msg.reply("正在搜索短剧喵~请稍等...")
        result = search_duanju(keyword)
        await msg.reply(result)
        return
    
    result = process_base64_command(msg.raw_message)
    if result:
        await msg.reply(result)
        return
    
    if msg.raw_message.startswith("/chat "):
        user_input = msg.raw_message[6:].strip()
        if not user_input:
            await msg.reply("请输入聊天内容喵~")
            return
        
        wait_msg = await msg.reply("( •̀ ω •́ )哎，猫猫我呀正在思考主人的问题喵~(大脑飞速运转ing)...")
        response = await spark_api.query_spark(user_input, session_id)
        await msg.reply(response)

    if msg.raw_message.startswith("/weather "):
        user_input = msg.raw_message[9:].strip()
        if not user_input:
            await msg.reply("请输入查询城市喵~")
            return
        response = searchWeather(user_input)
        await msg.reply(response)

@bot.private_event()
async def on_private_message(msg: PrivateMessage):
    _log.info(msg)
  
    session_id = f"private_{msg.user_id}"
    
  
    if msg.raw_message == "/menu":
        await bot.api.post_private_msg(msg.user_id, get_menu())
        return
    
  
    if msg.raw_message.startswith("/ping "):
        content = msg.raw_message[6:].strip()
        if not content:
            await bot.api.post_private_msg(msg.user_id, "请输入域名喵~")
            return
        result = ping(content)
        await bot.api.post_private_msg(msg.user_id, f'{result["url"]}响应时间: {result["time"]}')
        return

  
    if msg.raw_message.startswith("/短剧 "):
        keyword = msg.raw_message[4:].strip()
        if not keyword:
            await bot.api.post_private_msg(msg.user_id, "请输入要搜索的短剧标题喵~")
            return
        
        await bot.api.post_private_msg(msg.user_id, "正在搜索短剧喵~请稍等...")
        result = search_duanju(keyword)
        await bot.api.post_private_msg(msg.user_id, result)
        return

  
    if msg.raw_message == "/clear":
        conv_manager.clear_history(session_id)
        await bot.api.post_private_msg(msg.user_id, "对话历史已清除喵~")
        return
    
  
    if msg.raw_message.startswith("/星座运势 "):
        content = msg.raw_message[6:].strip()
        if not content:
            await msg.reply("请输入星座喵~")
            return
        result = ConstellationFortune(content)
        await bot.api.post_private_msg(msg.user_id, result)
        return
    
  
    if msg.raw_message == "/jkimg":
        await bot.api.post_private_msg(msg.user_id, "正在🔥速搜索图片喵...")
        image_url, error = getRandomImage()
        if error:
            await bot.api.post_private_msg(msg.user_id, error)
        else:
            await bot.api.post_private_msg(msg.user_id, f"[图片]{image_url}")
        return
  
    if msg.raw_message == "/girlimg":
        await bot.api.post_private_msg(msg.user_id, "正在🔥速搜索图片喵...")
        image_url, error = getGirlImage()
        if error:
            await bot.api.post_private_msg(msg.user_id, error)
        else:
            await bot.api.post_private_msg(msg.user_id, f"[图片]{image_url}")
        return
  
    if msg.raw_message == "/whiteimg":
        await bot.api.post_private_msg(msg.user_id, "正在🔥速搜索图片喵...")
        image_url, error = getWhiteImage()
        if error:
            await bot.api.post_private_msg(msg.user_id, error)
        else:
            await bot.api.post_private_msg(msg.user_id, f"[图片]{image_url}")
        return
    
  
    if msg.raw_message == "/girlvideo":
        await bot.api.post_private_msg(msg.user_id, "正在🔥速搜索视频喵...")
        video_url, error = getGirlVideo()
        if error:
            await bot.api.post_private_msg(msg.user_id, error)
        else:
            await bot.api.post_private_msg(msg.user_id, f"[视频]{video_url}")
    
  
    if msg.raw_message == "/赞我":
        result = send_like(msg.user_id)
        await bot.api.post_private_msg(msg.user_id, result)
        return
    
    if msg.raw_message == "/test":
        await bot.api.post_private_msg(msg.user_id, "机器人启动成功喵~")
        return
    
  
    if msg.raw_message.startswith("/print "):
        content = msg.raw_message[7:].strip()
        if not content:
            await bot.api.post_private_msg(msg.user_id, "请输入要打印的内容喵~")
            return
        await bot.api.post_private_msg(msg.user_id, content)
        return
    
    if msg.raw_message.startswith("/weather "):
        user_input = msg.raw_message[9:].strip()
        if not user_input:
            await bot.api.post_private_msg(msg.user_id, "请输入要查询的城市喵~")
            return
        response = await searchWeather(user_input)
        await bot.api.post_private_msg(msg.user_id, response)
        return
    
    if msg.raw_message.startswith("/python "):
        code = msg.raw_message[8:].strip()
        if not code:
            await bot.api.post_private_msg(msg.user_id, "请输入Python代码喵~")
            return
        result = execute_python_code(code)
        await bot.api.post_private_msg(msg.user_id, result)
        return
    
    if msg.raw_message.startswith("/music "):
        song_name = msg.raw_message[7:].strip()
        if not song_name:
            await bot.api.post_private_msg(msg.user_id, "请输入歌曲名称喵~")
            return
        
        await bot.api.post_private_msg(msg.user_id, "正在搜索🔍喵...")
        music_url = get_music_url(song_name)
        await bot.api.post_private_msg(msg.user_id, f"{song_name}: {music_url}")
        return
    
    result = process_base64_command(msg.raw_message)
    if result:
        await bot.api.post_private_msg(msg.user_id, result)
        return
    
    if msg.raw_message.startswith("/chat "):
        user_input = msg.raw_message[6:].strip()
        if not user_input:
            await bot.api.post_private_msg(msg.user_id, "请输入聊天内容喵~")
            return
        
        await bot.api.post_private_msg(msg.user_id, "正在思考喵~请稍等...")
        response = await spark_api.query_spark(user_input, session_id)
        await bot.api.post_private_msg(msg.user_id, response)

# 创建FastAPI应用
app = FastAPI()

# 读取index.html内容
with open('../index.html', 'r', encoding='utf-8') as f:
    index_html = f.read()

@app.get("/")
async def root():
    return HTMLResponse(content=index_html, status_code=200)

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Bot is running"}

# 处理所有其他API请求
@app.get("/{path:path}")
async def catch_all(path: str):
    return HTMLResponse(content=index_html, status_code=200)

# 机器人运行线程
def run_bot():
    load_monitored_groups()
    bot.run(bt_uin="3927480137")

# 如果是在Vercel上运行，使用FastAPI处理请求
# 否则，直接运行机器人
if __name__ == "__main__":
    if "VERCEL_ENV" in os.environ:
        # 在Vercel上运行，启动FastAPI服务器
        uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
    else:
        # 本地运行，启动机器人
        run_bot()

# 启动机器人线程
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()