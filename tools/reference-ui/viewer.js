'use strict';
let token = location.hash.slice(1);
try {
  if (token) sessionStorage.setItem('reference-token', token);
  else token = sessionStorage.getItem('reference-token') || '';
} catch (_) { /* A sessão inicial também funciona com armazenamento desabilitado. */ }
history.replaceState(null, '', '/');
const canvas = document.querySelector('#screen');
const context = canvas.getContext('2d');
const position = document.querySelector('#position');
const status = document.querySelector('#status');
const playButton = document.querySelector('#play');
let playing = false;
let frame = 0;
let epoch = 0;
let queue = Promise.resolve();
let pending = 0;
const held = new Set();
const mapping = {ArrowRight:'right',ArrowLeft:'left',ArrowUp:'up',ArrowDown:'down',
                 KeyZ:'a',KeyX:'b',Enter:'start',Backspace:'select'};
const opposites = {right:'left',left:'right',up:'down',down:'up'};
function updatePosition() {
  position.textContent = `${frame} quadros executados · sessão ${epoch + 1} · ${playing ? 'rodando' : 'pausado'}`;
  playButton.textContent = playing ? 'Pausar' : 'Rodar';
}
function showError(error) {
  playing = false;
  status.textContent = error.message;
  status.className = 'error';
  updatePosition();
}
function request(path, value) {
  pending++;
  const result = queue.catch(() => {}).then(async () => {
    const response = await fetch(path, {method:'POST',cache:'no-store',
      headers:{'Content-Type':'application/json','X-Reference-Token':token},
      body:JSON.stringify(value)});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Não foi possível executar a ação local.');
    return data;
  });
  queue = result.finally(() => { pending--; });
  // A cadeia é sempre observada, inclusive quando o usuário pausa durante uma requisição.
  queue.catch(() => {});
  return result;
}
function display(data) {
  const bytes = Uint8ClampedArray.from(atob(data.rgba), char => char.charCodeAt(0));
  if (bytes.length !== 160 * 144 * 4) throw new Error('Dimensões de vídeo inesperadas.');
  context.putImageData(new ImageData(bytes,160,144),0,0);
  frame = data.frame;
  epoch = data.epoch;
  updatePosition();
}
async function step(count) {
  display(await request('/api/step', {frames:count,keys:[...held].sort()}));
}
function pause() {
  playing = false;
  held.clear();
  updatePosition();
}
playButton.addEventListener('click', () => {
  playing = !playing;
  if (!playing) held.clear();
  canvas.focus();
  updatePosition();
});
document.querySelector('#step').addEventListener('click', () => {
  pause(); step(1).catch(showError);
});
document.querySelector('#advance').addEventListener('click', () => {
  pause(); step(60).catch(showError);
});
document.querySelector('#reset').addEventListener('click', async () => {
  pause();
  try { await request('/api/reset',{}); await step(1); status.textContent = 'Referência reiniciada.'; status.className = ''; }
  catch (error) { showError(error); }
});
document.querySelector('#replay').addEventListener('click', async () => {
  pause();
  status.textContent = 'Reproduzindo sequência local…';
  status.className = '';
  try {
    display(await request('/api/replay',{preset:document.querySelector('#preset').value}));
    status.textContent = 'Ponto carregado. Observe a tela e escolha a classificação.';
  } catch (error) { showError(error); }
});
document.querySelector('#label').addEventListener('click', async () => {
  pause();
  try {
    const data = await request('/api/label',{category:document.querySelector('#category').value});
    status.textContent = `Observação humana salva no quadro ${data.frame}. A sequência de botões também foi salva.`;
    status.className = '';
  } catch (error) { showError(error); }
});
window.addEventListener('keydown', event => {
  if (event.target instanceof Element && event.target.closest('select,input,textarea')) return;
  const key = mapping[event.code];
  if (!key) return;
  event.preventDefault();
  if (opposites[key]) held.delete(opposites[key]);
  held.add(key);
});
window.addEventListener('keyup', event => {
  const key = mapping[event.code];
  if (key) { event.preventDefault(); held.delete(key); }
});
window.addEventListener('blur', pause);
document.addEventListener('visibilitychange', () => { if (document.hidden) pause(); });
setInterval(() => { if (playing && pending === 0) step(1).catch(showError); },16);
if (!token) showError(new Error('Abra pelo Analisar.command para iniciar uma sessão local.'));
else step(1).then(() => { status.textContent = 'Pronto. Use Rodar para observar o jogo.'; }).catch(showError);
