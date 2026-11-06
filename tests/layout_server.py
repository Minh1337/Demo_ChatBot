"""Isolated UI preview: web assets + synthetic transcripts; no API or secrets served."""
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

WEB = Path(__file__).resolve().parents[1] / 'web'


class Preview(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB), **kwargs)

    def do_GET(self):
        if self.path.startswith('/preview'):
            long_chat = parse_qs(urlparse(self.path).query).get('chat') == ['long']
            messages = []
            if long_chat:
                for index in range(18):
                    messages.extend([
                        {'role': 'user', 'content': f'Ví dụ {index + 1}: giải thích cách tìm số đối xứng bằng Python.'},
                        {'role': 'assistant', 'content': 'Một số đối xứng đọc từ trái sang phải và từ phải sang trái đều giống nhau. Chuyển số thành chuỗi rồi so sánh với chuỗi đảo ngược.\n\n```python\nn = int(input("Nhập số: "))\ns = str(n)\nprint(s == s[::-1])\n```\n\nVí dụ 121 là số đối xứng; 123 thì không.', 'extras': {'mode': 'ai'}},
                    ])
            conversations = [{'id': 'preview-active', 'createdAt': 1, 'updatedAt': 100, 'messages': messages}]
            conversations += [{'id': f'example-{i}', 'createdAt': i, 'updatedAt': i, 'messages': [{'role': 'user', 'content': f'Bài học {i + 1}: Python và ý tưởng mới'}]} for i in range(25)]
            fixture = json.dumps({'version': 1, 'activeId': 'preview-active', 'conversations': conversations}, ensure_ascii=False)
            html = (WEB / 'index.html').read_text(encoding='utf-8')
            html = html.replace('<script src="/assets/conversations.js"', '<script>localStorage.setItem("pyban-conversations-v1", ' + json.dumps(fixture) + ');</script><script src="/assets/conversations.js"')
            data = html.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(data)
        else:
            if self.path.startswith('/assets/'):
                self.path = self.path.removeprefix('/assets')
            super().do_GET()


if __name__ == '__main__':
    ThreadingHTTPServer(('127.0.0.1', 8767), Preview).serve_forever()
