'use strict';

// ── Config ────────────────────────────────────────────────────
const REFRESH_INTERVAL = 8000;
const DATA_PATH = './build-data.json';

// ── State ─────────────────────────────────────────────────────
let testChart = null;
let coverageChart = null;
let buildHistory = [];

// ── Helpers ───────────────────────────────────────────────────
const $ = (id) => document.getElementById(id);
const setTxt = (id, val) => { const el = $(id); if (el) el.textContent = val; };

function setStatusCard(cardId, value, state) {
  const card = $(cardId);
  if (!card) return;
  card.className = 'status-card';
  if (state) card.classList.add(`state-${state}`);
  const valEl = card.querySelector('.status-value');
  if (valEl) valEl.textContent = value;
}

// ── Clock ─────────────────────────────────────────────────────
function updateClock() {
  const now = new Date();
  const h = String(now.getHours()).padStart(2, '0');
  const m = String(now.getMinutes()).padStart(2, '0');
  const s = String(now.getSeconds()).padStart(2, '0');
  setTxt('clock', `${h}:${m}:${s}`);
}
setInterval(updateClock, 1000);
updateClock();

// ── Status Map ────────────────────────────────────────────────
function statusState(raw) {
  if (!raw) return '';
  const s = raw.toLowerCase();
  if (s === 'success') return 'success';
  if (s === 'failure' || s === 'failed') return 'failure';
  if (s === 'running' || s === 'in progress') return 'running';
  return '';
}

function healthState(raw) {
  if (!raw) return '';
  return raw.toLowerCase() === 'healthy' ? 'success' : 'failure';
}

// ── Stage Simulation ──────────────────────────────────────────
const STAGES = [
  'checkout','setup','install','lint','test','coverage',
  'sonar','quality','docker-build','deploy','healthcheck','archive','dashboard'
];

function applyStageAnimation(overallStatus) {
  const items = document.querySelectorAll('.stage');
  items.forEach(el => el.className = 'stage');

  if (overallStatus === 'SUCCESS') {
    items.forEach(el => el.classList.add('done'));
  } else if (overallStatus === 'FAILURE') {
    const failIdx = Math.floor(Math.random() * 5) + 3;
    items.forEach((el, i) => {
      if (i < failIdx) el.classList.add('done');
      else if (i === failIdx) el.classList.add('failed');
    });
  }
}

// ── Build History ─────────────────────────────────────────────
function renderBuildHistory() {
  const list = $('build-list');
  if (!list) return;
  if (buildHistory.length === 0) {
    list.innerHTML = '<p class="empty-state">No build history yet</p>';
    return;
  }
  list.innerHTML = buildHistory.map(b => `
    <div class="build-item ${b.status.toLowerCase()}">
      <span class="build-num ${b.status.toLowerCase()}">#${b.build}</span>
      <span class="build-commit">${b.commit}</span>
      <span class="build-author">${b.author}</span>
    </div>
  `).join('');
}

function addToHistory(data) {
  const exists = buildHistory.find(b => b.build === data.buildNumber);
  if (!exists) {
    buildHistory.unshift({
      build: data.buildNumber,
      status: data.buildStatus,
      commit: data.commit || '???????',
      author: data.author || 'Unknown'
    });
    if (buildHistory.length > 15) buildHistory.pop();
  }
}

// ── Test Chart ────────────────────────────────────────────────
function createTestChart(passed, failed, skipped) {
  const ctx = $('test-chart');
  if (!ctx) return;
  if (testChart) { testChart.destroy(); }
  testChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Passed', 'Failed', 'Skipped'],
      datasets: [{
        data: [passed, failed, skipped],
        backgroundColor: ['rgba(34,197,94,0.7)', 'rgba(239,68,68,0.7)', 'rgba(245,158,11,0.7)'],
        borderColor: ['#22c55e', '#ef4444', '#f59e0b'],
        borderWidth: 1,
        borderRadius: 4,
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: '#252a38' }, ticks: { color: '#64748b' } },
        y: {
          beginAtZero: true,
          grid: { color: '#252a38' },
          ticks: { color: '#64748b', stepSize: 1 }
        }
      }
    }
  });
}

// ── Coverage Chart ────────────────────────────────────────────
function createCoverageChart(pct) {
  const ctx = $('coverage-chart');
  if (!ctx) return;
  if (coverageChart) { coverageChart.destroy(); }
  const remaining = Math.max(0, 100 - pct);
  const color = pct >= 80 ? '#22c55e' : pct >= 60 ? '#f59e0b' : '#ef4444';
  coverageChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      datasets: [{
        data: [pct, remaining],
        backgroundColor: [color, '#1a1e28'],
        borderWidth: 0,
        borderRadius: 4
      }]
    },
    options: {
      cutout: '72%',
      responsive: false,
      plugins: { legend: { display: false }, tooltip: { enabled: false } }
    }
  });
  setTxt('coverage-pct', `${pct}%`);
}

// ── System Dots ───────────────────────────────────────────────
function checkSystemHealth(data) {
  const setDot = (dotId, sysId, online, label) => {
    const dot = $(dotId);
    const val = $(sysId);
    if (dot) dot.className = `sys-dot ${online ? 'online' : 'offline'}`;
    if (val) val.textContent = online ? label || 'Online' : 'Offline';
  };
  setDot('dot-app',     'sys-app',     data.healthStatus === 'healthy',  'Healthy');
  setDot('dot-docker',  'sys-docker',  data.dockerStatus === 'running',  'Running');
  setDot('dot-sonar',   'sys-sonar',   true,                             'Ready');
  setDot('dot-jenkins', 'sys-jenkins', true,                             'Active');
}

// ── Main Update ───────────────────────────────────────────────
function applyData(data) {
  // Status strip
  setStatusCard('card-build',    `#${data.buildNumber}`,  '');
  setStatusCard('card-status',   data.buildStatus,        statusState(data.buildStatus));
  setStatusCard('card-coverage', `${data.coverage}%`,     parseFloat(data.coverage) >= 80 ? 'success' : 'failure');
  setStatusCard('card-docker',   data.dockerStatus,       data.dockerStatus === 'running' ? 'success' : 'failure');
  setStatusCard('card-health',   data.healthStatus,       healthState(data.healthStatus));

  // Commit info
  setTxt('info-branch',  data.branch   || '—');
  setTxt('info-commit',  data.commit   || '—');
  setTxt('info-author',  data.author   || '—');
  setTxt('info-message', data.message  || '—');
  setTxt('info-time',    data.timestamp || '—');

  // Tests (simulated from build status)
  const totalTests = 120;
  const failed  = data.buildStatus === 'SUCCESS' ? 0 : Math.floor(Math.random() * 8) + 1;
  const passed  = totalTests - failed;
  const skipped = 0;
  setTxt('ts-passed',  passed);
  setTxt('ts-failed',  failed);
  setTxt('ts-skipped', skipped);
  createTestChart(passed, failed, skipped);

  // Coverage chart
  const pct = parseFloat(data.coverage) || 0;
  createCoverageChart(pct);

  // Stages
  applyStageAnimation(data.buildStatus);

  // History
  addToHistory(data);
  renderBuildHistory();

  // System
  checkSystemHealth(data);
}

// ── Fetch Loop ────────────────────────────────────────────────
async function fetchData() {
  try {
    const resp = await fetch(`${DATA_PATH}?t=${Date.now()}`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();
    applyData(data);
    $('live-dot').style.background = '#22c55e';
  } catch (e) {
    console.warn('Dashboard data not available:', e.message);
    $('live-dot').style.background = '#f59e0b';
    applyDemoData();
  }
}

// ── Demo Data (when no build-data.json yet) ───────────────────
function applyDemoData() {
  const demo = {
    buildNumber:  '42',
    buildStatus:  'SUCCESS',
    branch:       'main',
    commit:       'a1b2c3d',
    author:       'Your Name',
    message:      'feat: add statistical functions',
    timestamp:    new Date().toLocaleString(),
    coverage:     '96.4',
    dockerStatus: 'running',
    healthStatus: 'healthy'
  };
  applyData(demo);
}

// ── Boot ──────────────────────────────────────────────────────
fetchData();
setInterval(fetchData, REFRESH_INTERVAL);
