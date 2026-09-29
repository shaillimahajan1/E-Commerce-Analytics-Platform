/**
 * E-COMMERCE ANALYTICS PLATFORM — EXECUTIVE BI DASHBOARD
 * Core Application Logic, Dynamic Chart.js Rendering, & Interactive Controls
 */

document.addEventListener('DOMContentLoaded', () => {
  const data = window.DASHBOARD_DATA;
  if (!data) {
    console.error('Fatal: window.DASHBOARD_DATA is missing or failed to load.');
    return;
  }

  // State
  let currentTheme = localStorage.getItem('dashboard_theme') || 'dark';
  const chartInstances = {};

  // Setup Application
  initTheme();
  initNavigation();
  renderAllCharts();
  renderAllTables();
  renderCohortHeatmap();

  /* ==========================================================================
     Theme Management (Dark / Light)
     ========================================================================== */
  function initTheme() {
    document.body.setAttribute('data-theme', currentTheme);
    const themeBtn = document.getElementById('themeToggleBtn');
    
    if (themeBtn) {
      themeBtn.addEventListener('click', () => {
        currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.body.setAttribute('data-theme', currentTheme);
        localStorage.setItem('dashboard_theme', currentTheme);
        updateChartThemes();
      });
    }
  }

  function getThemeColors() {
    const isDark = currentTheme === 'dark';
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
          // Resize charts to prevent canvas distortion
          window.dispatchEvent(new Event('resize'));
        }
      });
    });
  }

  /* ==========================================================================
     Formatting Utilities
     ========================================================================== */
  function formatBRL(val) {
    if (val === null || val === undefined) return '—';
    return 'R$ ' + Number(val).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function formatNumber(val) {
    if (val === null || val === undefined) return '0';
    return Number(val).toLocaleString('en-US');
  }

  function formatPct(val) {
    if (val === null || val === undefined) return '—';
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
     Chart.js Initializations
     ========================================================================== */
  function renderAllCharts() {
    const colors = getThemeColors();

    // Chart.js Global Default Settings
    Chart.defaults.font.family = colors.fontFamily;
    Chart.defaults.color = colors.textSecondary;

    // --- Chart 1: Monthly GMV & Orders Trajectory (Executive Overview) ---
    const ctxMonthly = document.getElementById('chartOverviewMonthly');
    if (ctxMonthly && data.monthly_trend) {
      const labels = data.monthly_trend.map(d => d.year_month);
      const gmvData = data.monthly_trend.map(d => d.gmv);
      const ordersData = data.monthly_trend.map(d => d.orders);

      chartInstances.monthly = new Chart(ctxMonthly, {
        type: 'bar',
        data: {
          labels: labels,
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
              label: 'Gross Merchandise Value (BRL)',
              data: gmvData,
              yAxisID: 'y',
              backgroundColor: 'rgba(99, 102, 241, 0.75)',
              hoverBackgroundColor: 'rgba(99, 102, 241, 0.95)',
              borderRadius: 4
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: { mode: 'index', intersect: false },
          plugins: {
            legend: {
              position: 'top',
              labels: { color: colors.textPrimary, usePointStyle: true, boxWidth: 8 }
            },
            tooltip: {
              callbacks: {
                label: function (ctx) {
                  if (ctx.dataset.yAxisID === 'y') {
                    return ` GMV: ${formatBRL(ctx.raw)}`;
                  }
                  return ` Orders: ${formatNumber(ctx.raw)}`;
                }
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
              display: true,
              position: 'left',
              grid: { color: colors.gridColor },
              ticks: {
                color: colors.textSecondary,
                callback: v => 'R$ ' + (v >= 1e6 ? (v / 1e6).toFixed(1) + 'M' : (v / 1e3).toFixed(0) + 'K')
              }
            },
            y1: {
              type: 'linear',
              display: true,
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

    // --- Chart 2: Top 10 Product Categories (Executive Overview) ---
    const ctxCategories = document.getElementById('chartOverviewCategories');
    if (ctxCategories && data.top_categories) {
      const top10 = data.top_categories.slice(0, 10);
      const labels = top10.map(c => cleanCategory(c.category));
      const gmvVals = top10.map(c => c.gmv);

      chartInstances.categories = new Chart(ctxCategories, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'GMV (BRL)',
            data: gmvVals,
            backgroundColor: [
              '#6366f1', '#4f46e5', '#4338ca', '#3730a3', '#06b6d4',
              '#0891b2', '#0e7490', '#10b981', '#059669', '#047857'
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
                label: ctx => ` GMV: ${formatBRL(ctx.raw)}`
              }
            }
          },
          scales: {
            x: {
              grid: { color: colors.gridColor },
              ticks: {
                color: colors.textSecondary,
                callback: v => 'R$ ' + (v >= 1e6 ? (v / 1e6).toFixed(1) + 'M' : (v / 1e3).toFixed(0) + 'K')
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

    // --- Chart 3: Brazilian Macro-Region Orders (Executive Overview) ---
    const ctxRegions = document.getElementById('chartOverviewRegions');
    if (ctxRegions && data.regional_logistics) {
      // Group by macro_region
      const regionMap = {};
      data.regional_logistics.forEach(r => {
        regionMap[r.macro_region] = (regionMap[r.macro_region] || 0) + (r.orders || 0);
      });
      const regionLabels = Object.keys(regionMap).sort((a, b) => regionMap[b] - regionMap[a]);
      const regionCounts = regionLabels.map(r => regionMap[r]);

      chartInstances.regions = new Chart(ctxRegions, {
        type: 'doughnut',
        data: {
          labels: regionLabels,
          datasets: [{
            data: regionCounts,
            backgroundColor: ['#6366f1', '#06b6d4', '#10b981', '#f59e0b', '#ec4899'],
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
                label: ctx => ` ${ctx.label}: ${formatNumber(ctx.raw)} orders`
              }
            }
          },
          cutout: '62%'
        }
      });
    }

    // --- Chart 4: GMV vs Freight Volume Over Time (Sales & Revenue) ---
    const ctxSalesGmvFreight = document.getElementById('chartSalesGmvFreight');
    if (ctxSalesGmvFreight && data.monthly_trend) {
      const labels = data.monthly_trend.map(d => d.year_month);
      const gmvVals = data.monthly_trend.map(d => d.gmv);
      const freightVals = data.monthly_trend.map(d => d.freight);

      chartInstances.salesGmvFreight = new Chart(ctxSalesGmvFreight, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Product GMV (BRL)',
              data: gmvVals,
              backgroundColor: 'rgba(99, 102, 241, 0.85)',
              borderRadius: 4
            },
            {
              label: 'Freight Collected (BRL)',
              data: freightVals,
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
              stacked: false,
              grid: { color: colors.gridColor },
              ticks: {
                color: colors.textSecondary,
                callback: v => 'R$ ' + (v >= 1e6 ? (v / 1e6).toFixed(1) + 'M' : (v / 1e3).toFixed(0) + 'K')
              }
            }
          }
        }
      });
    }

    // --- Chart 5: Payment Tender Split (Sales & Revenue) ---
    const ctxPaymentTypes = document.getElementById('chartSalesPaymentTypes');
    if (ctxPaymentTypes && data.payment_splits) {
      const pLabels = data.payment_splits.map(p => cleanCategory(p.payment_type));
      const pValues = data.payment_splits.map(p => p.total_value);

      chartInstances.paymentTypes = new Chart(ctxPaymentTypes, {
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

    // --- Chart 6: RFM Segment Spend Distribution (Customer Cohorts & RFM) ---
    const ctxRfmSpend = document.getElementById('chartRfmSpend');
    if (ctxRfmSpend && data.rfm_segments) {
      const rLabels = data.rfm_segments.map(r => r.segment);
      const rSpend = data.rfm_segments.map(r => r.total_spend);

      chartInstances.rfmSpend = new Chart(ctxRfmSpend, {
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
                callback: v => 'R$ ' + (v >= 1e6 ? (v / 1e6).toFixed(1) + 'M' : (v / 1e3).toFixed(0) + 'K')
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
  }

  /* ==========================================================================
     Cohort Retention Heatmap Rendering
     ========================================================================== */
  function renderCohortHeatmap() {
    const tableBody = document.querySelector('#cohortHeatmapTable tbody');
    if (!tableBody || !data.cohort_matrix) return;

    // Group rows by cohort
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
          // Dynamic color scale based on retention % (0.1% to 1.5%)
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

  /* ==========================================================================
     Data Table Renderers
     ========================================================================== */
  function renderAllTables() {
    // 1. Monthly Sales Table
    const tbodyMonthly = document.querySelector('#tableMonthlySales tbody');
    if (tbodyMonthly && data.monthly_trend) {
      tbodyMonthly.innerHTML = data.monthly_trend.map(row => `
        <tr>
          <td class="mono"><strong>${row.year_month}</strong></td>
          <td class="num">${formatNumber(row.orders)}</td>
          <td class="num">${formatNumber(row.customers)}</td>
          <td class="num font-mono">${formatBRL(row.gmv)}</td>
          <td class="num font-mono">${formatBRL(row.freight)}</td>
          <td class="num font-mono">${formatBRL(row.aov)}</td>
        </tr>
      `).join('');
    }

    // 2. RFM Details Table
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

    // 3. Top Sellers Table
    const tbodySellers = document.querySelector('#tableTopSellers tbody');
    if (tbodySellers && data.top_sellers) {
      tbodySellers.innerHTML = data.top_sellers.map(s => `
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

    // 4. Regional Logistics Table
    const tbodyLogistics = document.querySelector('#tableRegionalLogistics tbody');
    if (tbodyLogistics && data.regional_logistics) {
      tbodyLogistics.innerHTML = data.regional_logistics.map(r => `
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

    // 5. Top Products Table
    const tbodyProducts = document.querySelector('#tableTopProducts tbody');
    if (tbodyProducts && data.top_products) {
      tbodyProducts.innerHTML = data.top_products.map(p => `
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
