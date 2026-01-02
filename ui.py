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
        self.selected_files: List[Path] = []  # 存储文件路径
        self.selected_file_names: dict = {}  # 存储原始文件名映射 {path: original_name}
        self.is_file_mode = True
        self.is_converting = False
        self.output_dir: Optional[Path] = None
        
        # UI 组件
        self.file_btn = None
        self.folder_btn = None
        self.file_upload = None
        self.folder_upload = None
        self.selected_files_label = None
        self.quality_select = None
        self.output_dir_input = None
        self.output_dir_btn = None
        self.output_dir_label = None
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
            
            # 输出目录选择区域
            with ui.column().classes("form-group"):
                with ui.row().style("width: 100%; justify-content: center;"):
                    ui.label("输出目录").classes("text-weight-medium")
                
                with ui.row().style("width: 100%; justify-content: center; max-width: 500px; gap: 10px;"):
                    self.output_dir_input = ui.input(
                        label="MP3 输出目录路径",
                        placeholder="例如: C:/Users/username/Music/MP3 或 /Users/username/Music/MP3",
                        value="",
                        on_change=self._validate_output_dir
                    ).style("flex: 1;")
                    self.output_dir_btn = ui.button(
                        "验证",
                        on_click=self._validate_output_dir_click,
                        icon="check"
                    ).props("outline")
                
                with ui.row().style("width: 100%; justify-content: center;"):
                    self.output_dir_label = ui.label("请输入 MP3 文件的输出目录").classes("text-caption text-grey-6")
            
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
        self.selected_file_names = {}
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
        self.selected_file_names = {}
        self.selected_files_label.text = "未选择任何文件夹"
        self.selected_files_label.classes("empty", remove="")
        ui.notify("提示：请选择文件夹中的所有 FLAC 文件", type="info")
    
    def _validate_output_dir(self, e=None):
        """验证输出目录路径"""
        if not self.output_dir_input.value:
            self.output_dir_label.text = "请输入 MP3 文件的输出目录"
            self.output_dir_label.classes(remove="text-green text-red")
            self.output_dir = None
            return
        
        try:
            path = Path(self.output_dir_input.value.strip())
            if path.exists() and path.is_dir():
                # 验证目录是否可写
                test_file = path / ".test_write"
                try:
                    test_file.touch()
                    test_file.unlink()
                    self.output_dir = path
                    self.output_dir_label.text = f"✓ 输出目录有效: {path}"
                    self.output_dir_label.classes(remove="text-red")
                    self.output_dir_label.classes("text-green")
                except Exception:
                    self.output_dir_label.text = f"✗ 目录不可写: {path}"
                    self.output_dir_label.classes(remove="text-green")
                    self.output_dir_label.classes("text-red")
                    self.output_dir = None
            elif not path.exists():
                # 检查父目录是否存在
                parent = path.parent
                if parent.exists() and parent.is_dir():
                    self.output_dir_label.text = f"⚠ 目录不存在，转换时将自动创建: {path}"
                    self.output_dir_label.classes(remove="text-green text-red")
                    self.output_dir = path  # 允许创建新目录
                else:
                    self.output_dir_label.text = f"✗ 路径无效，父目录不存在: {path}"
                    self.output_dir_label.classes(remove="text-green")
                    self.output_dir_label.classes("text-red")
                    self.output_dir = None
            else:
                self.output_dir_label.text = f"✗ 路径不是目录: {path}"
                self.output_dir_label.classes(remove="text-green")
                self.output_dir_label.classes("text-red")
                self.output_dir = None
        except Exception as ex:
            self.output_dir_label.text = f"✗ 路径格式错误: {str(ex)}"
            self.output_dir_label.classes(remove="text-green")
            self.output_dir_label.classes("text-red")
            self.output_dir = None
    
    async def _validate_output_dir_click(self):
        """点击验证按钮"""
        self._validate_output_dir()
        if self.output_dir:
            ui.notify(f"输出目录已设置: {self.output_dir}", type="positive")
        else:
            ui.notify("请检查输出目录路径是否正确", type="warning")
    
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
            temp_path = Path(file_obj._path)  # NiceGUI 的临时文件路径
            
            print(f"[INFO] 文件名: {file_name}")
            print(f"[INFO] 文件类型: {file_obj.content_type}")
            print(f"[INFO] NiceGUI 临时路径: {temp_path}")
            
            # 检查文件扩展名
            if not file_name.lower().endswith('.flac'):
                msg = f"跳过非 FLAC 文件: {file_name}"
                print(f"[WARNING] {msg}")
                ui.notify(msg, type="warning")
                return
            
            # 验证临时文件存在
            if not temp_path.exists():
                error_msg = f"NiceGUI 临时文件不存在: {temp_path}"
                print(f"[ERROR] {error_msg}")
                ui.notify(error_msg, type="negative")
                return
            
            # 将文件复制到持久的临时目录
            # 因为 NiceGUI 的临时文件会被自动清理
            import tempfile
            import shutil
            
            persistent_temp_dir = Path(tempfile.gettempdir()) / "flac2mp3_uploads"
            persistent_temp_dir.mkdir(exist_ok=True)
            
            # 使用原始文件名保存
            persistent_file = persistent_temp_dir / file_name
            
            print(f"[INFO] 复制文件到持久目录: {persistent_file}")
            shutil.copy2(temp_path, persistent_file)
            
            if not persistent_file.exists():
                error_msg = f"复制文件失败: {persistent_file}"
                print(f"[ERROR] {error_msg}")
                ui.notify(error_msg, type="negative")
                return
            
            print(f"[SUCCESS] 文件已保存: {file_name} ({persistent_file.stat().st_size} 字节)")
            
            # 添加到已选文件列表
            # 使用持久化的文件路径
            if persistent_file not in self.selected_files:
                self.selected_files.append(persistent_file)
                # 保存原始文件名映射
                self.selected_file_names[persistent_file] = file_name
                print(f"[INFO] 已添加到选择列表，当前共 {len(self.selected_files)} 个文件")
                print(f"[INFO] 持久路径: {persistent_file}")
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
            # self.selected_files 中存储的是 Path 对象
            all_flac_files = []
            
            print(f"\n[DEBUG] ===== 开始转换 =====")
            print(f"[DEBUG] 已选择的文件数: {len(self.selected_files)}")
            
            for idx, file_path in enumerate(self.selected_files):
                # 获取原始文件名
                original_name = self.selected_file_names.get(file_path, file_path.name)
                
                print(f"[DEBUG] 检查文件 {idx + 1}:")
                print(f"[DEBUG]   临时路径: {file_path}")
                print(f"[DEBUG]   原始文件名: {original_name}")
                print(f"[DEBUG]   文件存在: {file_path.exists()}")
                print(f"[DEBUG]   是文件: {file_path.is_file()}")
                
                # 确保文件存在且是文件
                if file_path.exists() and file_path.is_file():
                    # 使用原始文件名判断是否为 FLAC 文件
                    if original_name.lower().endswith('.flac'):
                        all_flac_files.append(file_path)
                        print(f"[INFO] ✓ 添加文件: {original_name}")
                    else:
                        print(f"[WARNING] ✗ 跳过非 FLAC 文件: {original_name}")
                else:
                    print(f"[ERROR] ✗ 文件不存在或不是文件: {file_path}")
            
            print(f"[INFO] 收集到 {len(all_flac_files)} 个有效的 FLAC 文件")
            
            if not all_flac_files:
                error_msg = "未找到任何 FLAC 文件。请检查上传的文件是否仍然存在。"
                print(f"[ERROR] {error_msg}")
                ui.notify(error_msg, type="warning")
                return
            
            # 检查输出目录
            if not self.output_dir:
                error_msg = "请先设置 MP3 输出目录"
                print(f"[ERROR] {error_msg}")
                ui.notify(error_msg, type="warning")
                return
            
            # 确保输出目录存在
            mp3_output_dir = self.output_dir
            try:
                mp3_output_dir.mkdir(parents=True, exist_ok=True)
                print(f"[INFO] 输出目录已准备: {mp3_output_dir}")
            except Exception as ex:
                error_msg = f"无法创建输出目录: {mp3_output_dir} - {str(ex)}"
                print(f"[ERROR] {error_msg}")
                ui.notify(error_msg, type="negative")
                return
            
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
