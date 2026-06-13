type WebAudioWindow = Window & {
  webkitAudioContext?: typeof AudioContext;
};

let audioCtx: AudioContext | null = null;
let bgGainNode: GainNode | null = null;
let bgStarted = false;
let muted = window.localStorage.getItem('fv_audio_muted') === '1';

export function isMuted() {
  return muted;
}

export function setMuted(nextMuted: boolean) {
  muted = nextMuted;
  window.localStorage.setItem('fv_audio_muted', nextMuted ? '1' : '0');
  if (bgGainNode) bgGainNode.gain.value = nextMuted ? 0 : 0.18;
  if (nextMuted) window.speechSynthesis?.cancel();
  window.dispatchEvent(new CustomEvent('fv-audio-muted', { detail: nextMuted }));
}

function ensureAudioContext(): AudioContext | null {
  if (audioCtx && audioCtx.state !== 'closed') {
    if (audioCtx.state === 'suspended') audioCtx.resume().catch(() => {});
    return audioCtx;
  }
  try {
    const AudioCtor = window.AudioContext ?? (window as WebAudioWindow).webkitAudioContext;
    if (!AudioCtor) return null;
    audioCtx = new AudioCtor();
    return audioCtx;
  } catch {
    return null;
  }
}

export function initAudio() {
  const ctx = ensureAudioContext();
  if (!ctx || bgStarted) return;
  bgStarted = true;

  // Unlock Speech Synthesis during the first user interaction
  try {
    if (window.speechSynthesis && !muted) {
      const unlockUtterance = new SpeechSynthesisUtterance('');
      unlockUtterance.volume = 0;
      window.speechSynthesis.speak(unlockUtterance);
    }
  } catch {}

  const duration = 4;
  const bufferSize = ctx.sampleRate * duration;
  const buffer = ctx.createBuffer(2, bufferSize, ctx.sampleRate);
  for (let channel = 0; channel < 2; channel += 1) {
    const data = buffer.getChannelData(channel);
    let lastOut = 0;
    for (let i = 0; i < bufferSize; i += 1) {
      const white = Math.random() * 2 - 1;
      data[i] = ((lastOut + (0.02 * white)) / 1.02) * 3.2;
      lastOut = data[i];
      if (Math.random() < 0.001) data[i] += (Math.random() - 0.5) * 0.35;
    }
  }

  const source = ctx.createBufferSource();
  source.buffer = buffer;
  source.loop = true;
  const filter = ctx.createBiquadFilter();
  filter.type = 'lowpass';
  filter.frequency.value = 580;
  bgGainNode = ctx.createGain();
  bgGainNode.gain.value = muted ? 0 : 0.18;
  source.connect(filter);
  filter.connect(bgGainNode);
  bgGainNode.connect(ctx.destination);
  source.start();
}

function tone(freq: number, duration = 0.12, type: OscillatorType = 'sine', volume = 0.08, delay = 0) {
  if (muted) return;
  const ctx = ensureAudioContext();
  if (!ctx) return;
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.type = type;
  osc.frequency.value = freq;
  gain.gain.setValueAtTime(0.0001, ctx.currentTime + delay);
  gain.gain.exponentialRampToValueAtTime(volume, ctx.currentTime + delay + 0.015);
  gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + delay + duration);
  osc.connect(gain);
  gain.connect(ctx.destination);
  osc.start(ctx.currentTime + delay);
  osc.stop(ctx.currentTime + delay + duration);
}

export function playUiClick() {
  initAudio();
  tone(520, 0.08, 'triangle', 0.045);
}

export function playShotStrike() {
  initAudio();
  tone(92, 0.16, 'sawtooth', 0.18);
  tone(182, 0.09, 'square', 0.08, 0.015);
}

export function playClueCue() {
  initAudio();
  tone(740, 0.05, 'triangle', 0.035);
}

export function playCrowdCue(result: 'Goal' | 'Saved' | 'Missed') {
  initAudio();
  if (muted) return;
  const ctx = ensureAudioContext();
  if (!ctx) return;

  if (result === 'Goal') {
    if (bgGainNode) {
      bgGainNode.gain.setValueAtTime(bgGainNode.gain.value, ctx.currentTime);
      bgGainNode.gain.linearRampToValueAtTime(0.55, ctx.currentTime + 0.2);
      bgGainNode.gain.linearRampToValueAtTime(0.18, ctx.currentTime + 2.6);
    }
    [262, 330, 392, 523, 659].forEach((freq, index) => tone(freq, 0.55, 'triangle', 0.13, index * 0.08));
    return;
  }

  if (result === 'Saved') {
    [330, 262, 196, 147].forEach((freq, index) => tone(freq, 0.45, 'sine', 0.16, index * 0.12));
    return;
  }

  tone(100, 0.36, 'sawtooth', 0.18);
}

export function speakCommentary(text: string) {
  if (muted) return;
  try {
    if (!window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.05;
    utterance.pitch = 1.05;
    utterance.volume = 1.0;
    const voices = window.speechSynthesis.getVoices();
    const voice = voices.find((item) => item.lang.startsWith('en'));
    if (voice) utterance.voice = voice;
    
    // Prevent garbage collection bug in Chrome
    (window as any).__fv_utterance = utterance;
    
    window.speechSynthesis.speak(utterance);
    
    // Fix for Chrome occasionally getting stuck in paused state
    if (window.speechSynthesis.paused) {
      window.speechSynthesis.resume();
    }
  } catch {
    // Speech synthesis is optional.
  }
}
