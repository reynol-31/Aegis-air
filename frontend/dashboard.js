// frontend/dashboard.js
const BACKEND_URL = "http://127.0.0.1:5000"; // change if your backend uses another host/port

async function refresh(){
  const d = document.getElementById('denylist')
  const incPre = document.getElementById('incidents')
  const logsPre = document.getElementById('logs')

  d.innerHTML = ''
  incPre.textContent = ''
  logsPre.textContent = ''

  try {
    const res1 = await fetch(`${BACKEND_URL}/denylist`)
    if (!res1.ok) throw new Error(`denylist ${res1.status}`)
    const deny = await res1.json()
    if (deny.length === 0) {
      d.innerHTML = '<li>(none)</li>'
    } else {
      deny.forEach(ip => { const li = document.createElement('li'); li.textContent = ip; d.appendChild(li) })
    }
  } catch (e) {
    d.innerHTML = `<li>Failed to load denylist: ${e.message}</li>`
  }

  try {
    const res2 = await fetch(`${BACKEND_URL}/incidents`)
    if (!res2.ok) throw new Error(`incidents ${res2.status}`)
    const inc = await res2.json()
    if (inc.length === 0) incPre.textContent = '(no incidents logged yet)'
    else incPre.textContent = inc.slice(-50).join('\n')
  } catch (e) {
    incPre.textContent = `Failed to load incidents: ${e.message}`
  }

  try {
    const res3 = await fetch(`${BACKEND_URL}/logs_tail`)
    if (!res3.ok) throw new Error(`logs_tail ${res3.status}`)
    const logs = await res3.text()
    logsPre.textContent = logs || '(no logs)'
  } catch (e) {
    logsPre.textContent = `Failed to load logs: ${e.message}`
  }
}

function openDemo(){
  window.open('http://127.0.0.1:8000', '_blank')
}

// auto-refresh every 3s
setInterval(refresh, 3000)
refresh()
