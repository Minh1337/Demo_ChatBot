/* Browser-local conversations. Full transcripts are kept; only API context is bounded. */
(() => {
  const KEY = 'pyban-conversations-v1';
  const validMessage = item => item && ['user', 'assistant'].includes(item.role) && typeof item.content === 'string' && item.content.length > 0;

  class Store {
    constructor(storage, legacy = [], onError = () => {}) {
      this.storage = storage;
      this.onError = onError;
      this.conversations = [];
      this.activeId = null;
      try {
        const data = JSON.parse(storage.getItem(KEY) || 'null');
        if (data && Array.isArray(data.conversations)) {
          this.conversations = data.conversations.filter(item => item && typeof item.id === 'string' && Array.isArray(item.messages))
            .map(item => ({...item, messages:item.messages.filter(validMessage)}));
          this.activeId = data.activeId;
        }
      } catch { this.onError(); }
      if (!this.conversations.length && legacy.some(validMessage)) {
        const imported = this.create();
        imported.messages = legacy.filter(validMessage);
        this.save();
      }
      if (!this.conversations.length) this.create();
      if (!this.conversations.some(item => item.id === this.activeId)) this.activeId = this.conversations[0].id;
    }

    active() { return this.conversations.find(item => item.id === this.activeId); }

    create() {
      const conversation = {
        id: globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(36).slice(2)}`,
        createdAt: Date.now(), updatedAt: Date.now(), messages: [],
      };
      this.conversations.unshift(conversation);
      this.activeId = conversation.id;
      this.save();
      return conversation;
    }

    select(id) {
      if (!this.conversations.some(item => item.id === id)) return;
      this.activeId = id;
      this.save();
    }

    remove(id) {
      const index = this.conversations.findIndex(item => item.id === id);
      if (index < 0) return false;
      this.conversations.splice(index, 1);
      if (!this.conversations.length) this.create();
      else if (this.activeId === id) this.activeId = this.conversations[Math.min(index, this.conversations.length - 1)].id;
      this.save();
      return true;
    }

    append(id, message) {
      const conversation = this.conversations.find(item => item.id === id);
      if (!conversation || !validMessage(message)) return;
      conversation.messages.push(message);
      conversation.updatedAt = Date.now();
      this.save();
    }

    save() {
      try {
        this.storage.setItem(KEY, JSON.stringify({version:1, activeId:this.activeId, conversations:this.conversations}));
        return true;
      } catch { this.onError(); return false; }
    }
  }

  function title(conversation) {
    const first = conversation.messages.find(item => item.role === 'user');
    return first ? first.content.replace(/\s+/g, ' ').slice(0, 50) : 'Cuộc trò chuyện mới';
  }

  function context(messages) {
    const recent = messages.filter(validMessage).slice(-20).map(({role, content}) => ({role, content:content.slice(0, 8000)}));
    while (recent.length && recent.reduce((sum, item) => sum + item.content.length, 0) > 12000) recent.shift();
    while (recent[0]?.role === 'assistant') recent.shift();
    return recent;
  }

  const api = {Store, title, context, KEY};
  globalThis.PyBanConversations = api;
  if (typeof module !== 'undefined') module.exports = api;
})();
