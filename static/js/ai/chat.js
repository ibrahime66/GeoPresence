/* Chat GeoIA — envoi asynchrone : le message de l'utilisateur s'affiche
 * immédiatement, un indicateur "GeoIA réfléchit…" pendant l'attente de la
 * réponse, puis la réponse remplace l'indicateur — sans recharger la page
 * (CDC §15.3.3). Se dégrade en formulaire POST classique si JS est absent. */
(() => {
  "use strict";

  const configEl = document.getElementById("geoia-config");
  if (!configEl) return;
  const config = JSON.parse(configEl.textContent);
  let conversationId = config.conversationId;

  const els = {
    thread: document.getElementById("gpChatThread"),
    form: document.getElementById("gpChatForm"),
    textarea: document.getElementById("gpChatInput"),
    sendBtn: document.getElementById("gpChatSendBtn"),
    suggestions: document.getElementById("gpChatSuggestions"),
    sidebarList: document.getElementById("gpChatSidebarList"),
  };
  if (!els.form || !els.textarea) return;

  function apiUrl() {
    return conversationId ? `/ia/${conversationId}/` : "/ia/";
  }

  function scrollToBottom() {
    // Bureau : le fil défile en interne (overflow-y: auto). Mobile : le fil
    // n'a plus de défilement propre (cf. main.css, un seul niveau de
    // défilement sur mobile) — dans ce cas scrollTop est un no-op, on fait
    // défiler la page pour amener le formulaire d'envoi dans la vue à la place.
    if (els.thread.scrollHeight > els.thread.clientHeight) {
      els.thread.scrollTop = els.thread.scrollHeight;
    } else {
      els.form.scrollIntoView({ block: "end" });
    }
  }

  function clearEmptyState() {
    const empty = els.thread.querySelector(".gp-empty");
    if (empty) empty.remove();
  }

  function appendBubble(role, text) {
    const div = document.createElement("div");
    div.className = `gp-chat-bubble ${role.toLowerCase()}`;
    div.textContent = text;
    els.thread.appendChild(div);
    scrollToBottom();
    return div;
  }

  function appendTypingIndicator() {
    const div = document.createElement("div");
    div.className = "gp-chat-bubble assistant gp-chat-typing";
    div.innerHTML = "<span></span><span></span><span></span>";
    els.thread.appendChild(div);
    scrollToBottom();
    return div;
  }

  function setSuggestions(list) {
    els.suggestions.innerHTML = "";
    (list || []).forEach((text) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "gp-chat-suggestion-btn";
      btn.textContent = text;
      btn.addEventListener("click", () => sendQuestion(text));
      els.suggestions.appendChild(btn);
    });
  }

  function setFormDisabled(disabled) {
    els.textarea.disabled = disabled;
    els.sendBtn.disabled = disabled;
  }

  function addSidebarEntry(id, title) {
    if (!els.sidebarList) return;
    const emptyMsg = els.sidebarList.querySelector(".gp-chat-empty-list");
    if (emptyMsg) emptyMsg.remove();
    els.sidebarList.querySelectorAll(".gp-chat-conv-link.is-active").forEach((el) => el.classList.remove("is-active"));
    const link = document.createElement("a");
    link.href = `/ia/${id}/`;
    link.className = "gp-chat-conv-link is-active";
    link.textContent = title || config.newConversationLabel;
    els.sidebarList.insertBefore(link, els.sidebarList.firstChild);
  }

  let isSending = false;

  function sendQuestion(question) {
    question = (question || "").trim();
    // Garde explicite en plus de la désactivation du formulaire : celle-ci
    // empêche un clic/appui normal, mais pas un second envoi déclenché par
    // un autre chemin (ex. Entrée pendant qu'une requête est déjà en cours).
    // Sans ça, une deuxième question partirait vers une conversation encore
    // sans identifiant (avant retour de la première réponse) et créerait une
    // conversation séparée au lieu de s'ajouter à la bonne.
    if (!question || isSending) return;
    isSending = true;

    clearEmptyState();
    appendBubble("user", question);
    setSuggestions([]);
    setFormDisabled(true);
    els.textarea.value = "";
    const typingEl = appendTypingIndicator();

    const formData = new FormData();
    formData.append("question", question);

    fetch(apiUrl(), {
      method: "POST",
      headers: { "X-CSRFToken": config.csrfToken, "X-Requested-With": "XMLHttpRequest" },
      body: formData,
      credentials: "same-origin",
    })
      .then(async (response) => {
        const data = await response.json();
        typingEl.remove();
        if (!response.ok) {
          appendBubble("assistant", data.error || config.genericError);
          return;
        }
        const isNewConversation = !conversationId;
        if (data.conversation_id) conversationId = data.conversation_id;
        appendBubble("assistant", data.answer);
        setSuggestions(data.suggestions);
        if (isNewConversation && conversationId) {
          window.history.replaceState({}, "", `/ia/${conversationId}/`);
          addSidebarEntry(conversationId, data.conversation_title);
        }
      })
      .catch(() => {
        typingEl.remove();
        appendBubble("assistant", config.networkError);
      })
      .finally(() => {
        isSending = false;
        setFormDisabled(false);
        // preventScroll : sans ça, le navigateur fait défiler la page pour
        // amener le textarea dans la vue, ce qui pousse l'en-tête sous la
        // topbar collante (position: sticky) et donne l'impression qu'il a
        // disparu.
        els.textarea.focus({ preventScroll: true });
      });
  }

  els.form.addEventListener("submit", (e) => {
    e.preventDefault();
    sendQuestion(els.textarea.value);
  });

  els.textarea.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      els.form.requestSubmit();
    }
  });

  document.querySelectorAll(".gp-chat-suggestion-btn[data-question]").forEach((btn) => {
    btn.addEventListener("click", () => sendQuestion(btn.dataset.question));
  });

  scrollToBottom();
})();
