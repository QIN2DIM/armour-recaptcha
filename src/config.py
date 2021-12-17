import os
from os.path import dirname, join, exists

from loguru import logger

__all__ = ["PATH_CHROMEDRIVER", "logger", "PROJECT_DATABASE", "DIR_RUNTIME_CACHE"]
# ---------------------------------------------------
# TODO [√] 项目索引路径定位
# ---------------------------------------------------
# 定位工程根目录 SERVER_DIR_PROJECT
PROJECT_ROOT = dirname(__file__)

# 文件数据库 目录根
PROJECT_DATABASE = join(PROJECT_ROOT, "database")

# chromedriver 可执行文件路径
PATH_CHROMEDRIVER = join(PROJECT_ROOT, "chromedriver.exe")

# 运行缓存目录
DIR_RUNTIME_CACHE = join(PROJECT_DATABASE, "cache")

# ---------------------------------------------------
# TODO [√] 运行日志配置
# ---------------------------------------------------
# 运行日志路径
DIR_LOGGER = join(PROJECT_DATABASE, "logs")
# 运行日志
logger.add(
    sink=join(DIR_LOGGER, "error.log"),
    level="ERROR",
    rotation="1 week",
    encoding="utf8",
)

logger.add(
    sink=join(DIR_LOGGER, "runtime.log"),
    level="DEBUG",
    rotation="1 day",
    retention="20 days",
    encoding="utf8",
)

# ---------------------------------------------------
# TODO [*] 自动调整
# ---------------------------------------------------
# 若chromedriver不在CHROMEDRIVER_PATH指定的路径下 尝试从环境变量中查找路径'
if not exists(PATH_CHROMEDRIVER):
    CHROMEDRIVER_PATH = None

# 目录补全
for _pending in [PROJECT_DATABASE, DIR_RUNTIME_CACHE]:
    if not exists(_pending):
        os.mkdir(_pending)
