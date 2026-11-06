const form = document.querySelector('#chat-form');
const input = document.querySelector('#question');
const list = document.querySelector('#message-list');
const welcome = document.querySelector('#welcome');
const sendButton = document.querySelector('#send-button');
const conversationList = document.querySelector('#conversation-list');
const conversationPicker = document.querySelector('#conversation-picker');
const conversationTitle = document.querySelector('#conversation-title');
const storageNotice = document.querySelector('#storage-notice');
const chatScroll = document.querySelector('#chat-scroll');
const pending = new Map();
let legacy = [];
try { legacy = JSON.parse(sessionStorage.getItem('pyban-chat-context-v2') || '[]'); } catch { /* No previous session. */ }
const store = new PyBanConversations.Store({
  getItem: key => localStorage.getItem(key),
  setItem: (key, value) => localStorage.setItem(key, value),
}, Array.isArray(legacy) ? legacy : [], () => {
  storageNotice.hidden = false;
  storageNotice.textContent = 'Chưa lưu được lịch sử trên trình duyệt. Hãy kiểm tra dung lượng hoặc quyền lưu trữ; giữ tab này mở để tránh mất nội dung.';
});

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
}

function formatText(value) {
  const renderParagraphs = text => !text.trim() ? '' : escapeHtml(text)
    .replace(/`([^`\n]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .split(/\n\s*\n/).map(part => `<p>${part.replace(/\n/g, '<br>')}</p>`).join('');
  const blocks = [];
  const pattern = /```(?:python)?\s*\n([\s\S]*?)```/gi;
  let cursor = 0;
  let result = '';
  let match;
  while ((match = pattern.exec(value)) !== null) {
    result += renderParagraphs(value.slice(cursor, match.index));
    blocks.push(`<pre><code>${escapeHtml(match[1].trimEnd())}</code></pre>`);
    result += `<div class="code-block-placeholder">${blocks.length - 1}</div>`;
    cursor = pattern.lastIndex;
  }
  result += renderParagraphs(value.slice(cursor));
  blocks.forEach((block, index) => {
    result = result.replace(`<div class="code-block-placeholder">${index}</div>`, block);
  });
  return result;
}

function addMessage(role, content, extras = {}) {
  welcome.hidden = true;
  const article = document.createElement('article');
  article.className = `message ${role}`;
  if (role === 'assistant') {
    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.textContent = 'Py';
    article.append(avatar);
  }
  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  if (extras.status && extras.status !== 'answered') {
    const tag = document.createElement('span');
    tag.className = `status-tag ${extras.status}`;
    tag.textContent = ({clarify:'Làm rõ câu hỏi',unavailable:'Chưa có phản hồi AI'})[extras.status] || 'Thông tin';
    bubble.append(tag);
  }
  const body = document.createElement('div');
  body.innerHTML = formatText(content);
  bubble.append(body);
  if (extras.sources?.length) {
    const sources = document.createElement('div');
    sources.className = 'sources';
    extras.sources.forEach((source, index) => {
      const link = document.createElement('a');
      link.className = 'source-chip';
      link.href = source.url;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      link.textContent = `[${index + 1}] ${source.title}`;
      sources.append(link);
    });
    bubble.append(sources);
  }
  if (extras.mode === 'ai' || extras.mode === 'ai+retrieval') {
    const mode = document.createElement('div');
    mode.className = 'mode-label';
    mode.textContent = extras.mode === 'ai+retrieval' ? 'OpenRouter · có tham khảo tài liệu Python' : 'OpenRouter · chatbot hỏi đáp';
    bubble.append(mode);
  } else if (extras.mode === 'retrieval') {
    const mode = document.createElement('div');
    mode.className = 'mode-label';
    mode.textContent = 'Trả lời dự phòng · trích tài liệu Python';
    bubble.append(mode);
  }
  article.append(bubble);
  list.append(article);
  chatScroll.scrollTop = chatScroll.scrollHeight;
  return article;
}

function renderConversationList() {
  conversationList.replaceChildren();
  conversationPicker.replaceChildren();
  [...store.conversations].sort((a, b) => b.updatedAt - a.updatedAt).forEach(conversation => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = `conversation-item${conversation.id === store.activeId ? ' selected' : ''}`;
    button.textContent = PyBanConversations.title(conversation);
    button.title = button.textContent;
    button.setAttribute('aria-pressed', String(conversation.id === store.activeId));
    button.addEventListener('click', () => { store.select(conversation.id); renderConversation(); });
    conversationList.append(button);
    const option = document.createElement('option');
    option.value = conversation.id;
    option.textContent = PyBanConversations.title(conversation);
    option.selected = conversation.id === store.activeId;
    conversationPicker.append(option);
  });
}

function syncComposer() {
  sendButton.disabled = pending.has(store.activeId);
}

function renderConversation() {
  list.replaceChildren();
  const conversation = store.active();
  welcome.hidden = conversation.messages.length > 0;
  conversation.messages.forEach(item => addMessage(item.role, item.content, item.extras || {}));
  if (pending.has(conversation.id)) showWaiting(conversation.id);
  conversationTitle.textContent = PyBanConversations.title(conversation);
  renderConversationList();
  syncComposer();
  if (!conversation.messages.length) chatScroll.scrollTop = 0;
}

function showWaiting(id) {
  const waiting = addMessage('assistant', 'Đang đọc câu hỏi và ngữ cảnh cuộc trò chuyện...');
  waiting.dataset.pendingId = id;
  waiting.querySelector('.bubble').classList.add('typing');
}

function newConversation() {
  if (store.active().messages.length) store.create();
  input.value = '';
  input.style.height = 'auto';
  renderConversation();
  input.focus();
}

renderConversation();

async function ask(question) {
  const clean = question.trim();
  if (!clean || sendButton.disabled) return;
  const conversation = store.active();
  const id = conversation.id;
  const priorHistory = PyBanConversations.context(conversation.messages);
  store.append(id, {role:'user', content:clean});
  addMessage('user', clean);
  input.value = '';
  input.style.height = 'auto';
  pending.set(id, true);
  renderConversationList();
  conversationTitle.textContent = PyBanConversations.title(conversation);
  syncComposer();
  showWaiting(id);
  try {
    const response = await fetch('/api/chat', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify({question:clean, history:priorHistory})
    });
    const result = await response.json();
    if (!response.ok || typeof result.answer !== 'string') throw new Error(typeof result.detail === 'string' ? result.detail : 'Không gửi được câu hỏi.');
    store.append(id, {role:'assistant', content:result.answer, extras:{status:result.status, sources:result.sources, mode:result.mode}});
  } catch (error) {
    const message = `Chưa kết nối được máy chủ. Hãy kiểm tra cửa sổ VS Code rồi thử lại.\n\nChi tiết: ${error.message}`;
    store.append(id, {role:'assistant', content:message, extras:{status:'unavailable'}});
  } finally {
    pending.delete(id);
    if (store.activeId === id) { renderConversation(); input.focus(); }
    else { renderConversationList(); syncComposer(); }
  }
}

form.addEventListener('submit', event => { event.preventDefault(); ask(input.value); });
input.addEventListener('input', () => { input.style.height = 'auto'; input.style.height = `${Math.min(input.scrollHeight, 140)}px`; });
input.addEventListener('keydown', event => {
  if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); form.requestSubmit(); }
});
document.querySelectorAll('.suggestion').forEach(button => button.addEventListener('click', () => ask(button.dataset.prompt)));
document.querySelector('#clear-chat').addEventListener('click', newConversation);
document.querySelector('#new-chat').addEventListener('click', newConversation);
conversationPicker.addEventListener('change', () => { store.select(conversationPicker.value); renderConversation(); });
