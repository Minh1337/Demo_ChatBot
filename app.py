"""FastAPI service and local web UI for PyBan."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, model_validator

from rag.generation import GenerationError, configured, draft
from rag.retrieval import (
    detect_topic,
    detect_topics,
    is_coding_request,
    needs_problem_statement,
    retrieve,
)

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env", override=False)
WEB = ROOT / "web"

app = FastAPI(title="PyBan — Chatbot hỏi đáp", version="0.2.0")
app.mount("/assets", StaticFiles(directory=WEB), name="assets")


class ConversationMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=8000)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    history: list[ConversationMessage] = Field(default_factory=list, max_length=20)

    @model_validator(mode="after")
    def bound_history(self):
        if sum(len(message.content) for message in self.history) > 12000:
            raise ValueError("Conversation context exceeds 12000 characters")
        return self


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(WEB / "index.html")


@app.get("/api/config")
def config():
    return {"name": "PyBạn", "mode": "general_conversation", "python_sources": True, "llm_enabled": configured()}


@app.post("/api/chat")
def chat(body: ChatRequest):
    question = body.question.strip()
    if not question:
        return {"status": "clarify", "answer": "Bạn hãy nhập câu hỏi mà bạn muốn trao đổi nhé.", "sources": [], "mode": "local"}
    recent_text = "\n".join(message.content for message in body.history[-6:])
    recent_user_text = "\n".join(message.content for message in body.history[-6:] if message.role == "user")
    conversation_context = f"{recent_text}\n{question}"
    if needs_problem_statement(question) and not recent_text:
        return {
            "status": "clarify",
            "answer": "Được chứ! Bạn gửi đề bài hoặc mô tả việc cần làm nhé. Nếu có, hãy cho mình biết ngôn ngữ muốn dùng, dữ liệu đầu vào/đầu ra, ràng buộc và ví dụ. Nếu chưa chọn ngôn ngữ, mình có thể dùng Python. Mình sẽ cùng bạn phân tích rồi viết lời giải và giải thích từng bước.",
            "sources": [], "mode": "local",
        }
    retrieval_context = f"{recent_user_text}\n{question}"
    python_context = bool(detect_topics(retrieval_context) or is_coding_request(retrieval_context))
    passages = retrieve(retrieval_context) if python_context else []
    passages = [passage for passage in passages if passage["score"] >= 0.18]
    history = [{"role": message.role, "content": message.content} for message in body.history]
    failure = None
    try:
        answer = draft(question, passages, history=history)
    except GenerationError as exc:
        answer = None
        failure = exc
    mode = "ai+retrieval" if answer and passages else "ai" if answer else "retrieval" if passages else "local"
    if not answer:
        if passages:
            reason = str(failure) if failure else "Model chưa tạo được câu trả lời."
            answer = reason + "\n\nDưới đây là tài liệu Python liên quan để tham khảo:\n\n" + "\n\n".join(f"**{p['title']}**\n{p['text']}" for p in passages[:2])
        else:
            return {
                "status": "unavailable",
                "answer": str(failure) if failure else "Model chưa tạo được câu trả lời. Hãy thử lại sau.",
                "error_code": failure.code if failure else "empty_response",
                "sources": [], "mode": "local",
            }
    sources = [{"id": p["id"], "title": p["title"], "topic": p["topic"], "section": p["section"], "url": p["url"], "source": p["source"]} for p in passages[:3]]
    return {"status": "answered", "answer": answer, "sources": sources, "mode": mode, "topic": detect_topic(question), "error_code": failure.code if failure else None}
