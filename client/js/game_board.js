/**
 * Connect Four HTML5 Canvas 2D Board Renderer
 * Handles grid drawing, empty slots, hover column indicator, and token rendering.
 */

class GameBoardRenderer {
  constructor(canvasId, onColumnSelected) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    this.onColumnSelected = onColumnSelected;

    this.cols = 7;
    this.rows = 6;
    this.board = Array(6).fill(0).map(() => Array(7).fill(0));
    this.hoverCol = -1;
    this.isMyTurn = false;
    this.myPlayerNum = 1;
    this.winningCoords = null;

    this.initMetrics();
    this.bindEvents();
    this.render();
  }

  initMetrics() {
    this.width = this.canvas.width;
    this.height = this.canvas.height;
    this.slotRadius = 32;
    this.colWidth = this.width / this.cols;
    this.rowHeight = this.height / (this.rows + 1); // Extra top row for token hover
    this.boardOffsetY = this.rowHeight;
  }

  bindEvents() {
    // Pointer events cover mouse, touch, and pen input without generating a
    // second click after a touch release.
    this.canvas.style.touchAction = 'none';
    this.canvas.addEventListener('pointermove', (e) => this.handleMouseMove(e));
    this.canvas.addEventListener('pointerleave', () => this.handleMouseLeave());
    this.canvas.addEventListener('pointerup', (e) => this.handleClick(e));
  }

  handleMouseMove(e) {
    if (!this.isMyTurn) {
      this.hoverCol = -1;
      this.render();
      return;
    }
    const rect = this.canvas.getBoundingClientRect();
    const scaleX = this.canvas.width / rect.width;
    const x = (e.clientX - rect.left) * scaleX;
    const col = Math.floor(x / this.colWidth);
    if (col >= 0 && col < this.cols && this.board[0][col] === 0) {
      if (this.hoverCol !== col) {
        this.hoverCol = col;
        this.render();
      }
    } else {
      if (this.hoverCol !== -1) {
        this.hoverCol = -1;
        this.render();
      }
    }
  }

  handleMouseLeave() {
    this.hoverCol = -1;
    this.render();
  }

  handleClick(e) {
    if (!this.isMyTurn || this.hoverCol === -1) return;
    if (this.board[0][this.hoverCol] === 0 && this.onColumnSelected) {
      const selected = this.hoverCol;
      this.hoverCol = -1;
      this.onColumnSelected(selected);
      this.render();
    }
  }

  setBoard(boardMatrix) {
    this.board = boardMatrix.map(row => [...row]);
    this.render();
  }

  setTurn(isMyTurn, playerNum) {
    this.isMyTurn = isMyTurn;
    this.myPlayerNum = playerNum;
    if (!isMyTurn) this.hoverCol = -1;
    this.render();
  }

  setWinningCoords(coords) {
    this.winningCoords = coords;
    this.render();
  }

  reset() {
    this.board = Array(this.rows).fill(0).map(() => Array(this.cols).fill(0));
    this.winningCoords = null;
    this.hoverCol = -1;
    this.render();
  }

  render() {
    this.ctx.clearRect(0, 0, this.width, this.height);

    // 1. Draw Hover Token at top
    if (this.isMyTurn && this.hoverCol >= 0 && this.hoverCol < this.cols) {
      const hoverX = this.hoverCol * this.colWidth + this.colWidth / 2;
      const hoverY = this.rowHeight / 2;
      this.drawToken(hoverX, hoverY, this.myPlayerNum, true);
    }

    // 2. Draw Board Frame
    this.ctx.fillStyle = '#1e3a8a';
    this.roundRect(
      this.ctx,
      0,
      this.boardOffsetY,
      this.width,
      this.height - this.boardOffsetY,
      16,
      true,
      false
    );

    // 3. Draw Slots and Tokens
    for (let r = 0; r < this.rows; r++) {
      for (let c = 0; c < this.cols; c++) {
        const x = c * this.colWidth + this.colWidth / 2;
        const y = this.boardOffsetY + r * this.rowHeight + this.rowHeight / 2;
        const cell = this.board[r][c];

        if (cell === 0) {
          // Empty dark hole
          this.drawEmptySlot(x, y);
        } else {
          // Player token (1=Red, 2=Yellow)
          const isWinning = this.winningCoords && this.winningCoords.some(([wr, wc]) => wr === r && wc === c);
          this.drawToken(x, y, cell, false, isWinning);
        }
      }
    }
  }

  drawEmptySlot(x, y) {
    this.ctx.save();
    this.ctx.beginPath();
    this.ctx.arc(x, y, this.slotRadius, 0, Math.PI * 2);
    this.ctx.fillStyle = '#0b1329';
    this.ctx.fill();

    // Inner shadow outline
    this.ctx.lineWidth = 3;
    this.ctx.strokeStyle = '#172554';
    this.ctx.stroke();
    this.ctx.restore();
  }

  drawToken(x, y, player, isHover = false, isWinning = false) {
    this.ctx.save();
    this.ctx.beginPath();
    this.ctx.arc(x, y, isHover ? this.slotRadius * 0.85 : this.slotRadius, 0, Math.PI * 2);

    const grad = this.ctx.createRadialGradient(
      x - this.slotRadius * 0.3,
      y - this.slotRadius * 0.3,
      this.slotRadius * 0.1,
      x,
      y,
      this.slotRadius
    );

    if (player === 1) {
      // Red
      grad.addColorStop(0, '#f87171');
      grad.addColorStop(1, '#dc2626');
    } else {
      // Yellow
      grad.addColorStop(0, '#fde047');
      grad.addColorStop(1, '#d97706');
    }

    this.ctx.fillStyle = grad;
    this.ctx.globalAlpha = isHover ? 0.75 : 1.0;
    this.ctx.fill();

    if (isWinning) {
      // Golden pulsing border for winning line
      this.ctx.lineWidth = 6;
      this.ctx.strokeStyle = '#ffffff';
      this.ctx.shadowColor = '#fbbf24';
      this.ctx.shadowBlur = 15;
      this.ctx.stroke();
    } else {
      this.ctx.lineWidth = 2;
      this.ctx.strokeStyle = player === 1 ? '#991b1b' : '#92400e';
      this.ctx.stroke();
    }

    this.ctx.restore();
  }

  roundRect(ctx, x, y, width, height, radius, fill, stroke) {
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
    if (fill) ctx.fill();
    if (stroke) ctx.stroke();
    ctx.restore();
  }
}
