
// ══════════════════════════════════════════════════════════════════════════════

// ── IMAGEN: base64 fallback (compatible con GitHub Pages) ────────────────────



// ── PERFIL: actualizar topbar avatar ─────────────────────────────────────────


// ── PERFIL VIEW ───────────────────────────────────────────────────────────────
var _epPerfiles = [];

var renderPerfilView = function() {
  if (!CUD || !CU) return;
  updateTopbarAvatar();
  const name = CUD.name || CU.email || '—';
  const initials = name.trim().split(/\s+/).map(w=>w[0]||'').join('').slice(0,2).toUpperCase();

  const pla = $('perfil-avatar-lg');
  if (pla) {
    if (CUD.photoURL) pla.innerHTML = `<img src="${CUD.photoURL}">`;
    else pla.textContent = initials;
  }
  const pn=$('perfil-nombre'); if(pn) pn.textContent = name;
  const pe=$('perfil-email');  if(pe) pe.textContent = CU.email || '—';
  const pr=$('perfil-rol');    if(pr) pr.textContent = CUD.role  || '—';
  const pg=$('perfil-grupo');  if(pg) pg.textContent = GL(CUD.grupo) || '—';

  const piMap = {
    'pi-nombre': name,
    'pi-email' : CU.email || '—',
    'pi-rol'   : CUD.role  || '—',
    'pi-grupo' : GL(CUD.grupo) || '—',
    'pi-area'  : AL(CUD.area)  || '—',
    'pi-estado': CUD.status    || '—',
  };
  Object.entries(piMap).forEach(([id,val])=>{const el=$(id);if(el)el.textContent=val;});

  const pp=$('pi-perfiles');
  if (pp) {
    const perfs = CUD.perfilesProfesionales || [];
    pp.innerHTML = perfs.length
      ? perfs.map(p=>`<span class="tag am">${esc(p)}</span>`).join('')
      : '<span class="tg tsm">Sin perfiles asignados</span>';
  }

  const pcl=$('pi-caps-list');
  if (pcl) {
    const myCaps = allCaps.filter(c=>c.responsable===name||c.createdBy===CU.uid).slice(0,5);
    if (myCaps.length) {
      pcl.innerHTML = myCaps.map(c=>`<div style="padding:7px 0;border-bottom:1px solid var(--border)">
        <strong style="font-size:12px">${esc(c.nombre)}</strong>
        <span class="tg tsm"> · ${c.fecha||'—'}</span>
        <span class="badge ${c.actaEstado==='Aprobada'?'bd':'bp'}" style="margin-left:6px">${c.actaEstado||'Pendiente'}</span>
      </div>`).join('');
    } else {
      pcl.innerHTML = '<span class="tg tsm">No hay capacitaciones asignadas aún</span>';
    }
  }
}

window.uploadProfilePhoto = async e => {
  const file = e.target.files[0]; if (!file) return;
  const url = await uploadImage(file, 2);
  if (!url) return;
  try {
    await updateDoc(doc(db,'users',CU.uid), { photoURL:url, updatedAt:serverTimestamp() });
    CUD.photoURL = url;
    renderPerfilView();
    toast('Foto de perfil actualizada', 's');
  } catch(ex) { toast('Error: '+ex.message, 'e'); }
  e.target.value = '';
};

window.openEditPerfil = () => {
  const en=$('ep-nombre'); if(en) en.value = CUD.name || '';
  _epPerfiles = [...(CUD.perfilesProfesionales||[])];
  const pl=$('ep-perfiles-list');
  if (pl) pl.innerHTML = buildPerfilesHTML(_epPerfiles,'ep-perfiles-tags','onEpPerfilChange');
  renderPerfilesTags('ep-perfiles-tags', _epPerfiles, 'rmEpPerfil');
  $('modal-edit-perfil')?.classList.add('open');
};
window.onEpPerfilChange = cb => {
  if (cb.checked) _epPerfiles.push(cb.value);
  else _epPerfiles = _epPerfiles.filter(p=>p!==cb.value);
  renderPerfilesTags('ep-perfiles-tags', _epPerfiles, 'rmEpPerfil');
};
window.rmEpPerfil = p => {
  _epPerfiles = _epPerfiles.filter(x=>x!==p);
  const cb = document.querySelector(`#ep-perfiles-list input[value="${CSS.escape(p)}"]`);
  if (cb) cb.checked = false;
  renderPerfilesTags('ep-perfiles-tags', _epPerfiles, 'rmEpPerfil');
};
window.saveEditPerfil = async () => {
  const name = $('ep-nombre')?.value.trim();
  if (!name) { toast('El nombre es obligatorio','e'); return; }
  try {
    await updateDoc(doc(db,'users',CU.uid), {
      name, perfilesProfesionales:_epPerfiles, updatedAt:serverTimestamp()
    });
    CUD.name = name; CUD.perfilesProfesionales = _epPerfiles;
    const un=$('un'); if(un) un.textContent = name;
    renderPerfilView();
    toast('Perfil actualizado', 's');
    closeModal('modal-edit-perfil');
  } catch(e) { toast('Error: '+e.message, 'e'); }
};

// ── CAMBIAR CONTRASEÑA ────────────────────────────────────────────────────────
window.openChangePass = () => {
  ['cp-current','cp-new','cp-confirm'].forEach(id=>{ const e=$(id); if(e) e.value=''; });
  const m=$('cp-msg'); if(m){ m.className='auth-msg'; m.style.display='none'; }
  $('modal-change-pass')?.classList.add('open');
};

window.changePassword = async () => {
  const current  = $('cp-current')?.value || '';
  const newpass  = $('cp-new')?.value     || '';
  const confirm  = $('cp-confirm')?.value || '';
  const showCpMsg = (msg,type) => {
    const el=$('cp-msg'); if(!el) return;
    el.textContent=msg; el.className='auth-msg '+type; el.style.display='block';
  };
  if (!current) { showCpMsg('Ingrese su contraseña actual','e'); return; }
  if (newpass.length < 8) { showCpMsg('La nueva contraseña debe tener al menos 8 caracteres','e'); return; }
  if (newpass !== confirm) { showCpMsg('Las contraseñas no coinciden','e'); return; }
  try {
    // Re-authenticate then update
    const { EmailAuthProvider, reauthenticateWithCredential, updatePassword }
      = await import('https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js');
    const credential = EmailAuthProvider.credential(CU.email, current);
    await reauthenticateWithCredential(CU, credential);
    await updatePassword(CU, newpass);
    toast('Contraseña actualizada correctamente','s');
    closeModal('modal-change-pass');
  } catch(e) {
    const msgs = {
      'auth/wrong-password' :'Contraseña actual incorrecta.',
      'auth/invalid-credential':'Contraseña actual incorrecta.',
      'auth/too-many-requests':'Demasiados intentos. Espere.',
      'auth/requires-recent-login':'Sesión expirada. Vuelva a iniciar sesión.',
    };
    showCpMsg(msgs[e.code]||'Error: '+e.message, 'e');
  }
};

// ── FOOTER INSTITUCIONAL ──────────────────────────────────────────────────────
var loadFooterConfig = async function() {
  try {
    const snap = await getDoc(doc(db,'config','footer'));
    if (snap.exists()) applyFooterConfig(snap.data());
  } catch(e) { console.warn('Footer config:', e.message); }
}
var applyFooterConfig = function(d) {
  const map = {
    'footer-brand'    : d.brand,
    'footer-text'     : d.text,
    'footer-phone-txt': d.phone,
    'footer-email-txt': d.email,
    'footer-extra'    : d.extra,
  };
  Object.entries(map).forEach(([id,val])=>{ const el=$(id); if(el&&val) el.textContent=val; });
}
var prefillFooterModal = function() {
  [['fc-brand','footer-brand'],['fc-text','footer-text'],
   ['fc-phone','footer-phone-txt'],['fc-email','footer-email-txt'],['fc-extra','footer-extra']
  ].forEach(([inp,src])=>{
    const el=$(inp), src_el=$(src);
    if(el && src_el) el.value = src_el.textContent || '';
  });
}

window.openModal = id => {
  if (id === 'modal-footer-config') prefillFooterModal();
  $(id)?.classList.add('open');
};

window.saveFooterConfig = async () => {
  const data = {
    brand: $('fc-brand')?.value.trim() || 'IDS Norte de Santander',
    text : $('fc-text')?.value.trim()  || 'Observatorio Departamental de Salud',
    phone: $('fc-phone')?.value.trim() || '',
    email: $('fc-email')?.value.trim() || '',
    extra: $('fc-extra')?.value.trim() || 'v3.0 · 2026',
    updatedAt: serverTimestamp()
  };
  try {
    await setDoc(doc(db,'config','footer'), data);
    applyFooterConfig(data);
    toast('Banner actualizado','s');
    closeModal('modal-footer-config');
  } catch(e) { toast('Error: '+e.message,'e'); }
};

// ── CREAR USUARIO: secundario para no cambiar sesión activa ───────────────────
// IMPORTANTE: reemplaza el comportamiento interno sin redeclarar la función
// Guardamos el original y lo envolvemos
var __origSaveCreateUser = window.saveCreateUser;
window.saveCreateUser = async function() {
  // Temporarily override createUserWithEmailAndPassword to use secondary instance
  // by monkey-patching the global reference used internally
  // We call the same validation logic but intercept the auth call

  if (!canCreate()) { toast('Sin permiso para crear usuarios','e'); return; }
  const name  = $('cu-name')?.value.trim();
  const email = $('cu-email')?.value.trim();
  const pass  = $('cu-pass')?.value || '';
  const rol   = $('cu-rol')?.value  || 'contratista';
  const grupo = $('cu-grupo')?.value || CUD.grupo || '';
  const area  = $('cu-area')?.value  || (CUD.role==='gestor'?CUD.area:'');

  if (!name)  { toast('El nombre es obligatorio','e'); return; }
  if (!email) { toast('El correo es obligatorio','e'); return; }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { toast('Correo inválido','e'); return; }
  if (pass.length < 6) { toast('Contraseña mínimo 6 caracteres','e'); return; }
  if (!grupo) { toast('Seleccione el grupo','e'); return; }
  if (!area)  { toast('Seleccione el área','e'); return; }
  if (!assignableRoles().includes(rol)) { toast('No puede asignar ese rol','e'); return; }
  if (CUD.role==='coordinador'&&grupo!==CUD.grupo) { toast('Solo puede crear en su grupo','e'); return; }
  if (CUD.role==='gestor'&&area!==CUD.area) { toast('Solo puede crear en su área','e'); return; }

  try {
    // Use a secondary Firebase app to avoid changing current session
    const { initializeApp: _initApp } = await import('https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js');
    const { getAuth: _getAuth, createUserWithEmailAndPassword: _createUser }
      = await import('https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js');
    const _app2  = _initApp(FB_CONFIG, 'cu_' + Date.now());
    const _auth2 = _getAuth(_app2);
    const cred   = await _createUser(_auth2, email, pass);
    await setDoc(doc(db,'users',cred.user.uid), {
      name, email, role:rol, grupo, area,
      perfilesProfesionales: window._cuPerfiles || [],
      status: 'active',
      createdAt: serverTimestamp(),
      createdBy: CU.uid,
      createdByName: CUD.name || CU.email
    });
    await _auth2.signOut();
    toast('Usuario creado: '+name+' ('+rol+')', 's');
    closeModal('modal-create-user');
  } catch(e) {
    const msgs = {
      'auth/email-already-in-use': 'Este correo ya está registrado.',
      'auth/weak-password': 'Contraseña muy débil.',
    };
    toast(msgs[e.code] || 'Error: '+e.message, 'e');
  }
};

// ── doRegister: también usa app secundaria ────────────────────────────────────
var __origDoRegister = window.doRegister;
window.doRegister = async function() {
  const name  = $('rn')?.value.trim() || '';
  const email = $('re')?.value.trim() || '';
  const grupo = $('rg')?.value || '';
  const area  = $('ra')?.value || '';
  const pass  = $('rp')?.value || '';
  if (!name)  { showAuthMsg('reg-msg','Ingrese su nombre completo.','e'); return; }
  if (!email) { showAuthMsg('reg-msg','Ingrese su correo.','e'); return; }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { showAuthMsg('reg-msg','Formato de correo inválido.','e'); return; }
  if (!grupo) { showAuthMsg('reg-msg','Seleccione el grupo.','e'); return; }
  if (!area)  { showAuthMsg('reg-msg','Seleccione el área.','e'); return; }
  if (pass.length < 6) { showAuthMsg('reg-msg','Mínimo 6 caracteres.','e'); return; }
  try {
    const { initializeApp: _ia } = await import('https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js');
    const { getAuth: _ga, createUserWithEmailAndPassword: _cu }
      = await import('https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js');
    const _app = _ia(FB_CONFIG, 'reg_' + Date.now());
    const _ath = _ga(_app);
    const cred = await _cu(_ath, email, pass);
    await setDoc(doc(db,'users',cred.user.uid), {
      name, email, grupo, area, role:'contratista',
      perfilesProfesionales:[], status:'pending', createdAt:serverTimestamp()
    });
    await _ath.signOut();
    showAuthMsg('reg-msg','Solicitud enviada. Espere aprobación del administrador.','s');
    ['rn','re','rp'].forEach(id=>{ const e=$(id); if(e) e.value=''; });
    const rg=$('rg'); if(rg) rg.value='';
    const ra=$('ra'); if(ra) ra.innerHTML='<option value="">Seleccione área</option>';
  } catch(e) {
    const msgs = {'auth/email-already-in-use':'Correo ya registrado.','auth/weak-password':'Contraseña débil.'};
    showAuthMsg('reg-msg', msgs[e.code]||'Error: '+e.message, 'e');
  }
};

// ── IPS desde Firestore (con cache) ──────────────────────────────────────────
var _ipsCache = {};
var getIPSForMun = async function(munName) {
  if (_ipsCache[munName]) return _ipsCache[munName];
  try {
    const q = query(collection(db,'prestadores'), where('municipio','==',munName));
    const snap = await getDocs(q);
    const list = snap.docs.map(d => ({
      n: d.data().nombre_prestador || '',
      nat: d.data().naturaleza || '',
      ese: d.data().ese || 'NO',
    })).filter(p=>p.n);
    // Merge with embedded data
    const embedded = PRES[munName.normalize('NFC').trim()] || [];
    const seen = new Set();
    const merged = [...list, ...embedded].filter(p=>{ if(!p.n||seen.has(p.n))return false;seen.add(p.n);return true; });
    _ipsCache[munName] = merged;
    return merged;
  } catch(e) {
    const embedded = PRES[munName.normalize('NFC').trim()] || [];
    _ipsCache[munName] = embedded;
    return embedded;
  }
}

var buildIPSDDAsync = async function(ddId, selArr, munArr, onSelectFn, q='') {
  const dd=$(ddId); if(!dd) return;
  const allProm = munArr.map(m => getIPSForMun(m.n||m));
  const allLists = await Promise.all(allProm);
  const all = allLists.flat();
  const res = (q ? all.filter(p=>p.n.toLowerCase().includes(q.toLowerCase())) : all).slice(0,30);
  if (!res.length) {
    dd.innerHTML=`<div class="ta-empty">${all.length?'Sin resultados':'Seleccione municipio primero'}</div>`;
    dd.classList.add('open'); return;
  }
  dd.innerHTML = res.map(p=>{
    const s  = selArr.some(x=>x.n===p.n);
    const nc = p.nat?.includes('blica')?'chip-pub':'chip-prv';
    const es = p.ese==='SI'?'<span class="chip chip-ese">ESE</span>':'';
    const pj = JSON.stringify(JSON.stringify({n:p.n,nat:p.nat,ese:p.ese}));
    return `<div class="ta-item${s?' sel':''}"
      onclick="${onSelectFn}(${pj})">
      <span>${esc(p.n)}</span>
      <span><span class="chip ${nc}">${p.nat||''}</span>${es}</span>
    </div>`;
  }).join('');
  dd.classList.add('open');
}

// Override IPS filters with async Firestore version
window.filterIPS  = q => buildIPSDDAsync('ips-dd',  selPIPS, selPMuns, 'addPIPS',  q||'');
window.filterCIPS = q => buildIPSDDAsync('cips-dd', selCIPS, selCMuns, 'addCIPS',  q||'');

// ── showView: extended for perfil ─────────────────────────────────────────────
var __origShowView = window.showView;
window.showView = v => {
  __origShowView(v);
  if (v === 'perfil') renderPerfilView();
};

// ── INIT: called after setupApp ───────────────────────────────────────────────
var postSetupInit = async function() {
  await loadFooterConfig();
  updateTopbarAvatar();
  renderPerfilView();
}







// ══════════════════════════════════════════════════════════════════════════════
