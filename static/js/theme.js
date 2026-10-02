/**
 * SkillMarket Theme Manager
 * Supports Light & Dark modes, instant pre-render application,
 * persistent localStorage and server-side user synchronization.
 */

(function () {
  const THEME_KEY = 'skillmarket_theme';

  function getPreferredTheme() {
    // 1. Check data-user-theme set by server on <html>
    const serverTheme = document.documentElement.getAttribute('data-user-theme');
    if (serverTheme && (serverTheme === 'dark' || serverTheme === 'light')) {
      return serverTheme;
    }
    // 2. Check localStorage
    const saved = localStorage.getItem(THEME_KEY);
    if (saved && (saved === 'dark' || saved === 'light')) {
      return saved;
    }
    // 3. Fallback to system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  }

  function applyTheme(theme, syncServer = false) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(THEME_KEY, theme);

    // Update toggle icons on all theme buttons
    const toggleButtons = document.querySelectorAll('.theme-toggle-btn');
    toggleButtons.forEach((btn) => {
      if (theme === 'dark') {
        btn.innerHTML = '<i data-lucide="sun"></i>';
        btn.setAttribute('title', 'Switch to Light Mode');
        btn.setAttribute('aria-label', 'Switch to Light Mode');
      } else {
        btn.innerHTML = '<i data-lucide="moon"></i>';
        btn.setAttribute('title', 'Switch to Dark Mode');
        btn.setAttribute('aria-label', 'Switch to Dark Mode');
      }
    });

    if (window.lucide) {
      window.lucide.createIcons();
    }

    // Trigger custom event for charts to redraw with new theme colors
    window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));

    // Sync to backend if logged in
    if (syncServer) {
      fetch('/api/theme', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ theme })
      }).catch((err) => console.log('Theme sync notice:', err));
    }
  }

  // Set initial theme immediately to prevent FOUC
  const initialTheme = getPreferredTheme();
  document.documentElement.setAttribute('data-theme', initialTheme);

  document.addEventListener('DOMContentLoaded', () => {
    applyTheme(initialTheme, false);

    // Bind click events on all theme toggle buttons
    document.querySelectorAll('.theme-toggle-btn').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        applyTheme(newTheme, true);
        if (window.showToast) {
          window.showToast(`Switched to ${newTheme === 'dark' ? 'Dark' : 'Light'} Mode`, 'info');
        }
      });
    });
  });

  // Expose global helper
  window.SkillMarketTheme = {
    getTheme: () => document.documentElement.getAttribute('data-theme') || 'light',
    setTheme: (t) => applyTheme(t, true)
  };
})();
