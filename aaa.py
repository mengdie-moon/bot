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
  "私我",
  "加群",
  "籽料",
  "信赖",
  "低价",
  "身份证",
  "国际形势",
  "操",
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
  "滚",
  "滚蛋",
  "王八蛋",
  "混蛋",
  "杂种",
  "畜生",
  "贱人",
  "婊子",
  "屌",
  "牛逼",
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
  "强奸"
]

# 读取要检查的文本内容
with open('a.txt', 'r', encoding='utf-8') as f:
    text_to_check = f.read()

# 检查文本中是否包含敏感词
found_keywords = []
for keyword in KEYWORDS:
    keyword = keyword.strip()  # 去除空格
    if keyword in text_to_check:
        found_keywords.append(keyword)

# 打印找到的敏感词
if found_keywords:
    print("发现以下敏感词:")
    for keyword in found_keywords:
        print(f"- {keyword}")
else:
    print("未发现敏感词")