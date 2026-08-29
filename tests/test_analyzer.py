import base64
import os
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch

import requests
from PIL import Image

import analyzer


class FakeResponse:
    def __init__(self, payload=None, error=None):
        self.payload = payload
        self.error = error

    def raise_for_status(self):
        if self.error:
            raise self.error

    def json(self):
        return self.payload


class AnalyzerTestCase(unittest.TestCase):
    def setUp(self):
        self.logging_patch = patch("analyzer.logging.info")
        self.logging_patch.start()
        self.addCleanup(self.logging_patch.stop)


class DeepSeekClientTests(AnalyzerTestCase):
    def setUp(self):
        super().setUp()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.image_path = os.path.join(self.temp_dir.name, "screen.png")
        Image.new("RGB", (16, 12), "white").save(self.image_path, format="PNG")

    def tearDown(self):
        self.temp_dir.cleanup()
        super().tearDown()

    def make_client(self, mode="auto"):
        with patch.object(analyzer, "IMAGE_INPUT_MODE", mode):
            return analyzer.DeepSeekClient()

    def test_base64_request_contains_data_url_and_original_detail(self):
        client = self.make_client("base64")
        response = FakeResponse(
            {"choices": [{"message": {"content": "分析完成"}}]}
        )
        with patch("analyzer.requests.post", return_value=response) as post:
            result = client.ask_image(self.image_path, "分析图片", "系统提示")

        self.assertEqual(result, "分析完成")
        request = post.call_args.kwargs
        messages = request["json"]["messages"]
        self.assertEqual(messages[0], {"role": "system", "content": "系统提示"})
        content = messages[1]["content"]
        self.assertEqual(content[0], {"type": "text", "text": "分析图片"})
        self.assertEqual(content[1]["type"], "image_url")
        self.assertEqual(content[1]["image_url"]["detail"], "original")
        data_url = content[1]["image_url"]["url"]
        prefix, encoded = data_url.split(",", 1)
        self.assertEqual(prefix, "data:image/png;base64")
        with open(self.image_path, "rb") as image_file:
            self.assertEqual(base64.b64decode(encoded), image_file.read())

    def test_files_api_upload_and_file_id_reference(self):
        client = self.make_client("files_api")
        upload_response = FakeResponse({"id": "file-api-test"})
        chat_response = FakeResponse(
            {"choices": [{"message": {"content": "文件分析完成"}}]}
        )
        with patch(
            "analyzer.requests.post", side_effect=[upload_response, chat_response]
        ) as post:
            result = client.ask_image(self.image_path, "分析图片", "系统提示")

        self.assertEqual(result, "文件分析完成")
        self.assertEqual(post.call_count, 2)
        upload_call = post.call_args_list[0]
        self.assertEqual(upload_call.args[0], analyzer.DEEPSEEK_CONFIG["files_url"])
        self.assertEqual(upload_call.kwargs["data"]["purpose"], "user_data")
        self.assertEqual(
            upload_call.kwargs["data"]["expires_after[anchor]"], "created_at"
        )
        self.assertEqual(
            upload_call.kwargs["data"]["expires_after[seconds]"], "10800"
        )
        file_tuple = upload_call.kwargs["files"]["file"]
        self.assertEqual(file_tuple[0], "screen.png")
        self.assertEqual(file_tuple[2], "image/png")

        chat_content = post.call_args_list[1].kwargs["json"]["messages"][1]["content"]
        self.assertEqual(
            chat_content[1], {"type": "file", "file_id": "file-api-test"}
        )

    def test_auto_mode_uses_documented_32_mib_boundary(self):
        client = self.make_client("auto")
        self.assertEqual(
            client._resolve_image_mode(analyzer.BASE64_IMAGE_LIMIT), "base64"
        )
        self.assertEqual(
            client._resolve_image_mode(analyzer.BASE64_IMAGE_LIMIT + 1), "files_api"
        )

    def test_explicit_base64_rejects_image_over_32_mib(self):
        client = self.make_client("base64")
        with self.assertRaisesRegex(ValueError, "32 MiB"):
            client._resolve_image_mode(analyzer.BASE64_IMAGE_LIMIT + 1)

    def test_invalid_image_mode_is_rejected(self):
        with patch.object(analyzer, "IMAGE_INPUT_MODE", "invalid"):
            with self.assertRaisesRegex(ValueError, "IMAGE_INPUT_MODE"):
                analyzer.DeepSeekClient()

    def test_missing_corrupt_unsupported_and_oversized_images(self):
        client = self.make_client()
        missing_path = os.path.join(self.temp_dir.name, "missing.png")
        with self.assertRaisesRegex(ValueError, "不存在"):
            client._inspect_image(missing_path)

        corrupt_path = os.path.join(self.temp_dir.name, "corrupt.png")
        with open(corrupt_path, "wb") as corrupt_file:
            corrupt_file.write(b"not an image")
        with self.assertRaisesRegex(ValueError, "损坏或无法识别"):
            client._inspect_image(corrupt_path)

        bitmap_path = os.path.join(self.temp_dir.name, "screen.bmp")
        Image.new("RGB", (4, 4), "black").save(bitmap_path, format="BMP")
        with self.assertRaisesRegex(ValueError, "不支持的图片格式 BMP"):
            client._inspect_image(bitmap_path)

        with patch(
            "analyzer.os.path.getsize", return_value=analyzer.FILES_API_IMAGE_LIMIT + 1
        ):
            with self.assertRaisesRegex(ValueError, "64 MiB"):
                client._inspect_image(self.image_path)

        oversized_dimensions_path = os.path.join(self.temp_dir.name, "wide.png")
        Image.new("RGB", (analyzer.MAX_IMAGE_EDGE + 1, 1), "white").save(
            oversized_dimensions_path, format="PNG"
        )
        with self.assertRaisesRegex(ValueError, "8192 像素"):
            client._inspect_image(oversized_dimensions_path)

    def test_upload_and_chat_http_errors_are_propagated(self):
        client = self.make_client("files_api")
        http_error = requests.HTTPError("request failed")
        with patch(
            "analyzer.requests.post", return_value=FakeResponse(error=http_error)
        ):
            with self.assertRaises(requests.HTTPError):
                client.ask_image(self.image_path, "分析图片", "系统提示")

        client = self.make_client("base64")
        with patch(
            "analyzer.requests.post", return_value=FakeResponse(error=http_error)
        ):
            with self.assertRaises(requests.HTTPError):
                client.ask_image(self.image_path, "分析图片", "系统提示")


class MultiModelAnalyzerTests(AnalyzerTestCase):
    def test_ocr_disabled_does_not_import_easyocr_and_sends_image(self):
        client = Mock()
        client.ask_image.return_value = "图片答案"
        with (
            patch.object(analyzer, "OCR_ENABLED", False),
            patch("analyzer.DeepSeekClient", return_value=client),
            patch.dict(sys.modules, {"easyocr": None}),
        ):
            image_analyzer = analyzer.MultiModelAnalyzer()
            result = image_analyzer.analyze_image("screen.png")

        self.assertIsNone(image_analyzer.reader)
        self.assertEqual(result, "图片答案")
        client.ask_image.assert_called_once()
        client.ask.assert_not_called()

    def test_ocr_enabled_lazily_initializes_reader_and_sends_text(self):
        reader = Mock()
        reader.readtext.return_value = ["第一行", "第二行"]
        easyocr_module = types.SimpleNamespace(
            Reader=Mock(return_value=reader)
        )
        client = Mock()
        client.ask.return_value = "文本答案"

        with (
            patch.object(analyzer, "OCR_ENABLED", True),
            patch("analyzer.DeepSeekClient", return_value=client),
            patch.dict(sys.modules, {"easyocr": easyocr_module}),
        ):
            image_analyzer = analyzer.MultiModelAnalyzer()
            result = image_analyzer.analyze_image("screen.png")

        easyocr_module.Reader.assert_called_once_with(["ch_sim", "en"])
        reader.readtext.assert_called_once_with("screen.png", detail=0)
        self.assertEqual(result, "文本答案")
        prompt = client.ask.call_args.args[0]
        self.assertIn("第一行\n第二行", prompt)
        client.ask_image.assert_not_called()

    def test_analysis_errors_are_returned_as_readable_message(self):
        client = Mock()
        client.ask_image.side_effect = requests.HTTPError("API unavailable")
        with (
            patch.object(analyzer, "OCR_ENABLED", False),
            patch("analyzer.DeepSeekClient", return_value=client),
            patch("analyzer.logging.error"),
        ):
            image_analyzer = analyzer.MultiModelAnalyzer()
            result = image_analyzer.analyze_image("screen.png")

        self.assertEqual(result, "AI 思考时出错了: API unavailable")


if __name__ == "__main__":
    unittest.main()
