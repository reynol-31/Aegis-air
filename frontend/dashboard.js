const BACKEND_URL = "http://127.0.0.1:5000"; // backend

async function refresh(){
  // UI elements
  const d = document.getElementById('denylist')
  const incCont = document.getElementById('incidents')
  const logsPre = document.getElementById('logs')
  const statReq = document.getElementById('stat-req')
  const statBlock = document.getElementById('stat-block')
  const statInc = document.getElementById('stat-incs')

  d.innerHTML = ''; incCont.innerHTML=''; logsPre.textContent='Loading...'
  statReq.textContent = '—'; statBlock.textContent = '—'; statInc.textContent = '—'

  try {
    const logsRes = await fetch(`${BACKEND_URL}/logs_tail`)
    const logsTxt = await logsRes.text()
    logsPre.textContent = logsTxt || '(no logs)'
    const lines = logsTxt.split('\n').filter(l=>l.trim()); statReq.textContent = lines.length
  } catch (e) {
    logsPre.textContent = 'Failed to load logs: ' + e.message
  }

  try {
    const res2 = await fetch(`${BACKEND_URL}/incidents`)
    const inc = await res2.json()
    if (inc && inc.length) {
      incCont.innerHTML = ''
      inc.slice(-10).reverse().forEach(i=>{
        const el = document.createElement('div')
        el.className = 'incident'
        el.innerHTML = `<div style="width:8px;height:8px;border-radius:6px;background:#ef4444;margin-top:6px"></div>
                        <div><div class="text">${i}</div><div class="meta">${new Date().toLocaleString()}</div></div>`
        incCont.appendChild(el)
      })
      statInc.textContent = inc.length
    } else {
      incCont.innerHTML = '<div class="small">(no incidents)</div>'
      statInc.textContent = 0
    }
  } catch (e) {
    incCont.innerHTML = `<div class="small">Failed to load incidents: ${e.message}</div>`
  }

  try {
    const res3 = await fetch(`${BACKEND_URL}/denylist`)
    const deny = await res3.json()
    d.innerHTML = ''
    if (!deny || deny.length === 0) d.innerHTML = '<li>(none)</li>'
    else deny.forEach(ip => {
      const li = document.createElement('li'); li.textContent = ip; d.appendChild(li)
    })
    statBlock.textContent = (deny||[]).length
  } catch (e) {
    d.innerHTML = `<li>Failed to load denylist: ${e.message}</li>`
  }
}

function openDemo(){ window.open('http://127.0.0.1:8000/static/index.html', '_blank') }

// simple remote simulate actions by calling dummy webapp endpoints
async function simulate(kind){
  const base = "http://127.0.0.1:8000"
  try {
    if (kind === 'page') await fetch(`${base}/`)
    if (kind === 'api') await fetch(`${base}/api/data`)
    if (kind === 'login-ok') await fetch(`${base}/login`, {method:'POST', body: new URLSearchParams({user:'alice', pass:'wonderland'})})
    if (kind === 'login-fail') await fetch(`${base}/login`, {method:'POST', body: new URLSearchParams({user:'admin', pass:'wrong'})})
    if (kind === 'admin') await fetch(`${base}/admin`)
  } catch (e) {
    console.warn('simulate error', e)
  }
  // refresh dashboard after small delay
  setTimeout(refresh, 600)
}

async function runAttack(){
  // call backend endpoint to run attack if you implemented it; otherwise call local script
  // fallback: trigger a burst of client calls
  for (let i=0;i<8;i++){
    simulate('page'); simulate('login-fail'); simulate('api');
  }
  setTimeout(refresh, 800)
}

setInterval(refresh, 10000)
refresh()
