const symptoms = ['fever','cough','sore_throat','nasal_congestion','headache','body_pain','chills','nausea','vomiting','diarrhea','abdominal_pain','burning_urination','frequent_urination','fatigue','rash','joint_pain','bleeding_gums','retro_orbital_pain'];

const form = document.getElementById('symptomForm');
const list = document.getElementById('symptomList');
const result = document.getElementById('result');
const resetBtn = document.getElementById('resetBtn');

symptoms.forEach(sym => {
  const label = document.createElement('label');
  label.innerHTML = `<input type='checkbox' name='${sym}'> ${sym.replace('_',' ')}`;
  list.appendChild(label);
});

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const checked = document.querySelectorAll('input[type="checkbox"]:checked');
  const data = {};
  checked.forEach(c => data[c.name] = 1);

  const res = await fetch('/api/predict', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({symptoms: data})
  });

  const json = await res.json();
  result.innerHTML = `<h3>Predicted Disease: ${json.prediction}</h3>`;
});

resetBtn.addEventListener('click', () => {
  document.querySelectorAll('input[type="checkbox"]').forEach(c => c.checked = false);
  result.innerHTML = '';
});