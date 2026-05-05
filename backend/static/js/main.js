/**
 * Skill2Hire — Frontend Logic
 * Handles: Predict form, Insights tab, Chart rendering
 */

'use strict';

// ── Chart instances ──────────────────────────────────────
let modelChart   = null;
let branchChart  = null;
let cgpaChart    = null;

// ── Utilities ────────────────────────────────────────────
function $(id) { return document.getElementById(id); }

function showEl(id)  { $(id).hidden = false; }
function hideEl(id)  { $(id).hidden = true; }
function setText(id, val) { $(id).textContent = val; }

function setLoading(on) {
  $('submit-btn').disabled = on;
  $('btn-text').textContent = on ? 'Predicting…' : 'Predict Placement';
  $('btn-spinner').hidden = !on;
}

// ── Tab switching ────────────────────────────────────────
function switchTab(tab) {
  const tabs   = document.querySelectorAll('.tab');
  const panels = document.querySelectorAll('[role="tabpanel"]');

  tabs.forEach(t => {
    t.classList.toggle('active', t.id === `tab-${tab}`);
    t.setAttribute('aria-selected', t.id === `tab-${tab}`);
  });

  panels.forEach(p => {
    p.hidden = p.id !== `panel-${tab}`;
  });

  if (tab === 'insights') loadInsights();
}

// Expose globally (used by onclick in HTML)
window.switchTab  = switchTab;
window.loadInsights = loadInsights;

// ── Predict Form ─────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  $('predict-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    hideEl('form-errors');
    hideEl('results');

    const form = e.target;
    const payload = {
      name:                  form.name.value.trim(),
      cgpa:                  parseFloat(form.cgpa.value),
      aptitude_score:        parseInt(form.aptitude_score.value, 10),
      programming_skills:    parseInt(form.programming_skills.value, 10),
      communication_skills:  parseInt(form.communication_skills.value, 10),
      num_projects:          parseInt(form.num_projects.value, 10),
      internship_experience: form.internship_experience.checked ? 1 : 0,
      certifications_count:  parseInt(form.certifications_count.value, 10),
      branch:                form.branch.value,
      job_description:       $('job_description').value.trim(),
    };

    setLoading(true);
    try {
      const res = await fetch('/api/predict', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(payload),
      });

      const data = await res.json();

      if (!res.ok) {
        showErrors(data.errors || [data.error || 'Prediction failed.']);
        return;
      }

      renderResults(data);
    } catch (err) {
      showErrors(['Network error — is the server running?']);
    } finally {
      setLoading(false);
    }
  });
});

// ── Render Results ────────────────────────────────────────
function renderResults(data) {
  // Big probability number
  const prob = data.placement_probability;
  setText('placement-prob', `${prob}%`);
  setText('confidence-score', `Model confidence: ${data.confidence}%`);

  // Model comparison chart
  renderModelChart(data.model_predictions || {});

  // Skill tags
  const tags = $('job-skills');
  tags.innerHTML = '';
  if (data.job_skills_found && data.job_skills_found.length) {
    data.job_skills_found.forEach(skill => {
      const span = document.createElement('span');
      span.className = 'skill-tag';
      span.textContent = skill;
      tags.appendChild(span);
    });
  } else {
    tags.innerHTML = '<span style="color:var(--text-muted);font-size:.85rem">No job description provided.</span>';
  }

  // Suggestions list
  const ul = $('suggestions-list');
  ul.innerHTML = '';
  (data.skill_gap_suggestions || []).forEach(s => {
    const li = document.createElement('li');
    li.textContent = s;
    ul.appendChild(li);
  });

  showEl('results');
  $('results').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ── Model Chart ───────────────────────────────────────────
function renderModelChart(predictions) {
  const labels = Object.keys(predictions).map(k =>
    k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
  );
  const values = Object.values(predictions);

  if (modelChart) modelChart.destroy();
  const ctx = $('model-chart').getContext('2d');
  modelChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Placement Probability (%)',
        data: values,
        backgroundColor: values.map(v =>
          v >= 70 ? 'rgba(16,185,129,0.75)' :
          v >= 50 ? 'rgba(99,102,241,0.75)' :
                   'rgba(239,68,68,0.75)'
        ),
        borderColor: values.map(v =>
          v >= 70 ? '#10b981' : v >= 50 ? '#6366f1' : '#ef4444'
        ),
        borderWidth: 1.5,
        borderRadius: 8,
      }],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: { label: ctx => `${ctx.parsed.y.toFixed(1)}%` },
        },
      },
      scales: {
        x: {
          ticks: { color: '#94a3b8', font: { size: 11 } },
          grid:  { color: 'rgba(255,255,255,0.05)' },
        },
        y: {
          min: 0, max: 100,
          ticks: { color: '#94a3b8', callback: v => `${v}%` },
          grid:  { color: 'rgba(255,255,255,0.05)' },
        },
      },
    },
  });
}

// ── Insights ──────────────────────────────────────────────
async function loadInsights() {
  hideEl('insights-error');
  hideEl('insights-content');

  try {
    const res  = await fetch('/api/insights');
    const data = await res.json();

    if (!res.ok) {
      showInsightsError(data.error || 'Failed to load insights.');
      return;
    }

    setText('stat-total',          data.total_students.toLocaleString());
    setText('stat-placement-rate', `${data.overall_placement_rate}%`);
    setText('stat-avg-cgpa',       data.avg_cgpa.toFixed(2));
    setText('stat-internship-rate',`${data.internship_placement_rate}%`);

    renderBranchChart(data.placement_by_branch || []);
    renderCgpaChart(data.avg_cgpa_placed, data.avg_cgpa_not_placed);

    showEl('insights-content');
  } catch (err) {
    showInsightsError('Network error — is the server running?');
  }
}

function renderBranchChart(branches) {
  const labels = branches.map(b => b.branch);
  const values = branches.map(b => b.placement_rate);

  if (branchChart) branchChart.destroy();
  const ctx = $('branch-chart').getContext('2d');
  branchChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Placement Rate (%)',
        data: values,
        backgroundColor: 'rgba(99,102,241,0.65)',
        borderColor: '#6366f1',
        borderWidth: 1.5,
        borderRadius: 8,
      }],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
        y: {
          min: 0, max: 100,
          ticks: { color: '#94a3b8', callback: v => `${v}%` },
          grid: { color: 'rgba(255,255,255,0.05)' },
        },
      },
    },
  });
}

function renderCgpaChart(placed, notPlaced) {
  if (cgpaChart) cgpaChart.destroy();
  const ctx = $('cgpa-chart').getContext('2d');
  cgpaChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Placed', 'Not Placed'],
      datasets: [{
        label: 'Average CGPA',
        data: [placed, notPlaced],
        backgroundColor: ['rgba(16,185,129,0.7)', 'rgba(239,68,68,0.7)'],
        borderColor:     ['#10b981', '#ef4444'],
        borderWidth: 1.5,
        borderRadius: 10,
      }],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
        y: {
          min: 0, max: 10,
          ticks: { color: '#94a3b8' },
          grid: { color: 'rgba(255,255,255,0.05)' },
        },
      },
    },
  });
}

// ── Error Helpers ─────────────────────────────────────────
function showErrors(errors) {
  const box = $('form-errors');
  box.innerHTML = errors.map(e => `<div>⚠ ${e}</div>`).join('');
  showEl('form-errors');
}

function showInsightsError(msg) {
  const box = $('insights-error');
  box.textContent = `⚠ ${msg}`;
  showEl('insights-error');
}
