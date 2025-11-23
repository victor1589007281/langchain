"""日志配置"""

import logging
import sys
from pathlib import Path
from app.core.config import settings


def setup_logging():
    """设置日志配置"""

    # 创建日志目录
    log_dir = Path(settings.LOG_FILE).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    # 配置日志格式
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # 配置根日志记录器
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format=log_format,
        handlers=[
            # 控制台输出
            logging.StreamHandler(sys.stdout),
            # 文件输出
            logging.FileHandler(settings.LOG_FILE, encoding="utf-8")
        ]
    )

    # 设置第三方库的日志级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)

