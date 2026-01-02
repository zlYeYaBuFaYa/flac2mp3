"""
FLAC to MP3 转换器主程序
"""
import logging
from nicegui import ui
from ui import ConverterUI

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@ui.page('/')
def index():
    """主页面"""
    ConverterUI()


if __name__ in {"__main__", "__mp_main__"}:
    # 启动应用
    ui.run(
        title="FLAC to MP3 转换器",
        favicon="🎵",
        port=8080,
        show=True,  # 自动打开浏览器
        reload=False  # 生产环境关闭自动重载
    )
