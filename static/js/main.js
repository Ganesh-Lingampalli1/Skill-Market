/**
 * SkillMarket - Core Client Interactions
 * Bookmarks, Progress Tracking, Search Modal, OTP Handling, and Toasts
 */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize Lucide icons
  if (window.lucide) {
    window.lucide.createIcons();
  }

  // --- 1. Top-Right Profile Dropdown ---
  const profileTrigger = document.querySelector('.profile-trigger-btn');
  const profileMenu = document.querySelector('.profile-dropdown-menu');

  if (profileTrigger && profileMenu) {
    profileTrigger.addEventListener('click', (e) => {
      e.stopPropagation();
      profileMenu.classList.toggle('show');
    });

    document.addEventListener('click', (e) => {
      if (!profileTrigger.contains(e.target) && !profileMenu.contains(e.target)) {
        profileMenu.classList.remove('show');
      }
    });
  }

  // --- 1b. Mobile Navigation Drawer ---
  const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
  const mobileNavDrawer = document.querySelector('.mobile-nav-drawer');

  if (mobileMenuBtn && mobileNavDrawer) {
    mobileMenuBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = mobileNavDrawer.classList.toggle('show');
      mobileMenuBtn.setAttribute('aria-expanded', isOpen);
      const icon = mobileMenuBtn.querySelector('i');
      if (icon) {
        icon.setAttribute('data-lucide', isOpen ? 'x' : 'menu');
        if (window.lucide) window.lucide.createIcons();
      }
    });

    document.addEventListener('click', (e) => {
      if (!mobileMenuBtn.contains(e.target) && !mobileNavDrawer.contains(e.target)) {
        mobileNavDrawer.classList.remove('show');
        mobileMenuBtn.setAttribute('aria-expanded', 'false');
        const icon = mobileMenuBtn.querySelector('i');
        if (icon) {
          icon.setAttribute('data-lucide', 'menu');
          if (window.lucide) window.lucide.createIcons();
        }
      }
    });
  }

  // --- 2. Toast Notifications ---
  window.showToast = function (message, type = 'info') {
    let container = document.querySelector('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    let iconName = 'info';
    if (type === 'success') iconName = 'check-circle-2';
    else if (type === 'error') iconName = 'alert-circle';
    else if (type === 'warning') iconName = 'alert-triangle';

    toast.innerHTML = `
      <i data-lucide="${iconName}" style="flex-shrink:0;"></i>
      <div style="flex:1;">${message}</div>
    `;

    container.appendChild(toast);
    if (window.lucide) {
      window.lucide.createIcons();
    }

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  };

  // --- 3. AJAX Bookmarking ---
  document.querySelectorAll('.bookmark-toggle-btn').forEach((btn) => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      e.stopPropagation();

      const skillId = btn.getAttribute('data-skill-id');
      if (!skillId) return;

      try {
        const response = await fetch(`/bookmarks/toggle/${skillId}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
          }
        });

        if (response.redirected) {
          window.location.href = response.url;
          return;
        }

        const data = await response.json();
        if (data.success) {
          btn.classList.toggle('active', data.bookmarked);
          const icon = btn.querySelector('i');
          if (icon) {
            if (data.bookmarked) {
              icon.setAttribute('data-lucide', 'heart-fill');
              icon.style.fill = 'currentColor';
            } else {
              icon.setAttribute('data-lucide', 'heart');
              icon.style.fill = 'none';
            }
            if (window.lucide) window.lucide.createIcons();
          }

          // Update navbar or dashboard bookmark counter if present
          const bookmarkCounter = document.querySelector('.stat-bookmarks-count');
          if (bookmarkCounter && typeof data.total_bookmarks !== 'undefined') {
            bookmarkCounter.textContent = data.total_bookmarks;
          }

          window.showToast(data.message, data.bookmarked ? 'success' : 'info');
        }
      } catch (err) {
        console.error('Bookmark toggle error:', err);
      }
    });
  });

  // --- 4. AJAX Roadmap Step Progress Toggle ---
  document.querySelectorAll('.step-complete-btn').forEach((btn) => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      const pathId = btn.getAttribute('data-path-id');
      const stepId = btn.getAttribute('data-step-id');
      if (!pathId || !stepId) return;

      btn.disabled = true;

      try {
        const response = await fetch(`/roadmaps/${pathId}/step/${stepId}/toggle`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
          }
        });

        if (response.redirected) {
          window.location.href = response.url;
          return;
        }

        const data = await response.json();
        if (data.success) {
          const stepRow = document.querySelector(`.roadmap-step[data-step-id="${stepId}"]`);
          if (stepRow) {
            stepRow.classList.toggle('completed', data.completed);
          }

          if (data.completed) {
            btn.className = 'btn btn-sm btn-success step-complete-btn';
            btn.innerHTML = '<i data-lucide="check"></i> Completed';
          } else {
            btn.className = 'btn btn-sm btn-outline step-complete-btn';
            btn.innerHTML = '<i data-lucide="circle"></i> Mark as Complete';
          }

          // Update Progress Bar
          const progressFill = document.querySelector('.roadmap-progress-fill');
          const progressText = document.querySelector('.roadmap-progress-pct');
          const completedCountText = document.querySelector('.roadmap-completed-count');

          if (progressFill) {
            progressFill.style.width = `${data.progress_percentage}%`;
          }
          if (progressText) {
            progressText.textContent = `${data.progress_percentage}%`;
          }
          if (completedCountText) {
            completedCountText.textContent = `${data.completed_count} of ${data.total_steps} steps`;
          }

          if (window.lucide) window.lucide.createIcons();
          window.showToast(data.message, 'success');
        }
      } catch (err) {
        console.error('Progress toggle error:', err);
      } finally {
        btn.disabled = false;
      }
    });
  });

  // --- 5. OTP 6-Digit Auto-advance and Backspace ---
  const otpInputs = document.querySelectorAll('.otp-box');
  if (otpInputs.length === 6) {
    otpInputs.forEach((input, index) => {
      input.addEventListener('input', (e) => {
        const val = e.target.value;
        if (val.length >= 1) {
          input.value = val[val.length - 1]; // keep single digit
          if (index < 5) {
            otpInputs[index + 1].focus();
          }
        }
      });

      input.addEventListener('keydown', (e) => {
        if (e.key === 'Backspace' && !input.value && index > 0) {
          otpInputs[index - 1].focus();
        }
      });

      // Handle paste
      input.addEventListener('paste', (e) => {
        e.preventDefault();
        const pastedData = (e.clipboardData || window.clipboardData).getData('text').trim();
        if (/^\d{6}$/.test(pastedData)) {
          pastedData.split('').forEach((digit, i) => {
            if (otpInputs[i]) otpInputs[i].value = digit;
          });
          otpInputs[5].focus();
        }
      });
    });
  }

  // --- 6. OTP Resend Handler ---
  const resendBtn = document.getElementById('resend-otp-btn');
  if (resendBtn) {
    resendBtn.addEventListener('click', async (e) => {
      e.preventDefault();
      const email = resendBtn.getAttribute('data-email');
      if (!email) return;

      resendBtn.disabled = true;
      resendBtn.textContent = 'Sending...';

      try {
        const formData = new FormData();
        formData.append('email', email);

        const response = await fetch('/resend-otp', {
          method: 'POST',
          body: formData
        });
        const data = await response.json();

        if (data.success) {
          window.showToast(data.message, 'success');
          startResendCooldown(resendBtn, 60);
        } else {
          window.showToast(data.message, 'warning');
          resendBtn.disabled = false;
          resendBtn.textContent = 'Resend OTP';
        }
      } catch (err) {
        console.error('OTP resend error:', err);
        resendBtn.disabled = false;
        resendBtn.textContent = 'Resend OTP';
      }
    });
  }

  function startResendCooldown(button, seconds) {
    button.disabled = true;
    let remaining = seconds;
    const interval = setInterval(() => {
      remaining -= 1;
      button.textContent = `Resend in ${remaining}s`;
      if (remaining <= 0) {
        clearInterval(interval);
        button.disabled = false;
        button.textContent = 'Resend OTP';
      }
    }, 1000);
  }

  // --- 7. Quick Search Modal ---
  const searchModalOverlay = document.querySelector('.search-modal-overlay');
  const searchTriggers = document.querySelectorAll('.search-trigger-btn');
  const searchInput = document.querySelector('.search-modal-input');
  const searchResultsList = document.querySelector('.search-results-list');

  function openSearchModal() {
    if (searchModalOverlay) {
      searchModalOverlay.classList.add('active');
      if (searchInput) {
        setTimeout(() => searchInput.focus(), 100);
      }
    }
  }

  function closeSearchModal() {
    if (searchModalOverlay) {
      searchModalOverlay.classList.remove('active');
      if (searchInput) searchInput.value = '';
      if (searchResultsList) searchResultsList.innerHTML = '';
    }
  }

  searchTriggers.forEach((trigger) => trigger.addEventListener('click', openSearchModal));

  if (searchModalOverlay) {
    searchModalOverlay.addEventListener('click', (e) => {
      if (e.target === searchModalOverlay) {
        closeSearchModal();
      }
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeSearchModal();
      // Cmd/Ctrl + K shortcut
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        openSearchModal();
      }
    });
  }

  // Debounced search input
  let searchTimeout = null;
  if (searchInput && searchResultsList) {
    searchInput.addEventListener('input', (e) => {
      clearTimeout(searchTimeout);
      const query = e.target.value.trim();

      if (query.length < 2) {
        searchResultsList.innerHTML = '<div style="padding:1.5rem; text-align:center; color:var(--text-muted);">Type at least 2 characters to search skills & roadmaps...</div>';
        return;
      }

      searchTimeout = setTimeout(async () => {
        try {
          const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
          const data = await res.json();

          let html = '';
          if (data.skills.length === 0 && data.roadmaps.length === 0) {
            html = '<div style="padding:1.5rem; text-align:center; color:var(--text-muted);">No skills or roadmaps found matching your query.</div>';
          } else {
            if (data.skills.length > 0) {
              html += '<div style="padding:0.5rem 1.5rem 0.25rem; font-size:0.75rem; font-weight:700; text-transform:uppercase; color:var(--text-muted);">Skills</div>';
              data.skills.forEach((s) => {
                html += `
                  <a href="${s.url}" class="search-result-item">
                    <div>
                      <div style="font-weight:600;">${s.name}</div>
                      <div style="font-size:0.8rem; color:var(--text-muted);">${s.category}</div>
                    </div>
                    <span class="badge badge-neutral">${s.salary}</span>
                  </a>
                `;
              });
            }

            if (data.roadmaps.length > 0) {
              html += '<div style="padding:0.75rem 1.5rem 0.25rem; font-size:0.75rem; font-weight:700; text-transform:uppercase; color:var(--text-muted);">Career Roadmaps</div>';
              data.roadmaps.forEach((r) => {
                html += `
                  <a href="${r.url}" class="search-result-item">
                    <div>
                      <div style="font-weight:600;">${r.name}</div>
                      <div style="font-size:0.8rem; color:var(--text-muted);">${r.duration}</div>
                    </div>
                    <i data-lucide="arrow-right" style="width:16px; height:16px;"></i>
                  </a>
                `;
              });
            }
          }

          searchResultsList.innerHTML = html;
          if (window.lucide) window.lucide.createIcons();
        } catch (err) {
          console.error('Search API error:', err);
        }
      }, 200);
    });
  }
});
