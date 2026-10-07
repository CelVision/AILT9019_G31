/**
 * Canned Interaction & Reaction Manager
 * Handles 6 preset phrases and 4 reaction stickers with animated speech bubbles.
 */

const CANNED_PHRASES = {
  1: "Good luck!",
  2: "Nice move!",
  3: "Thinking...",
  4: "Close one!",
  5: "Well played!",
  6: "Good game!"
};

const CANNED_STICKERS = {
  1: "👍",
  2: "👏",
  3: "🤔",
  4: "🎉"
};

class CannedChatManager {
  constructor(onSendReaction) {
    this.onSendReaction = onSendReaction;
    this.p1Bubble = document.getElementById('p1SpeechBubble');
    this.p2Bubble = document.getElementById('p2SpeechBubble');
    this.p1Timeout = null;
    this.p2Timeout = null;

    this.bindButtons();
  }

  bindButtons() {
    // Preset phrase buttons
    document.querySelectorAll('.phrase-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = parseInt(btn.dataset.id, 10);
        if (this.onSendReaction) {
          this.onSendReaction('phrase', id);
        }
      });
    });

    // Sticker buttons
    document.querySelectorAll('.sticker-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = parseInt(btn.dataset.id, 10);
        if (this.onSendReaction) {
          this.onSendReaction('sticker', id);
        }
      });
    });
  }

  showReaction(playerNum, category, id) {
    const text = category === 'phrase' ? CANNED_PHRASES[id] : CANNED_STICKERS[id];
    if (!text) return;

    const bubble = playerNum === 1 ? this.p1Bubble : this.p2Bubble;
    if (!bubble) return;

    if (playerNum === 1 && this.p1Timeout) clearTimeout(this.p1Timeout);
    if (playerNum === 2 && this.p2Timeout) clearTimeout(this.p2Timeout);

    bubble.textContent = text;
    bubble.classList.remove('hidden');

    const timer = setTimeout(() => {
      bubble.classList.add('hidden');
    }, 3200);

    if (playerNum === 1) this.p1Timeout = timer;
    else this.p2Timeout = timer;
  }
}
