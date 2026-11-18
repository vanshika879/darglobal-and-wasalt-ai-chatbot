document.addEventListener("DOMContentLoaded", () => {
  const messagesArea = document.getElementById("messagesArea");
  const chatForm = document.getElementById("chatForm");
  const messageInput = document.getElementById("messageInput");
  const sendBtn = document.getElementById("sendBtn");
  const modelSelect = document.getElementById("modelSelect");

  // Modals & Buttons
  const settingsBtn = document.getElementById("settingsBtn");
  const settingsModal = document.getElementById("settingsModal");
  const closeSettingsBtn = document.getElementById("closeSettingsBtn");
  const openRouterKeyInput = document.getElementById("openRouterKeyInput");
  const saveKeyBtn = document.getElementById("saveKeyBtn");
  const clearKeyBtn = document.getElementById("clearKeyBtn");

  const portfolioBtn = document.getElementById("portfolioBtn");
  const portfolioModal = document.getElementById("portfolioModal");
  const closePortfolioBtn = document.getElementById("closePortfolioBtn");
  const propertiesGrid = document.getElementById("propertiesGrid");
  const tabBtns = document.querySelectorAll(".tab-btn");

  const bookConsultBtn = document.getElementById("bookConsultBtn");
  const leadModal = document.getElementById("leadModal");
  const closeLeadBtn = document.getElementById("closeLeadBtn");
  const leadForm = document.getElementById("leadForm");

  let conversationHistory = [];
  let cachedProperties = [];

  // Load API Key from localStorage
  const savedKey = localStorage.getItem("dg_openrouter_key") || "";
  if (savedKey) {
    openRouterKeyInput.value = savedKey;
  }

  // Auto-resize input textarea
  messageInput.addEventListener("input", function() {
    this.style.height = "auto";
    this.style.height = Math.min(this.scrollHeight, 120) + "px";
  });

  messageInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      chatForm.dispatchEvent(new Event("submit"));
    }
  });

  // Suggestion chips
  document.querySelectorAll(".chip").forEach(chip => {
    chip.addEventListener("click", () => {
      const prompt = chip.getAttribute("data-prompt");
      if (prompt) {
        messageInput.value = prompt;
        chatForm.dispatchEvent(new Event("submit"));
      }
    });
  });

  // Chat Submission
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = messageInput.value.trim();
    if (!message) return;

    // Reset input
    messageInput.value = "";
    messageInput.style.height = "auto";

    // Append User Message Bubble
    appendMessage("user", message);

    // Show Loading Assistant Bubble
    const assistantBubbleId = appendLoadingBubble();

    // Disable send button while awaiting response
    sendBtn.disabled = true;

    try {
      const selectedModel = modelSelect.value;
      const apiKey = localStorage.getItem("dg_openrouter_key") || "";

      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: message,
          history: conversationHistory,
          model: selectedModel,
          api_key: apiKey
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to generate response`);
      }

      const data = await response.json();
      replaceLoadingBubble(assistantBubbleId, data);

      // Update history
      conversationHistory.push({ role: "user", content: message });
      conversationHistory.push({ role: "assistant", content: data.response });

    } catch (err) {
      console.error(err);
      replaceLoadingBubble(assistantBubbleId, {
        response: `⚠️ **Connection Notice:** Unable to reach AI service (${err.message}). Please check your OpenRouter API key in settings or verify network connectivity.`,
        model_used: "error",
        retrieved_documents: []
      });
    } finally {
      sendBtn.disabled = false;
      messageInput.focus();
    }
  });

  function appendMessage(role, text) {
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${role}`;

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = role === "assistant" ? "DG" : "You";

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";

    if (role === "assistant" && typeof marked !== "undefined") {
      bubble.innerHTML = marked.parse(text);
    } else {
      bubble.textContent = text;
    }

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(bubble);
    messagesArea.appendChild(msgDiv);
    scrollToBottom();
  }

  function appendLoadingBubble() {
    const bubbleId = "loading-" + Date.now();
    const msgDiv = document.createElement("div");
    msgDiv.className = "message assistant";
    msgDiv.id = bubbleId;

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = "DG";

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";
    bubble.innerHTML = `<em>Consulting DarGlobal & Wasalt luxury database...</em>`;

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(bubble);
    messagesArea.appendChild(msgDiv);
    scrollToBottom();
    return bubbleId;
  }

  function replaceLoadingBubble(bubbleId, data) {
    const container = document.getElementById(bubbleId);
    if (!container) return;

    const bubble = container.querySelector(".message-bubble");
    const rawContent = data.response || "No response received.";

    let parsedHtml = (typeof marked !== "undefined") ? marked.parse(rawContent) : `<p>${rawContent}</p>`;

    // Append source tags if documents were retrieved
    if (data.retrieved_documents && data.retrieved_documents.length > 0) {
      let sourcesHtml = `
        <div class="sources-panel">
          <div class="sources-toggle">✦ Verified Data Sources:</div>
          <div class="sources-list">
      `;
      data.retrieved_documents.forEach(doc => {
        const title = doc.title || "Record";
        const url = doc.metadata?.url || "#";
        const entity = doc.entity || "DarGlobal";
        sourcesHtml += `<a href="${url}" target="_blank" rel="noopener noreferrer" class="source-tag">🏛️ [${entity}] ${title}</a>`;
      });
      sourcesHtml += `
          </div>
        </div>
      `;
      parsedHtml += sourcesHtml;
    }

    if (data.model_used) {
      parsedHtml += `<span class="model-meta-badge">Model: ${data.model_used}</span>`;
    }

    bubble.innerHTML = parsedHtml;
    scrollToBottom();
  }

  function scrollToBottom() {
    messagesArea.scrollTop = messagesArea.scrollHeight;
  }

  // Modals management
  function setupModal(openBtn, modalEl, closeBtn) {
    openBtn?.addEventListener("click", () => modalEl.classList.add("active"));
    closeBtn?.addEventListener("click", () => modalEl.classList.remove("active"));
    modalEl?.addEventListener("click", (e) => {
      if (e.target === modalEl) modalEl.classList.remove("active");
    });
  }

  setupModal(settingsBtn, settingsModal, closeSettingsBtn);
  setupModal(portfolioBtn, portfolioModal, closePortfolioBtn);
  setupModal(bookConsultBtn, leadModal, closeLeadBtn);

  // Settings: Save / Clear API Key
  saveKeyBtn.addEventListener("click", () => {
    const keyVal = openRouterKeyInput.value.trim();
    if (keyVal) {
      localStorage.setItem("dg_openrouter_key", keyVal);
      alert("OpenRouter API Key saved successfully!");
    } else {
      localStorage.removeItem("dg_openrouter_key");
      alert("OpenRouter API Key removed.");
    }
    settingsModal.classList.remove("active");
  });

  clearKeyBtn.addEventListener("click", () => {
    openRouterKeyInput.value = "";
    localStorage.removeItem("dg_openrouter_key");
    alert("API Key cleared.");
  });

  // Portfolio fetch & display
  portfolioBtn.addEventListener("click", async () => {
    if (cachedProperties.length === 0) {
      try {
        const res = await fetch("/api/properties");
        const json = await res.json();
        cachedProperties = json.properties || [];
        renderProperties("all");
      } catch (e) {
        propertiesGrid.innerHTML = `<div style="color:red;">Failed to load properties.</div>`;
      }
    }
  });

  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      tabBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const filter = btn.getAttribute("data-filter");
      renderProperties(filter);
    });
  });

  function renderProperties(filter) {
    let list = cachedProperties;
    if (filter === "darglobal") {
      list = cachedProperties.filter(p => (p.developer || "").toLowerCase().includes("darglobal"));
    } else if (filter === "wasalt") {
      list = cachedProperties.filter(p => (p.source || p.portal || "").toLowerCase().includes("wasalt") || (p.country || "").includes("Saudi"));
    }

    if (list.length === 0) {
      propertiesGrid.innerHTML = `<div>No properties found for this category.</div>`;
      return;
    }

    propertiesGrid.innerHTML = list.map(p => `
      <div class="property-card">
        <div>
          <div class="prop-badge">${p.brand_partner || p.developer || "Exclusive"}</div>
          <div class="prop-title">${p.name}</div>
          <div class="prop-location">📍 ${p.city}, ${p.country}</div>
          <div class="prop-price">${p.price_starting || "Inquire for price"}</div>
          <div class="prop-amenities">${(p.key_amenities || []).slice(0, 3).map(a => `• ${a}`).join("<br>")}</div>
        </div>
        <div>
          <a href="${p.website_url || '#'}" target="_blank" rel="noopener noreferrer" class="prop-link">
            Official Presentation ↗
          </a>
        </div>
      </div>
    `).join("");
  }

  // Lead capture form
  leadForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      name: document.getElementById("leadName").value,
      email: document.getElementById("leadEmail").value,
      phone: document.getElementById("leadPhone").value,
      property_interest: document.getElementById("leadProperty").value
    };

    try {
      const res = await fetch("/api/lead", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      alert(data.message || "Thank you. Our VIP advisor will contact you shortly.");
      leadForm.reset();
      leadModal.classList.remove("active");
    } catch (err) {
      alert("Error submitting inquiry. Please try again.");
    }
  });
});
