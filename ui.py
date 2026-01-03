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
        self.selected_files: List[Path] = []  # 存储文件路径（本地路径）
        self.is_file_mode = True
        self.is_converting = False
        self.selected_folder_path: Optional[Path] = None  # 存储选择的文件夹路径（用于确定输出目录）
        self.client_disconnected = False  # 标记客户端是否已断开
        
        # UI 组件
        self.file_btn = None
        self.folder_btn = None
        self.file_path_input = None
        self.selected_files_label = None
        self.quality_select = None
        self.output_dir_input = None
        self.output_dir_btn = None
        self.output_dir_label = None
        self.convert_btn = None
        self.progress_bar = None
        self.status_label = None
        
        self._init_converter()
        self._setup_ui()
    
    def _init_converter(self):
        """初始化音频转换器"""
        try:
            self.converter = AudioConverter()
        except RuntimeError as e:
            logger.error(f"初始化转换器失败: {e}")
            ui.notify(f"错误: {e}", type="negative", position="top")
    
    def _safe_update_ui(self, update_func, silent=False):
        """安全更新 UI 元素，捕获客户端断开异常"""
        # 如果客户端已断开，直接返回，不再尝试更新
        if self.client_disconnected:
            return False
            
        try:
            update_func()
            return True
        except RuntimeError as e:
            if "client" in str(e).lower() or "deleted" in str(e).lower():
                # 客户端已断开，设置标志并记录一次警告
                if not self.client_disconnected:
                    self.client_disconnected = True
                    if not silent:
                        logger.info("客户端已断开连接，后续 UI 更新将静默跳过")
                return False
            else:
                # 其他运行时错误，继续抛出
                raise
        except Exception as e:
            logger.error(f"更新 UI 时出错: {e}", exc_info=True)
            return False
    
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
                width: 100%;
                margin: 20px auto;
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .header {
                text-align: center;
                margin-bottom: 40px;
                width: 100%;
                display: flex;
                flex-direction: column;
                align-items: center;
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
                width: 100%;
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .form-group label {
                display: block;
                color: #333;
                font-size: 14px;
                font-weight: 500;
                margin-bottom: 10px;
                text-align: center;
            }
            .file-selector-container {
                background: #f8f9fa;
                border-radius: 12px;
                padding: 16px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                margin-top: 24px;
                width: 100%;
                display: flex;
                justify-content: center;
            }
            .file-selector {
                display: flex;
                gap: 12px;
                justify-content: center;
            }
            .file-btn {
                flex: 1;
                min-width: 180px;
                max-width: 180px;
                width: 180px;
                padding: 12px 20px;
                background: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                text-align: center;
                font-size: 14px;
                font-weight: 500;
                color: #555;
                cursor: pointer;
                transition: all 0.2s ease;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            }
            .file-btn:hover {
                background: #f5f5f5;
                border-color: #667eea;
                color: #667eea;
                transform: translateY(-1px);
                box-shadow: 0 2px 6px rgba(102, 126, 234, 0.15);
            }
            .file-btn.active {
                background: #667eea;
                border-color: #667eea;
                color: white;
                box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
            }
            .selected-files {
                margin-top: 12px;
                padding: 10px 14px;
                background: #f8f9fa;
                border-radius: 8px;
                font-size: 13px;
                color: #666;
                min-height: 36px;
                display: flex;
                align-items: center;
                justify-content: center;
                text-align: center;
            }
            .selected-files.empty {
                color: #999;
                font-style: italic;
            }
            .top-controls {
                margin-bottom: 30px;
            }
            .quality-convert-row {
                display: flex;
                gap: 16px;
                align-items: flex-end;
                justify-content: center;
            }
            .quality-wrapper {
                flex: 1;
                max-width: 380px;
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .quality-wrapper label {
                display: block;
                text-align: center;
                margin-bottom: 8px;
            }
            .quality-convert-row .quality-select {
                width: 100%;
                margin: 0;
            }
            .info-text {
                font-size: 12px;
                color: #999;
                margin-top: 8px;
                text-align: center;
            }
            .convert-btn {
                padding: 12px 28px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 15px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s ease;
                box-shadow: 0 3px 12px rgba(102, 126, 234, 0.35);
                min-width: 140px;
                height: fit-content;
            }
            .convert-btn:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 16px rgba(102, 126, 234, 0.45);
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
            with ui.column().classes("header").style("text-align: center; width: 100%; display: flex; flex-direction: column; align-items: center;"):
                ui.label("🎵 FLAC to MP3 转换器").classes("text-h4 text-weight-bold").style("text-align: center; width: 100%; display: block;")
                ui.label("轻松将 FLAC 音频文件转换为 MP3 格式").classes("text-body2 text-grey-7").style("text-align: center; width: 100%; display: block;")
            
            # 比特率选择和开始转换按钮（置顶，并排）
            with ui.column().classes("form-group top-controls").style("width: 100%;"):
                with ui.row().classes("quality-convert-row").style("width: 100%; justify-content: center;"):
                    # 质量选择
                    with ui.column().classes("quality-wrapper"):
                        ui.label("转换质量").classes("text-weight-medium").style("text-align: center;")
                        self.quality_select = ui.select(
                            {
                                "320": "高质量 (320 kbps) - 推荐",
                                "256": "标准质量 (256 kbps)",
                                "192": "中等质量 (192 kbps)",
                                "128": "普通质量 (128 kbps)"
                            },
                            value="320"
                        ).classes("quality-select").style("width: 100%;")
                    
                    # 开始转换按钮
                    self.convert_btn = ui.button(
                        "开始转换",
                        on_click=self._start_conversion
                    ).classes("convert-btn").style("min-width: 140px; padding: 12px 28px; height: fit-content;")
            
            # 输出目录选择区域（隐藏但保留功能）
            with ui.column().classes("form-group").style("display: none;"):
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
            
            # 文件选择区域（与效果图一致）
            with ui.column().classes("form-group").style("width: 100%;"):
                # 路径输入框（隐藏但功能保留）
                self.file_path_input = ui.input(
                    placeholder="请输入文件或文件夹路径",
                    value="",
                    on_change=lambda e: self._parse_and_validate_path()
                ).style("display: none;")
                
                # 已选择文件显示
                self.selected_files_label = ui.label("未选择任何文件").classes("selected-files empty").style("width: 100%; text-align: center;")
            
            # 选择文件/文件夹按钮（底部，阴影背景）
            with ui.card().classes("file-selector-container").style("width: 100%;"):
                with ui.row().classes("file-selector").style("width: 100%; justify-content: center;"):
                    self.file_btn = ui.button("选择文件", on_click=self._set_file_mode).classes("file-btn").style("width: 180px; min-width: 180px; max-width: 180px;")
                    self.folder_btn = ui.button("选择文件夹", on_click=self._set_folder_mode).classes("file-btn").style("width: 180px; min-width: 180px; max-width: 180px;")
            
            # 进度条
            self.progress_bar = ui.linear_progress(show_value=False).classes("w-full mt-4").style("width: 100%; visibility: hidden;")
            
            # 状态标签（支持多行显示）
            self.status_label = ui.label("").classes("text-center mt-2").style("text-align: center; width: 100%; white-space: pre-line;")
        
    def _set_file_mode(self):
        """设置为文件模式（显示路径输入对话框）"""
        self.is_file_mode = True
        self.file_btn.classes("active", remove="")
        self.folder_btn.classes(remove="active")
        # 显示路径输入对话框
        self._show_path_input_dialog()
    
    def _set_folder_mode(self):
        """设置为文件夹模式（显示路径输入对话框）"""
        self.is_file_mode = False
        self.folder_btn.classes("active", remove="")
        self.file_btn.classes(remove="active")
        # 显示路径输入对话框
        self._show_path_input_dialog()
    
    def _show_path_input_dialog(self):
        """显示路径输入对话框"""
        mode_text = "文件" if self.is_file_mode else "文件夹"
        placeholder = f"请输入 FLAC {mode_text}路径" + ("（多个文件用分号;分隔）" if self.is_file_mode else "")
        
        with ui.dialog() as dialog, ui.card().style("min-width: 400px;"):
            ui.label(f"请输入 {mode_text}路径").classes("text-h6")
            path_input = ui.input(
                label="路径",
                placeholder=placeholder,
                value=self.file_path_input.value if self.file_path_input.value else ""
            ).classes("w-full")
            
            with ui.row().classes("w-full justify-end gap-2 mt-4"):
                ui.button("取消", on_click=dialog.close).props("outline")
                def confirm():
                    if path_input.value:
                        self.file_path_input.value = path_input.value
                        self._parse_and_validate_path()
                    dialog.close()
                ui.button("确定", on_click=confirm).props("color=primary")
        
        dialog.open()
    
    def _parse_and_validate_path(self):
        """解析并验证输入的路径"""
        if not self.file_path_input or not self.file_path_input.value:
            path_str = ""
        else:
            path_str = self.file_path_input.value.strip()
        
        if not path_str:
            self.selected_files_label.text = "未选择任何文件"
            self.selected_files_label.classes("empty", remove="")
            self.selected_files = []
            return
        
        try:
            if self.is_file_mode:
                # 文件模式：支持多个文件路径（用分号分隔）
                self.selected_folder_path = None  # 清除文件夹路径
                paths = [p.strip() for p in path_str.split(';') if p.strip()]
                file_paths = []
                
                for p in paths:
                    path = Path(p)
                    if path.exists() and path.is_file():
                        if path.suffix.lower() == '.flac':
                            file_paths.append(path)
                        else:
                            logger.warning(f"跳过非 FLAC 文件: {path.name}")
                    else:
                        logger.warning(f"文件不存在: {path}")
                
                self.selected_files = file_paths
                
                if file_paths:
                    total = len(file_paths)
                    if total <= 3:
                        file_names = ", ".join([f.name for f in file_paths])
                        display_text = f"已选择 {total} 个文件: {file_names}"
                    else:
                        first_three = ", ".join([f.name for f in file_paths[:3]])
                        display_text = f"已选择 {total} 个文件: {first_three} ... (还有 {total - 3} 个文件)"
                    self.selected_files_label.text = display_text
                    self.selected_files_label.classes(remove="empty")
                    ui.notify(f"已选择 {total} 个文件", type="positive")
                else:
                    self.selected_files_label.text = "未找到有效的 FLAC 文件"
                    self.selected_files_label.classes("empty", remove="")
                    ui.notify("未找到有效的 FLAC 文件", type="warning")
            else:
                # 文件夹模式
                folder_path = Path(path_str)
                if folder_path.exists() and folder_path.is_dir():
                    # 保存文件夹路径，用于确定输出目录
                    self.selected_folder_path = folder_path
                    # 查找文件夹中的所有 FLAC 文件（只搜索当前目录，不递归）
                    # 使用 glob 而不是 rglob，避免递归搜索子目录
                    # 使用集合去重，避免大小写不同导致的重复
                    flac_files_set = set()
                    for pattern in ["*.flac", "*.FLAC"]:
                        for file_path in folder_path.glob(pattern):
                            # 只包含文件，不包括目录
                            if file_path.is_file():
                                flac_files_set.add(file_path)
                    # 转换为列表并排序，保持顺序一致
                    flac_files = sorted(list(flac_files_set))
                    self.selected_files = flac_files
                    
                    if flac_files:
                        total = len(flac_files)
                        folder_name = folder_path.name
                        # 优化多文件显示：如果文件数量很多，只显示文件夹名和数量
                        if total > 10:
                            display_text = f"已选择文件夹: {folder_name} (包含 {total} 个 FLAC 文件)"
                        else:
                            # 文件数量不多时，显示部分文件名
                            file_names_preview = ", ".join([f.name for f in flac_files[:3]])
                            if total > 3:
                                display_text = f"已选择文件夹: {folder_name} ({file_names_preview} ... 等 {total} 个文件)"
                            else:
                                display_text = f"已选择文件夹: {folder_name} ({file_names_preview} 共 {total} 个文件)"
                        self.selected_files_label.text = display_text
                        self.selected_files_label.classes(remove="empty")
                        ui.notify(f"已找到 {total} 个 FLAC 文件", type="positive")
                    else:
                        self.selected_files_label.text = f"文件夹 '{folder_name}' 中未找到 FLAC 文件"
                        self.selected_files_label.classes(remove="empty")
                        ui.notify(f"文件夹 '{folder_name}' 中未找到 FLAC 文件", type="warning")
                else:
                    ui.notify(f"文件夹不存在: {folder_path}", type="negative")
                    self.selected_files_label.text = "文件夹不存在"
                    self.selected_files_label.classes(remove="empty")
                    self.selected_files = []
        
        except Exception as e:
            logger.error(f"解析路径失败: {e}", exc_info=True)
            ui.notify(f"路径解析失败: {str(e)}", type="negative")
            self.selected_files_label.text = "路径格式错误"
            self.selected_files_label.classes("empty", remove="")
            self.selected_files = []
    
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
        self.client_disconnected = False  # 重置客户端断开标志
        self._safe_update_ui(lambda: self.convert_btn.disable())
        self._safe_update_ui(lambda: setattr(self.convert_btn, 'text', "转换中..."))
        # 显示进度条（使用 visibility 而不是 display，避免布局问题）
        self._safe_update_ui(lambda: self.progress_bar.style("visibility: visible;"))
        self._safe_update_ui(lambda: setattr(self.progress_bar, 'value', 0))
        self._safe_update_ui(lambda: setattr(self.status_label, 'text', "准备开始转换..."))
        
        try:
            # 直接使用选择的文件路径（已经是本地路径，不需要上传）
            # 使用集合去重，避免重复文件
            all_flac_files_set = set()
            
            print(f"\n[DEBUG] ===== 开始转换 =====")
            print(f"[DEBUG] 已选择的文件数: {len(self.selected_files)}")
            
            for idx, file_path in enumerate(self.selected_files):
                print(f"[DEBUG] 检查文件 {idx + 1}: {file_path}")
                
                # 确保文件存在且是 FLAC 文件
                if file_path.exists() and file_path.is_file():
                    if file_path.suffix.lower() == '.flac':
                        # 使用文件路径的绝对路径作为键，确保去重
                        all_flac_files_set.add(file_path.resolve())
                        print(f"[INFO] ✓ 添加文件: {file_path.name}")
                    else:
                        print(f"[WARNING] ✗ 跳过非 FLAC 文件: {file_path.name}")
                else:
                    print(f"[ERROR] ✗ 文件不存在或不是文件: {file_path}")
            
            # 转换为列表并排序，保持顺序一致
            all_flac_files = sorted(list(all_flac_files_set))
            print(f"[INFO] 收集到 {len(all_flac_files)} 个有效的 FLAC 文件（已去重）")
            
            if not all_flac_files:
                error_msg = "未找到任何 FLAC 文件。请检查选择的文件路径是否正确。"
                print(f"[ERROR] {error_msg}")
                ui.notify(error_msg, type="warning")
                return
            
            # 自动确定输出目录
            # 如果选择的是文件，在文件的父目录的同级目录创建 mp3 文件夹
            # 如果选择的是文件夹，在文件夹的同级目录创建 mp3 文件夹
            if self.is_file_mode:
                # 文件模式：取第一个文件的父目录，在其同级目录创建 mp3 文件夹
                first_file = all_flac_files[0]
                parent_dir = first_file.parent
                mp3_output_dir = parent_dir.parent / "mp3"
                print(f"[INFO] 文件模式：使用第一个文件的父目录 {parent_dir} 的同级目录创建 mp3 文件夹")
            else:
                # 文件夹模式：在选择的文件夹的同级目录创建 mp3 文件夹
                if self.selected_folder_path:
                    folder_path = self.selected_folder_path
                else:
                    # 如果没有保存文件夹路径，使用第一个文件的父目录（回退方案）
                    folder_path = all_flac_files[0].parent
                mp3_output_dir = folder_path.parent / "mp3"
                print(f"[INFO] 文件夹模式：在文件夹 {folder_path} 的同级目录创建 mp3 文件夹")
            
            # 创建输出目录
            try:
                mp3_output_dir.mkdir(parents=True, exist_ok=True)
                print(f"[INFO] 输出目录已准备: {mp3_output_dir}")
            except Exception as ex:
                error_msg = f"无法创建输出目录: {mp3_output_dir} - {str(ex)}"
                print(f"[ERROR] {error_msg}")
                ui.notify(error_msg, type="negative")
                return
            
            total = len(all_flac_files)
            self._safe_update_ui(lambda: setattr(self.status_label, 'text', f"准备转换 {total} 个文件..."))
            
            # 转换文件
            converted_count = 0
            failed_count = 0
            
            for idx, flac_file in enumerate(all_flac_files, 1):
                try:
                    # 更新进度（0-1之间的值）
                    progress = idx / total
                    progress_percent = int(progress * 100)
                    status_text = f"正在转换: {flac_file.name} ({idx}/{total}) - {progress_percent}%"
                    
                    # 安全更新UI元素（使用默认参数避免闭包问题）
                    self._safe_update_ui(lambda p=progress: setattr(self.progress_bar, 'value', p))
                    self._safe_update_ui(lambda text=status_text: setattr(self.status_label, 'text', text))
                    
                    # 执行转换，输出到 mp3 目录
                    output_file = self.converter.convert_file(
                        flac_file,
                        output_dir=mp3_output_dir,  # 使用 mp3 目录
                        bitrate=bitrate
                    )
                    
                    converted_count += 1
                    
                    # 更新进度状态（转换成功后）
                    success_status_text = f"已转换 {idx}/{total} 个文件 ({progress_percent}%) - 当前: {flac_file.name}"
                    self._safe_update_ui(lambda text=success_status_text: setattr(self.status_label, 'text', text))
                    
                    # 让 UI 更新
                    await asyncio.sleep(0.01)
                    
                except Exception as e:
                    failed_count += 1
                    error_msg = f"✗ 失败: {flac_file.name} - {str(e)}"
                    logger.error(error_msg)
                    
                    # 更新进度状态（即使失败也更新）
                    progress_percent = int((idx / total) * 100)
                    error_status_text = f"已处理 {idx}/{total} 个文件 ({progress_percent}%) - 当前失败: {flac_file.name}"
                    self._safe_update_ui(lambda text=error_status_text: setattr(self.status_label, 'text', text))
            
            # 转换完成
            self._safe_update_ui(lambda: setattr(self.progress_bar, 'value', 1.0))
            
            # 生成完成提示信息
            if failed_count == 0:
                completion_msg = f"✅ 转换完成！成功转换 {converted_count} 个文件"
                completion_detail = f"所有文件已保存到: {mp3_output_dir}"
                final_status_text = f"{completion_msg}\n{completion_detail}"
                self._safe_update_ui(lambda text=final_status_text: setattr(self.status_label, 'text', text))
                self._safe_update_ui(lambda msg=completion_msg: ui.notify(msg, type="positive", timeout=5))
            else:
                completion_msg = f"⚠️ 转换完成：成功 {converted_count} 个，失败 {failed_count} 个"
                completion_detail = f"成功文件已保存到: {mp3_output_dir}"
                final_status_text = f"{completion_msg}\n{completion_detail}"
                self._safe_update_ui(lambda text=final_status_text: setattr(self.status_label, 'text', text))
                self._safe_update_ui(lambda msg=completion_msg: ui.notify(msg, type="warning", timeout=5))
            
        except Exception as e:
            error_msg = f"❌ 转换过程出错: {str(e)}"
            self._safe_update_ui(lambda text=error_msg: setattr(self.status_label, 'text', text), silent=True)
            self._safe_update_ui(lambda msg=error_msg: ui.notify(msg, type="negative", timeout=5), silent=True)
            logger.error(error_msg, exc_info=True)
        
        finally:
            # 恢复 UI 状态
            self.is_converting = False
            # 注意：如果客户端已断开，不再尝试更新UI
            if not self.client_disconnected:
                try:
                    self.convert_btn.enable()
                    self.convert_btn.text = "开始转换"
                    # 保持进度条和状态标签显示一段时间，让用户看到完成信息
                    await asyncio.sleep(3)
                    # 隐藏进度条（但保留布局空间）
                    self.progress_bar.style("visibility: hidden;")
                except RuntimeError as e:
                    # 如果客户端已断开，只记录日志
                    if "client" in str(e).lower() or "deleted" in str(e).lower():
                        self.client_disconnected = True
                        logger.info("客户端已断开，跳过 UI 状态恢复")
                    else:
                        raise
            else:
                # 客户端已断开，只记录日志
                logger.info("转换完成（客户端已断开，UI 状态未恢复）")


def create_app():
    """创建并返回 NiceGUI 应用"""
    app = ConverterUI()
    return app
