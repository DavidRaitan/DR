const API = (() => {
  const base = '/api';

  function token() {
    return localStorage.getItem('jw_token');
  }

  async function req(method, path, body) {
    const headers = { 'Content-Type': 'application/json' };
    const tok = token();
    if (tok) headers['Authorization'] = 'Bearer ' + tok;
    const opts = { method, headers };
    if (body !== undefined) opts.body = JSON.stringify(body);
    const res = await fetch(base + path, opts);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      const e = new Error(
        typeof err.detail === 'object' ? err.detail.message : (err.detail || 'Request failed')
      );
      e.status = res.status;
      e.detail = err.detail;
      throw e;
    }
    return res.json();
  }

  async function formReq(path, formData) {
    const headers = {};
    const tok = token();
    if (tok) headers['Authorization'] = 'Bearer ' + tok;
    const res = await fetch(base + path, { method: 'POST', headers, body: formData });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw Object.assign(new Error(err.detail || 'Request failed'), { status: res.status });
    }
    return res.json();
  }

  function _qs(obj) {
    const p = new URLSearchParams();
    Object.entries(obj).forEach(([k, v]) => { if (v) p.set(k, v); });
    const s = p.toString();
    return s ? '?' + s : '';
  }

  return {
    // Spark
    spark:         (genre, focus) => req('POST', '/spark', { genre, focus }),
    continueStory: (story)        => req('POST', '/continue', { story }),
    sparkOptions:  ()             => req('GET',  '/spark/options'),

    // World Builder
    setting:  (seed) => req('POST', '/world/setting', { seed }),
    species:  (seed) => req('POST', '/world/species', { seed }),
    magic:    (seed) => req('POST', '/world/magic', { seed }),

    // Character
    character: (seed) => req('POST', '/character', { seed }),

    // Structure
    threeAct:      ()      => req('GET',  '/structure/three-act'),
    classifyScene: (scene) => req('POST', '/structure/classify-scene', { scene }),

    // Library
    stories:  (genre, length, style) => req('GET', `/library/${_qs({ genre, length, style })}`),
    story:    (id)                   => req('GET', `/library/${id}`),
    publish:  (data)                 => req('POST', '/library/', data),
    like:     (id)                   => req('POST', `/library/${id}/like`),
    comment:  (id, data)             => req('POST', `/library/${id}/comment`, data),
    libOpts:  ()                     => req('GET', '/library/options'),

    // Mentors
    mentors:   ()                    => req('GET',  '/mentor/'),
    askMentor: (mentor, question)    => req('POST', '/mentor/ask', { mentor, question }),

    // Auth
    register: (username, email, password) => req('POST', '/auth/register', { username, email, password }),
    login: (email, password) => {
      const fd = new FormData();
      fd.append('username', email);
      fd.append('password', password);
      return formReq('/auth/login', fd);
    },
    me:            ()              => req('GET', '/auth/me'),
    myStories:     ()              => req('GET', '/auth/me/stories'),
    updateProfile: (bio, avatar)   => req('PUT', '/auth/profile', { bio, avatar }),
    awardXP:       (amount)        => req('POST', '/auth/xp', { amount }),
    usageInfo:     ()              => req('GET', '/auth/usage'),

    // Saved work
    saveWork:   (kind, title, content) => req('POST', '/auth/me/saved', { kind, title, content }),
    getSaved:   (kind)                 => req('GET',  `/auth/me/saved${_qs({ kind })}`),
    deleteSaved: (id)                  => req('DELETE', `/auth/me/saved/${id}`),

    // Health
    health: () => req('GET', '/health'),
  };
})();
