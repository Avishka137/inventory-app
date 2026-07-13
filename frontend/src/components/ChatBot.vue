<template>
  <!-- FAB -->
  <button class="chat-fab" @click="toggleChat" :class="{ active: isOpen }">
    <transition name="icon-flip">
      <svg v-if="!isOpen" key="open" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
      <svg v-else key="close" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M18 6L6 18M6 6l12 12"/></svg>
    </transition>
    <span v-if="unread > 0 && !isOpen" class="fab-badge">{{ unread }}</span>
    <div class="fab-ring"></div>
  </button>

  <transition name="chat-pop">
    <div class="chat-panel" v-if="isOpen">
      <!-- Header -->
      <div class="chat-header">
        <div class="chat-header-left">
          <div class="ai-avatar"><span>✦</span><div class="avatar-pulse"></div></div>
          <div>
            <div class="chat-title">Inventory AI</div>
            <div class="chat-sub"><span class="status-dot"></span>Powered by Gemini</div>
          </div>
        </div>
        <div class="header-actions">
          <!-- Tab switcher -->
          <button class="tab-btn" :class="{ active: activeTab === 'chat' }" @click="activeTab = 'chat'">
            <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
            Chat
          </button>
          <button class="tab-btn" :class="{ active: activeTab === 'knowledge' }" @click="activeTab = 'knowledge'; loadKnowledge()">
            <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
            My Notes
          </button>
          <button class="chat-close" @click="isOpen = false">
            <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M18 6L6 18M6 6l12 12"/></svg>
          </button>
        </div>
      </div>

      <!-- CHAT TAB -->
      <div class="chat-messages" ref="messagesEl" v-if="activeTab === 'chat'">
        <transition name="fade-up">
          <div class="chat-welcome" v-if="messages.length === 0">
            <div class="welcome-orb">
              <span>🧠</span>
              <div class="orb-ring r1"></div>
              <div class="orb-ring r2"></div>
            </div>
            <h3>Smart Inventory AI</h3>
            <p>I check <strong>your notes first</strong>, then use AI. Teach me things and I'll remember!</p>
            <div class="suggestions">
              <button v-for="s in suggestions" :key="s.text" class="suggestion-btn" @click="sendSuggestion(s.text)">
                <span>{{ s.icon }}</span> {{ s.text }}
              </button>
            </div>
          </div>
        </transition>

        <transition-group name="msg-appear">
          <div v-for="(msg, i) in messages" :key="i" :class="['message', msg.role]">
            <div class="msg-avatar" v-if="msg.role === 'assistant'">✦</div>
            <div class="msg-bubble" v-html="formatMessage(msg.content)"></div>
          </div>
        </transition-group>

        <div class="message assistant" v-if="loading" key="typing">
          <div class="msg-avatar">✦</div>
          <div class="msg-bubble typing"><span></span><span></span><span></span></div>
        </div>
      </div>

      <!-- KNOWLEDGE TAB -->
      <div class="knowledge-panel" v-if="activeTab === 'knowledge'">
        <div class="knowledge-add">
          <div class="field" style="margin-bottom:8px">
            <label>Topic (e.g. "wireless mouse")</label>
            <input v-model="newTopic" placeholder="Item or topic name…" @keydown.enter="saveNote" />
          </div>
          <div class="field" style="margin-bottom:10px">
            <label>Your Note</label>
            <textarea v-model="newNote" placeholder="What do you know about it?…" rows="2" @keydown.ctrl.enter="saveNote"></textarea>
          </div>
          <button class="btn btn-primary" style="width:100%" @click="saveNote" :disabled="!newTopic || !newNote">
            ✦ Save to My Knowledge Base
          </button>
        </div>

        <div class="knowledge-list">
          <div v-if="knowledgeItems.length === 0" class="knowledge-empty">
            No notes yet. Teach me by typing above, or tell me in chat:<br>
            <em>"Remember that the keyboard is mechanical"</em>
          </div>
          <div v-for="k in knowledgeItems" :key="k.id" class="knowledge-item">
            <div class="ki-header">
              <span class="ki-topic">{{ k.topic }}</span>
              <button class="ki-delete" @click="deleteNote(k.id)">✕</button>
            </div>
            <p class="ki-note">{{ k.note }}</p>
          </div>
        </div>
      </div>

      <!-- Input (chat tab only) -->
      <div class="chat-input-wrap" v-if="activeTab === 'chat'">
        <input v-model="inputText" @keydown.enter="sendMessage" :disabled="loading" class="chat-input" placeholder="Ask or teach me something…" ref="inputEl" />
        <button class="send-btn" @click="sendMessage" :disabled="loading || !inputText.trim()">
          <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22,2 15,22 11,13 2,9"/></svg>
        </button>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, nextTick, watch } from "vue";
import axios from "axios";

const isOpen     = ref(false);
const inputText  = ref("");
const messages   = ref([]);
const loading    = ref(false);
const unread     = ref(0);
const messagesEl = ref(null);
const inputEl    = ref(null);
const activeTab  = ref("chat");

// Knowledge base
const knowledgeItems = ref([]);
const newTopic = ref("");
const newNote  = ref("");

const suggestions = [
  { icon: "⚠️", text: "What items are low on stock?" },
  { icon: "💰", text: "What is my total inventory value?" },
  { icon: "📊", text: "Which category has the most products?" },
  { icon: "🧠", text: "What do you know about my products?" },
];

watch(isOpen, async (val) => {
  if (val) { unread.value = 0; await nextTick(); inputEl.value?.focus(); scrollToBottom(); }
});

function toggleChat() { isOpen.value = !isOpen.value; }

async function sendMessage() {
  const text = inputText.value.trim();
  if (!text || loading.value) return;
  messages.value.push({ role: "user", content: text });
  inputText.value = "";
  loading.value = true;
  await scrollToBottom();
  try {
    const { data } = await axios.post("http://localhost:5000/api/chat", { message: text });
    if (data.error) {
      messages.value.push({ role: "assistant", content: "⚠️ " + data.error });
    } else {
      messages.value.push({ role: "assistant", content: data.reply });
      if (!isOpen.value) unread.value++;
      // Refresh knowledge if something was saved
      if (data.reply.includes("Got it! I've saved")) loadKnowledge();
    }
  } catch {
    messages.value.push({ role: "assistant", content: "⚠️ Could not reach Flask. Make sure it's running!" });
  } finally {
    loading.value = false;
    await scrollToBottom();
  }
}

function sendSuggestion(text) { inputText.value = text; sendMessage(); }

async function loadKnowledge() {
  try {
    const { data } = await axios.get("http://localhost:5000/api/knowledge");
    knowledgeItems.value = data;
  } catch {}
}

async function saveNote() {
  if (!newTopic.value.trim() || !newNote.value.trim()) return;
  try {
    await axios.post("http://localhost:5000/api/knowledge", { topic: newTopic.value, note: newNote.value });
    newTopic.value = "";
    newNote.value  = "";
    await loadKnowledge();
  } catch {}
}

async function deleteNote(id) {
  try {
    await axios.delete(`http://localhost:5000/api/knowledge/${id}`);
    await loadKnowledge();
  } catch {}
}

async function scrollToBottom() {
  await nextTick();
  if (messagesEl.value) messagesEl.value.scrollTop = messagesEl.value.scrollHeight;
}

function formatMessage(text) {
  return text
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/^- (.+)$/gm, "<li>$1</li>")
    .replace(/(<li>[\s\S]*<\/li>)/, "<ul>$1</ul>")
    .replace(/\n/g, "<br/>");
}
</script>

<style scoped>
.chat-fab {
  position: fixed; bottom: 28px; right: 28px;
  width: 56px; height: 56px; border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), #8b5cf6);
  border: none; color: #fff; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 24px rgba(99,102,241,0.5);
  transition: transform .3s cubic-bezier(.34,1.56,.64,1), box-shadow .3s;
  z-index: 200; overflow: visible;
}
.chat-fab:hover { transform: scale(1.12) rotate(5deg); box-shadow: 0 8px 36px rgba(99,102,241,0.7); }
.chat-fab.active { background: linear-gradient(135deg, #374151, #1f2937); box-shadow: var(--shadow); transform: scale(1); }
.fab-ring { position: absolute; inset: -6px; border-radius: 50%; border: 2px solid rgba(99,102,241,0.35); animation: ringPulse 2.5s ease-out infinite; }
@keyframes ringPulse { 0% { transform: scale(1); opacity: 0.7; } 100% { transform: scale(1.5); opacity: 0; } }
.fab-badge { position: absolute; top: -5px; right: -5px; background: var(--red); color: #fff; font-size: 10px; font-weight: 800; width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 2px solid var(--bg); }

.chat-panel {
  position: fixed; bottom: 96px; right: 28px;
  width: 380px; height: 560px;
  background: var(--surface); border: 1px solid var(--border2); border-radius: 22px;
  display: flex; flex-direction: column; overflow: hidden;
  box-shadow: 0 24px 64px rgba(0,0,0,0.6); z-index: 199;
}
.chat-pop-enter-active { animation: chatPop .3s cubic-bezier(.34,1.56,.64,1); }
.chat-pop-leave-active { animation: chatPop .2s ease reverse; }
@keyframes chatPop { from { opacity: 0; transform: scale(.88) translateY(20px); } to { opacity: 1; transform: scale(1) translateY(0); } }

.chat-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 14px; border-bottom: 1px solid var(--border);
  background: linear-gradient(135deg, rgba(99,102,241,0.08), rgba(139,92,246,0.05));
  flex-shrink: 0; gap: 8px;
}
.chat-header-left { display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
.ai-avatar { position: relative; width: 34px; height: 34px; background: linear-gradient(135deg, var(--accent), #8b5cf6); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 15px; box-shadow: 0 0 14px rgba(99,102,241,0.4); flex-shrink: 0; }
.avatar-pulse { position: absolute; inset: -3px; border-radius: 13px; border: 1.5px solid rgba(99,102,241,0.4); animation: avatarPulse 2s ease-in-out infinite; }
@keyframes avatarPulse { 0%,100% { opacity: 0.6; } 50% { opacity: 0.15; } }
.chat-title { font-size: 13px; font-weight: 700; }
.chat-sub { font-size: 10px; color: var(--text3); display: flex; align-items: center; gap: 4px; }
.status-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--green); box-shadow: 0 0 5px var(--green); animation: statusBlink 2s infinite; flex-shrink: 0; }
@keyframes statusBlink { 0%,100% { opacity:1; } 50% { opacity: 0.4; } }

.header-actions { display: flex; align-items: center; gap: 5px; }
.tab-btn {
  display: flex; align-items: center; gap: 5px;
  padding: 5px 10px; border-radius: 8px;
  background: transparent; border: 1px solid var(--border);
  color: var(--text3); font-size: 11px; font-weight: 600;
  cursor: pointer; transition: all .15s; font-family: var(--font);
}
.tab-btn.active { background: rgba(99,102,241,0.15); color: var(--accent2); border-color: rgba(99,102,241,0.3); }
.tab-btn:hover:not(.active) { background: var(--surface2); color: var(--text); }
.chat-close { width: 28px; height: 28px; background: var(--surface2); border: 1px solid var(--border); border-radius: 7px; color: var(--text3); cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all .15s; }
.chat-close:hover { color: var(--text); transform: rotate(90deg); }

.chat-messages { flex: 1; overflow-y: auto; padding: 14px; display: flex; flex-direction: column; gap: 10px; scroll-behavior: smooth; }

.chat-welcome { text-align: center; padding: 12px 8px; }
.welcome-orb { position: relative; width: 64px; height: 64px; margin: 0 auto 12px; display: flex; align-items: center; justify-content: center; font-size: 28px; }
.orb-ring { position: absolute; border-radius: 50%; border: 1.5px solid rgba(99,102,241,0.3); animation: orbExpand 3s ease-out infinite; }
.orb-ring.r1 { width: 64px; height: 64px; }
.orb-ring.r2 { width: 80px; height: 80px; animation-delay: 0.8s; }
@keyframes orbExpand { 0% { transform: scale(.8); opacity: .6; } 100% { transform: scale(1.3); opacity: 0; } }
.chat-welcome h3 { font-size: 14px; font-weight: 700; margin-bottom: 5px; }
.chat-welcome p  { font-size: 12px; color: var(--text3); margin-bottom: 12px; line-height: 1.5; }

.suggestions { display: flex; flex-direction: column; gap: 6px; }
.suggestion-btn { background: var(--surface2); border: 1px solid var(--border2); border-radius: 9px; color: var(--text2); font-family: var(--font); font-size: 11px; padding: 8px 12px; cursor: pointer; text-align: left; transition: all .18s; display: flex; align-items: center; gap: 7px; }
.suggestion-btn:hover { background: rgba(99,102,241,0.1); color: var(--accent2); border-color: rgba(99,102,241,0.3); transform: translateX(4px); }

.msg-appear-enter-active { animation: msgIn .28s cubic-bezier(.34,1.56,.64,1); }
@keyframes msgIn { from { opacity: 0; transform: translateY(8px) scale(.96); } to { opacity: 1; transform: translateY(0) scale(1); } }
.message { display: flex; gap: 7px; align-items: flex-end; }
.message.user { flex-direction: row-reverse; }
.msg-avatar { width: 26px; height: 26px; background: linear-gradient(135deg, var(--accent), #8b5cf6); border-radius: 7px; display: flex; align-items: center; justify-content: center; font-size: 12px; flex-shrink: 0; }
.msg-bubble { max-width: 80%; padding: 9px 13px; border-radius: 13px; font-size: 12.5px; line-height: 1.55; word-break: break-word; }
.message.user .msg-bubble { background: linear-gradient(135deg, var(--accent), #8b5cf6); color: #fff; border-bottom-right-radius: 4px; box-shadow: 0 4px 14px rgba(99,102,241,0.3); }
.message.assistant .msg-bubble { background: var(--surface2); border: 1px solid var(--border); color: var(--text); border-bottom-left-radius: 4px; }
.typing { display: flex; gap: 5px; align-items: center; padding: 12px 14px; }
.typing span { width: 7px; height: 7px; background: var(--accent2); border-radius: 50%; animation: typingBounce 1.2s ease-in-out infinite; }
.typing span:nth-child(2) { animation-delay: .2s; }
.typing span:nth-child(3) { animation-delay: .4s; }
@keyframes typingBounce { 0%,60%,100% { transform: translateY(0); opacity:.4; } 30% { transform: translateY(-7px); opacity:1; } }

.fade-up-enter-active { animation: fadeUp .3s ease; }
@keyframes fadeUp { from { opacity:0; transform: translateY(10px); } to { opacity:1; transform: translateY(0); } }

/* ── Knowledge tab ── */
.knowledge-panel { flex: 1; overflow-y: auto; display: flex; flex-direction: column; }
.knowledge-add { padding: 14px; border-bottom: 1px solid var(--border); background: var(--surface2); flex-shrink: 0; }
.knowledge-list { flex: 1; overflow-y: auto; padding: 12px; display: flex; flex-direction: column; gap: 8px; }
.knowledge-empty { text-align: center; color: var(--text3); font-size: 12px; padding: 24px 16px; line-height: 1.7; }
.knowledge-empty em { color: var(--accent2); font-style: normal; }
.knowledge-item { background: var(--surface2); border: 1px solid var(--border); border-radius: 10px; padding: 10px 12px; }
.ki-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.ki-topic { font-size: 11px; font-weight: 700; color: var(--accent2); text-transform: uppercase; letter-spacing: .06em; font-family: var(--mono); }
.ki-delete { background: none; border: none; color: var(--text3); cursor: pointer; font-size: 11px; padding: 2px 5px; border-radius: 4px; transition: all .15s; }
.ki-delete:hover { background: rgba(248,113,113,0.15); color: var(--red); }
.ki-note { font-size: 12px; color: var(--text2); line-height: 1.5; }

/* ── Input ── */
.chat-input-wrap { display: flex; gap: 8px; padding: 12px 14px; border-top: 1px solid var(--border); background: var(--surface2); flex-shrink: 0; }
.chat-input { flex: 1; background: var(--bg); border: 1px solid var(--border2); border-radius: 10px; color: var(--text); font-family: var(--font); font-size: 13px; padding: 9px 13px; outline: none; transition: border .18s; }
.chat-input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-glow); }
.chat-input:disabled { opacity: 0.5; }
.send-btn { width: 38px; height: 38px; background: linear-gradient(135deg, var(--accent), #8b5cf6); border: none; border-radius: 10px; color: #fff; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all .2s cubic-bezier(.34,1.56,.64,1); box-shadow: 0 4px 14px rgba(99,102,241,0.4); flex-shrink: 0; }
.send-btn:hover:not(:disabled) { transform: scale(1.1) rotate(-5deg); }
.send-btn:disabled { opacity: 0.35; cursor: not-allowed; }

.icon-flip-enter-active { animation: flipIn .25s ease; }
.icon-flip-leave-active { animation: flipIn .2s ease reverse; position: absolute; }
@keyframes flipIn { from { transform: rotate(-90deg) scale(.5); opacity:0; } to { transform: rotate(0) scale(1); opacity:1; } }
</style>  ``