/**
 * E-COMMERCE ANALYTICS PLATFORM — EXECUTIVE BI DASHBOARD
 * Core Application Logic, Reactive Multi-Dimensional Cross-Filtering,
 * Chart.js Visualizations & Interactive Controls
 */

document.addEventListener('DOMContentLoaded', () => {
  const data = window.DASHBOARD_DATA;
  if (!data) {
    console.error('Fatal: window.DASHBOARD_DATA is missing or failed to load.');
    return;
  }

  // Application State
  const state = {
    theme: localStorage.getItem('dashboard_theme') || 'dark',
    filters: {
      category: 'ALL',
      macroRegion: 'ALL',
      yearMonth: 'ALL'
    }
  };

  const chartInstances = {};
  let currentCategoryKeys = [];
  let currentRegionKeys = [];
  let currentMonthKeys = [];

  // Initialize
  initTheme();
  initNavigation();
  initFilterControls();
  renderStaticPages(); // Cohorts, Sellers, Logistics, Products
  applyFiltersAndRender();

  /* ==========================================================================
     Theme Management (Dark / Light)
     ========================================================================== */
  function initTheme() {
    document.body.setAttribute('data-theme', state.theme);
    const themeBtn = document.getElementById('themeToggleBtn');

    if (themeBtn) {
      themeBtn.addEventListener('click', () => {
        state.theme = state.theme === 'dark' ? 'light' : 'dark';
        document.body.setAttribute('data-theme', state.theme);
        localStorage.setItem('dashboard_theme', state.theme);
        updateChartThemes();
      });
    }
  }

  function getThemeColors() {
    const isDark = state.theme === 'dark';
    return {
      textPrimary: isDark ? '#f8fafc' : '#0f172a',
      textSecondary: isDark ? '#94a3b8' : '#64748b',
      gridColor: isDark ? 'rgba(255, 255, 255, 0.06)' : 'rgba(0, 0, 0, 0.06)',
      cardBg: isDark ? '#111827' : '#ffffff',
      fontFamily: "'Inter', sans-serif"
    };
  }

  function updateChartThemes() {
    const colors = getThemeColors();
    Object.values(chartInstances).forEach(chart => {
      if (!chart) return;
      if (chart.options.scales) {
        Object.keys(chart.options.scales).forEach(scaleKey => {
          const scale = chart.options.scales[scaleKey];
          if (scale.ticks) scale.ticks.color = colors.textSecondary;
          if (scale.grid) scale.grid.color = colors.gridColor;
        });
      }
      if (chart.options.plugins && chart.options.plugins.legend) {
        chart.options.plugins.legend.labels.color = colors.textPrimary;
      }
      chart.update();
    });
  }

  /* ==========================================================================
     Tab Navigation
     ========================================================================== */
  function initNavigation() {
    const navTabs = document.querySelectorAll('.nav-tab');
    const tabPanes = document.querySelectorAll('.tab-pane');

    navTabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const targetTabId = tab.getAttribute('data-tab');

        navTabs.forEach(t => t.classList.remove('active'));
        tabPanes.forEach(p => p.classList.remove('active'));

        tab.classList.add('active');
        const targetPane = document.getElementById(targetTabId);
        if (targetPane) {
          targetPane.classList.add('active');
          window.dispatchEvent(new Event('resize'));
        }
      });
    });
  }

  /* ==========================================================================
     Formatting Utilities
     ========================================================================== */
  function formatBRL(val) {
    if (val === null || val === undefined || isNaN(val)) return '—';
    return 'R$ ' + Number(val).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function formatBRLShort(val) {
    if (val === null || val === undefined || isNaN(val)) return 'R$ 0';
    if (val >= 1e6) return 'R$ ' + (val / 1e6).toFixed(2) + 'M';
    if (val >= 1e3) return 'R$ ' + (val / 1e3).toFixed(1) + 'K';
    return 'R$ ' + Number(val).toFixed(0);
  }

  function formatNumber(val) {
    if (val === null || val === undefined || isNaN(val)) return '0';
    return Number(val).toLocaleString('en-US');
  }

  function formatPct(val) {
    if (val === null || val === undefined || isNaN(val)) return '—';
    return Number(val).toFixed(1) + '%';
  }

  function truncateId(str, start = 8, end = 4) {
    if (!str || str.length <= start + end) return str;
    return `${str.substring(0, start)}...${str.substring(str.length - end)}`;
  }

  function cleanCategory(cat) {
    if (!cat) return 'Uncategorized';
    return cat.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  }

  /* ==========================================================================
     Interactive Filter Controls & State Management
     ========================================================================== */
  function initFilterControls() {
    const cube = data.cube || [];

    // Populate Category dropdown
    const catSelect = document.getElementById('filterCategory');
    if (catSelect && cube.length > 0) {
      const catTotals = {};
      cube.forEach(r => {
        catTotals[r.cat] = (catTotals[r.cat] || 0) + r.gmv;
      });
      const sortedCats = Object.keys(catTotals).sort((a, b) => catTotals[b] - catTotals[a]);

      sortedCats.forEach(cat => {
        const opt = document.createElement('option');
        opt.value = cat;
        opt.textContent = `${cleanCategory(cat)} (${formatBRLShort(catTotals[cat])})`;
        catSelect.appendChild(opt);
      });

      catSelect.addEventListener('change', e => {
        setFilter('category', e.target.value);
      });
    }

    // Region dropdown
    const regSelect = document.getElementById('filterRegion');
    if (regSelect) {
      regSelect.addEventListener('change', e => {
        setFilter('macroRegion', e.target.value);
      });
    }

    // Period / Month dropdown
    const periodSelect = document.getElementById('filterPeriod');
    if (periodSelect && cube.length > 0) {
      const months = Array.from(new Set(cube.map(r => r.ym))).sort();
      months.forEach(m => {
        const opt = document.createElement('option');
        opt.value = m;
        opt.textContent = m;
        periodSelect.appendChild(opt);
      });

      periodSelect.addEventListener('change', e => {
        setFilter('yearMonth', e.target.value);
      });
    }

    // Reset button
    const resetBtn = document.getElementById('resetFiltersBtn');
    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        resetAllFilters();
      });
    }
  }

  function setFilter(dim, value) {
    state.filters[dim] = value;
    syncFilterUI();
    applyFiltersAndRender();
  }

  function resetAllFilters() {
    state.filters.category = 'ALL';
    state.filters.macroRegion = 'ALL';
    state.filters.yearMonth = 'ALL';
    syncFilterUI();
    applyFiltersAndRender();
  }

  function syncFilterUI() {
    const catSelect = document.getElementById('filterCategory');
    const regSelect = document.getElementById('filterRegion');
    const periodSelect = document.getElementById('filterPeriod');
    const resetBtn = document.getElementById('resetFiltersBtn');
    const pillsContainer = document.getElementById('filterPillsContainer');

    if (catSelect) catSelect.value = state.filters.category;
    if (regSelect) regSelect.value = state.filters.macroRegion;
    if (periodSelect) periodSelect.value = state.filters.yearMonth;

    // Render filter pills
    const activeFilters = [];
    if (state.filters.category !== 'ALL') {
      activeFilters.push({ dim: 'category', label: `Category: ${cleanCategory(state.filters.category)}` });
    }
    if (state.filters.macroRegion !== 'ALL') {
      activeFilters.push({ dim: 'macroRegion', label: `Region: ${state.filters.macroRegion}` });
    }
    if (state.filters.yearMonth !== 'ALL') {
      activeFilters.push({ dim: 'yearMonth', label: `Month: ${state.filters.yearMonth}` });
    }

    if (pillsContainer) {
      pillsContainer.innerHTML = activeFilters.map(f => `
        <span class="filter-pill">
          ${f.label}
          <button class="remove-pill-btn" data-dim="${f.dim}" title="Remove filter">&times;</button>
        </span>
      `).join('');

      // Add click listeners to remove pill buttons
      pillsContainer.querySelectorAll('.remove-pill-btn').forEach(btn => {
        btn.addEventListener('click', e => {
          e.stopPropagation();
          const dim = btn.getAttribute('data-dim');
          setFilter(dim, 'ALL');
        });
      });
    }

    if (resetBtn) {
      resetBtn.style.display = activeFilters.length > 0 ? 'inline-flex' : 'none';
    }

    // Toggle .is-filtered styling on KPI cards
    document.querySelectorAll('.kpi-card').forEach(card => {
      if (activeFilters.length > 0) {
        card.classList.add('is-filtered');
      } else {
        card.classList.remove('is-filtered');
      }
    });
  }

  /* ==========================================================================
     Filtering & Reactive Calculation Engine
     ========================================================================== */
  function applyFiltersAndRender() {
    const cube = data.cube || [];
    const isFiltered = (
      state.filters.category !== 'ALL' ||
      state.filters.macroRegion !== 'ALL' ||
      state.filters.yearMonth !== 'ALL'
    );

    // Filter matched rows from the multi-dimensional cube
    const matchedRows = cube.filter(r => {
      if (state.filters.category !== 'ALL' && r.cat !== state.filters.category) return false;
      if (state.filters.macroRegion !== 'ALL' && r.reg !== state.filters.macroRegion) return false;
      if (state.filters.yearMonth !== 'ALL' && r.ym !== state.filters.yearMonth) return false;
      return true;
    });

    // 1. Calculate Aggregated Metrics
    let gmv = 0;
    let freight = 0;
    let orders = 0;
    let onTimeSum = 0;
    let csatSum = 0;

    if (!isFiltered) {
      gmv = data.kpis.total_gmv;
      freight = data.kpis.total_freight;
      orders = data.kpis.total_orders;
      var aov = data.kpis.aov;
      var onTimePct = data.kpis.on_time_pct;
      var csat = data.kpis.avg_csat;
    } else {
      matchedRows.forEach(r => {
        gmv += r.gmv;
        freight += r.frt;
        orders += r.ord;
        onTimeSum += (r.ont * r.ord);
        csatSum += (r.csat * r.ord);
      });
      var aov = orders > 0 ? gmv / orders : 0;
      var onTimePct = orders > 0 ? onTimeSum / orders : 0;
      var csat = orders > 0 ? csatSum / orders : 0;
    }

    // 2. Update KPI Elements in DOM
    const kpiGmvEl = document.getElementById('kpi-val-gmv');
    const kpiOrdersEl = document.getElementById('kpi-val-orders');
    const kpiAovEl = document.getElementById('kpi-val-aov');
    const kpiOntimeEl = document.getElementById('kpi-val-ontime');
    const kpiCsatEl = document.getElementById('kpi-val-csat');

    const kpiSubGmvEl = document.getElementById('kpi-sub-gmv');
    const kpiSubOrdersEl = document.getElementById('kpi-sub-orders');
    const kpiSubAovEl = document.getElementById('kpi-sub-aov');
    const kpiSubOntimeEl = document.getElementById('kpi-sub-ontime');
    const kpiSubCsatEl = document.getElementById('kpi-sub-csat');

    if (kpiGmvEl) kpiGmvEl.textContent = formatBRLShort(gmv);
    if (kpiOrdersEl) kpiOrdersEl.textContent = formatNumber(orders);
    if (kpiAovEl) kpiAovEl.textContent = formatBRL(aov);
    if (kpiOntimeEl) kpiOntimeEl.textContent = formatPct(onTimePct);
    if (kpiCsatEl) kpiCsatEl.textContent = csat.toFixed(2) + ' ★';

    if (isFiltered) {
      const filterDesc = [];
      if (state.filters.category !== 'ALL') filterDesc.push(cleanCategory(state.filters.category));
      if (state.filters.macroRegion !== 'ALL') filterDesc.push(state.filters.macroRegion);
      if (state.filters.yearMonth !== 'ALL') filterDesc.push(state.filters.yearMonth);
      const filterStr = filterDesc.join(' • ');

      if (kpiSubGmvEl) kpiSubGmvEl.innerHTML = `<span style="color: var(--primary-light); font-weight: 600;">Filtered: ${filterStr}</span>`;
      if (kpiSubOrdersEl) kpiSubOrdersEl.textContent = `Completed orders for selection`;
      if (kpiSubAovEl) kpiSubAovEl.textContent = `Merchandise spend per order`;
      if (kpiSubOntimeEl) kpiSubOntimeEl.textContent = `On-time delivery for selection`;
      if (kpiSubCsatEl) kpiSubCsatEl.textContent = `Average customer review rating`;
    } else {
      if (kpiSubGmvEl) kpiSubGmvEl.innerHTML = `&uarr; +4.2% MoM (Prior month R$ 985K)`;
      if (kpiSubOrdersEl) kpiSubOrdersEl.textContent = `Across 27 Brazilian States`;
      if (kpiSubAovEl) kpiSubAovEl.textContent = `Merchandise GMV per order`;
      if (kpiSubOntimeEl) kpiSubOntimeEl.textContent = `Promised SLA: 24.5d | Actual: 12.5d`;
      if (kpiSubCsatEl) kpiSubCsatEl.textContent = `99,224 Verified Customer Reviews`;
    }

    // 3. Update Dynamic Charts
    renderOverviewMonthlyChart(matchedRows, isFiltered);
    renderOverviewCategoriesChart(matchedRows, isFiltered);
    renderOverviewRegionsChart(matchedRows, isFiltered);
    renderSalesGmvFreightChart(matchedRows, isFiltered);
    renderMonthlySalesTable(matchedRows, isFiltered);
    renderDynamicTakeaways(gmv, orders, onTimePct, csat, isFiltered);
  }

  /* ==========================================================================
     Chart 1: Monthly GMV & Orders Trajectory (with Click-to-Filter)
     ========================================================================== */
  function renderOverviewMonthlyChart(matchedRows, isFiltered) {
    const ctx = document.getElementById('chartOverviewMonthly');
    if (!ctx) return;
    const colors = getThemeColors();

    // Group monthly data
    const monthMap = {};
    const months = data.monthly_trend.map(d => d.year_month);
    months.forEach(m => {
      monthMap[m] = { gmv: 0, orders: 0 };
    });

    if (!isFiltered) {
      data.monthly_trend.forEach(d => {
        monthMap[d.year_month] = { gmv: d.gmv, orders: d.orders };
      });
    } else {
      matchedRows.forEach(r => {
        if (monthMap[r.ym]) {
          monthMap[r.ym].gmv += r.gmv;
          monthMap[r.ym].orders += r.ord;
        }
      });
    }

    currentMonthKeys = months;
    const gmvData = months.map(m => monthMap[m].gmv);
    const ordersData = months.map(m => monthMap[m].orders);

    // Highlighting colors for selected month
    const backgroundColors = months.map(m => {
      if (state.filters.yearMonth === m) return '#f59e0b'; // Gold highlight
      if (state.filters.yearMonth !== 'ALL') return 'rgba(99, 102, 241, 0.25)'; // Dim others
      return 'rgba(99, 102, 241, 0.75)';
    });

    if (chartInstances.monthly) {
      chartInstances.monthly.data.labels = months;
      chartInstances.monthly.data.datasets[0].data = ordersData;
      chartInstances.monthly.data.datasets[1].data = gmvData;
      chartInstances.monthly.data.datasets[1].backgroundColor = backgroundColors;
      chartInstances.monthly.update();
      return;
    }

    chartInstances.monthly = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: months,
        datasets: [
          {
            type: 'line',
            label: 'Orders Count',
            data: ordersData,
            yAxisID: 'y1',
            borderColor: '#06b6d4',
            backgroundColor: '#06b6d4',
            borderWidth: 2.5,
            tension: 0.3,
            pointRadius: 3,
            pointHoverRadius: 6
          },
          {
            type: 'bar',
            label: 'GMV (BRL)',
            data: gmvData,
            yAxisID: 'y',
            backgroundColor: backgroundColors,
            borderRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        onClick: (evt, elements) => {
          if (elements && elements.length > 0) {
            const idx = elements[0].index;
            const clickedMonth = currentMonthKeys[idx];
            if (state.filters.yearMonth === clickedMonth) {
              setFilter('yearMonth', 'ALL');
            } else {
              setFilter('yearMonth', clickedMonth);
            }
          }
        },
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: {
            position: 'top',
            labels: { color: colors.textPrimary, usePointStyle: true, boxWidth: 8 }
          },
          tooltip: {
            callbacks: {
              label: ctx => ctx.dataset.yAxisID === 'y' ? ` GMV: ${formatBRL(ctx.raw)}` : ` Orders: ${formatNumber(ctx.raw)}`
            }
          }
        },
        scales: {
          x: {
            grid: { color: colors.gridColor },
            ticks: { color: colors.textSecondary, maxRotation: 45 }
          },
          y: {
            type: 'linear',
            position: 'left',
            grid: { color: colors.gridColor },
            ticks: {
              color: colors.textSecondary,
              callback: v => formatBRLShort(v)
            }
          },
          y1: {
            type: 'linear',
            position: 'right',
            grid: { drawOnChartArea: false },
            ticks: {
              color: '#06b6d4',
              callback: v => formatNumber(v)
            }
          }
        }
      }
    });
  }

  /* ==========================================================================
     Chart 2: Top Categories by GMV (with Click-to-Filter)
     ========================================================================== */
  function renderOverviewCategoriesChart(matchedRows, isFiltered) {
    const ctx = document.getElementById('chartOverviewCategories');
    if (!ctx) return;
    const colors = getThemeColors();

    const catTotals = {};
    if (!isFiltered) {
      data.top_categories.slice(0, 10).forEach(c => {
        catTotals[c.category] = c.gmv;
      });
    } else {
      matchedRows.forEach(r => {
        catTotals[r.cat] = (catTotals[r.cat] || 0) + r.gmv;
      });
    }

    const sortedCats = Object.keys(catTotals).sort((a, b) => catTotals[b] - catTotals[a]).slice(0, 10);
    currentCategoryKeys = sortedCats;
    const labels = sortedCats.map(c => cleanCategory(c));
    const gmvVals = sortedCats.map(c => catTotals[c]);

    const bgColors = sortedCats.map(c => {
      if (state.filters.category === c) return '#f59e0b'; // Gold highlight
      if (state.filters.category !== 'ALL') return 'rgba(99, 102, 241, 0.2)'; // Dim others
      return '#6366f1';
    });

    if (chartInstances.categories) {
      chartInstances.categories.data.labels = labels;
      chartInstances.categories.data.datasets[0].data = gmvVals;
      chartInstances.categories.data.datasets[0].backgroundColor = bgColors;
      chartInstances.categories.update();
      return;
    }

    chartInstances.categories = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'GMV (BRL)',
          data: gmvVals,
          backgroundColor: bgColors,
          borderRadius: 5
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        onClick: (evt, elements) => {
          if (elements && elements.length > 0) {
            const idx = elements[0].index;
            const clickedCat = currentCategoryKeys[idx];
            if (state.filters.category === clickedCat) {
              setFilter('category', 'ALL');
            } else {
              setFilter('category', clickedCat);
            }
          }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: ctx => ` GMV: ${formatBRL(ctx.raw)} (Click to filter)`
            }
          }
        },
        scales: {
          x: {
            grid: { color: colors.gridColor },
            ticks: {
              color: colors.textSecondary,
              callback: v => formatBRLShort(v)
            }
          },
          y: {
            grid: { display: false },
            ticks: { color: colors.textPrimary }
          }
        }
      }
    });
  }

  /* ==========================================================================
     Chart 3: Macro-Region Distribution (with Click-to-Filter)
     ========================================================================== */
  function renderOverviewRegionsChart(matchedRows, isFiltered) {
    const ctx = document.getElementById('chartOverviewRegions');
    if (!ctx) return;
    const colors = getThemeColors();

    const regTotals = {};
    const defaultRegions = ['Southeast', 'South', 'Northeast', 'Central-West', 'North'];
    defaultRegions.forEach(r => { regTotals[r] = 0; });

    if (!isFiltered) {
      data.regional_logistics.forEach(r => {
        regTotals[r.macro_region] = (regTotals[r.macro_region] || 0) + r.orders;
      });
    } else {
      matchedRows.forEach(r => {
        if (regTotals[r.reg] !== undefined) {
          regTotals[r.reg] += r.ord;
        }
      });
    }

    const regLabels = defaultRegions;
    currentRegionKeys = regLabels;
    const regCounts = regLabels.map(r => regTotals[r]);

    const palette = ['#6366f1', '#06b6d4', '#10b981', '#f59e0b', '#ec4899'];
    const bgColors = regLabels.map((r, i) => {
      if (state.filters.macroRegion === r) return '#f59e0b'; // Gold highlight
      if (state.filters.macroRegion !== 'ALL') return 'rgba(100, 116, 139, 0.2)'; // Dim others
      return palette[i % palette.length];
    });

    if (chartInstances.regions) {
      chartInstances.regions.data.labels = regLabels;
      chartInstances.regions.data.datasets[0].data = regCounts;
      chartInstances.regions.data.datasets[0].backgroundColor = bgColors;
      chartInstances.regions.update();
      return;
    }

    chartInstances.regions = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: regLabels,
        datasets: [{
          data: regCounts,
          backgroundColor: bgColors,
          borderWidth: 2,
          borderColor: colors.cardBg
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        onClick: (evt, elements) => {
          if (elements && elements.length > 0) {
            const idx = elements[0].index;
            const clickedReg = currentRegionKeys[idx];
            if (state.filters.macroRegion === clickedReg) {
              setFilter('macroRegion', 'ALL');
            } else {
              setFilter('macroRegion', clickedReg);
            }
          }
        },
        plugins: {
          legend: {
            position: 'right',
            labels: { color: colors.textPrimary, usePointStyle: true, boxWidth: 10 }
          },
          tooltip: {
            callbacks: {
              label: ctx => ` ${ctx.label}: ${formatNumber(ctx.raw)} orders (Click to filter)`
            }
          }
        },
        cutout: '62%'
      }
    });
  }

  /* ==========================================================================
     Chart 4: GMV vs Freight Volume (Sales & Revenue Page)
     ========================================================================== */
  function renderSalesGmvFreightChart(matchedRows, isFiltered) {
    const ctx = document.getElementById('chartSalesGmvFreight');
    if (!ctx) return;
    const colors = getThemeColors();

    const monthMap = {};
    const months = data.monthly_trend.map(d => d.year_month);
    months.forEach(m => {
      monthMap[m] = { gmv: 0, frt: 0 };
    });

    if (!isFiltered) {
      data.monthly_trend.forEach(d => {
        monthMap[d.year_month] = { gmv: d.gmv, frt: d.freight };
      });
    } else {
      matchedRows.forEach(r => {
        if (monthMap[r.ym]) {
          monthMap[r.ym].gmv += r.gmv;
          monthMap[r.ym].frt += r.frt;
        }
      });
    }

    const gmvVals = months.map(m => monthMap[m].gmv);
    const frtVals = months.map(m => monthMap[m].frt);

    if (chartInstances.salesGmvFreight) {
      chartInstances.salesGmvFreight.data.labels = months;
      chartInstances.salesGmvFreight.data.datasets[0].data = gmvVals;
      chartInstances.salesGmvFreight.data.datasets[1].data = frtVals;
      chartInstances.salesGmvFreight.update();
      return;
    }

    chartInstances.salesGmvFreight = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: months,
        datasets: [
          {
            label: 'Product GMV (BRL)',
            data: gmvVals,
            backgroundColor: 'rgba(99, 102, 241, 0.85)',
            borderRadius: 4
          },
          {
            label: 'Freight Collected (BRL)',
            data: frtVals,
            backgroundColor: 'rgba(6, 182, 212, 0.85)',
            borderRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: { color: colors.textPrimary, usePointStyle: true, boxWidth: 8 }
          },
          tooltip: {
            callbacks: {
              label: ctx => ` ${ctx.dataset.label}: ${formatBRL(ctx.raw)}`
            }
          }
        },
        scales: {
          x: {
            grid: { color: colors.gridColor },
            ticks: { color: colors.textSecondary }
          },
          y: {
            grid: { color: colors.gridColor },
            ticks: {
              color: colors.textSecondary,
              callback: v => formatBRLShort(v)
            }
          }
        }
      }
    });
  }

  /* ==========================================================================
     Monthly Sales Table Rendering (Dynamic)
     ========================================================================== */
  function renderMonthlySalesTable(matchedRows, isFiltered) {
    const tbody = document.querySelector('#tableMonthlySales tbody');
    if (!tbody) return;

    if (!isFiltered) {
      tbody.innerHTML = data.monthly_trend.map(row => `
        <tr>
          <td class="mono"><strong>${row.year_month}</strong></td>
          <td class="num">${formatNumber(row.orders)}</td>
          <td class="num">${formatNumber(row.customers)}</td>
          <td class="num font-mono">${formatBRL(row.gmv)}</td>
          <td class="num font-mono">${formatBRL(row.freight)}</td>
          <td class="num font-mono">${formatBRL(row.aov)}</td>
        </tr>
      `).join('');
    } else {
      const monthMap = {};
      matchedRows.forEach(r => {
        if (!monthMap[r.ym]) {
          monthMap[r.ym] = { ym: r.ym, orders: 0, gmv: 0, frt: 0 };
        }
        monthMap[r.ym].orders += r.ord;
        monthMap[r.ym].gmv += r.gmv;
        monthMap[r.ym].frt += r.frt;
      });

      const sortedMonths = Object.keys(monthMap).sort();
      tbody.innerHTML = sortedMonths.map(m => {
        const row = monthMap[m];
        const aov = row.orders > 0 ? row.gmv / row.orders : 0;
        return `
          <tr>
            <td class="mono"><strong>${row.ym}</strong></td>
            <td class="num">${formatNumber(row.orders)}</td>
            <td class="num">—</td>
            <td class="num font-mono">${formatBRL(row.gmv)}</td>
            <td class="num font-mono">${formatBRL(row.frt)}</td>
            <td class="num font-mono">${formatBRL(aov)}</td>
          </tr>
        `;
      }).join('');
    }
  }

  /* ==========================================================================
     Dynamic Executive Key Takeaways
     ========================================================================== */
  function renderDynamicTakeaways(gmv, orders, onTimePct, csat, isFiltered) {
    const container = document.getElementById('executiveTakeawaysList');
    if (!container) return;

    if (!isFiltered) {
      container.innerHTML = `
        <div class="takeaway-item">
          <span class="badge blue">Growth</span>
          <p>Marketplace scaled from R$ 120k/mo in Jan 2017 to over R$ 1.0M/mo by mid-2018, stabilizing at ~6,500 monthly orders.</p>
        </div>
        <div class="takeaway-item">
          <span class="badge amber">Operations</span>
          <p>Promised delivery dates include a conservative ~12-day buffer (24.5d promised vs 12.5d actual), maintaining on-time delivery at 92.1%.</p>
        </div>
        <div class="takeaway-item">
          <span class="badge red">Retention</span>
          <p>Repeat purchase rate sits at 3.12%, highlighting a reliance on top-of-funnel customer acquisition rather than repeat engagement.</p>
        </div>
      `;
    } else {
      const activeDesc = [];
      if (state.filters.category !== 'ALL') activeDesc.push(`Category: <strong>${cleanCategory(state.filters.category)}</strong>`);
      if (state.filters.macroRegion !== 'ALL') activeDesc.push(`Region: <strong>${state.filters.macroRegion}</strong>`);
      if (state.filters.yearMonth !== 'ALL') activeDesc.push(`Month: <strong>${state.filters.yearMonth}</strong>`);

      container.innerHTML = `
        <div class="takeaway-item">
          <span class="badge green">Drilldown Active</span>
          <p>Filtered slice (${activeDesc.join(' | ')}): Generated <strong>${formatBRL(gmv)}</strong> across <strong>${formatNumber(orders)}</strong> orders with an AOV of <strong>${formatBRL(orders > 0 ? gmv / orders : 0)}</strong>.</p>
        </div>
        <div class="takeaway-item">
          <span class="badge ${onTimePct >= 90 ? 'blue' : 'amber'}">SLA Performance</span>
          <p>Fulfillment for this specific segment attained an on-time delivery rate of <strong>${formatPct(onTimePct)}</strong>.</p>
        </div>
        <div class="takeaway-item">
          <span class="badge ${csat >= 4.0 ? 'blue' : 'red'}">Customer CSAT</span>
          <p>Buyers awarded an average satisfaction rating of <strong>${csat.toFixed(2)} ★</strong> for this segment.</p>
        </div>
      `;
    }
  }

  /* ==========================================================================
     Static Pages & Visuals (Cohorts, RFM, Sellers, Logistics, Products)
     ========================================================================== */
  function renderStaticPages() {
    renderCohortHeatmap();
    renderRfmVisuals();
    renderTopSellersTable();
    renderRegionalLogisticsTable();
    renderTopProductsTable();
    renderPaymentSplitChart();
  }

  function renderPaymentSplitChart() {
    const ctx = document.getElementById('chartSalesPaymentTypes');
    if (!ctx || !data.payment_splits) return;
    const colors = getThemeColors();

    const pLabels = data.payment_splits.map(p => cleanCategory(p.payment_type));
    const pValues = data.payment_splits.map(p => p.total_value);

    chartInstances.paymentTypes = new Chart(ctx, {
      type: 'pie',
      data: {
        labels: pLabels,
        datasets: [{
          data: pValues,
          backgroundColor: ['#6366f1', '#06b6d4', '#10b981', '#f59e0b', '#8b5cf6'],
          borderWidth: 2,
          borderColor: colors.cardBg
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'right',
            labels: { color: colors.textPrimary, usePointStyle: true, boxWidth: 10 }
          },
          tooltip: {
            callbacks: {
              label: ctx => ` ${ctx.label}: ${formatBRL(ctx.raw)}`
            }
          }
        }
      }
    });
  }

  function renderCohortHeatmap() {
    const tableBody = document.querySelector('#cohortHeatmapTable tbody');
    if (!tableBody || !data.cohort_matrix) return;

    const cohortsMap = {};
    data.cohort_matrix.forEach(row => {
      if (!cohortsMap[row.cohort]) {
        cohortsMap[row.cohort] = {
          cohort: row.cohort,
          size: row.cohort_size,
          months: {}
        };
      }
      cohortsMap[row.cohort].months[row.month_number] = row.retention_rate_pct;
    });

    const sortedCohorts = Object.keys(cohortsMap).sort();
    tableBody.innerHTML = '';

    sortedCohorts.forEach(cohortKey => {
      const c = cohortsMap[cohortKey];
      const tr = document.createElement('tr');

      let rowHtml = `<td>${c.cohort}</td><td>${formatNumber(c.size)}</td>`;

      for (let m = 0; m <= 12; m++) {
        const ret = c.months[m];
        if (ret === undefined || ret === null) {
          rowHtml += `<td class="cohort-cell" style="color: var(--text-muted); opacity: 0.25;">—</td>`;
        } else if (m === 0) {
          rowHtml += `<td class="cohort-cell" style="background: rgba(99, 102, 241, 0.35); font-weight: 600;">100%</td>`;
        } else {
          const opacity = Math.min(1, Math.max(0.12, (ret / 1.0)));
          const bgColor = `rgba(16, 185, 129, ${opacity * 0.45})`;
          const textColor = ret > 0.5 ? '#10b981' : 'var(--text-primary)';
          rowHtml += `<td class="cohort-cell" style="background: ${bgColor}; color: ${textColor};" title="Month ${m}: ${ret.toFixed(2)}%">${ret.toFixed(2)}%</td>`;
        }
      }

      tr.innerHTML = rowHtml;
      tableBody.appendChild(tr);
    });
  }

  function renderRfmVisuals() {
    // RFM Spend Chart
    const ctx = document.getElementById('chartRfmSpend');
    if (ctx && data.rfm_segments) {
      const colors = getThemeColors();
      const rLabels = data.rfm_segments.map(r => r.segment);
      const rSpend = data.rfm_segments.map(r => r.total_spend);

      chartInstances.rfmSpend = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: rLabels,
          datasets: [{
            label: 'Total Platform Spend (BRL)',
            data: rSpend,
            backgroundColor: [
              '#10b981', '#3b82f6', '#6366f1', '#f59e0b', '#ef4444', '#64748b'
            ],
            borderRadius: 5
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: ctx => ` Spend: ${formatBRL(ctx.raw)}`
              }
            }
          },
          scales: {
            x: {
              grid: { color: colors.gridColor },
              ticks: {
                color: colors.textSecondary,
                callback: v => formatBRLShort(v)
              }
            },
            y: {
              grid: { display: false },
              ticks: { color: colors.textPrimary }
            }
          }
        }
      });
    }

    // RFM Table
    const tbodyRfm = document.querySelector('#tableRfmDetails tbody');
    if (tbodyRfm && data.rfm_segments) {
      tbodyRfm.innerHTML = data.rfm_segments.map(row => `
        <tr>
          <td><strong>${row.segment}</strong></td>
          <td class="num">${formatNumber(row.customer_count)}</td>
          <td class="num font-mono">${formatBRL(row.total_spend)}</td>
          <td class="num font-mono">${formatBRL(row.avg_clv)}</td>
          <td class="num">${Math.round(row.avg_recency_days)} days</td>
        </tr>
      `).join('');
    }
  }

  function renderTopSellersTable() {
    const tbody = document.querySelector('#tableTopSellers tbody');
    if (tbody && data.top_sellers) {
      tbody.innerHTML = data.top_sellers.map(s => `
        <tr>
          <td class="num"><strong>#${s.revenue_rank}</strong></td>
          <td><span class="id-badge" title="${s.seller_id}">${truncateId(s.seller_id)}</span></td>
          <td>${s.seller_city.toUpperCase()}, ${s.seller_state}</td>
          <td><span class="badge ${s.seller_revenue_tier.includes('Tier 1') ? 'blue' : 'green'}">${s.seller_revenue_tier.split(' - ')[0]}</span></td>
          <td class="num font-mono"><strong>${formatBRL(s.lifetime_revenue)}</strong></td>
          <td class="num">${formatNumber(s.lifetime_orders_count)}</td>
          <td class="num"><span class="${s.on_time_rate_pct >= 90 ? 'positive' : 'negative'}">${s.on_time_rate_pct.toFixed(1)}%</span></td>
          <td class="num">${s.average_delivery_days.toFixed(1)} d</td>
          <td class="num font-mono" style="color: #f59e0b;">${s.average_review_score.toFixed(2)} ★</td>
        </tr>
      `).join('');
    }
  }

  function renderRegionalLogisticsTable() {
    const tbody = document.querySelector('#tableRegionalLogistics tbody');
    if (tbody && data.regional_logistics) {
      tbody.innerHTML = data.regional_logistics.map(r => `
        <tr>
          <td><span class="badge blue">${r.macro_region}</span></td>
          <td class="mono"><strong>${r.state}</strong></td>
          <td class="num">${formatNumber(r.orders)}</td>
          <td class="num">${r.avg_delivery_days.toFixed(1)} d</td>
          <td class="num">${r.promised_delivery_days.toFixed(1)} d</td>
          <td class="num" style="color: var(--success); font-weight: 500;">${r.on_time_pct.toFixed(1)}%</td>
          <td class="num" style="color: ${r.late_pct > 10 ? 'var(--danger)' : 'var(--text-secondary)'};">${r.late_pct.toFixed(1)}%</td>
          <td class="num font-mono">${formatBRL(r.avg_freight)}</td>
        </tr>
      `).join('');
    }
  }

  function renderTopProductsTable() {
    const tbody = document.querySelector('#tableTopProducts tbody');
    if (tbody && data.top_products) {
      tbody.innerHTML = data.top_products.map(p => `
        <tr>
          <td class="num"><strong>#${p.rank}</strong></td>
          <td><span class="id-badge" title="${p.product_id}">${truncateId(p.product_id)}</span></td>
          <td>${cleanCategory(p.category)}</td>
          <td><span class="badge ${p.size_tier.includes('Standard') ? 'blue' : 'amber'}">${p.size_tier}</span></td>
          <td class="num">${formatNumber(p.lifetime_units_sold)}</td>
          <td class="num font-mono"><strong>${formatBRL(p.lifetime_revenue)}</strong></td>
          <td class="num font-mono">${formatBRL(p.average_unit_price)}</td>
          <td class="num font-mono" style="color: #f59e0b;">${p.average_review_score.toFixed(2)} ★</td>
          <td class="num font-mono" style="color: var(--primary-light); font-weight: 600;">${(p.cumulative_revenue_pct).toFixed(2)}%</td>
        </tr>
      `).join('');
    }
  }
});
