import os
import re

FRONTEND_DIR = r'f:\Sanyukt\frontend'

# New official logo brand component
BRAND_LOGO_HTML = '''<a href="/index.html" class="brand-group" style="text-decoration:none;">
      <img src="/static/img/sanyukt-logo.svg" alt="Government of Maharashtra — Sanyukt ID" class="brand-logo-img">
    </a>'''

# Standard official Government of Maharashtra footer
STANDARD_FOOTER = '''<footer class="site-footer">
  <div class="footer-top">
    <div class="footer-col">
      <h4>Government of Maharashtra</h4>
      <ul>
        <li><a href="/index.html">State Portal Home</a></li>
        <li><a href="/services.html">Citizen Services Directory</a></li>
        <li><a href="/applications.html">Track Application Status</a></li>
        <li><a href="/officer-dashboard.html">Administrative Officer Portal</a></li>
      </ul>
    </div>
    <div class="footer-col">
      <h4>Citizen Services</h4>
      <ul>
        <li><a href="/apply.html?service=PROP_CERT">7/12 Land Records (e-Mahabhumi)</a></li>
        <li><a href="/apply.html?service=PROP_TRANSFER">Online Ferfar & Property Transfer</a></li>
        <li><a href="/apply.html?service=INCOME_CERT">Tahasildar Income Certificates</a></li>
        <li><a href="/apply.html?service=BLDG_PERMISSION">Municipal BPAMS Clearances</a></li>
        <li><a href="/apply.html?service=SCHOLARSHIP">MahaDBT Education Scholarships</a></li>
      </ul>
    </div>
    <div class="footer-col">
      <h4>Policies & Support</h4>
      <ul>
        <li><a href="#">Citizen Charter & Service SLAs</a></li>
        <li><a href="#">Privacy & Data Protection Policy</a></li>
        <li><a href="#">Hyperlinking Policy</a></li>
        <li><a href="#">Terms of Service</a></li>
        <li><a href="#">Grievance Redressal (Aaple Sarkar)</a></li>
      </ul>
    </div>
    <div class="footer-col">
      <h4>Helpline & Helpdesk</h4>
      <p style="color:#FFF;font-weight:bold;font-size:15px;margin-bottom:4px;">1800-120-8040</p>
      <p style="font-size:11px;color:#A0B3C6;margin-bottom:8px;">Toll-Free | 24 Hours x 7 Days Support</p>
      <p style="font-size:11px;color:#A0B3C6;">Department of Information Technology,<br>Mantralaya, Mumbai - 400 032</p>
    </div>
  </div>
  <div class="footer-bottom">
    <div>&copy; 2026 Government of Maharashtra. All rights reserved. Developed by <strong>Team ERRORISTS</strong>.</div>
  </div>
</footer>'''

# Standard Citizen Header
CITIZEN_HEADER = '''<!-- Tricolor Top Accent -->
<div class="gov-tricolor-bar"></div>

<!-- Accessibility & Utility Bar -->
<div class="top-utility-bar">
  <div class="utility-container">
    <div class="utility-left">
      <span class="utility-item"><strong>महाराष्ट्र शासन</strong> | Government of Maharashtra</span>
      <span class="utility-item" style="color:#7D8C9B;">|</span>
      <span class="utility-item"><span id="live-clock">Loading live time...</span></span>
    </div>
    <div class="utility-right">
      <a href="#main-content" style="color:#495057;font-size:11px;">Skip to Main Content</a>
      <span>|</span>
      <button class="utility-btn" onclick="document.body.style.fontSize='13px'">A-</button>
      <button class="utility-btn" onclick="document.body.style.fontSize='14px'">A</button>
      <button class="utility-btn" onclick="document.body.style.fontSize='15px'">A+</button>
      <span>|</span>
      <a href="#" class="lang-badge">मराठी</a>
      <a href="#" class="lang-badge active">English</a>
    </div>
  </div>
</div>

<!-- Main Branding Header -->
<header class="main-header">
  <div class="header-container">
    <a href="/index.html" class="brand-group" style="text-decoration:none;">
      <img src="/static/img/sanyukt-logo.svg" alt="Government of Maharashtra — Sanyukt ID" class="brand-logo-img">
    </a>
    <div class="header-actions">
      <div class="helpline-box">
        <div class="helpline-label">Toll-Free Citizen Helpline</div>
        <div class="helpline-num">1800-120-8040</div>
      </div>
      <div id="header-user-info" class="header-user-status"></div>
    </div>
  </div>
</header>

<!-- Navigation Bar -->
<nav class="main-nav">
  <div class="nav-container">
    <ul class="nav-links">
      <li><a href="/index.html">Home</a></li>
      <li><a href="/services.html">Citizen Services</a></li>
      <li><a href="/applications.html">Track Applications</a></li>
      <li><a href="/dashboard.html">Dashboard</a></li>
      <li><a href="/consent.html">Consent</a></li>
      <li><a href="/notifications.html">Notifications</a></li>
      <li><a href="/profile.html">Profile</a></li>
      <li><a href="/officer-dashboard.html" class="nav-officer-link">Officer Portal</a></li>
    </ul>
  </div>
</nav>'''

# Standard Officer Header
OFFICER_HEADER = '''<!-- Tricolor Top Accent -->
<div class="gov-tricolor-bar"></div>

<!-- Accessibility & Utility Bar -->
<div class="top-utility-bar">
  <div class="utility-container">
    <div class="utility-left">
      <span class="utility-item"><strong>महाराष्ट्र शासन</strong> | Government of Maharashtra — Administrative Officer Portal</span>
      <span class="utility-item" style="color:#7D8C9B;">|</span>
      <span class="utility-item"><span id="live-clock">Loading live time...</span></span>
    </div>
    <div class="utility-right">
      <a href="#main-content" style="color:#495057;font-size:11px;">Skip to Main Content</a>
      <span>|</span>
      <button class="utility-btn" onclick="document.body.style.fontSize='13px'">A-</button>
      <button class="utility-btn" onclick="document.body.style.fontSize='14px'">A</button>
      <button class="utility-btn" onclick="document.body.style.fontSize='15px'">A+</button>
      <span>|</span>
      <a href="#" class="lang-badge">मराठी</a>
      <a href="#" class="lang-badge active">English</a>
    </div>
  </div>
</div>

<!-- Main Branding Header -->
<header class="main-header">
  <div class="header-container">
    <a href="/officer-dashboard.html" class="brand-group" style="text-decoration:none;">
      <img src="/static/img/sanyukt-logo.svg" alt="Government of Maharashtra — Sanyukt ID" class="brand-logo-img">
    </a>
    <div class="header-actions">
      <div class="helpline-box">
        <div class="helpline-label">Internal Support Desk</div>
        <div class="helpline-num">022-2202-5000</div>
      </div>
      <div id="header-user-info" class="header-user-status"></div>
    </div>
  </div>
</header>

<!-- Navigation Bar -->
<nav class="main-nav">
  <div class="nav-container">
    <ul class="nav-links">
      <li><a href="/officer-dashboard.html">Officer Dashboard</a></li>
      <li><a href="/officer-applications.html">All Applications</a></li>
      <li><a href="/audit-logs.html">System Audit Logs</a></li>
      <li><a href="/index.html" class="nav-officer-link">Citizen State Portal</a></li>
    </ul>
  </div>
</nav>'''

officer_pages = {'officer-dashboard.html', 'officer-applications.html', 'audit-logs.html'}

for fname in sorted(os.listdir(FRONTEND_DIR)):
    if not fname.endswith('.html'):
        continue
    filepath = os.path.join(FRONTEND_DIR, fname)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Remove any prototype banners
    content = re.sub(r'<div class="proto-banner".*?</div>', '', content, flags=re.DOTALL)
    content = re.sub(r'<div class="prototype-banner".*?</div>', '', content, flags=re.DOTALL)

    # 2. If it's an officer page or old header page, replace header + nav
    is_officer = fname in officer_pages
    is_old_header = '<header class="site-header">' in content

    if is_officer and is_old_header:
        # Replace up to </nav>
        content = re.sub(r'<header class="site-header">.*?</nav>', OFFICER_HEADER, content, flags=re.DOTALL)
    elif not is_officer and is_old_header:
        content = re.sub(r'<header class="site-header">.*?</nav>', CITIZEN_HEADER, content, flags=re.DOTALL)
    else:
        # It already has main-header, replace old brand-group with new SVG logo
        content = re.sub(
            r'<div class="brand-group">.*?<div class="brand-titles">.*?</div>\s*</div>',
            BRAND_LOGO_HTML,
            content,
            flags=re.DOTALL
        )
        # Also catch any existing link brand-group with emblem-seal
        content = re.sub(
            r'<a href="[^"]*" class="brand-group"[^>]*>.*?</a>',
            BRAND_LOGO_HTML,
            content,
            flags=re.DOTALL
        )

    # 3. Standardize footer
    content = re.sub(r'<footer.*?</footer>', STANDARD_FOOTER, content, flags=re.DOTALL)

    # 4. Standardize container class on main
    # Ensure <main class="container page-body" ...> has proper max-width container
    content = content.replace('class="container page-body"', 'class="page-wrapper" id="main-content"')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'Successfully updated {fname}')

print('ALL HTML PAGES STANDARDIZED!')
