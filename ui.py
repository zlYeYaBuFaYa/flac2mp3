"""
NiceGUI 用户界面模块
实现 FLAC to MP3 转换器的图形界面
"""
from nicegui import ui
from pathlib import Path
from typing import List, Optional
import asyncio
from converter import AudioConverter
import logging

logger = logging.getLogger(__name__)


class ConverterUI:
    """转换器用户界面类"""
    
    def __init__(self):
        """初始化界面"""
        self.converter = None
        self.selected_files: List[Path] = []
        self.is_file_mode = True
        self.is_converting = False
        
        # UI 组件
        self.file_btn = None
        self.folder_btn = None
        self.file_upload = None
        self.folder_upload = None
        self.selected_files_label = None
        self.quality_select = None
        self.convert_btn = None
        self.progress_bar = None
        self.status_label = None
        self.log_area = None
        
        self._init_converter()
        self._setup_ui()
    
    def _init_converter(self):
        """初始化音频转换器"""
        try:
            self.converter = AudioConverter()
        except RuntimeError as e:
            logger.error(f"初始化转换器失败: {e}")
            ui.notify(f"错误: {e}", type="negative", position="top")
    
    def _setup_ui(self):
        """设置用户界面"""
        # 设置页面样式
        ui.add_head_html("""
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                padding: 40px;
                max-width: 600px;
                margin: 20px auto;
            }
            .header {
                text-align: center;
                margin-bottom: 40px;
            }
            .header h1 {
                color: #333;
                font-size: 28px;
                font-weight: 600;
                margin-bottom: 8px;
            }
            .header p {
                color: #666;
                font-size: 14px;
            }
            .form-group {
                margin-bottom: 30px;
                text-align: center;
            }
            .form-group label {
                display: block;
                color: #333;
                font-size: 14px;
                font-weight: 500;
                margin-bottom: 10px;
                text-align: center;
            }
            .file-selector {
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
                justify-content: center;
            }
            .file-btn {
                flex: 1;
                max-width: 200px;
                min-width: 150px;
                padding: 14px 20px;
                background: #f5f5f5;
                border: 2px dashed #ddd;
                border-radius: 12px;
                text-align: center;
                font-size: 14px;
                color: #666;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .file-btn:hover {
                background: #e8e8e8;
                border-color: #667eea;
                color: #667eea;
            }
            .file-btn.active {
                background: #667eea;
                border-color: #667eea;
                color: white;
            }
            .selected-files {
                margin-top: 15px;
                padding: 12px;
                background: #f8f9fa;
                border-radius: 8px;
                font-size: 13px;
                color: #666;
                min-height: 40px;
                text-align: center;
            }
            .selected-files.empty {
                color: #999;
                font-style: italic;
            }
            .info-text {
                font-size: 12px;
                color: #999;
                margin-top: 8px;
                text-align: center;
            }
            .convert-btn {
                width: 100%;
                padding: 16px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                margin-top: 10px;
            }
            .convert-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
            }
            .convert-btn:disabled {
                background: #ccc;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }
        </style>
        """)
        
        with ui.card().classes("container"):
            # 标题区域
            with ui.column().classes("header").style("text-align: center;"):
                ui.label("🎵 FLAC to MP3 转换器").classes("text-h4 text-weight-bold").style("text-align: center;")
                ui.label("轻松将 FLAC 音频文件转换为 MP3 格式").classes("text-body2 text-grey-7").style("text-align: center;")
            
            # 文件选择区域
            with ui.column().classes("form-group"):
                with ui.row().style("width: 100%; justify-content: center;"):
                    ui.label("选择文件或文件夹").classes("text-weight-medium")
                
                # 文件/文件夹切换按钮 - 使用居中容器
                with ui.row().classes("file-selector gap-2").style("width: 100%; justify-content: center; margin: 0 auto;"):
                    self.file_btn = ui.button("选择文件", on_click=self._switch_to_file_mode).classes("file-btn")
                    self.folder_btn = ui.button("选择文件夹", on_click=self._switch_to_folder_mode).classes("file-btn")
                
                # 文件上传组件 - 居中
                with ui.row().style("width: 100%; justify-content: center;"):
                    self.file_upload = ui.upload(
                        on_upload=self._handle_file_upload,
                        auto_upload=True,
                        multiple=True
                    ).props("accept=.flac").style("max-width: 500px; width: 100%;")
                
                # 文件夹上传提示
                with ui.row().style("width: 100%; justify-content: center;"):
                    self.folder_hint = ui.label(
                        "提示：在文件选择模式下，可以按住 Ctrl/Cmd 键选择多个文件，或直接选择文件夹中的所有 FLAC 文件"
                    ).classes("text-caption text-grey-6 mt-2").style("display: none; text-align: center;")
                
                # 已选择文件显示
                with ui.row().style("width: 100%; justify-content: center;"):
                    self.selected_files_label = ui.label("未选择任何文件").classes("selected-files empty")
            
            # 质量选择区域
            with ui.column().classes("form-group"):
                with ui.row().style("width: 100%; justify-content: center;"):
                    ui.label("转换质量").classes("text-weight-medium")
                
                with ui.row().style("width: 100%; justify-content: center;"):
                    self.quality_select = ui.select(
                        {
                            "320": "高质量 (320 kbps) - 推荐",
                            "256": "标准质量 (256 kbps)",
                            "192": "中等质量 (192 kbps)",
                            "128": "普通质量 (128 kbps)"
                        },
                        value="320",
                        label="比特率"
                    ).style("max-width: 500px; width: 100%;")
                
                with ui.row().style("width: 100%; justify-content: center;"):
                    ui.label("更高的比特率意味着更好的音质，但文件也会更大").classes("info-text")
            
            # 转换按钮
            with ui.row().style("width: 100%; justify-content: center; margin-top: 10px;"):
                self.convert_btn = ui.button(
                    "开始转换",
                    on_click=self._start_conversion
                ).classes("convert-btn").props("color=primary").style("max-width: 500px; width: 100%;")
            
            # 进度条
            self.progress_bar = ui.linear_progress(show_value=False).classes("w-full mt-4").style("display: none")
            
            # 状态标签
            self.status_label = ui.label("").classes("text-center mt-2")
            
            # 日志区域
            with ui.expansion("转换日志", icon="description").classes("w-full mt-4"):
                self.log_area = ui.log().classes("w-full h-40")
        
        # 初始化文件模式
        self._switch_to_file_mode()
    
    def _switch_to_file_mode(self):
        """切换到文件选择模式"""
        self.is_file_mode = True
        self.file_btn.classes("active", remove="")
        self.folder_btn.classes(remove="active")
        self.file_upload.style("display: block")
        self.folder_hint.style("display: none")
        self.selected_files = []
        self.selected_files_label.text = "未选择任何文件"
        self.selected_files_label.classes("empty", remove="")
    
    def _switch_to_folder_mode(self):
        """切换到文件夹选择模式"""
        self.is_file_mode = False
        self.folder_btn.classes("active", remove="")
        self.file_btn.classes(remove="active")
        self.folder_hint.style("display: block")
        self.file_upload.style("display: block")  # 仍然使用文件上传，但提示选择文件夹中的所有文件
        self.selected_files = []
        self.selected_files_label.text = "未选择任何文件夹"
        self.selected_files_label.classes("empty", remove="")
        ui.notify("提示：请选择文件夹中的所有 FLAC 文件", type="info")
    
    def _get_mp3_output_dir(self, file_or_folder_path: Path) -> Path:
        """
        根据选择的文件或文件夹，确定 mp3 输出目录
        
        Args:
            file_or_folder_path: 选择的文件或文件夹路径
        
        Returns:
            mp3 输出目录路径
        """
        # 如果是文件，获取其父目录
        if file_or_folder_path.is_file():
            parent_dir = file_or_folder_path.parent
        else:
            # 如果是文件夹，使用该文件夹
            parent_dir = file_or_folder_path
        
        # 在父目录的同级创建 mp3 文件夹
        # 例如: /Users/Music/FLAC/song.flac -> /Users/Music/mp3/
        # 或: /Users/Music/FLAC/ -> /Users/Music/mp3/
        grandparent_dir = parent_dir.parent
        mp3_dir = grandparent_dir / "mp3"
        
        # 创建 mp3 目录（如果不存在）
        mp3_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"MP3 输出目录: {mp3_dir}")
        return mp3_dir
    
    def _handle_file_upload(self, e):
        """处理文件上传"""
        try:
            # NiceGUI 的 upload 事件结构：
            # e.file.name - 文件名
            # e.file._path - NiceGUI 已保存的临时文件路径
            # e.file.content_type - 文件 MIME 类型
            
            print(f"\n[DEBUG] ===== 文件上传事件 =====")
            
            # 从事件对象获取文件信息
            if not hasattr(e, 'file'):
                error_msg = "事件对象中没有 file 属性"
                print(f"[ERROR] {error_msg}")
                print(f"[ERROR] 事件对象: {e}")
                ui.notify(error_msg, type="negative")
                return
            
            file_obj = e.file
            file_name = file_obj.name
            file_path = Path(file_obj._path)  # NiceGUI 已经保存好的临时文件路径
            
            print(f"[INFO] 文件名: {file_name}")
            print(f"[INFO] 文件类型: {file_obj.content_type}")
            print(f"[INFO] 临时路径: {file_path}")
            
            # 检查文件扩展名
            if not file_name.lower().endswith('.flac'):
                msg = f"跳过非 FLAC 文件: {file_name}"
                print(f"[WARNING] {msg}")
                ui.notify(msg, type="warning")
                return
            
            # 验证文件存在
            if not file_path.exists():
                error_msg = f"临时文件不存在: {file_path}"
                print(f"[ERROR] {error_msg}")
                ui.notify(error_msg, type="negative")
                return
            
            print(f"[SUCCESS] 文件已上传: {file_name} ({file_path.stat().st_size} 字节)")
            
            # 添加到已选文件列表
            # 直接使用 NiceGUI 保存的临时文件路径
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)
                print(f"[INFO] 已添加到选择列表，当前共 {len(self.selected_files)} 个文件")
            else:
                print(f"[INFO] 文件已在列表中，跳过")
            
            # 更新显示
            if self.selected_files:
                file_names = ", ".join([f.name for f in self.selected_files[:3]])
                if len(self.selected_files) > 3:
                    file_names += f" 等共 {len(self.selected_files)} 个文件"
                display_text = f"已选择 {len(self.selected_files)} 个文件: {file_names}"
                self.selected_files_label.text = display_text
                self.selected_files_label.classes(remove="empty")
                print(f"[UI] 更新显示: {display_text}")
                ui.notify(f"已添加文件: {file_name}", type="positive")
            else:
                self.selected_files_label.text = "未选择任何 FLAC 文件"
                self.selected_files_label.classes("empty", remove="")
            
            print(f"[DEBUG] ===== 文件上传完成 =====\n")
        
        except Exception as ex:
            print(f"\n[ERROR] ===== 处理文件上传时出错 =====")
            print(f"[ERROR] 错误类型: {type(ex)}")
            print(f"[ERROR] 错误信息: {ex}")
            import traceback
            traceback.print_exc()
            logger.error(f"处理文件上传时出错: {ex}", exc_info=True)
            ui.notify(f"文件上传处理失败: {str(ex)}", type="negative")
            print(f"[ERROR] ===== 错误处理完成 =====\n")
    
    async def _start_conversion(self):
        """开始转换"""
        if not self.converter:
            ui.notify("转换器未初始化", type="negative")
            return
        
        if not self.selected_files:
            ui.notify("请先选择要转换的文件或文件夹", type="warning")
            return
        
        if self.is_converting:
            return
        
        # 获取比特率
        bitrate = int(self.quality_select.value)
        
        # 更新 UI 状态
        self.is_converting = True
        self.convert_btn.disable()
        self.convert_btn.text = "转换中..."
        self.progress_bar.style("display: block")
        self.progress_bar.value = 0
        self.status_label.text = "准备开始转换..."
        self.log_area.clear()
        
        try:
            # 收集所有需要转换的文件
            # 上传的文件已经是 Path 对象，直接使用
            all_flac_files = []
            for file_path in self.selected_files:
                path = Path(file_path)
                # 确保文件存在且是 FLAC 文件
                if path.exists() and path.is_file() and path.suffix.lower() == ".flac":
                    all_flac_files.append(path)
            
            if not all_flac_files:
                ui.notify("未找到任何 FLAC 文件", type="warning")
                return
            
            # 确定 mp3 输出目录
            # 使用第一个文件来确定输出目录
            first_file = all_flac_files[0]
            mp3_output_dir = self._get_mp3_output_dir(first_file)
            
            total = len(all_flac_files)
            self.log_area.push(f"找到 {total} 个 FLAC 文件，开始转换...")
            self.log_area.push(f"MP3 输出目录: {mp3_output_dir}")
            
            # 转换文件
            converted_count = 0
            failed_count = 0
            
            for idx, flac_file in enumerate(all_flac_files, 1):
                try:
                    # 更新进度
                    progress = idx / total
                    self.progress_bar.value = progress
                    self.status_label.text = f"正在转换: {flac_file.name} ({idx}/{total})"
                    self.log_area.push(f"[{idx}/{total}] 转换: {flac_file.name}")
                    
                    # 执行转换，输出到 mp3 目录
                    output_file = self.converter.convert_file(
                        flac_file,
                        output_dir=mp3_output_dir,  # 使用 mp3 目录
                        bitrate=bitrate
                    )
                    
                    converted_count += 1
                    self.log_area.push(f"✓ 成功: {output_file.name}")
                    
                    # 让 UI 更新
                    await asyncio.sleep(0.01)
                    
                except Exception as e:
                    failed_count += 1
                    error_msg = f"✗ 失败: {flac_file.name} - {str(e)}"
                    self.log_area.push(error_msg)
                    logger.error(error_msg)
            
            # 转换完成
            self.progress_bar.value = 1.0
            self.status_label.text = f"转换完成！成功: {converted_count}, 失败: {failed_count}"
            
            if failed_count == 0:
                ui.notify(f"转换完成！共转换 {converted_count} 个文件", type="positive")
            else:
                ui.notify(f"转换完成，但有 {failed_count} 个文件失败", type="warning")
            
            self.log_area.push(f"\n转换完成！成功: {converted_count}, 失败: {failed_count}")
            
        except Exception as e:
            error_msg = f"转换过程出错: {str(e)}"
            self.log_area.push(error_msg)
            self.status_label.text = "转换失败"
            ui.notify(error_msg, type="negative")
            logger.error(error_msg)
        
        finally:
            # 恢复 UI 状态
            self.is_converting = False
            self.convert_btn.enable()
            self.convert_btn.text = "开始转换"
            await asyncio.sleep(2)
            self.progress_bar.style("display: none")


def create_app():
    """创建并返回 NiceGUI 应用"""
    app = ConverterUI()
    return app
