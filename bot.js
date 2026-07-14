// Minimal bot frontend integration for tests
async function sendBotCommand(cmd) {
  const res = await fetch('/api/bot', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: cmd })
  });
  return res.json();
}

// Example hook
document.addEventListener('DOMContentLoaded', () => {
  // placeholder for UI wiring
});
