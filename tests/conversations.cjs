const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {Store, context} = require('../web/conversations.js');

function memoryStorage() {
  const data = new Map();
  return {getItem:key => data.get(key) || null, setItem:(key, value) => data.set(key, value)};
}

test('full transcripts survive reload; new chats keep separate context', () => {
  const storage = memoryStorage();
  const store = new Store(storage);
  const first = store.activeId;
  for (let i = 0; i < 30; i++) store.append(first, {role:i % 2 ? 'assistant':'user', content:`Message ${i}`});
  const second = store.create().id;
  store.append(second, {role:'user', content:'Another topic'});
  const restored = new Store(storage);
  assert.equal(restored.activeId, second);
  assert.equal(restored.conversations.find(item => item.id === first).messages.length, 30);
  assert.equal(context(restored.active().messages).length, 1);
  restored.select(first);
  assert.equal(context(restored.active().messages).length, 20);
  assert.equal(restored.active().messages.length, 30);
});

test('context stays within API limits without deleting the transcript', () => {
  const messages = Array.from({length:30}, (_, i) => ({role:i % 2 ? 'assistant':'user', content:'x'.repeat(2000)}));
  const recent = context(messages);
  assert.ok(recent.length <= 20);
  assert.ok(recent.reduce((sum, item) => sum + item.content.length, 0) <= 12000);
  assert.equal(recent[0].role, 'user');
  assert.equal(messages.length, 30);
});

test('legacy session is migrated and failed storage is reported', () => {
  const storage = memoryStorage();
  const migrated = new Store(storage, [{role:'user', content:'Old session'}]);
  assert.equal(new Store(storage).active().messages[0].content, 'Old session');
  assert.equal(migrated.conversations.length, 1);
  let errors = 0;
  const failing = new Store({getItem:() => null, setItem:() => {throw new Error('quota');}}, [], () => errors++);
  failing.append(failing.activeId, {role:'user', content:'Still in memory'});
  assert.ok(errors > 0);
  assert.equal(failing.active().messages.length, 1);
});

test('conversation history can be deleted without leaving an invalid active chat', () => {
  const storage = memoryStorage();
  const store = new Store(storage);
  const first = store.activeId;
  store.append(first, {role:'user', content:'First topic'});
  const second = store.create().id;
  store.append(second, {role:'user', content:'Second topic'});
  assert.equal(store.remove(first), true);
  assert.equal(store.conversations.some(item => item.id === first), false);
  assert.equal(store.activeId, second);
  assert.equal(store.remove(second), true);
  assert.equal(store.conversations.length, 1);
  assert.equal(store.active().messages.length, 0);
});

test('conversation list exposes a menu before deleting a conversation', () => {
  const source = fs.readFileSync(path.join(__dirname, '../web/app.js'), 'utf8');
  assert.match(source, /conversation-menu-toggle/);
  assert.match(source, /deleteButton\.textContent = 'Xóa'/);
  assert.match(source, /window\.confirm/);
});

class Element {
  constructor() {this.children = []; this.dataset = {}; this.className = ''; this.value = ''; this.style = {}; this.disabled = false; this.classList = {add: name => {this.className += ` ${name}`;}};}
  append(child) {this.children.push(child);}
  replaceChildren() {this.children = [];}
  setAttribute() {}
  addEventListener() {}
  scrollIntoView() {}
  focus() {}
  querySelector(selector) {return this.children.find(child => child.className.split(' ').includes(selector.slice(1)));}
}

test('switching and starting a new chat during requests saves replies to their original chat', async () => {
  const storage = memoryStorage();
  const elements = new Map();
  const requests = [];
  const sandbox = vm.createContext({
    console, localStorage:storage, sessionStorage:memoryStorage(),
    document:{querySelector: selector => {if (!elements.has(selector)) elements.set(selector, new Element()); return elements.get(selector);}, querySelectorAll:() => [], createElement:() => new Element()},
    fetch:(_url, options) => new Promise(resolve => requests.push({options, resolve})),
  });
  for (const filename of ['conversations.js', 'app.js']) vm.runInContext(fs.readFileSync(path.join(__dirname, '../web', filename), 'utf8'), sandbox);
  const firstId = vm.runInContext('store.activeId', sandbox);
  const firstRequest = vm.runInContext("ask('First topic')", sandbox);
  assert.equal(new Store(storage).active().messages[0].content, 'First topic');
  vm.runInContext('newConversation()', sandbox);
  const secondId = vm.runInContext('store.activeId', sandbox);
  const secondRequest = vm.runInContext("ask('Second topic')", sandbox);
  assert.notEqual(firstId, secondId);
  assert.deepEqual(JSON.parse(requests[1].options.body).history, []);
  requests[0].resolve({ok:true, json:async () => ({answer:'Reply A', status:'answered', mode:'ai', sources:[]})});
  await firstRequest;
  assert.equal(vm.runInContext('store.activeId', sandbox), secondId);
  requests[1].resolve({ok:true, json:async () => ({answer:'Reply B', status:'answered', mode:'ai', sources:[]})});
  await secondRequest;
  const restored = new Store(storage);
  assert.equal(restored.conversations.find(item => item.id === firstId).messages[1].content, 'Reply A');
  assert.equal(restored.conversations.find(item => item.id === secondId).messages[1].content, 'Reply B');
  const followup = vm.runInContext("ask('More about this')", sandbox);
  assert.deepEqual(JSON.parse(requests[2].options.body).history.map(item => item.content), ['Second topic', 'Reply B']);
  requests[2].resolve({ok:true, json:async () => ({answer:'Follow-up', status:'answered', mode:'ai', sources:[]})});
  await followup;
});
