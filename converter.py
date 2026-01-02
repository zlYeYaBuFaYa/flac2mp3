"""
音频转换核心模块
使用 ffmpeg 将 FLAC 文件转换为 MP3 格式
"""
import os
import subprocess
import shutil
from pathlib import Path
from typing import List, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class AudioConverter:
    """音频转换器类"""
    
    def __init__(self):
        """初始化转换器，检查 ffmpeg 是否可用"""
        self.ffmpeg_path = self._find_ffmpeg()
        if not self.ffmpeg_path:
            raise RuntimeError("未找到 ffmpeg，请确保已安装并添加到系统 PATH")
    
    def _find_ffmpeg(self) -> Optional[str]:
        """查找系统中的 ffmpeg 可执行文件"""
        ffmpeg_name = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
        ffmpeg_path = shutil.which(ffmpeg_name)
        return ffmpeg_path
    
    def _get_flac_files(self, path: Path) -> List[Path]:
        """获取路径中的所有 FLAC 文件"""
        flac_files = []
        
        if path.is_file():
            if path.suffix.lower() == ".flac":
                flac_files.append(path)
        elif path.is_dir():
            # 递归查找目录中的所有 FLAC 文件
            flac_files = list(path.rglob("*.flac"))
            # 也支持大写扩展名
            flac_files.extend(path.rglob("*.FLAC"))
        
        return flac_files
    
    def convert_file(
        self,
        input_file: Path,
        output_dir: Optional[Path] = None,
        bitrate: int = 320,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> Path:
        """
        转换单个 FLAC 文件为 MP3
        
        Args:
            input_file: 输入的 FLAC 文件路径
            output_dir: 输出目录，如果为 None 则输出到输入文件同目录
            bitrate: MP3 比特率 (kbps)
            progress_callback: 进度回调函数 (file_name, current, total)
        
        Returns:
            输出的 MP3 文件路径
        """
        if not input_file.exists():
            raise FileNotFoundError(f"文件不存在: {input_file}")
        
        # 确定输出文件路径
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"{input_file.stem}.mp3"
        else:
            output_file = input_file.parent / f"{input_file.stem}.mp3"
        
        # 构建 ffmpeg 命令
        cmd = [
            self.ffmpeg_path,
            "-i", str(input_file),
            "-codec:a", "libmp3lame",
            "-b:a", f"{bitrate}k",
            "-y",  # 覆盖已存在的文件
            str(output_file)
        ]
        
        try:
            # 执行转换
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"转换成功: {input_file.name} -> {output_file.name}")
            return output_file
        except subprocess.CalledProcessError as e:
            error_msg = f"转换失败: {input_file.name}\n错误信息: {e.stderr}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def convert_files(
        self,
        input_paths: List[Path],
        output_dir: Optional[Path] = None,
        bitrate: int = 320,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> List[Path]:
        """
        批量转换 FLAC 文件为 MP3
        
        Args:
            input_paths: 输入文件或目录路径列表
            output_dir: 输出目录，如果为 None 则输出到输入文件同目录
            bitrate: MP3 比特率 (kbps)
            progress_callback: 进度回调函数 (file_name, current, total)
        
        Returns:
            输出的 MP3 文件路径列表
        """
        # 收集所有 FLAC 文件
        all_flac_files = []
        for path in input_paths:
            flac_files = self._get_flac_files(Path(path))
            all_flac_files.extend(flac_files)
        
        if not all_flac_files:
            raise ValueError("未找到任何 FLAC 文件")
        
        total = len(all_flac_files)
        output_files = []
        failed_files = []
        
        for idx, flac_file in enumerate(all_flac_files, 1):
            try:
                if progress_callback:
                    progress_callback(flac_file.name, idx, total)
                
                output_file = self.convert_file(
                    flac_file,
                    output_dir=output_dir,
                    bitrate=bitrate
                )
                output_files.append(output_file)
            except Exception as e:
                logger.error(f"转换失败: {flac_file.name} - {str(e)}")
                failed_files.append((flac_file.name, str(e)))
        
        if failed_files:
            failed_msg = "\n".join([f"{name}: {error}" for name, error in failed_files])
            logger.warning(f"部分文件转换失败:\n{failed_msg}")
        
        return output_files
