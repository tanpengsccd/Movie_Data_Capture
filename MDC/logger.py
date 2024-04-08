# logger.py

from loguru import logger

# 配置loguru，例如设置日志输出路径、日志级别等
logger.add("debugfile_{time}.log", format="{time} {level} {message}", rotation="1 day", level="DEBUG")

# 可选：设置其他loguru选项，例如格式化、旋转日志等
logger.add("infofile_{time}.log", format="{time} {level} {message}", rotation="1 day", level="INFO")
logger.add("errorfile_{time}.log", format="{time} {level} {message}", rotation="1 day", level="ERROR")
