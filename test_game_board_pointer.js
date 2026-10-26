/**
 * Lightweight regression tests for GameBoardRenderer pointer input.
 * Run with: node tests/test_game_board_pointer.js
 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const listeners = {};
const ctx = {
  clearRect() {}, save() {}, restore() {}, beginPath() {}, arc() {},
  fill() {}, stroke() {}, moveTo() {}, lineTo() {}, quadraticCurveTo() {},
  closePath() {},
  createRadialGradient() { return { addColorStop() {} }; },
  set fillStyle(value) {}, set strokeStyle(value) {}, set lineWidth(value) {},
  set globalAlpha(value) {}, set shadowColor(value) {}, set shadowBlur(value) {}
};
const canvas = {
  width: 640,
  height: 550,
  getContext() { return ctx; },
  addEventListener(name, callback) { listeners[name] = callback; },
  getBoundingClientRect() { return { left: 100, top: 50, width: 320, height: 275 }; }
};
global.document = { getElementById() { return canvas; } };
vm.runInThisContext(fs.readFileSync('client/js/game_board.js', 'utf8'));

const selected = [];
const board = new GameBoardRenderer('gameCanvas', (column) => selected.push(column));
board.setTurn(true, 1);

function pointer(type, clientX, clientY = 100) {
  let prevented = false;
  const event = {
    pointerType: type, clientX, clientY,
    preventDefault() { prevented = true; }
  };
  listeners.pointerdown(event);
  return prevented;
}

// A touch tap selects a column even when no mouse hover has occurred.
assert.equal(board.hoverCol, -1);
assert.equal(pointer('touch', 100 + (3.5 * 320 / 7)), true);
assert.deepEqual(selected, [3]);

// CSS-scaled canvas coordinates map to the correct internal column.
pointer('pen', 100 + (6.5 * 320 / 7));
assert.deepEqual(selected, [3, 6]);

// Out-of-bounds, full columns, and opponent turns cannot submit moves.
pointer('touch', 99);
assert.deepEqual(selected, [3, 6]);
board.setBoard(Array.from({ length: 6 }, () => [1, 0, 0, 0, 0, 0, 0]));
pointer('touch', 100 + (0.5 * 320 / 7));
assert.deepEqual(selected, [3, 6]);
board.setTurn(false, 1);
pointer('touch', 100 + (1.5 * 320 / 7));
assert.deepEqual(selected, [3, 6]);

// Desktop pointer movement still updates the hover preview.
board.setTurn(true, 1);
listeners.pointermove({ pointerType: 'mouse', clientX: 100 + (2.5 * 320 / 7), clientY: 100 });
assert.equal(board.hoverCol, 2);

console.log('PASS: touch/pen selection, coordinate scaling, invalid/full-column guards, turn guard, desktop hover');
