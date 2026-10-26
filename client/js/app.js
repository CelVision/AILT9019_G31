/**
 * ConnectFour Connect — Main Application Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  // UI Elements
  const onboardingModal = document.getElementById('onboardingModal');
  const registrationForm = document.getElementById('registrationForm');
  const nicknameInput = document.getElementById('nicknameInput');
  const birthYearInput = document.getElementById('birthYearInput');
  const formError = document.getElementById('formError');

  const queueModal = document.getElementById('queueModal');
  const queueProgress = document.getElementById('queueProgress');
  const queueTimerText = document.getElementById('queueTimerText');
  const btnCancelQueue = document.getElementById('btnCancelQueue');

  const matchSection = document.getElementById('matchSection');
  const connectionStatus = document.getElementById('connectionStatus');

  const player1Card = document.getElementById('player1Card');
  const player1Name = document.getElementById('player1Name');
  const player1Role = document.getElementById('player1Role');
  const player2Card = document.getElementById('player2Card');
  const player2Name = document.getElementById('player2Name');
  const player2Role = document.getElementById('player2Role');

  const turnIndicator = document.getElementById('turnIndicator');
  const timerBar = document.getElementById('timerBar');
  const timerText = document.getElementById('timerText');

  const resultModal = document.getElementById('resultModal');
  const resultIcon = document.getElementById('resultIcon');
  const resultTitle = document.getElementById('resultTitle');
  const resultSubtitle = document.getElementById('resultSubtitle');
  const statTurns = document.getElementById('statTurns');
  const statDuration = document.getElementById('statDuration');
  const btnRematch = document.getElementById('btnRematch');
  const btnReturnLobby = document.getElementById('btnReturnLobby');

  const fallbackToast = document.getElementById('fallbackToast');
  const toastMessage = document.getElementById('toastMessage');

  const chatBadge = document.getElementById('chatBadge');
  const chatMessageList = document.getElementById('chatMessageList');
  const chatTypingIndicator = document.getElementById('chatTypingIndicator');
  const chatForm = document.getElementById('chatForm');
  const chatInput = document.getElementById('chatInput');
  const btnSendChat = document.getElementById('btnSendChat');
  const chatSafetyNotice = document.getElementById('chatSafetyNotice');

  // State
  let myPlayerNum = 1; // 1 (Red) or 2 (Yellow)
  let currentTurn = 1;
  let queueInterval = null;
  let turnInterval = null;
  let matchStartTime = null;
  let totalTurns = 0;
  let pendingJoin = null;
  let isQueued = false;
  let isPveMatch = false;

  // Initialize Socket Client
  const socketClient = new GameSocketClient();

  // Initialize Board Renderer
  const boardRenderer = new GameBoardRenderer('gameCanvas', (selectedCol) => {
    // Player made a move
    socketClient.send('player_move', { column: selectedCol });
  });

  // Initialize Canned Chat Manager
  const cannedChat = new CannedChatManager((category, id) => {
    // Send reaction through WebSocket
    socketClient.send('send_reaction', { category, id });
    cannedChat.showReaction(myPlayerNum, category, id);
  });

  // Connection events
  socketClient.on('connected', () => {
    connectionStatus.className = 'status-pill status-connected';
    connectionStatus.querySelector('.status-label').textContent = 'Connected';
    // Send the join as soon as the socket is open; the server owns the queue.
    if (pendingJoin) {
      socketClient.send('queue_join', pendingJoin);
      pendingJoin = null;
    }
  });

  socketClient.on('disconnected', () => {
    connectionStatus.className = 'status-pill status-disconnected';
    connectionStatus.querySelector('.status-label').textContent = 'Offline';
  });

  // Protocol Events
  socketClient.on('queue_status', (payload) => {
    if (!payload || !isQueued) return;
    const total = payload.timeout_seconds || 15;
    const elapsed = payload.elapsed_seconds || 0;
    const pct = Math.min(100, (elapsed / total) * 100);
    const remaining = Math.max(0, Math.ceil(payload.remaining_seconds || 0));
    queueProgress.style.width = `${pct}%`;
    queueTimerText.textContent = payload.waiting > 1
      ? `${remaining}s until an AI opponent joins · ${payload.waiting} waiting`
      : `${remaining}s until an AI opponent joins`;
  });

  socketClient.on('error', (payload) => {
    // Distinguish between queue-time errors (show in form) and in-game errors (show toast)
    const message = payload && payload.message
      ? payload.message
      : 'Something went wrong. Please try again.';

    if (!queueModal.classList.contains('hidden')) {
      isQueued = false;
      clearInterval(queueInterval);
      queueModal.classList.add('hidden');
      onboardingModal.classList.remove('hidden');
      formError.textContent = message;
      formError.classList.remove('hidden');
      socketClient.disconnect();
    } else {
      showToast(message);
    }
  });

  socketClient.on('queue_left', () => {
    isQueued = false;
  });

  socketClient.on('match_found', (payload) => {
    isQueued = false;
    // Hide modals
    clearInterval(queueInterval);
    queueModal.classList.add('hidden');
    onboardingModal.classList.add('hidden');
    matchSection.classList.remove('hidden');

    myPlayerNum = payload.assigned_player;
    currentTurn = 1;
    totalTurns = 0;
    matchStartTime = Date.now();
    boardRenderer.reset();

    // Setup player labels
    player1Name.textContent = myPlayerNum === 1 ? 'You (Red)' : `${payload.opponent_nickname} (Red)`;
    player1Role.textContent = myPlayerNum === 1 ? 'Host' : 'Opponent';
    player2Name.textContent = myPlayerNum === 2 ? 'You (Yellow)' : `${payload.opponent_nickname} (Yellow)`;
    player2Role.textContent = payload.is_pve ? 'AI Bot (GLM)' : 'Peer';

    resultModal.classList.add('hidden');
    const arenaStatus = document.getElementById('gameArenaStatus');
    if (arenaStatus) arenaStatus.textContent = 'Active Match';

    // Setup chat mode & daily topics
    isPveMatch = Boolean(payload.is_pve);
    if (!chatMessageList.hasChildNodes() || chatMessageList.children.length <= 1) {
      chatMessageList.innerHTML = '';
      const emptyHint = document.createElement('div');
      emptyHint.className = 'chat-empty-hint';
      emptyHint.textContent = isPveMatch
        ? 'Chat with AI Coach or tap any daily icebreaker card above!'
        : 'Tap any Daily Campus Icebreaker topic above to share topics safely!';
      chatMessageList.appendChild(emptyHint);
    } else {
      const divider = document.createElement('div');
      divider.className = 'chat-empty-hint';
      divider.textContent = '🎮 --- Match Started ---';
      chatMessageList.appendChild(divider);
    }
    chatTypingIndicator.classList.add('hidden');

    if (isPveMatch) {
      chatBadge.textContent = 'AI Companion';
      chatBadge.className = 'chat-badge pve';
      chatInput.disabled = false;
      chatInput.placeholder = 'Chat with AI Coach (e.g. coffee, midterm, study tips)...';
      btnSendChat.disabled = false;
      chatSafetyNotice.classList.add('hidden');
    } else {
      chatBadge.textContent = 'Peer Match';
      chatBadge.className = 'chat-badge pvp';
      chatInput.disabled = true;
      chatInput.placeholder = 'Pick an Icebreaker Topic above to chat safely...';
      btnSendChat.disabled = true;
      chatSafetyNotice.classList.remove('hidden');
    }

    updateTurnState(1);
    startTurnTimer(payload.turn_duration_seconds || 30);
  });

  socketClient.on('board_update', (payload) => {
    totalTurns++;
    boardRenderer.setBoard(payload.board);
    currentTurn = payload.current_turn;
    updateTurnState(currentTurn);
    startTurnTimer(30);
  });

  socketClient.on('broadcast_reaction', (payload) => {
    cannedChat.showReaction(payload.from_player, payload.category, payload.id);
  });

  socketClient.on('game_over', (payload) => {
    clearInterval(turnInterval);
    boardRenderer.setTurn(false, myPlayerNum);
    if (payload.winning_coordinates) {
      boardRenderer.setWinningCoords(payload.winning_coordinates);
    }
    const arenaStatus = document.getElementById('gameArenaStatus');
    if (arenaStatus) arenaStatus.textContent = 'Match Finished';

    // Win or lose does NOT affect chat: keep chat fully active for post-match talk!
    if (isPveMatch) {
      chatInput.disabled = false;
      chatInput.placeholder = 'Chat post-game (e.g. GG, rematch, tips)...';
      btnSendChat.disabled = false;
    }

    setTimeout(() => {
      showGameOverModal(payload);
    }, 600);
  });

  socketClient.on('pve_fallback_notice', (payload) => {
    showToast(payload.message || 'AI opponent operating in local fallback mode.');
  });

  socketClient.on('rematch_waiting', (payload) => {
    showToast(payload.message || 'Waiting for your opponent to accept the rematch.');
  });

  // Chat & Icebreaker Events
  socketClient.on('chat_message', (payload) => {
    appendChatMessage(payload);
  });

  socketClient.on('chat_reply', (payload) => {
    hideChatTyping();
    appendChatMessage(payload);
  });

  // Daily Topic Pills Click Handlers
  document.querySelectorAll('.topic-pill-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const topicId = parseInt(btn.dataset.id, 10);
      const text = btn.textContent.trim();
      socketClient.send('chat_send', { topic_id: topicId, text });
      if (isPveMatch) {
        showChatTyping();
      }
    });
  });

  // Chat Form Submit Handler
  chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const text = chatInput.value.trim();
    if (!text) return;
    socketClient.send('chat_send', { text });
    chatInput.value = '';
    if (isPveMatch) {
      showChatTyping();
    }
  });

  function appendChatMessage(msg) {
    const emptyHint = chatMessageList.querySelector('.chat-empty-hint');
    if (emptyHint) emptyHint.remove();

    const isMe = msg.from_player === myPlayerNum;
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${isMe ? 'me' : 'them'} ${msg.topic_id ? 'topic-card' : ''}`;

    const senderSpan = document.createElement('span');
    senderSpan.className = 'chat-sender';
    senderSpan.textContent = isMe ? 'You' : (msg.sender_name || 'Opponent');

    const textSpan = document.createElement('span');
    textSpan.className = 'chat-text';
    textSpan.textContent = msg.text;

    const timeSpan = document.createElement('span');
    timeSpan.className = 'chat-time';
    const d = msg.timestamp ? new Date(msg.timestamp * 1000) : new Date();
    timeSpan.textContent = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    bubble.appendChild(senderSpan);
    bubble.appendChild(textSpan);
    bubble.appendChild(timeSpan);

    chatMessageList.appendChild(bubble);
    chatMessageList.scrollTop = chatMessageList.scrollHeight;
  }

  function showChatTyping() {
    chatTypingIndicator.classList.remove('hidden');
    chatMessageList.scrollTop = chatMessageList.scrollHeight;
  }

  function hideChatTyping() {
    chatTypingIndicator.classList.add('hidden');
  }

  // Registration Form Submit
  registrationForm.addEventListener('submit', (e) => {
    e.preventDefault();
    formError.classList.add('hidden');

    const nickname = nicknameInput.value.trim();
    const birthYear = parseInt(birthYearInput.value, 10);
    const currentYear = new Date().getFullYear();
    const age = currentYear - birthYear;

    if (nickname.length < 2 || nickname.length > 16) {
      formError.textContent = 'Nickname must be 2–16 characters.';
      formError.classList.remove('hidden');
      return;
    }

    if (!Number.isInteger(birthYear) || age < 18 || birthYear < 1920) {
      formError.textContent = 'Birth year must be valid and the player must be 18+.';
      formError.classList.remove('hidden');
      return;
    }

    // Connect to WebSocket; queue_join fires from the 'connected' handler.
    pendingJoin = { nickname, birth_year: birthYear };
    showQueueModal();
    socketClient.connect();
  });

  function showQueueModal() {
    onboardingModal.classList.add('hidden');
    queueModal.classList.remove('hidden');
    isQueued = true;
    queueProgress.style.width = '0%';
    queueTimerText.textContent = 'Joining the queue…';
  }

  btnCancelQueue.addEventListener('click', () => {
    clearInterval(queueInterval);
    isQueued = false;
    if (pendingJoin) pendingJoin = null;
    socketClient.send('queue_left', {});
    queueModal.classList.add('hidden');
    onboardingModal.classList.remove('hidden');
    socketClient.disconnect();
  });

  function updateTurnState(turn) {
    const isMyTurn = turn === myPlayerNum;
    boardRenderer.setTurn(isMyTurn, myPlayerNum);

    if (turn === 1) {
      player1Card.classList.add('active-turn');
      player2Card.classList.remove('active-turn');
    } else {
      player2Card.classList.add('active-turn');
      player1Card.classList.remove('active-turn');
    }

    turnIndicator.textContent = isMyTurn ? 'Your Turn' : "Opponent's Turn";
    turnIndicator.style.color = isMyTurn ? '#38bdf8' : '#94a3b8';
  }

  function startTurnTimer(duration) {
    clearInterval(turnInterval);
    let timeLeft = duration;
    timerBar.style.width = '100%';
    timerText.textContent = `${timeLeft}s`;

    turnInterval = setInterval(() => {
      timeLeft--;
      const pct = (timeLeft / duration) * 100;
      timerBar.style.width = `${pct}%`;
      timerText.textContent = `${timeLeft}s`;

      if (timeLeft <= 0) {
        clearInterval(turnInterval);
      }
    }, 1000);
  }

  function showGameOverModal(data) {
    resultModal.classList.remove('hidden');
    const elapsedSec = matchStartTime ? Math.round((Date.now() - matchStartTime) / 1000) : 0;
    const mins = Math.floor(elapsedSec / 60);
    const secs = elapsedSec % 60;
    statDuration.textContent = `${mins}m ${secs}s`;
    statTurns.textContent = totalTurns;

    if (data.winner === myPlayerNum) {
      resultIcon.textContent = '🏆';
      resultTitle.textContent = 'Victory!';
      resultSubtitle.textContent = 'You connected 4 tokens!';
    } else if (data.winner === 0) {
      resultIcon.textContent = '🤝';
      resultTitle.textContent = 'Draw Game';
      resultSubtitle.textContent = 'The board is completely filled!';
    } else {
      resultIcon.textContent = '👏';
      resultTitle.textContent = 'Well Played!';
      resultSubtitle.textContent = 'Your opponent connected 4 in a row.';
    }
  }

  btnReturnLobby.addEventListener('click', () => {
    resultModal.classList.add('hidden');
    matchSection.classList.add('hidden');
    onboardingModal.classList.remove('hidden');
    socketClient.disconnect();
  });

  btnRematch.addEventListener('click', () => {
    resultModal.classList.add('hidden');
    socketClient.send('rematch_request', {});
  });

  function showToast(msg) {
    toastMessage.textContent = msg;
    fallbackToast.classList.remove('hidden');
    setTimeout(() => {
      fallbackToast.classList.add('hidden');
    }, 4000);
  }
});
