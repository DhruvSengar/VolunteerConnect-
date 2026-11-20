// Mobile menu: the header's toggle opens and closes the nav.
const topbar = document.querySelector('.topbar');
const toggle = document.querySelector('.topbar__toggle');
if (topbar && toggle) {
  toggle.addEventListener('click', () => {
    const open = topbar.classList.toggle('is-open');
    toggle.setAttribute('aria-expanded', String(open));
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && topbar.classList.contains('is-open')) { topbar.classList.remove('is-open'); toggle.setAttribute('aria-expanded', 'false'); toggle.focus(); }
  });
}

// Live search on the opportunities page: results replace the list while a query is typed.
const search = document.querySelector('#live-search');
const results = document.querySelector('#search-results');
const list = document.querySelector('#opportunity-grid');
const status = document.querySelector('#search-status');
if (search && results && list) {
  let timer, latest = 0;
  const el = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; };
  const render = (items) => {
    results.replaceChildren(...items.map((x) => {
      const card = el('article', 'card card--link');
      const h = el('h3', 'card__title'); const a = el('a', null, x.title); a.href = `/opportunities/${encodeURIComponent(x.id)}/`; h.append(a);
      const meta = el('div', 'card__meta'); meta.append(el('span', null, x.location), el('span', null, `${x.slots} ${x.slots === 1 ? 'place' : 'places'} left`));
      card.append(h, meta);
      return card;
    }));
    if (!items.length) { const empty = el('div', 'empty'); empty.append(el('strong', null, 'No opportunities match')); empty.append(el('span', null, 'Try a town, a sector or part of a title.')); results.append(empty); }
  };
  search.addEventListener('input', () => {
    clearTimeout(timer);
    const q = search.value.trim();
    if (!q) { results.hidden = true; list.hidden = false; status.textContent = ''; return; }
    timer = setTimeout(async () => {
      const id = ++latest;
      try {
        const response = await fetch(`/opportunities/search/?q=${encodeURIComponent(q)}`);
        if (!response.ok) throw new Error(response.status);
        const data = await response.json();
        if (id !== latest) return; // a newer query has started
        render(data.results);
        results.hidden = false; list.hidden = true;
        status.textContent = `${data.results.length} ${data.results.length === 1 ? 'result' : 'results'} for “${q}”`;
      } catch {
        if (id === latest) status.textContent = 'Search is not available right now. Press Enter to search instead.';
      }
    }, 250);
  });
}

// Forms that destroy data ask first: <form data-confirm="...">.
document.querySelectorAll('form[data-confirm]').forEach((form) => {
  form.addEventListener('submit', (e) => { if (!confirm(form.dataset.confirm)) e.preventDefault(); });
});
