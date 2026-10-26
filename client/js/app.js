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

  // State
  let myPlayerNum = 1; // 1 (Red) or 2 (Yellow)
  let currentTurn = 1;
  let queueInterval = null;
  let turnInterval = null;
  let matchStartTime = null;
  let totalTurns = 0;

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
  });

  socketClient.on('disconnected', () => {
    connectionStatus.className = 'status-pill status-disconnected';
    connectionStatus.querySelector('.status-label').textContent = 'Offline';
  });

  // Protocol Events
  socketClient.on('match_found', (payload) => {
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

    setTimeout(() => {
      showGameOverModal(payload);
    }, 1200);
  });

  socketClient.on('pve_fallback_notice', (payload) => {
    showToast(payload.message || 'AI opponent operating in local fallback mode.');
  });

  socketClient.on('queue_status', (payload) => {
    const timeout = payload.timeout_seconds || 15;
    const elapsed = Math.min(timeout, payload.elapsed_seconds || 0);
    queueProgress.style.width = `${(elapsed / timeout) * 100}%`;
    const remaining = Math.max(0, timeout - elapsed);
    queueTimerText.textContent = `${remaining}s remaining before AI opponent joins`;
  });

  socketClient.on('rematch_waiting', (payload) => {
    showToast(payload.message || 'Waiting for your opponent to accept the rematch.');
  });

  socketClient.on('error', (payload) => {
    const message = payload && payload.message
      ? payload.message
      : 'The server rejected that request.';
    if (!queueModal.classList.contains('hidden')) {
      clearInterval(queueInterval);
      queueModal.classList.add('hidden');
      onboardingModal.classList.remove('hidden');
      formError.textContent = message;
      formError.classList.remove('hidden');
    } else {
      showToast(message);
    }
  });

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

    // Connect to WebSocket and enter queue
    socketClient.connect();
    showQueueModal(nickname, birthYear);
  });

  function showQueueModal(nickname, birthYear) {
    onboardingModal.classList.add('hidden');
    queueModal.classList.remove('hidden');

    let secondsElapsed = 0;
    const maxSeconds = 15;
    queueProgress.style.width = '0%';
    queueTimerText.textContent = `${maxSeconds}s remaining before AI opponent joins`;

    queueInterval = setInterval(() => {
      secondsElapsed++;
      const pct = (secondsElapsed / maxSeconds) * 100;
      queueProgress.style.width = `${pct}%`;
      const remaining = Math.max(0, maxSeconds - secondsElapsed);
      queueTimerText.textContent = `${remaining}s remaining before AI opponent joins`;

      if (secondsElapsed === 1) {
        socketClient.send('queue_join', { nickname, birth_year: birthYear });
      }
    }, 1000);
  }

  btnCancelQueue.addEventListener('click', () => {
    clearInterval(queueInterval);
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
