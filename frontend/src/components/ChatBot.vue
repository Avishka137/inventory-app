<template>
  <button class="chat-fab" @click="toggleChat" :class="{ active: isOpen }">
    <transition name="icon-flip">
      <svg v-if="!isOpen" key="open" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
      </svg>
      <svg v-else key="close" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
        <path d="M18 6L6 18M6 6l12 12"/>
      </svg>
    </transition>
    <span v-if="unread > 0 && !isOpen" class="fab-badge">{{ unread }}</span>
    <div class="fab-ring"></div>
  </button>

  <transition name="chat-pop">
    <div class="chat-panel" v-if="isOpen">

      <!-- Header -->
      <div class="chat-header">
        <div class="chat-header-left">
          <div class="ai-avatar">
            <span class="avatar-icon">✦</span>
            <div class="avatar-pulse"></div>
          </div>
          <div>
            <div class="chat-title">Inventory AI</div>
            <div class="chat-sub">
              <span class="status-dot"></span>
              Powered by Gemini
            </div>
          </div>
        </div>
        <button class="chat-close" @click="isOpen = false">
          <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
            <path d="M18 6L6 18M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <!-- Messages -->
      <div class="chat-messages" ref="messagesEl">
        <transition name="fade-up">
          <div class="chat-welcome" v-if="messages.length === 0">
            <div class="welcome-orb">
              <span>📦</span>
              <div class="orb-ring r1"></div>
              <div class="orb-ring r2"></div>
              <div class="orb-ring r3"></div>
            </div>
            <h3>Inventory Assistant</h3>
            <p>I know everything about your stock. Ask me anything!</p>
          </div>
        </transition>

        <transition-group name="msg-appear">
          <div v-for="(msg, i) in messages" :key="i" :class="['message', msg.role]">
            <div class="msg-avatar" v-if="msg.role === 'assistant'">✦</div>
            <div class="msg-bubble" v-html="formatMessage(msg.content)"></div>
          </div>
        </transition-group>

        <transition name="msg-appear">
          <div class="message assistant" v-if="loading" key="typing">
            <div class="msg-avatar">✦</div>
            <div class="msg-bubble typing">
              <span></span><span></span><span></span>
            </div>
          </div>
        </transition>
      </div>

      <!-- Quick suggestions — always visible -->
      <div class="quick-suggestions">
        <button
          v-for="s in suggestions"
          :key="s.text"
          class="quick-btn"
          @click="sendSuggestion(s)"
          :disabled="loading"
        >{{ s.icon }} {{ s.text }}</button>
      </div>

      <!-- Input -->
      <div class="chat-input-wrap">
        <input
          v-model="inputText"
          @keydown.enter="sendMessage"
          :disabled="loading"
          class="chat-input"
          placeholder="Ask about your inventory…"
          ref="inputEl"
        />
        <button class="send-btn" @click="sendMessage" :disabled="loading || !inputText.trim()">
          <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
            <line x1="22" y1="2" x2="11" y2="13"/>
            <polygon points="22,2 15,22 11,13 2,9"/>
          </svg>
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

const suggestions = [
  { icon: "⚠️", text: "What items are low on stock?" },
  { icon: "💰", text: "What is my total inventory value?" },
  { icon: "📊", text: "Which category has the most products?" },
  { icon: "🏆", text: "Show me the most expensive items" },
];

watch(isOpen, async (val) => {
  if (val) {
    unread.value = 0;
    await nextTick();
    inputEl.value?.focus();
    scrollToBottom();
  }
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
    }
  } catch {
    messages.value.push({ role: "assistant", content: "⚠️ Could not reach Flask. Make sure it's running!" });
  } finally {
    loading.value = false;
    await scrollToBottom();
  }
}

function sendSuggestion(s) {
  inputText.value = s.text;
  sendMessage();
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

.fab-ring {
  position: absolute; inset: -6px; border-radius: 50%;
  border: 2px solid rgba(99,102,241,0.35);
  animation: ringPulse 2.5s ease-out infinite;
}
@keyframes ringPulse { 0% { transform: scale(1); opacity: 0.7; } 100% { transform: scale(1.5); opacity: 0; } }

.fab-badge {
  position: absolute; top: -5px; right: -5px;
  background: var(--red); color: #fff; font-size: 10px; font-weight: 800;
  width: 20px; height: 20px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  border: 2px solid var(--bg); animation: badgePop .3s cubic-bezier(.34,1.56,.64,1);
}
@keyframes badgePop { from { transform: scale(0); } to { transform: scale(1); } }

.icon-flip-enter-active { animation: flipIn .25s ease; }
.icon-flip-leave-active { animation: flipIn .2s ease reverse; position: absolute; }
@keyframes flipIn { from { transform: rotate(-90deg) scale(0.5); opacity: 0; } to { transform: rotate(0) scale(1); opacity: 1; } }

.chat-panel {
  position: fixed; bottom: 96px; right: 28px;
  width: 380px; height: 520px; max-height: calc(100vh - 120px);
  background: var(--surface); border: 1px solid var(--border2);
  border-radius: 22px; display: flex; flex-direction: column;
  overflow: hidden;
  box-shadow: 0 24px 64px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.04);
  z-index: 199;
}

.chat-pop-enter-active { animation: chatPop .3s cubic-bezier(.34,1.56,.64,1); }
.chat-pop-leave-active { animation: chatPop .2s ease reverse; }
@keyframes chatPop { from { opacity: 0; transform: scale(.88) translateY(20px); } to { opacity: 1; transform: scale(1) translateY(0); } }

.chat-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 18px; border-bottom: 1px solid var(--border);
  background: linear-gradient(135deg, rgba(99,102,241,0.08), rgba(139,92,246,0.05));
  flex-shrink: 0;
}
.chat-header-left { display: flex; align-items: center; gap: 11px; }

.ai-avatar {
  position: relative; width: 36px; height: 36px;
  background: linear-gradient(135deg, var(--accent), #8b5cf6);
  border-radius: 11px; display: flex; align-items: center; justify-content: center;
  box-shadow: 0 0 16px rgba(99,102,241,0.5);
}
.avatar-icon { font-size: 16px; position: relative; z-index: 1; }
.avatar-pulse {
  position: absolute; inset: -3px; border-radius: 13px;
  border: 1.5px solid rgba(99,102,241,0.4);
  animation: avatarPulse 2s ease-in-out infinite;
}
@keyframes avatarPulse { 0%,100% { opacity: 0.6; transform: scale(1); } 50% { opacity: 0.2; transform: scale(1.08); } }

.chat-title { font-size: 14px; font-weight: 700; }
.chat-sub { font-size: 11px; color: var(--text3); display: flex; align-items: center; gap: 5px; margin-top: 1px; }
.status-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--green); box-shadow: 0 0 5px var(--green); animation: statusBlink 2s ease-in-out infinite; flex-shrink: 0; }
@keyframes statusBlink { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }

.chat-close {
  width: 30px; height: 30px; background: var(--surface2); border: 1px solid var(--border);
  border-radius: 8px; color: var(--text3); cursor: pointer;
  display: flex; align-items: center; justify-content: center; transition: all .15s;
}
.chat-close:hover { background: var(--surface3); color: var(--text); transform: rotate(90deg); }

.chat-messages {
  flex: 1; overflow-y: auto; padding: 16px;
  display: flex; flex-direction: column; gap: 12px; scroll-behavior: smooth;
}

.chat-welcome { text-align: center; padding: 16px 8px; }
.welcome-orb {
  position: relative; width: 72px; height: 72px;
  margin: 0 auto 16px; display: flex; align-items: center; justify-content: center; font-size: 32px;
}
.orb-ring { position: absolute; border-radius: 50%; border: 1.5px solid rgba(99,102,241,0.3); animation: orbExpand 3s ease-out infinite; }
.orb-ring.r1 { width: 72px; height: 72px; animation-delay: 0s; }
.orb-ring.r2 { width: 88px; height: 88px; animation-delay: 0.6s; }
.orb-ring.r3 { width: 104px; height: 104px; animation-delay: 1.2s; }
@keyframes orbExpand { 0% { transform: scale(0.8); opacity: 0.6; } 100% { transform: scale(1.3); opacity: 0; } }
.chat-welcome h3 { font-size: 15px; font-weight: 700; margin-bottom: 6px; }
.chat-welcome p  { font-size: 12px; color: var(--text3); margin-bottom: 8px; }

.msg-appear-enter-active { animation: msgIn .28s cubic-bezier(.34,1.56,.64,1); }
.msg-appear-leave-active { animation: msgIn .15s ease reverse; }
@keyframes msgIn { from { opacity: 0; transform: translateY(10px) scale(.95); } to { opacity: 1; transform: translateY(0) scale(1); } }

.message { display: flex; gap: 8px; align-items: flex-end; }
.message.user { flex-direction: row-reverse; }
.msg-avatar {
  width: 28px; height: 28px; background: linear-gradient(135deg, var(--accent), #8b5cf6);
  border-radius: 8px; display: flex; align-items: center; justify-content: center;
  font-size: 13px; flex-shrink: 0; box-shadow: 0 0 10px rgba(99,102,241,0.3);
}
.msg-bubble { max-width: 80%; padding: 10px 14px; border-radius: 14px; font-size: 13px; line-height: 1.55; word-break: break-word; }
.message.user .msg-bubble { background: linear-gradient(135deg, var(--accent), #8b5cf6); color: #fff; border-bottom-right-radius: 4px; box-shadow: 0 4px 16px rgba(99,102,241,0.3); }
.message.assistant .msg-bubble { background: var(--surface2); border: 1px solid var(--border); color: var(--text); border-bottom-left-radius: 4px; }

.typing { display: flex; gap: 5px; align-items: center; padding: 14px 16px; }
.typing span { width: 7px; height: 7px; background: var(--accent2); border-radius: 50%; animation: typingBounce 1.2s ease-in-out infinite; }
.typing span:nth-child(2) { animation-delay: .2s; }
.typing span:nth-child(3) { animation-delay: .4s; }
@keyframes typingBounce { 0%,60%,100% { transform: translateY(0); opacity: 0.4; } 30% { transform: translateY(-8px); opacity: 1; } }

.fade-up-enter-active { animation: fadeUp .3s ease; }
@keyframes fadeUp { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }

/* ── Quick suggestions bar — always visible ── */
.quick-suggestions {
  display: flex; gap: 6px; padding: 8px 12px;
  overflow-x: auto; flex-shrink: 0;
  border-top: 1px solid var(--border);
  background: var(--surface);
  scrollbar-width: none;
}
.quick-suggestions::-webkit-scrollbar { display: none; }
.quick-btn {
  background: var(--surface2); border: 1px solid var(--border2);
  border-radius: 20px; color: var(--text2);
  font-family: var(--font); font-size: 11px; font-weight: 500;
  padding: 5px 12px; cursor: pointer; white-space: nowrap;
  transition: all .18s; flex-shrink: 0;
}
.quick-btn:hover:not(:disabled) { background: rgba(99,102,241,0.15); color: var(--accent2); border-color: rgba(99,102,241,0.4); }
.quick-btn:disabled { opacity: 0.4; cursor: not-allowed; }

/* ── Input ── */
.chat-input-wrap {
  display: flex; gap: 8px; padding: 12px 16px;
  border-top: 1px solid var(--border); background: var(--surface2); flex-shrink: 0;
}
.chat-input {
  flex: 1; background: var(--bg); border: 1px solid var(--border2);
  border-radius: 12px; color: var(--text); font-family: var(--font);
  font-size: 13px; padding: 10px 14px; outline: none; transition: border .18s, box-shadow .18s;
}
.chat-input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-glow); }
.chat-input:disabled { opacity: 0.5; }
.send-btn {
  width: 40px; height: 40px; background: linear-gradient(135deg, var(--accent), #8b5cf6);
  border: none; border-radius: 12px; color: #fff; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all .2s cubic-bezier(.34,1.56,.64,1);
  box-shadow: 0 4px 16px rgba(99,102,241,0.4); flex-shrink: 0;
}
.send-btn:hover:not(:disabled) { transform: scale(1.1) rotate(-5deg); box-shadow: 0 6px 24px rgba(99,102,241,0.6); }
.send-btn:disabled { opacity: 0.35; cursor: not-allowed; transform: none; }
</style>