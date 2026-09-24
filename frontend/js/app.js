/* ── State ─────────────────────────────────────────────────────────────── */
const store = {
  view: 'spark',
  mentorId: 'architect',
  chatHistory: [],
  last: {},
};

/* ── XP / Progress ─────────────────────────────────────────────────────── */
const LEVELS = [
  { name: 'Novice',      min: 0    },
  { name: 'Apprentice',  min: 100  },
  { name: 'Architect',   min: 300  },
  { name: 'Storysmith',  min: 700  },
  { name: 'Master',      min: 1500 },
];

function getLocalXP() { return parseInt(localStorage.getItem('jw_xp') || '0', 10); }

async function addXP(amount) {
  if (Auth.user) {
    try {
      const result = await API.awardXP(amount);
      Auth.user.xp = result.xp;
      Auth.user.level = result.level;
    } catch (_) {}
  } else {
    localStorage.setItem('jw_xp', getLocalXP() + amount);
  }
  renderProgress();
}

function getCurrentLevel(xp) {
  for (let i = LEVELS.length - 1; i >= 0; i--) {
    if (xp >= LEVELS[i].min) return i;
  }
  return 0;
}

function renderProgress() {
  const xp = Auth.user ? (Auth.user.xp || 0) : getLocalXP();
  const li = getCurrentLevel(xp);
  const level = LEVELS[li];
  const next = LEVELS[li + 1];
  const pct = next ? Math.min(100, ((xp - level.min) / (next.min - level.min)) * 100) : 100;
  document.getElementById('level-name').textContent = level.name;
  document.getElementById('xp-display').textContent = xp + ' XP';
  document.getElementById('progress-fill').style.width = pct + '%';
}

/* ── Usage counter ─────────────────────────────────────────────────────── */
async function refreshUsage() {
  try {
    const u = await API.usageInfo();
    const el = document.getElementById('usage-display');
    if (el && u.ai_enabled) {
      el.textContent = `${u.remaining} AI credits left today`;
      el.style.color = u.remaining < 5 ? '#c75a5a' : '';
    }
  } catch (_) {}
}

/* ── Auth ──────────────────────────────────────────────────────────────── */
const Auth = {
  user: null,

  async init() {
    const tok = localStorage.getItem('jw_token');
    if (!tok) return;
    try {
      const data = await API.me();
      this.user = data;
      this.renderAuthArea();
    } catch (e) {
      localStorage.removeItem('jw_token');
    }
  },

  renderAuthArea() {
    const area = document.getElementById('auth-area');
    if (this.user) {
      const initials = this.user.username.slice(0, 2).toUpperCase();
      area.innerHTML = `
        <div class="user-chip">
          <div class="user-avatar">${initials}</div>
          <span class="user-name">${this.user.username}</span>
          <button class="btn-ghost" onclick="Auth.logout()" title="Sign out">↩</button>
        </div>
        <div id="usage-display" class="muted" style="font-size:.75rem;margin-top:.3rem;text-align:center"></div>
      `;
    } else {
      area.innerHTML = `
        <button class="btn-ghost full-width" onclick="UI.openAuthModal()">Sign In / Register</button>
        <div id="usage-display" class="muted" style="font-size:.75rem;margin-top:.3rem;text-align:center"></div>
      `;
    }
    renderProgress();
    refreshUsage();
  },

  logout() {
    localStorage.removeItem('jw_token');
    this.user = null;
    this.renderAuthArea();
    toast('Signed out');
  },
};

/* ── UI helpers ────────────────────────────────────────────────────────── */
const UI = {
  openAuthModal() {
    document.getElementById('auth-modal').classList.remove('hidden');
  },
  closeAuthModal() {
    document.getElementById('auth-modal').classList.add('hidden');
    document.getElementById('login-error').classList.add('hidden');
    document.getElementById('register-error').classList.add('hidden');
  },
  switchAuthTab(tab) {
    document.querySelectorAll('.auth-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tab));
    document.getElementById('login-form').classList.toggle('hidden', tab !== 'login');
    document.getElementById('register-form').classList.toggle('hidden', tab !== 'register');
  },
};

window.Auth = Auth;
window.UI = UI;

/* ── Auth form handlers ────────────────────────────────────────────────── */
window.Auth.login = async function(e) {
  e.preventDefault();
  const f = e.target;
  const errEl = document.getElementById('login-error');
  errEl.classList.add('hidden');
  try {
    const data = await API.login(f.email.value, f.password.value);
    localStorage.setItem('jw_token', data.access_token);
    Auth.user = data.user;
    Auth.renderAuthArea();
    UI.closeAuthModal();
    toast('Welcome back, ' + data.user.username + '!');
  } catch (err) {
    errEl.textContent = err.message;
    errEl.classList.remove('hidden');
  }
};

window.Auth.register = async function(e) {
  e.preventDefault();
  const f = e.target;
  const errEl = document.getElementById('register-error');
  errEl.classList.add('hidden');
  try {
    const data = await API.register(f.username.value, f.email.value, f.password.value);
    localStorage.setItem('jw_token', data.access_token);
    Auth.user = data.user;
    Auth.renderAuthArea();
    UI.closeAuthModal();
    toast('Welcome to Just Wright, ' + data.user.username + '!');
  } catch (err) {
    errEl.textContent = err.message;
    errEl.classList.remove('hidden');
  }
};

/* ── Rate limit handler ────────────────────────────────────────────────── */
function handleRateLimit(err) {
  if (err.status === 429) {
    const detail = err.detail || {};
    const msg = detail.message || 'You have used all your free AI credits for today.';
    const tip = detail.tip || '';
    showLimitBanner(msg, tip);
    return true;
  }
  return false;
}

function showLimitBanner(msg, tip) {
  let banner = document.getElementById('rate-limit-banner');
  if (!banner) {
    banner = document.createElement('div');
    banner.id = 'rate-limit-banner';
    banner.style.cssText = 'position:fixed;bottom:5rem;left:50%;transform:translateX(-50%);background:#26233a;border:1px solid #c8794a;border-radius:10px;padding:1rem 1.5rem;max-width:420px;width:90%;z-index:900;font-family:system-ui,sans-serif;text-align:center';
    document.body.appendChild(banner);
  }
  banner.innerHTML = `
    <div style="font-size:1.5rem;margin-bottom:.4rem">⏳</div>
    <div style="color:#e8e4d8;margin-bottom:.4rem">${esc(msg)}</div>
    ${tip ? `<div style="color:#8a8598;font-size:.82rem;margin-bottom:.75rem">${esc(tip)}</div>` : ''}
    <div style="display:flex;gap:.5rem;justify-content:center;flex-wrap:wrap">
      ${!Auth.user ? `<button class="btn-primary" style="margin:0;width:auto;padding:.4rem 1rem" onclick="UI.openAuthModal();document.getElementById('rate-limit-banner').remove()">Sign in for more credits</button>` : ''}
      <button class="btn-ghost" onclick="this.closest('#rate-limit-banner').remove()">Dismiss</button>
    </div>
  `;
  setTimeout(() => banner?.remove(), 12000);
}

/* ── Toast ─────────────────────────────────────────────────────────────── */
function toast(msg, duration = 2500) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.classList.remove('hidden');
  setTimeout(() => el.classList.add('hidden'), duration);
}

/* ── Navigation ────────────────────────────────────────────────────────── */
function navigate(view) {
  store.view = view;
  document.querySelectorAll('.nav-item').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.view === view);
  });
  views[view]();
}

document.querySelectorAll('.nav-item').forEach(btn => {
  btn.addEventListener('click', () => navigate(btn.dataset.view));
});

/* ── Helpers ───────────────────────────────────────────────────────────── */
function badge(isAI) {
  return `<span class="ai-badge ${isAI ? 'live' : 'sample'}">${isAI ? '✦ AI Generated' : '✦ Sample'}</span>`;
}

function fieldGrid(fields) {
  return `<div class="field-grid">${fields.map(([label, val]) => `
    <div class="field-item"><label>${label}</label><div class="field-value">${esc(String(val ?? '—'))}</div></div>
  `).join('')}</div>`;
}

function setMain(html) {
  document.getElementById('main').innerHTML = html;
}

/* ── Views ─────────────────────────────────────────────────────────────── */
const views = {

  /* Spark ─────────────────────────────────────────────────────────────── */
  spark() {
    setMain(`
      <div class="panel">
        <h1>Inspiration Engine</h1>
        <p class="subtitle">Break through the blank page with a story spark.</p>
        <div class="card">
          <label>Genre</label>
          <select id="spark-genre">
            <option value="any">Any</option>
            <option value="fantasy">Fantasy</option>
            <option value="sci-fi">Sci-Fi</option>
            <option value="romance">Romance</option>
            <option value="mystery">Mystery</option>
            <option value="horror">Horror</option>
            <option value="literary">Literary</option>
          </select>
          <label>Theme or Focus <span class="hint">(optional)</span></label>
          <input type="text" id="spark-focus" placeholder="e.g. grief, second chances, unreliable memory" />
          <button class="btn-primary" onclick="actions.getSpark()">Give Me a Spark</button>
        </div>
        <div id="spark-output" class="output-box empty">Your spark will appear here…</div>
        <div id="spark-actions" class="hidden mt" style="display:flex;gap:.5rem;flex-wrap:wrap">
          <button class="btn-secondary" onclick="actions.continueSpark()">Continue this spark →</button>
          <button class="btn-secondary" onclick="actions.saveLast('spark')">💾 Save</button>
        </div>
        <div id="continue-output" class="hidden">
          <hr/>
          <div id="continue-text" class="output-box"></div>
          <button class="btn-secondary mt" onclick="actions.publishDraft()">Publish to Library →</button>
        </div>
      </div>
    `);
  },

  /* World Builder ─────────────────────────────────────────────────────── */
  world() {
    setMain(`
      <div class="panel">
        <h1>World Builder</h1>
        <p class="subtitle">Settings, species, and magic systems.</p>
        <div class="tabs">
          <button class="tab-btn active" data-tab="setting" onclick="actions.worldTab(this,'setting')">Setting</button>
          <button class="tab-btn" data-tab="species" onclick="actions.worldTab(this,'species')">Species</button>
          <button class="tab-btn" data-tab="magic" onclick="actions.worldTab(this,'magic')">Magic System</button>
        </div>
        <div class="card">
          <label>Seed idea <span class="hint">(optional)</span></label>
          <input type="text" id="world-seed" placeholder="e.g. archipelago trade empire, bioluminescent forest…" />
          <button class="btn-primary" onclick="actions.buildWorld()">Generate</button>
        </div>
        <div id="world-output"></div>
      </div>
    `);
  },

  /* Character Forge ───────────────────────────────────────────────────── */
  character() {
    setMain(`
      <div class="panel">
        <h1>Character Forge</h1>
        <p class="subtitle">Psychology-first characters with contradiction and depth.</p>
        <div class="card">
          <label>Seed idea <span class="hint">(optional)</span></label>
          <input type="text" id="char-seed" placeholder="e.g. disgraced archivist, teenage mechanic on a desert planet…" />
          <button class="btn-primary" onclick="actions.forgeChar()">Forge Character</button>
        </div>
        <div id="char-output"></div>
      </div>
    `);
  },

  /* Structure ─────────────────────────────────────────────────────────── */
  structure() {
    setMain(`
      <div class="panel">
        <h1>Structure Teacher</h1>
        <p class="subtitle">The three-act framework and scene analysis.</p>
        <div class="tabs">
          <button class="tab-btn active" data-tab="learn" onclick="actions.structureTab(this,'learn')">Learn</button>
          <button class="tab-btn" data-tab="analyze" onclick="actions.structureTab(this,'analyze')">Analyze a Scene</button>
        </div>
        <div id="struct-learn-area">
          <div id="struct-learn-output" class="mt"></div>
          <button class="btn-secondary mt" onclick="actions.loadThreeAct()">Load the Three-Act Breakdown</button>
        </div>
        <div id="struct-analyze-area" class="hidden">
          <div class="card mt">
            <label>Paste your scene</label>
            <textarea id="scene-text" placeholder="Paste a scene or describe it briefly…"></textarea>
            <button class="btn-primary" onclick="actions.analyzeScene()">Analyze Scene</button>
          </div>
          <div id="scene-output"></div>
        </div>
      </div>
    `);
  },

  /* Library ───────────────────────────────────────────────────────────── */
  library() {
    setMain(`
      <div class="panel">
        <h1>Community Library</h1>
        <p class="subtitle">Read, share, and critique original stories.</p>
        <div class="tabs">
          <button class="tab-btn active" data-tab="browse" onclick="actions.libTab(this,'browse')">Browse</button>
          <button class="tab-btn" data-tab="publish" onclick="actions.libTab(this,'publish')">Publish</button>
          ${Auth.user ? `<button class="tab-btn" data-tab="mine" onclick="actions.libTab(this,'mine')">My Stories</button>` : ''}
        </div>
        <div id="lib-browse">
          <div class="form-row mt">
            <div>
              <label>Genre</label>
              <select id="lib-genre"><option value="">All</option><option>fantasy</option><option>sci-fi</option><option>romance</option><option>mystery</option><option>horror</option><option>literary</option></select>
            </div>
            <div>
              <label>Length</label>
              <select id="lib-length"><option value="">All</option><option>flash</option><option>short</option><option>novella</option></select>
            </div>
            <div>
              <label>Style</label>
              <select id="lib-style"><option value="">All</option><option>lyrical</option><option>spare</option><option>cinematic</option><option>epistolary</option></select>
            </div>
            <div style="display:flex;align-items:flex-end">
              <button class="btn-secondary" onclick="actions.loadStories()">Filter</button>
            </div>
          </div>
          <div id="story-grid" class="story-grid mt"></div>
        </div>
        <div id="lib-publish" class="hidden">
          <div class="card mt">
            <label>Title</label>
            <input type="text" id="pub-title" placeholder="Your story title" />
            <label>Story</label>
            <textarea id="pub-body" style="min-height:200px" placeholder="Paste or write your story here…"></textarea>
            <div class="form-row">
              <div><label>Genre</label>
                <select id="pub-genre"><option value="any">Any</option><option>fantasy</option><option>sci-fi</option><option>romance</option><option>mystery</option><option>horror</option><option>literary</option></select>
              </div>
              <div><label>Length</label>
                <select id="pub-length"><option>flash</option><option>short</option><option>novella</option></select>
              </div>
              <div><label>Style</label>
                <select id="pub-style"><option>cinematic</option><option>lyrical</option><option>spare</option><option>epistolary</option></select>
              </div>
              <div><label>Critique Mode</label>
                <select id="pub-mode">
                  <option value="open">Open — anyone can comment</option>
                  <option value="workshop">Workshop — guided lenses</option>
                  <option value="closed">Closed — read only</option>
                </select>
              </div>
            </div>
            <button class="btn-primary" onclick="actions.publishStory()">Publish to Library</button>
          </div>
        </div>
        <div id="lib-mine" class="hidden"><div id="my-story-grid" class="story-grid mt"></div></div>
        <div id="story-detail" class="hidden"></div>
      </div>
    `);
    actions.loadStories();

    const draft = sessionStorage.getItem('jw_draft');
    if (draft) {
      const d = JSON.parse(draft);
      sessionStorage.removeItem('jw_draft');
      actions.libTab(document.querySelector('[data-tab="publish"]'), 'publish');
      setTimeout(() => {
        const b = document.getElementById('pub-body');
        if (b) b.value = d.body || '';
        const t = document.getElementById('pub-title');
        if (t) t.value = d.title || '';
      }, 50);
    }
  },

  /* Mentors ───────────────────────────────────────────────────────────── */
  mentors() {
    store.chatHistory = [];
    setMain(`
      <div class="panel">
        <h1>AI Mentors</h1>
        <p class="subtitle">Five distinct voices to challenge and shape your writing.</p>
        <div class="mentor-chips" id="mentor-chips"></div>
        <div id="mentor-desc" class="muted" style="margin-bottom:.75rem"></div>
        <div class="card">
          <div class="chat-window" id="chat-window"></div>
          <div style="display:flex;gap:.5rem;margin-top:.5rem">
            <input type="text" id="mentor-q" placeholder="Ask your mentor anything…" style="flex:1"
              onkeydown="if(event.key==='Enter')actions.askMentor()" />
            <button class="btn-secondary" onclick="actions.askMentor()">Send</button>
          </div>
        </div>
      </div>
    `);
    actions.loadMentors();
  },

  /* My Work ───────────────────────────────────────────────────────────── */
  mywork() {
    if (!Auth.user) {
      setMain(`<div class="panel"><h1>My Work</h1><p class="subtitle">Sign in to save and access your work.</p><button class="btn-primary" style="width:auto;margin-top:1rem" onclick="UI.openAuthModal()">Sign In</button></div>`);
      return;
    }
    setMain(`
      <div class="panel">
        <h1>My Work</h1>
        <p class="subtitle">Everything you've saved — sparks, characters, worlds, scenes.</p>
        <div class="tabs">
          <button class="tab-btn active" onclick="actions.loadMyWork(this,'')">All</button>
          <button class="tab-btn" onclick="actions.loadMyWork(this,'spark')">Sparks</button>
          <button class="tab-btn" onclick="actions.loadMyWork(this,'character')">Characters</button>
          <button class="tab-btn" onclick="actions.loadMyWork(this,'world')">Worlds</button>
        </div>
        <div id="my-work-list" class="mt"></div>
      </div>
    `);
    actions.loadMyWork(document.querySelector('#main .tab-btn'), '');
  },
};

/* ── Actions ───────────────────────────────────────────────────────────── */
const actions = {

  /* Spark */
  async getSpark() {
    const btn = document.querySelector('#main .btn-primary');
    if (btn) btn.disabled = true;
    const out = document.getElementById('spark-output');
    out.textContent = 'Generating…';
    out.classList.remove('empty');
    try {
      const genre = document.getElementById('spark-genre').value;
      const focus = document.getElementById('spark-focus').value;
      const data = await API.spark(genre, focus);
      out.innerHTML = badge(data.ai) + esc(data.spark);
      document.getElementById('spark-actions').classList.remove('hidden');
      document.getElementById('spark-actions').style.display = 'flex';
      await addXP(10);
      store.lastSpark = data.spark;
      refreshUsage();
    } catch (e) {
      if (!handleRateLimit(e)) out.textContent = 'Could not generate: ' + e.message;
    } finally {
      if (btn) btn.disabled = false;
    }
  },

  async continueSpark() {
    if (!store.lastSpark) return;
    const out = document.getElementById('continue-output');
    out.classList.remove('hidden');
    const textEl = document.getElementById('continue-text');
    textEl.textContent = 'Continuing…';
    try {
      const data = await API.continueStory(store.lastSpark);
      textEl.innerHTML = badge(data.ai) + esc(data.continuation);
      store.lastContinuation = data.continuation;
      await addXP(15);
      refreshUsage();
    } catch (e) {
      if (!handleRateLimit(e)) textEl.textContent = 'Error: ' + e.message;
    }
  },

  publishDraft() {
    const body = (store.lastSpark || '') + '\n\n' + (store.lastContinuation || '');
    sessionStorage.setItem('jw_draft', JSON.stringify({ body }));
    navigate('library');
  },

  saveLast(kind) {
    if (kind === 'spark') {
      const text = [store.lastSpark, store.lastContinuation].filter(Boolean).join('\n\n');
      return actions.saveItem('spark', (store.lastSpark || '').slice(0, 60), text);
    }
    const data = store.last[kind];
    if (!data) { toast('Nothing to save.'); return; }
    return actions.saveItem(kind, data.name || kind, JSON.stringify(data));
  },

  async saveItem(kind, title, content) {
    if (!Auth.user) { toast('Sign in to save your work.'); UI.openAuthModal(); return; }
    if (!content || !content.trim()) { toast('Nothing to save.'); return; }
    try {
      await API.saveWork(kind, title, content);
      toast('Saved to My Work!');
    } catch (e) {
      toast('Could not save: ' + e.message);
    }
  },

  /* World */
  worldTab(btn, tab) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    store.worldTab = tab;
    document.getElementById('world-output').innerHTML = '';
  },

  async buildWorld() {
    const seed = document.getElementById('world-seed').value;
    const tab = store.worldTab || 'setting';
    const out = document.getElementById('world-output');
    out.innerHTML = '<div class="output-box">Generating…</div>';
    try {
      let data, fields, kind;
      if (tab === 'setting') {
        data = await API.setting(seed); kind = 'world';
        fields = [['Name', data.name], ['Geography', data.geography], ['Climate', data.climate], ['Culture', data.culture], ['Conflict', data.conflict]];
      } else if (tab === 'species') {
        data = await API.species(seed); kind = 'world';
        fields = [['Name', data.name], ['Origin', data.origin], ['Biology', data.biology], ['Culture', data.culture], ['Tension', data.tension]];
      } else {
        data = await API.magic(seed); kind = 'world';
        const keys = Object.keys(data).filter(k => k !== 'name');
        fields = [['Name', data.name], ...keys.map(k => [k.replace(/_/g,' '), data[k]])];
      }
      store.last.world = data;
      out.innerHTML = `
        <div class="card">
          ${fieldGrid(fields)}
          <button class="btn-secondary mt" onclick="actions.saveLast('world')">💾 Save</button>
        </div>`;
      await addXP(20);
      refreshUsage();
    } catch (e) {
      if (!handleRateLimit(e)) out.innerHTML = `<div class="output-box">Error: ${esc(e.message)}</div>`;
    }
  },

  /* Character */
  async forgeChar() {
    const seed = document.getElementById('char-seed').value;
    const out = document.getElementById('char-output');
    out.innerHTML = '<div class="output-box">Forging character…</div>';
    try {
      const d = await API.character(seed);
      const fields = [
        ['Name', d.name], ['Age', d.age], ['Occupation', d.occupation],
        ['Psychology', d.psychology], ['Core Wound', d.wound], ['Desire', d.desire],
        ['Contradiction', d.contradiction], ['Voice', d.voice], ['Physical', d.physical],
        ['Secret', d.secret], ['Arc', d.arc],
      ];
      store.last.character = d;
      out.innerHTML = `
        <div class="card">
          ${fieldGrid(fields)}
          <button class="btn-secondary mt" onclick="actions.saveLast('character')">💾 Save</button>
        </div>`;
      await addXP(20);
      refreshUsage();
    } catch (e) {
      if (!handleRateLimit(e)) out.innerHTML = `<div class="output-box">Error: ${esc(e.message)}</div>`;
    }
  },

  /* Structure */
  structureTab(btn, tab) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('struct-learn-area').classList.toggle('hidden', tab !== 'learn');
    document.getElementById('struct-analyze-area').classList.toggle('hidden', tab !== 'analyze');
  },

  async loadThreeAct() {
    const out = document.getElementById('struct-learn-output');
    out.textContent = 'Loading…';
    try {
      const d = await API.threeAct();
      out.innerHTML = `
        <h2>${d.title}</h2>
        <p class="muted" style="margin:.5rem 0 1rem">${d.overview}</p>
        <div class="three-act-acts">
          ${d.acts.map(a => `
            <div class="act-card">
              <h3>${esc(a.name)}</h3>
              <p>${esc(a.purpose)}</p>
              <ul>${a.key_beats.map(b => `<li>${esc(b)}</li>`).join('')}</ul>
              <p class="muted" style="margin-top:.5rem;font-size:.8rem">Length: ${esc(a.length)}</p>
            </div>
          `).join('')}
        </div>
        <div class="card mt">
          <strong>Craft Tips</strong>
          <ul class="tips-list">${d.tips.map(t => `<li>${esc(t)}</li>`).join('')}</ul>
        </div>
      `;
      await addXP(5);
    } catch (e) {
      out.textContent = 'Error: ' + e.message;
    }
  },

  async analyzeScene() {
    const scene = document.getElementById('scene-text').value;
    const out = document.getElementById('scene-output');
    if (!scene.trim()) return;
    out.innerHTML = '<div class="output-box">Analyzing…</div>';
    try {
      const d = await API.classifyScene(scene);
      out.innerHTML = `<div class="card">${fieldGrid([
        ['Act', d.act], ['Function', d.function], ['Analysis', d.analysis],
        ['What Works', d.what_works], ['Suggestion', d.suggestion],
      ])}</div>`;
      await addXP(15);
      refreshUsage();
    } catch (e) {
      if (!handleRateLimit(e)) out.innerHTML = `<div class="output-box">Error: ${esc(e.message)}</div>`;
    }
  },

  /* Library */
  libTab(btn, tab) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('lib-browse').classList.toggle('hidden', tab !== 'browse');
    document.getElementById('lib-publish').classList.toggle('hidden', tab !== 'publish');
    const mineEl = document.getElementById('lib-mine');
    if (mineEl) mineEl.classList.toggle('hidden', tab !== 'mine');
    document.getElementById('story-detail').classList.add('hidden');
    if (tab === 'mine') actions.loadMyStories();
  },

  async loadStories() {
    const genre = document.getElementById('lib-genre')?.value;
    const length = document.getElementById('lib-length')?.value;
    const style = document.getElementById('lib-style')?.value;
    const grid = document.getElementById('story-grid');
    if (!grid) return;
    grid.innerHTML = '<p class="muted">Loading…</p>';
    try {
      const data = await API.stories(genre, length, style);
      if (!data.stories.length) { grid.innerHTML = '<p class="muted">No stories yet. Be first to publish.</p>'; return; }
      grid.innerHTML = data.stories.map(s => `
        <div class="story-card" onclick="actions.openStory(${s.id})">
          <div class="story-title">${esc(s.title)}</div>
          <div class="story-meta">
            <span class="tag">${s.genre}</span>
            <span class="tag">${s.length}</span>
            <span class="tag">${s.style}</span>
            <span>♥ ${s.likes}</span>
            <span>${s.critique_mode}</span>
          </div>
          <div class="muted" style="font-size:.78rem">by ${esc(s.author)}</div>
        </div>
      `).join('');
    } catch (e) {
      grid.innerHTML = '<p class="muted">Error loading stories: ' + esc(e.message) + '</p>';
    }
  },

  async loadMyStories() {
    if (!Auth.user) return;
    const grid = document.getElementById('my-story-grid');
    if (!grid) return;
    grid.innerHTML = '<p class="muted">Loading…</p>';
    try {
      const stories = await API.myStories();
      if (!stories.length) { grid.innerHTML = '<p class="muted">You have not published any stories yet.</p>'; return; }
      grid.innerHTML = stories.map(s => `
        <div class="story-card" onclick="actions.openStory(${s.id})">
          <div class="story-title">${esc(s.title)}</div>
          <div class="story-meta"><span class="tag">${s.genre}</span><span>♥ ${s.likes}</span></div>
        </div>
      `).join('');
    } catch (e) {
      grid.innerHTML = '<p class="muted">Error: ' + esc(e.message) + '</p>';
    }
  },

  async openStory(id) {
    const detail = document.getElementById('story-detail');
    detail.innerHTML = '<p class="muted">Loading…</p>';
    document.getElementById('lib-browse').classList.add('hidden');
    document.getElementById('lib-publish').classList.add('hidden');
    const mineEl = document.getElementById('lib-mine');
    if (mineEl) mineEl.classList.add('hidden');
    detail.classList.remove('hidden');
    try {
      const s = await API.story(id);
      const canComment = s.critique_mode !== 'closed';
      const workshopLenses = s.critique_mode === 'workshop'
        ? `<div class="tabs" style="margin-bottom:.5rem">
            ${['character','plot','world','writing'].map(l =>
              `<button class="tab-btn" onclick="actions.selectLens(this,'${l}')">${l}</button>`).join('')}
           </div>` : '';
      detail.innerHTML = `
        <span class="back-link" onclick="actions.backToLibrary()">← Back to Library</span>
        <h2>${esc(s.title)}</h2>
        <div class="story-meta" style="margin:.5rem 0">
          <span class="tag">${s.genre}</span><span class="tag">${s.length}</span>
          <span class="tag">${s.style}</span><span>by ${esc(s.author)}</span>
        </div>
        <div class="story-body">${esc(s.body)}</div>
        <div class="like-bar">
          <button class="btn-like" onclick="actions.likeStory(${s.id}, this)">♥ Like</button>
          <span id="like-count">${s.likes} likes</span>
        </div>
        <hr/>
        <h3>Comments <span class="muted" style="font-size:.85rem">(${s.critique_mode} mode)</span></h3>
        <div id="comments-list">
          ${s.comments.length ? s.comments.map(c => `
            <div class="comment">
              <div class="comment-meta">${esc(c.author)}${c.lens ? `<span class="lens-tag">${c.lens}</span>` : ''}</div>
              <div>${esc(c.body)}</div>
            </div>
          `).join('') : '<p class="muted">No comments yet.</p>'}
        </div>
        ${canComment ? `
          <div class="card mt">
            ${workshopLenses}
            <input type="hidden" id="comment-lens" value="" />
            <label>Your Comment</label>
            <textarea id="comment-body" placeholder="Share your thoughts…"></textarea>
            <button class="btn-primary" onclick="actions.submitComment(${s.id})">Post Comment</button>
          </div>
        ` : '<p class="muted mt">This story is closed to comments.</p>'}
      `;
      await addXP(5);
    } catch (e) {
      detail.innerHTML = '<p class="muted">Error: ' + esc(e.message) + '</p>';
    }
  },

  selectLens(btn, lens) {
    document.querySelectorAll('#story-detail .tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('comment-lens').value = lens;
    const ta = document.getElementById('comment-body');
    const prompts = { character: 'Examine the characters…', plot: 'Examine the plot…', world: 'Examine the world…', writing: 'Examine the prose…' };
    ta.placeholder = prompts[lens] || 'Share your thoughts…';
  },

  async likeStory(id, btn) {
    btn.disabled = true;
    try {
      const data = await API.like(id);
      document.getElementById('like-count').textContent = data.likes + ' likes';
      await addXP(2);
    } catch(e) { btn.disabled = false; }
  },

  async submitComment(id) {
    const body = document.getElementById('comment-body').value.trim();
    const lens = document.getElementById('comment-lens')?.value || null;
    if (!body) return;
    try {
      await API.comment(id, { body, lens });
      const c = document.getElementById('comments-list');
      const name = Auth.user ? Auth.user.username : 'Anonymous';
      c.innerHTML += `<div class="comment"><div class="comment-meta">${esc(name)}${lens ? `<span class="lens-tag">${lens}</span>` : ''}</div><div>${esc(body)}</div></div>`;
      document.getElementById('comment-body').value = '';
      await addXP(10);
      toast('Comment posted!');
    } catch (e) {
      toast('Error: ' + esc(e.message));
    }
  },

  backToLibrary() {
    document.getElementById('story-detail').classList.add('hidden');
    document.getElementById('lib-browse').classList.remove('hidden');
    actions.loadStories();
  },

  async publishStory() {
    const title = document.getElementById('pub-title').value.trim();
    const body = document.getElementById('pub-body').value.trim();
    if (!title || !body) { toast('Title and story body are required.'); return; }
    try {
      await API.publish({
        title, body,
        genre: document.getElementById('pub-genre').value,
        length: document.getElementById('pub-length').value,
        style: document.getElementById('pub-style').value,
        critique_mode: document.getElementById('pub-mode').value,
        author: Auth.user ? Auth.user.username : 'Anonymous',
      });
      await addXP(50);
      toast('Story published!');
      actions.libTab(document.querySelector('[data-tab="browse"]'), 'browse');
      actions.loadStories();
    } catch (e) {
      toast('Error: ' + esc(e.message));
    }
  },

  /* Mentors */
  async loadMentors() {
    const chips = document.getElementById('mentor-chips');
    try {
      const mentors = await API.mentors();
      chips.innerHTML = mentors.map(m => `
        <button class="mentor-chip ${m.id === store.mentorId ? 'active' : ''}"
          onclick="actions.selectMentor(this,'${m.id}','${esc(m.focus)}')"
          data-id="${m.id}">${esc(m.name)}</button>
      `).join('');
      if (mentors.length) {
        const first = mentors.find(m => m.id === store.mentorId) || mentors[0];
        document.getElementById('mentor-desc').textContent = first.focus;
      }
    } catch (e) {
      chips.innerHTML = '<span class="muted">Could not load mentors</span>';
    }
  },

  selectMentor(btn, id, focus) {
    store.mentorId = id;
    document.querySelectorAll('.mentor-chip').forEach(c => c.classList.toggle('active', c.dataset.id === id));
    document.getElementById('mentor-desc').textContent = focus;
  },

  async askMentor() {
    const q = document.getElementById('mentor-q').value.trim();
    if (!q) return;
    document.getElementById('mentor-q').value = '';
    const win = document.getElementById('chat-window');
    win.innerHTML += `<div class="bubble user">${esc(q)}</div>`;
    win.scrollTop = win.scrollHeight;
    try {
      const data = await API.askMentor(store.mentorId, q);
      win.innerHTML += `<div class="bubble mentor">${esc(data.reply)}</div>`;
      win.scrollTop = win.scrollHeight;
      await addXP(10);
      refreshUsage();
    } catch (e) {
      if (!handleRateLimit(e)) {
        win.innerHTML += `<div class="bubble mentor">Error: ${esc(e.message)}</div>`;
      }
    }
  },

  /* My Work */
  async loadMyWork(btn, kind) {
    if (btn) {
      document.querySelectorAll('#main .tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    }
    const list = document.getElementById('my-work-list');
    if (!list) return;
    list.innerHTML = '<p class="muted">Loading…</p>';
    try {
      const items = await API.getSaved(kind);
      if (!items.length) { list.innerHTML = '<p class="muted">Nothing saved yet. Use the 💾 buttons to save your work.</p>'; return; }
      list.innerHTML = items.map(item => {
        let preview = item.content;
        try { const p = JSON.parse(item.content); preview = p.name || p.title || preview; } catch (_) {}
        return `
          <div class="card" style="display:flex;justify-content:space-between;align-items:start;gap:1rem">
            <div>
              <div style="font-weight:600">${esc(item.title || preview.slice(0, 60))}</div>
              <div class="muted" style="font-size:.78rem">${item.kind} · ${item.created_at.slice(0,10)}</div>
            </div>
            <button class="btn-ghost" onclick="actions.deleteSaved(${item.id}, this)" title="Delete">✕</button>
          </div>
        `;
      }).join('');
    } catch (e) {
      list.innerHTML = '<p class="muted">Error: ' + esc(e.message) + '</p>';
    }
  },

  async deleteSaved(id, btn) {
    btn.disabled = true;
    try {
      await API.deleteSaved(id);
      btn.closest('.card').remove();
      toast('Deleted');
    } catch (e) {
      btn.disabled = false;
      toast('Error: ' + esc(e.message));
    }
  },
};

function esc(str) {
  if (str === null || str === undefined) return '';
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

/* ── Boot ──────────────────────────────────────────────────────────────── */
(async function boot() {
  await Auth.init();
  renderProgress();
  navigate('spark');
})();
