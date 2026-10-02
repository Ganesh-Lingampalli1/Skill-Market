/**
 * SkillMarket - Chart.js Visualizations
 * Dynamic Light / Dark mode colors and responsive chart instances
 */

window.SkillMarketCharts = (function () {
  let instances = {};

  function getThemeColors() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    return {
      textColor: isDark ? '#cbd5e1' : '#475569',
      gridColor: isDark ? '#243247' : '#e2e8f0',
      primary: isDark ? '#38bdf8' : '#0284c7',
      primaryLight: isDark ? 'rgba(56, 189, 248, 0.2)' : 'rgba(2, 132, 199, 0.2)',
      accent: isDark ? '#818cf8' : '#6366f1',
      accentLight: isDark ? 'rgba(129, 140, 248, 0.2)' : 'rgba(99, 102, 241, 0.2)',
      success: isDark ? '#34d399' : '#10b981',
      tooltipBg: isDark ? '#1e293b' : '#0f172a',
      tooltipText: '#ffffff'
    };
  }

  function initSalaryChart(canvasId, labels, minSalaries, maxSalaries) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const colors = getThemeColors();

    if (instances[canvasId]) {
      instances[canvasId].destroy();
    }

    instances[canvasId] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Starting Package (₹ LPA)',
            data: minSalaries,
            backgroundColor: colors.primaryLight,
            borderColor: colors.primary,
            borderWidth: 1.5,
            borderRadius: 6
          },
          {
            label: 'Experienced / Top Package (₹ LPA)',
            data: maxSalaries,
            backgroundColor: colors.accentLight,
            borderColor: colors.accent,
            borderWidth: 1.5,
            borderRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: { color: colors.textColor, font: { family: 'Inter', size: 12, weight: 500 } }
          },
          tooltip: {
            backgroundColor: colors.tooltipBg,
            titleColor: colors.tooltipText,
            bodyColor: colors.tooltipText,
            padding: 12,
            cornerRadius: 8,
            callbacks: {
              label: (item) => `${item.dataset.label}: ₹${item.raw} LPA`
            }
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: colors.textColor, font: { family: 'Inter', size: 11 } }
          },
          y: {
            grid: { color: colors.gridColor },
            ticks: {
              color: colors.textColor,
              callback: (v) => `₹${v}L`
            }
          }
        }
      }
    });
  }

  function initDemandChart(canvasId, labels, scores) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const colors = getThemeColors();

    if (instances[canvasId]) {
      instances[canvasId].destroy();
    }

    instances[canvasId] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Market Demand Score (Out of 100)',
            data: scores,
            backgroundColor: colors.primary,
            borderRadius: 6
          }
        ]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: colors.tooltipBg,
            titleColor: colors.tooltipText,
            bodyColor: colors.tooltipText,
            padding: 10,
            cornerRadius: 8,
            callbacks: {
              label: (item) => `Demand Score: ${item.raw}/100`
            }
          }
        },
        scales: {
          x: {
            max: 100,
            grid: { color: colors.gridColor },
            ticks: { color: colors.textColor }
          },
          y: {
            grid: { display: false },
            ticks: { color: colors.textColor, font: { family: 'Inter', weight: 600 } }
          }
        }
      }
    });
  }

  function initCategoryChart(canvasId, labels, counts) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const colors = getThemeColors();

    if (instances[canvasId]) {
      instances[canvasId].destroy();
    }

    const palette = [
      '#0284c7', '#6366f1', '#10b981', '#f59e0b',
      '#ec4899', '#8b5cf6', '#14b8a6'
    ];

    instances[canvasId] = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [
          {
            data: counts,
            backgroundColor: palette.slice(0, labels.length),
            borderWidth: 2,
            borderColor: document.documentElement.getAttribute('data-theme') === 'dark' ? '#151e2e' : '#ffffff'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'right',
            labels: { color: colors.textColor, font: { family: 'Inter', size: 12 }, padding: 16 }
          }
        },
        cutout: '68%'
      }
    });
  }

  // Redraw all active charts upon theme change
  window.addEventListener('themeChanged', () => {
    const colors = getThemeColors();
    Object.values(instances).forEach((chart) => {
      if (chart.options.scales) {
        if (chart.options.scales.x) {
          if (chart.options.scales.x.ticks) chart.options.scales.x.ticks.color = colors.textColor;
          if (chart.options.scales.x.grid) chart.options.scales.x.grid.color = colors.gridColor;
        }
        if (chart.options.scales.y) {
          if (chart.options.scales.y.ticks) chart.options.scales.y.ticks.color = colors.textColor;
          if (chart.options.scales.y.grid) chart.options.scales.y.grid.color = colors.gridColor;
        }
      }
      if (chart.options.plugins && chart.options.plugins.legend && chart.options.plugins.legend.labels) {
        chart.options.plugins.legend.labels.color = colors.textColor;
      }
      chart.update();
    });
  });

  return {
    initSalaryChart,
    initDemandChart,
    initCategoryChart
  };
})();
