/**
 * SkillMarket Global Floating AI Career Assistant
 * Position persistence, session chat memory, dragging, and context awareness.
 */

(function() {
  'use strict';

  document.addEventListener('DOMContentLoaded', function() {
    const widget = document.getElementById('sm-ai-widget');
    if (!widget) return; // Do not initialize if widget is absent (e.g. on /admin)

    const launcher = document.getElementById('sm-ai-launcher');
    const windowEl = document.getElementById('sm-ai-window');
    const header = document.getElementById('sm-ai-header');
    const closeBtn = document.getElementById('sm-ai-close-btn');
    const clearBtn = document.getElementById('sm-ai-clear-btn');
    const form = document.getElementById('sm-ai-form');
    const input = document.getElementById('sm-ai-input');
    const messagesContainer = document.getElementById('sm-ai-messages');
    const typingIndicator = document.getElementById('sm-ai-typing');
    const contextPill = document.getElementById('sm-ai-context-text');
    const modelTag = document.getElementById('sm-ai-model-tag');
    const suggestionsContainer = document.getElementById('sm-ai-suggestions');

    let chatHistory = [];
    let isOpen = false;

    // Load saved launcher position
    try {
      const savedPos = localStorage.getItem('sm_ai_launcher_pos');
      if (savedPos) {
        const { left, top } = JSON.parse(savedPos);
        if (left && top && left < window.innerWidth && top < window.innerHeight) {
          launcher.style.left = `${left}px`;
          launcher.style.top = `${top}px`;
          launcher.style.right = 'auto';
          launcher.style.bottom = 'auto';
        }
      }
    } catch (e) {
      console.warn('Could not load launcher position', e);
    }

    // Restore chat history from sessionStorage
    try {
      const savedHistory = sessionStorage.getItem('sm_ai_chat_history');
      if (savedHistory) {
        chatHistory = JSON.parse(savedHistory);
        if (chatHistory.length > 0) {
          // Clear initial welcome message
          messagesContainer.innerHTML = '';
          chatHistory.forEach(msg => {
            renderMessage(msg.sender, msg.text, msg.time, false);
          });
          scrollToBottom();
        }
      }
    } catch (e) {
      console.warn('Could not restore chat history', e);
    }

    // Set page context pill
    updatePageContext();

    // Toggle Window Visibility
    function openChat() {
      isOpen = true;
      windowEl.style.display = 'flex';
      launcher.style.display = 'none';
      scrollToBottom();
      setTimeout(() => input && input.focus(), 150);
      if (window.lucide) lucide.createIcons();
    }

    function closeChat() {
      isOpen = false;
      windowEl.style.display = 'none';
      launcher.style.display = 'flex';
    }

    closeBtn.addEventListener('click', closeChat);

    // Draggable Launcher with click distinction
    let isDraggingLauncher = false;
    let dragStartX = 0;
    let dragStartY = 0;
    let initialLeft = 0;
    let initialTop = 0;
    let hasMoved = false;

    launcher.addEventListener('mousedown', startDragLauncher);
    launcher.addEventListener('touchstart', startDragLauncher, { passive: false });

    function startDragLauncher(e) {
      const isTouch = e.type === 'touchstart';
      dragStartX = isTouch ? e.touches[0].clientX : e.clientX;
      dragStartY = isTouch ? e.touches[0].clientY : e.clientY;

      const rect = launcher.getBoundingClientRect();
      initialLeft = rect.left;
      initialTop = rect.top;
      hasMoved = false;

      if (!isTouch) {
        document.addEventListener('mousemove', onDragLauncher);
        document.addEventListener('mouseup', endDragLauncher);
      } else {
        document.addEventListener('touchmove', onDragLauncher, { passive: false });
        document.addEventListener('touchend', endDragLauncher);
      }
    }

    function onDragLauncher(e) {
      const isTouch = e.type === 'touchmove';
      const clientX = isTouch ? e.touches[0].clientX : e.clientX;
      const clientY = isTouch ? e.touches[0].clientY : e.clientY;

      const deltaX = clientX - dragStartX;
      const deltaY = clientY - dragStartY;

      if (Math.abs(deltaX) > 4 || Math.abs(deltaY) > 4) {
        hasMoved = true;
        isDraggingLauncher = true;
        launcher.classList.add('dragging');
      }

      if (isDraggingLauncher) {
        if (isTouch) e.preventDefault();
        let newLeft = initialLeft + deltaX;
        let newTop = initialTop + deltaY;

        // Clamp to screen bounds
        newLeft = Math.max(10, Math.min(window.innerWidth - 68, newLeft));
        newTop = Math.max(10, Math.min(window.innerHeight - 68, newTop));

        launcher.style.left = `${newLeft}px`;
        launcher.style.top = `${newTop}px`;
        launcher.style.right = 'auto';
        launcher.style.bottom = 'auto';
      }
    }

    function endDragLauncher() {
      document.removeEventListener('mousemove', onDragLauncher);
      document.removeEventListener('mouseup', endDragLauncher);
      document.removeEventListener('touchmove', onDragLauncher);
      document.removeEventListener('touchend', endDragLauncher);

      launcher.classList.remove('dragging');

      if (hasMoved) {
        try {
          const rect = launcher.getBoundingClientRect();
          localStorage.setItem('sm_ai_launcher_pos', JSON.stringify({ left: rect.left, top: rect.top }));
        } catch (e) {}
      } else {
        // Just a simple click -> toggle window
        openChat();
      }
      isDraggingLauncher = false;
    }

    // Draggable Window Header
    let isDraggingWindow = false;
    let winStartX = 0, winStartY = 0;
    let winInitLeft = 0, winInitTop = 0;

    header.addEventListener('mousedown', startDragWindow);
    header.addEventListener('touchstart', startDragWindow, { passive: false });

    function startDragWindow(e) {
      if (e.target.closest('.sm-ai-btn-icon')) return; // Ignore clicks on action buttons
      const isTouch = e.type === 'touchstart';
      winStartX = isTouch ? e.touches[0].clientX : e.clientX;
      winStartY = isTouch ? e.touches[0].clientY : e.clientY;

      const rect = windowEl.getBoundingClientRect();
      winInitLeft = rect.left;
      winInitTop = rect.top;
      isDraggingWindow = true;

      if (!isTouch) {
        document.addEventListener('mousemove', onDragWindow);
        document.addEventListener('mouseup', endDragWindow);
      } else {
        document.addEventListener('touchmove', onDragWindow, { passive: false });
        document.addEventListener('touchend', endDragWindow);
      }
    }

    function onDragWindow(e) {
      if (!isDraggingWindow) return;
      const isTouch = e.type === 'touchmove';
      if (isTouch) e.preventDefault();

      const clientX = isTouch ? e.touches[0].clientX : e.clientX;
      const clientY = isTouch ? e.touches[0].clientY : e.clientY;

      let newLeft = winInitLeft + (clientX - winStartX);
      let newTop = winInitTop + (clientY - winStartY);

      newLeft = Math.max(10, Math.min(window.innerWidth - windowEl.offsetWidth - 10, newLeft));
      newTop = Math.max(10, Math.min(window.innerHeight - windowEl.offsetHeight - 10, newTop));

      windowEl.style.left = `${newLeft}px`;
      windowEl.style.top = `${newTop}px`;
      windowEl.style.right = 'auto';
      windowEl.style.bottom = 'auto';
    }

    function endDragWindow() {
      isDraggingWindow = false;
      document.removeEventListener('mousemove', onDragWindow);
      document.removeEventListener('mouseup', endDragWindow);
      document.removeEventListener('touchmove', onDragWindow);
      document.removeEventListener('touchend', endDragWindow);
    }

    // Clear Conversation
    clearBtn.addEventListener('click', function() {
      if (confirm('Clear career assistant conversation history?')) {
        chatHistory = [];
        sessionStorage.removeItem('sm_ai_chat_history');
        messagesContainer.innerHTML = `
          <div class="sm-ai-message sm-ai-message-assistant">
            <div class="sm-ai-bubble">
              <p>Conversation cleared. How can I assist your career progression today?</p>
            </div>
            <div class="sm-ai-time">Just now</div>
          </div>
        `;
      }
    });

    // Handle Form Submit
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      const text = input.value.trim();
      if (!text) return;
      sendMessage(text);
      input.value = '';
    });

    // Suggestion Chips Click
    suggestionsContainer.addEventListener('click', function(e) {
      const chip = e.target.closest('.sm-ai-chip');
      if (chip) {
        const prompt = chip.getAttribute('data-prompt');
        if (prompt) {
          sendMessage(prompt);
        }
      }
    });

    function sendMessage(text) {
      const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

      // Append user bubble
      renderMessage('user', text, timeStr, true);
      scrollToBottom();

      // Show typing indicator
      typingIndicator.style.display = 'flex';
      scrollToBottom();

      // Collect page context
      const pageContext = collectPageContext();

      // Send to Backend
      fetch('/api/ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
          message: text,
          page_context: pageContext,
          history: chatHistory
        })
      })
      .then(res => res.json())
      .then(data => {
        typingIndicator.style.display = 'none';
        if (data.reply) {
          const respTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
          renderMessage('assistant', data.reply, respTime, true);
          if (data.model) {
            modelTag.textContent = data.source === 'ai_api' ? data.model : 'Career Intelligence';
          }
          if (data.suggestions && data.suggestions.length > 0) {
            renderSuggestions(data.suggestions);
          }
        } else if (data.error) {
          renderMessage('assistant', `⚠️ ${data.error}`, timeStr, false);
        }
        scrollToBottom();
      })
      .catch(err => {
        typingIndicator.style.display = 'none';
        renderMessage('assistant', "⚠️ Unable to reach career assistant service. Please check your connection.", timeStr, false);
        scrollToBottom();
      });
    }

    function renderMessage(sender, rawText, timeStr, save) {
      const msgDiv = document.createElement('div');
      msgDiv.className = `sm-ai-message sm-ai-message-${sender}`;

      const bubble = document.createElement('div');
      bubble.className = 'sm-ai-bubble';

      if (sender === 'assistant') {
        bubble.innerHTML = parseSimpleMarkdown(rawText);
      } else {
        bubble.textContent = rawText;
      }

      const timeDiv = document.createElement('div');
      timeDiv.className = 'sm-ai-time';
      timeDiv.textContent = timeStr || 'Just now';

      msgDiv.appendChild(bubble);
      msgDiv.appendChild(timeDiv);
      messagesContainer.appendChild(msgDiv);

      if (save) {
        chatHistory.push({ sender, text: rawText, time: timeStr });
        try {
          sessionStorage.setItem('sm_ai_chat_history', JSON.stringify(chatHistory));
        } catch (e) {}
      }

      if (window.lucide) lucide.createIcons();
    }

    function renderSuggestions(suggestions) {
      suggestionsContainer.innerHTML = '';
      suggestions.forEach(s => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'sm-ai-chip';
        btn.setAttribute('data-prompt', s);
        btn.textContent = s;
        suggestionsContainer.appendChild(btn);
      });
    }

    function scrollToBottom() {
      setTimeout(() => {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
      }, 50);
    }

    function parseSimpleMarkdown(text) {
      if (!text) return '';
      let html = text
        // Headers
        .replace(/^### (.*$)/gim, '<h4>$1</h4>')
        .replace(/^## (.*$)/gim, '<h3>$1</h3>')
        // Bold
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // Inline code
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        // Links
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>')
        // Bullet list items
        .replace(/^\s*-\s+(.*$)/gim, '<li>$1</li>');

      // Wrap contiguous <li> with <ul>
      html = html.replace(/(<li>[\s\S]*?<\/li>)/g, '<ul>$1</ul>');
      // Clean duplicate consecutive <ul> tags
      html = html.replace(/<\/ul>\s*<ul>/g, '');

      // Wrap paragraphs
      const paragraphs = html.split(/\n\n+/).map(p => {
        p = p.trim();
        if (p.startsWith('<h') || p.startsWith('<ul') || p.startsWith('<li')) {
          return p;
        }
        return `<p>${p.replace(/\n/g, '<br>')}</p>`;
      });

      return paragraphs.join('');
    }

    function collectPageContext() {
      const path = window.location.pathname;
      const title = document.title;
      const context = { url: path, title: title };

      // Check if on skill gap result page
      const gapBtn = document.querySelector('.ask-ai-gap-btn');
      if (gapBtn) {
        context.role = gapBtn.getAttribute('data-role');
        context.score = gapBtn.getAttribute('data-score');
        context.missing = gapBtn.getAttribute('data-missing');
      }

      // Check if on resume result page
      const resumeBtn = document.querySelector('.ask-ai-resume-btn');
      if (resumeBtn) {
        context.resumeSkills = resumeBtn.getAttribute('data-skills');
        context.targetRole = resumeBtn.getAttribute('data-role');
      }

      return context;
    }

    function updatePageContext() {
      const path = window.location.pathname;
      let label = 'SkillMarket Overview';
      if (path.includes('skill-gap')) label = 'Skill Gap Analyzer';
      else if (path.includes('resume-analyzer')) label = 'Resume Skill Analyzer';
      else if (path.includes('dashboard')) label = 'User Dashboard';
      else if (path.includes('roadmaps')) label = 'Career Roadmap';
      else if (path.includes('skills')) label = 'Skills Directory';
      else if (path.includes('analytics')) label = 'Market Insights';

      if (contextPill) contextPill.textContent = `Context: ${label}`;
    }

    // Expose Global API
    window.SkillMarketAI = {
      open: openChat,
      close: closeChat,
      openWithPrompt: function(prompt) {
        openChat();
        if (prompt) {
          sendMessage(prompt);
        }
      },
      send: sendMessage
    };

    // Listen to custom window events
    window.addEventListener('skillmarket:open-ai', function(e) {
      const prompt = e.detail && e.detail.prompt;
      if (window.SkillMarketAI) {
        window.SkillMarketAI.openWithPrompt(prompt);
      }
    });

  });
})();
