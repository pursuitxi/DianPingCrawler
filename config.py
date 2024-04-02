# 基础配置
KEYWORDS = "阿那亚"
LOGIN_TYPE = "cookie"  # qrcode or phone or cookie
COOKIES = ""
CRAWLER_TYPE = "detail"

# 指定大众点评需要爬虫的商家ID列表

DIANPING_ID_LIST = [
    "G8s51WX7iIv75MLb"
]


# 是否开启 IP 代理
ENABLE_IP_PROXY = False

# 代理IP池数量
IP_PROXY_POOL_COUNT = 2

# 设置为True不会打开浏览器（无头浏览器），设置False会打开一个浏览器（小红书如果一直扫码登录不通过，打开浏览器手动过一下滑动验证码）
HEADLESS = True

# 是否保存登录状态
SAVE_LOGIN_STATE = True

# 数据保存类型选项配置,支持三种类型：csv、json
SAVE_DATA_OPTION = "csv" # csv or json

# 用户浏览器缓存的浏览器文件配置
USER_DATA_DIR = "%s_user_data_dir"  # %s will be replaced by platform name

# 爬取视频/帖子的数量控制
CRAWLER_MAX_NOTES_COUNT = 20

# 并发爬虫数量控制
MAX_CONCURRENCY_NUM = 4

# 评论关键词筛选(只会留下包含关键词的评论,为空不限制)
COMMENT_KEYWORDS = [
    # "真棒"
    # ........................
]


