/**
 * Real-Time Hackathon Chatbot Client
 * Handles WebSockets, multi-turn state rendering, countdown timer, and quick actions.
 */

class HackathonChatClient {
  constructor() {
    this.sessionId = localStorage.getItem("hack_session_id") || this.generateSessionId();
    localStorage.setItem("hack_session_id", this.sessionId);
    
    this.ws = null;
    this.isConnecting = false;
    this.chatInput = document.getElementById("chatInput");
    this.sendBtn = document.getElementById("sendBtn");
    this.messagesContainer = document.getElementById("messagesContainer");
    this.timerElement = document.getElementById("countdownTimer");
    this.connectionDot = document.getElementById("connectionDot");
    this.connectionText = document.getElementById("connectionText");
    this.ticketsList = document.getElementById("ticketsList");

    this.init();
  }

  generateSessionId() {
    return 'hacker_' + Math.random().toString(36).substring(2, 10);
  }

  init() {
    this.connectWebSocket();
    this.setupEventListeners();
    this.startCountdownTimer();
    this.loadSessionState();
  }

  connectWebSocket() {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws/${this.sessionId}`;

    this.connectionText.innerText = "Connecting...";
    this.connectionDot.style.background = "#f59e0b";
    this.connectionDot.style.boxShadow = "0 0 10px #f59e0b";

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        this.connectionText.innerText = "Real-Time WebSocket Online";
        this.connectionDot.style.background = "#10b981";
        this.connectionDot.style.boxShadow = "0 0 10px #10b981";
      };

      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        this.removeTypingIndicator();
        this.renderBotMessage(data);
        if (data.action && data.action.action_type === "TICKET_CREATED") {
          this.loadSessionState();
        }
      };

      this.ws.onerror = (err) => {
        console.warn("WebSocket error:", err);
      };

      this.ws.onclose = () => {
        this.connectionText.innerText = "Reconnecting...";
        this.connectionDot.style.background = "#ef4444";
        this.connectionDot.style.boxShadow = "0 0 10px #ef4444";
        setTimeout(() => this.connectWebSocket(), 3000);
      };
    } catch (e) {
      console.error("WS init error:", e);
    }
  }

  setupEventListeners() {
    this.sendBtn.addEventListener("click", () => this.sendMessage());
    this.chatInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });

    // Profile input auto-save on blur
    ["profileTeam", "profileTable", "profileTrack"].forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        el.addEventListener("change", () => this.saveProfile());
      }
    });
  }

  sendMessage(textOverride = null) {
    const text = (textOverride || this.chatInput.value).trim();
    if (!text) return;

    if (!textOverride) {
      this.chatInput.value = "";
    }

    // 1. Render User Message in UI immediately
    this.renderUserMessage(text);
    this.showTypingIndicator();

    // 2. Transmit via WebSocket (or REST fallback)
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ text: text }));
    } else {
      // Fallback to REST API
      fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: this.sessionId, message: text })
      })
      .then(res => res.json())
      .then(data => {
        this.removeTypingIndicator();
        this.renderBotMessage(data);
      })
      .catch(err => {
        this.removeTypingIndicator();
        this.renderBotMessage({
          reply_text: "⚠️ Network issue communicating with chatbot server. Please check connection.",
          intent: "error",
          confidence: 0.0,
          quick_replies: ["Try again"]
        });
      });
    }
  }

  renderUserMessage(text) {
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const row = document.createElement("div");
    row.className = "message-row user";
    row.innerHTML = `
      <div class="msg-avatar">👤</div>
      <div class="msg-body-wrapper">
        <div class="msg-bubble">${this.escapeHtml(text)}</div>
        <div class="msg-meta" style="justify-content: flex-end;">${timeStr}</div>
      </div>
    `;
    this.messagesContainer.appendChild(row);
    this.scrollToBottom();
  }

  renderBotMessage(data) {
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const row = document.createElement("div");
    row.className = "message-row assistant";

    const parsedMarkdown = (window.marked && typeof marked.parse === 'function')
      ? marked.parse(data.reply_text)
      : this.simpleMarkdown(data.reply_text);

    let quickRepliesHtml = "";
    if (data.quick_replies && data.quick_replies.length > 0) {
      quickRepliesHtml = `
        <div class="quick-replies">
          ${data.quick_replies.map(chip => `<button class="quick-chip" onclick="window.client.sendMessage('${this.escapeHtml(chip)}')">${this.escapeHtml(chip)}</button>`).join('')}
        </div>
      `;
    }

    const intentTag = data.intent ? `<span class="badge-intent">${data.intent} (${Math.round((data.confidence || 0.9) * 100)}%)</span>` : '';
    const latencyTag = data.execution_time_ms ? `<span>• ${data.execution_time_ms.toFixed(1)}ms</span>` : '';

    row.innerHTML = `
      <div class="msg-avatar">⚡</div>
      <div class="msg-body-wrapper">
        <div class="msg-bubble">${parsedMarkdown}</div>
        <div class="msg-meta">
          ${intentTag}
          <span>${timeStr}</span>
          ${latencyTag}
        </div>
        ${quickRepliesHtml}
      </div>
    `;

    this.messagesContainer.appendChild(row);
    this.scrollToBottom();
  }

  showTypingIndicator() {
    this.removeTypingIndicator();
    const ind = document.createElement("div");
    ind.id = "typingIndicator";
    ind.className = "message-row assistant";
    ind.innerHTML = `
      <div class="msg-avatar">⚡</div>
      <div class="msg-bubble" style="padding: 10px 14px;">
        <div class="typing-indicator">
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
        </div>
      </div>
    `;
    this.messagesContainer.appendChild(ind);
    this.scrollToBottom();
  }

  removeTypingIndicator() {
    const el = document.getElementById("typingIndicator");
    if (el) el.remove();
  }

  scrollToBottom() {
    this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
  }

  saveProfile() {
    const team = document.getElementById("profileTeam").value.trim();
    const table = document.getElementById("profileTable").value.trim();
    const track = document.getElementById("profileTrack").value.trim();

    fetch("/api/profile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: this.sessionId,
        team_name: team,
        table_number: table,
        track: track
      })
    });
  }

  loadSessionState() {
    fetch(`/api/state/${this.sessionId}`)
      .then(res => res.json())
      .then(data => {
        if (data.user_profile) {
          if (data.user_profile.team_name) document.getElementById("profileTeam").value = data.user_profile.team_name;
          if (data.user_profile.table_number) document.getElementById("profileTable").value = data.user_profile.table_number;
          if (data.user_profile.track) document.getElementById("profileTrack").value = data.user_profile.track;
        }

        // Render tickets
        if (data.tickets && data.tickets.length > 0) {
          this.ticketsList.innerHTML = data.tickets.map(t => `
            <div class="ticket-item ${t.status === 'RESOLVED' ? 'resolved' : ''}">
              <div class="ticket-header">
                <span>${t.ticket_id} (T-${t.table_number})</span>
                <span class="ticket-status">${t.status}</span>
              </div>
              <div style="font-size: 0.76rem; color: #94a3b8;">${this.escapeHtml(t.topic)}</div>
            </div>
          `).join('');
        } else {
          this.ticketsList.innerHTML = `<div style="font-size: 0.78rem; color: #64748b; font-style: italic;">No active tickets</div>`;
        }
      })
      .catch(err => console.log("State sync:", err));
  }

  startCountdownTimer() {
    // 14 hours countdown simulation or target date
    const target = new Date(Date.now() + 14 * 3600 * 1000);
    const update = () => {
      const diff = Math.max(0, target - new Date());
      const hours = Math.floor(diff / (1000 * 60 * 60));
      const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const secs = Math.floor((diff % (1000 * 60)) / 1000);
      this.timerElement.innerText = `${String(hours).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    };
    update();
    setInterval(update, 1000);
  }

  simpleMarkdown(text) {
    if (!text) return "";
    return text
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      .replace(/^\> (.*$)/gim, '<blockquote style="border-left: 3px solid #38bdf8; padding-left: 8px; margin: 6px 0; color: #93c5fd;">$1</blockquote>')
      .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
      .replace(/\*(.*)\*/gim, '<em>$1</em>')
      .replace(/`([^`]+)`/gim, '<code>$1</code>')
      .replace(/\n/gim, '<br>');
  }

  escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/[&<>"']/g, m => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    })[m]);
  }
}

// Global initialization
window.addEventListener("DOMContentLoaded", () => {
  window.client = new HackathonChatClient();
});
