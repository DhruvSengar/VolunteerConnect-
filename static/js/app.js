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
  const MIN_CHARS = 2; // live results start at 2 characters
  let timer, latest = 0;
  const run = async () => {
    const q = search.value.trim();
    if (q.length < MIN_CHARS) { // too short: keep the full list; latest++ drops any reply still on its way
      latest++; results.hidden = true; list.hidden = false;
      status.textContent = q ? `Type at least ${MIN_CHARS} characters to search.` : '';
      return;
    }
    const id = ++latest;
    try {
      const response = await fetch(`/opportunities/search/?q=${encodeURIComponent(q)}`);
      if (!response.ok) throw new Error(response.status);
      const data = await response.json();
      if (id !== latest) return; // a newer query has started
      results.innerHTML = data.html; // server-rendered cards (Django escapes every value)
      results.hidden = false; list.hidden = true;
      status.textContent = `${data.results.length} ${data.results.length === 1 ? 'result' : 'results'} for “${q}”`;
    } catch {
      if (id === latest) status.textContent = 'Search is not available right now. Try again in a moment.';
    }
  };
  search.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(run, 250); });
  // Enter searches in place too; the page reload stays only as the fallback when scripts are off
  search.form.addEventListener('submit', (e) => { e.preventDefault(); clearTimeout(timer); run(); });
}

// Forms that destroy data ask first: <form data-confirm="...">.
document.querySelectorAll('form[data-confirm]').forEach((form) => {
  form.addEventListener('submit', (e) => { if (!confirm(form.dataset.confirm)) e.preventDefault(); });
});
