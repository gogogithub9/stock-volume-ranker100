import os
from datetime import datetime

# ============ Database Configuration ============
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'db', 'stock_volume.db')
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

# ============ Crawler Configuration ============
CRAWLER_INTERVAL = 600  # 爬虫执行间隔（秒），600 = 10分钟
TOP_N = 100             # 爬取排名数量
TIMEOUT = 30            # 请求超时时间（秒）
RETRY_COUNT = 3         # 重试次数
RETRY_DELAY = 5         # 重试延迟（秒）

# ============ Data Source Configuration ============
# 优先级：AkShare > Tushare
USE_AKSHARE = True      # 使用AkShare数据源
USE_TUSHARE = True      # 使用Tushare数据源（备用）
TUSHARE_TOKEN = ''      # Tushare Token（如需使用，请填写）

# ============ Web Application Configuration ============
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5000
FLASK_DEBUG = False
SECRET_KEY = 'stock-volume-ranker-secret-key-2024'

# ============ Logging Configuration ============
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'crawler.log')
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR
LOG_MAX_BYTES = 10485760  # 10MB
LOG_BACKUP_COUNT = 5

# ============ API Configuration ============
API_MAX_RESULTS = 1000
API_DEFAULT_LIMIT = 100
API_HISTORY_DAYS = 90  # 默认历史数据天数

# ============ System Configuration ============
START_TIME = datetime.now()
VERSION = '1.0.0'
