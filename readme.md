# Prometheus

截取当前屏幕，使用 DeepSeek 或 Kimi 分析截图内容，并将分析结果和原图发送到邮箱。

## 安装与运行

```shell
pip install requests Pillow pyautogui pynput
python main.py
```

只有启用本地 OCR 时才需要安装 EasyOCR：

```shell
pip install easyocr
```

后台运行(关闭终端也可以)：

```shell
D:\Environment\Anaconda3\pythonw.exe D:\Program\Prometheus\main.py
```

运行后按 `Delete` 截图、分析并发送邮件，按 `Esc` 退出。

## 多模态与 OCR 配置

在 `config.py` 中配置 AI 提供商、API Key、模型和图片处理方式。默认使用
DeepSeek 的 `deepseek-v4-flash-vision-exp`。

切换到 Kimi：

```python
AI_PROVIDER = "kimi"
```

Kimi API Key 推荐通过环境变量提供：

```powershell
$env:MOONSHOT_API_KEY = "你的 API Key"
python main.py
```

也可以直接填写 `KIMI_CONFIG["api_key"]`。默认使用支持视觉输入的 `kimi-k2.6`。
Kimi 的 Base64 模式直接内嵌图片；
Files API 模式以 `purpose=image` 上传，通过 `ms://file_id` 引用，并在对话请求
完成或失败后自动删除临时文件。Kimi Files API 单文件最大 100 MiB。

- `OCR_ENABLED = False`：截图直接发送给多模态模型，不加载 EasyOCR。
- `OCR_ENABLED = True`：先使用 EasyOCR 提取中英文文字，再发送纯文本请求。
- `IMAGE_INPUT_MODE = "base64"`：把图片编码为 Data URL；单图最大 32 MiB。
- `IMAGE_INPUT_MODE = "files_api"`：先上传图片，再通过 `file_id` 引用；单图最大 64 MiB。
- `IMAGE_INPUT_MODE = "auto"`：不超过 32 MiB 时使用 Base64，否则使用 Files API。

## 模型与 OCR 开关

- 使用 `deepseek-v4-flash-vision-exp` 等支持图片输入的多模态模型时，设置
  `OCR_ENABLED = False`，程序会直接把截图发送给模型。
- 使用 `deepseek-v4-flash` 或 `deepseek-v4-pro` 时，必须设置
  `OCR_ENABLED = True`。这两个模型按纯文本链路调用，程序会先使用 EasyOCR
  提取截图文字，再将文字发送给模型；同时需要安装 `easyocr`。

例如，使用 `deepseek-v4-flash`：

```python
OCR_ENABLED = True

DEEPSEEK_CONFIG = {
    # 其他配置保持不变
    "model": "deepseek-v4-flash",
}
```

DeepSeek Files API 上传的截图会设置为创建后 3 小时过期，不会主动删除；Kimi
上传的截图会在使用后立即请求删除。支持的图片格式为 JPEG、PNG、GIF 和 WebP，
单边尺寸最大为 8192 像素。
