// Sticky header scroll shadow
window.addEventListener('scroll', function() {
  var h = document.querySelector('.main-header, .site-header');
  if (h) h.classList.toggle('scrolled', window.scrollY > 8);
}, { passive: true });

// Set --header-height CSS var dynamically for sticky nav
function updateHeaderHeight() {
  var h = document.querySelector('.main-header, .site-header');
  if (h) document.documentElement.style.setProperty('--header-height', h.offsetHeight + 'px');
}
window.addEventListener('DOMContentLoaded', updateHeaderHeight);
window.addEventListener('resize', updateHeaderHeight);

/**
 * Sanyukt ID — Auth Utilities
 */
const auth = {
  login(data) {
    localStorage.setItem('sanyukt_token', data.access_token);
    localStorage.setItem('sanyukt_role', data.role);
    localStorage.setItem('sanyukt_username', data.username);
    if (data.citizen_name) localStorage.setItem('sanyukt_name', data.citizen_name);
    if (data.officer_name) localStorage.setItem('sanyukt_name', data.officer_name);
    if (data.sanyukt_id) localStorage.setItem('sanyukt_id', data.sanyukt_id);
    if (data.citizen_id) localStorage.setItem('sanyukt_citizen_id', data.citizen_id);
    if (data.officer_id) localStorage.setItem('sanyukt_officer_id', data.officer_id);
  },
  logout() {
    ['sanyukt_token','sanyukt_role','sanyukt_username','sanyukt_name','sanyukt_id','sanyukt_citizen_id','sanyukt_officer_id'].forEach(k => localStorage.removeItem(k));
    window.location.href = '/login.html';
  },
  isLoggedIn() { return !!localStorage.getItem('sanyukt_token'); },
  getRole() { return localStorage.getItem('sanyukt_role') || ''; },
  getName() { return localStorage.getItem('sanyukt_name') || localStorage.getItem('sanyukt_username') || ''; },
  getSanyuktId() { return localStorage.getItem('sanyukt_id') || ''; },
  requireLogin() {
    if (!this.isLoggedIn()) { window.location.href = '/login.html'; return false; }
    return true;
  },
  requireCitizen() {
    if (!this.requireLogin()) return false;
    if (this.getRole() !== 'citizen') { window.location.href = '/officer-dashboard.html'; return false; }
    return true;
  },
  requireOfficer() {
    if (!this.requireLogin()) return false;
    if (this.getRole() !== 'officer') { window.location.href = '/dashboard.html'; return false; }
    return true;
  }
};

// Update header user info
function updateHeaderUser() {
  const userEl = document.getElementById('header-user-info');
  if (!userEl) return;
  if (auth.isLoggedIn()) {
    const role = auth.getRole();
    const name = auth.getName();
    const id = auth.getSanyuktId();
    let html = `<span style="font-weight:700;color:#0C3866;">${name}</span>`;
    if (id) html += ` <span style="color:#5C6B7B;font-size:11px;font-family:monospace;">(${id})</span>`;
    if (role === 'officer') {
      html += ` | <a href="/officer-dashboard.html" style="font-weight:600;">Officer Portal</a>`;
    } else if (role === 'citizen') {
      html += ` | <a href="/dashboard.html" style="font-weight:600;">Citizen Dashboard</a>`;
    }
    html += ` | <a href="#" onclick="auth.logout();return false;" style="color:#C5221F;font-weight:600;">Logout</a>`;
    userEl.innerHTML = html;
  } else {
    userEl.innerHTML = `<a href="/login.html" class="btn btn-outline btn-sm">Citizen / Officer Login</a> <a href="/register.html" class="btn btn-primary btn-sm">Register</a>`;
  }
}

// Highlight active nav
function highlightNav() {
  const path = window.location.pathname || '/';
  document.querySelectorAll('.nav-links a, .site-nav a').forEach(a => {
    const href = a.getAttribute('href');
    if (href === path || (path === '/' && href === '/index.html')) {
      a.classList.add('active');
    }
  });
}

// Show alert
function showAlert(id, msg, type = 'info') {
  const el = document.getElementById(id);
  if (!el) return;
  el.className = `alert alert-${type}`;
  el.textContent = msg;
  el.style.display = 'block';
  setTimeout(() => { el.style.display = 'none'; }, 6000);
}

// Format date
function fmtDate(iso) {
  if (!iso) return '-';
  const d = new Date(iso);
  return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) + ' ' +
         d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
}

// Status badge
function statusBadge(status) {
  const s = (status || '').toLowerCase().replace(/ /g, '_');
  return `<span class="badge badge-${s}">${status || ''}</span>`;
}

function updateClock() {
  const el = document.getElementById('live-clock');
  if (el) {
    const now = new Date();
    el.textContent = now.toLocaleDateString('en-IN', { weekday: 'short', day: '2-digit', month: 'short', year: 'numeric' }) + ' | ' + now.toLocaleTimeString('en-IN');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  updateHeaderUser();
  highlightNav();
  updateClock();
  setInterval(updateClock, 1000);
});

