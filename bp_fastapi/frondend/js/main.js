const API_BASE = "http://127.0.0.1:8000";

const form = document.getElementById('bpForm');
const resultDiv = document.getElementById('result');
const readingP = document.getElementById('reading');
const categoryP = document.getElementById('category');
const historyDiv = document.getElementById('history');

async function fetchHistory() {
  const res = await fetch(`${API_BASE}/api/history?limit=20`);
  if (!res.ok) {
    historyDiv.innerHTML = '<p class="small">Could not load history.</p>';
    return;
  }
  const rows = await res.json();
  if (!rows.length) {
    historyDiv.innerHTML = '<p class="small">No saved readings yet.</p>';
    return;
  }
  historyDiv.innerHTML = '';
  rows.forEach(r => {
    const div = document.createElement('div');
    div.className = 'history-item';
    const left = document.createElement('div');
    left.innerHTML = `<strong>${r.systolic}/${r.diastolic} mm Hg</strong><div class="small">${new Date(r.created_at).toLocaleString()} • ${r.category}</div>`;
    const right = document.createElement('div');
    const delBtn = document.createElement('button');
    delBtn.textContent = 'Delete';
    delBtn.onclick = async () => {
      await fetch(`${API_BASE}/api/history/${r.id}`, { method: 'DELETE' });
      fetchHistory();
    };
    right.appendChild(delBtn);
    div.appendChild(left);
    div.appendChild(right);
    historyDiv.appendChild(div);
  });
}

form.addEventListener('submit', async (ev) => {
  ev.preventDefault();
  const systolic = Number(document.getElementById('systolic').value);
  const diastolic = Number(document.getElementById('diastolic').value);

  if (!systolic || !diastolic) return alert('Enter both values');
  if (systolic <= diastolic) return alert('Systolic must be greater than diastolic.');

  const payload = { systolic, diastolic };
  const res = await fetch(`${API_BASE}/api/calculate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    const err = await res.json().catch(()=>({detail:res.statusText}));
    return alert('Error: ' + (err.detail || res.statusText));
  }

  const data = await res.json();
  readingP.textContent = `${data.systolic}/${data.diastolic} mm Hg`;
  categoryP.textContent = data.category;
  resultDiv.classList.remove('hidden');
  document.getElementById('systolic').value = '';
  document.getElementById('diastolic').value = '';
  fetchHistory();
});

fetchHistory();
