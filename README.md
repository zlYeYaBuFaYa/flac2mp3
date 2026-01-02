# FLAC to MP3 转换器

一个基于 Python 和 NiceGUI 开发的音频格式转换工具，支持将 FLAC 文件批量转换为 MP3 格式。

## 功能特性

- 🎵 支持单个文件或整个文件夹的批量转换
- 🎨 简洁优美的现代化界面设计
- ⚙️ 可调节的 MP3 比特率（128/192/256/320 kbps）
- 📊 实时转换进度显示
- 📝 详细的转换日志
- 🖥️ 跨平台支持（Windows / macOS / Linux）

## 系统要求

- Python 3.8 或更高版本
- FFmpeg（已安装并添加到系统 PATH）

### 检查 FFmpeg 安装

在终端中运行以下命令检查 FFmpeg 是否已安装：

```bash
ffmpeg -version
```

如果未安装，请访问 [FFmpeg 官网](https://ffmpeg.org/download.html) 下载并安装。

## 安装步骤

### 1. 克隆或下载项目

```bash
cd /path/to/flac2mp3
```

### 2. 创建虚拟环境（推荐）

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 启动应用

```bash
python main.py
```

应用会自动在浏览器中打开（默认地址：http://localhost:8080）

### 使用界面

1. **选择文件或文件夹**
   - 点击"选择文件"按钮，选择单个或多个 FLAC 文件
   - 或点击"选择文件夹"按钮，选择包含 FLAC 文件的文件夹

2. **选择转换质量**
   - 从下拉菜单中选择 MP3 比特率：
     - 320 kbps - 高质量（推荐）
     - 256 kbps - 标准质量
     - 192 kbps - 中等质量
     - 128 kbps - 普通质量

3. **选择输出目录**（可选）
   - 默认：MP3 文件会保存在原 FLAC 文件的同一目录下
   - 自定义：选择"选择自定义目录"，然后：
     - 在输入框中输入输出目录的完整路径
     - 点击"验证"按钮验证路径
     - 如果目录不存在，程序会自动创建
     - 路径验证成功后会显示绿色提示

4. **开始转换**
   - 点击"开始转换"按钮
   - 转换过程中会显示进度条和当前转换的文件
   - 转换完成后会显示成功和失败的文件数量

5. **查看日志**
   - 点击"转换日志"展开查看详细的转换信息

### 输出位置

- **默认模式**：转换后的 MP3 文件会保存在原 FLAC 文件的同一目录下
- **自定义模式**：所有转换的 MP3 文件会统一保存到指定的输出目录中

## 项目结构

```
flac2mp3/
├── main.py              # 主程序入口
├── ui.py                # NiceGUI 用户界面模块
├── converter.py         # 音频转换核心模块
├── requirements.txt     # Python 依赖包
├── README.md           # 项目文档
└── preview.html        # 界面效果预览（参考）
```

## 代码说明

### converter.py
音频转换核心模块，使用 FFmpeg 进行格式转换：
- `AudioConverter`: 转换器主类
- `convert_file()`: 转换单个文件，支持自定义输出目录
- `convert_files()`: 批量转换文件，支持自定义输出目录

### ui.py
NiceGUI 用户界面模块：
- `ConverterUI`: 界面主类
- 实现文件/文件夹选择
- 实现转换进度显示
- 实现日志记录

### main.py
应用入口，启动 NiceGUI 服务器。

## 故障排除

### FFmpeg 未找到

**错误信息：** `未找到 ffmpeg，请确保已安装并添加到系统 PATH`

**解决方法：**
1. 确认 FFmpeg 已正确安装
2. 将 FFmpeg 添加到系统 PATH 环境变量
3. 重启终端/命令行窗口

### 转换失败

**可能原因：**
- FLAC 文件损坏
- 输出目录没有写入权限
- 磁盘空间不足

**解决方法：**
- 检查文件是否完整
- 确认有足够的磁盘空间
- 查看转换日志了解详细错误信息

### 端口被占用

如果 8080 端口被占用，可以修改 `main.py` 中的端口号：

```python
ui.run(port=8081)  # 使用其他端口
```

## 开发说明

### 扩展功能

项目采用模块化设计，易于扩展：

1. **添加新的音频格式支持**
   - 修改 `converter.py` 中的转换逻辑
   - 更新文件过滤器

2. **自定义界面样式**
   - 修改 `ui.py` 中的 CSS 样式
   - 使用 NiceGUI 的主题系统

3. **添加新功能**
   - 在 `ConverterUI` 类中添加新的方法
   - 在界面中添加新的 UI 组件

## 许可证

本项目采用 MIT 许可证。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v1.0.0
- 初始版本
- 支持 FLAC 转 MP3
- 支持文件/文件夹批量转换
- 支持可调节比特率
- 现代化界面设计
