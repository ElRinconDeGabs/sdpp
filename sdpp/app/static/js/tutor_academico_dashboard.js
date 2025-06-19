// Variables globales
let estudiantesConTutores = [];
let tutoresDisponibles = [];
let cedulaAcademico = null;

// Obtener info del usuario actual
async function obtenerUsuario() {
  try {
    const res = await fetch('/api/auth/usuario');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (data.success) {
      document.getElementById('nombreTutorAcademico').textContent = `Bienvenido, ${data.nombre}`;
      cedulaAcademico = data.cedula || null;
    }
  } catch (err) {
    console.error('Error al obtener usuario:', err);
  }
}

// Cargar estudiantes con tutores asignados
async function cargarEstudiantesConTutores() {
  try {
    const res = await fetch('/api/auth/estudiantes-con-tutores');
    if (!res.ok) throw new Error(`Error HTTP: ${res.status}`);
    const data = await res.json();
    if (!data.success) throw new Error(data.message);

    estudiantesConTutores = data.estudiantes;

    const tabla = document.getElementById('tablaAsignacion');
    tabla.innerHTML = '';

    estudiantesConTutores.forEach(est => {
      const fila = document.createElement('tr');
      fila.innerHTML = `
        <td>${est.nombre_estudiante || 'Nombre no disponible'}</td>
        <td>${est.tutor_empresarial || 'Sin asignar'}</td>
      `;
      tabla.appendChild(fila);
    });
  } catch (err) {
    console.error('❌ Error al cargar estudiantes con tutores:', err);
    alert('Ocurrió un error al cargar estudiantes.');
  }
}

// Cargar tutores empresariales
async function cargarTutores() {
  try {
    const res = await fetch('/api/auth/tutores-empresariales');
    if (!res.ok) throw new Error(`Error HTTP: ${res.status}`);
    const data = await res.json();
    if (!data.success) throw new Error(data.message);

    tutoresDisponibles = data.tutores;

    const select = document.getElementById('selectTutorEmpresarial');
    select.innerHTML = `<option value="">-- Selecciona un tutor empresarial --</option>`;

    data.tutores.forEach(t => {
      const opt = document.createElement('option');
      opt.value = t.cedula || t.id_usuario;
      opt.textContent = t.nombre || 'Sin nombre';
      select.appendChild(opt);
    });
  } catch (err) {
    console.error('❌ Error al cargar tutores:', err);
    alert('No se pudieron cargar los tutores.');
  }
}

// Cargar estudiantes para asignar
async function cargarEstudiantesParaAsignar() {
  try {
    const res = await fetch('/api/auth/estudiantes-con-tutores');
    if (!res.ok) throw new Error(`Error HTTP: ${res.status}`);
    const data = await res.json();
    if (!data.success) throw new Error(data.message);

    const select = document.getElementById('selectEstudiante');
    select.innerHTML = `<option value="">-- Selecciona un estudiante --</option>`;

    data.estudiantes.forEach(est => {
      const opt = document.createElement('option');
      opt.value = est.cedula || est.id_estudiante;
      opt.textContent = est.nombre_estudiante || 'Sin nombre';
      select.appendChild(opt);
    });
  } catch (err) {
    console.error('❌ Error al cargar estudiantes:', err);
    alert('No se pudieron cargar los estudiantes.');
  }
}

// Asignar tutor
async function asignarTutor() {
  const cedulaEst = document.getElementById('selectEstudiante')?.value;
  const cedulaTut = document.getElementById('selectTutorEmpresarial')?.value;

  if (!cedulaEst || !cedulaTut || !cedulaAcademico) {
    alert('Faltan datos para realizar la asignación.');
    return;
  }

  try {
    const res = await fetch('/api/auth/asignar-tutor', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        cedula_empresarial: cedulaTut,
        cedula_estudiante: cedulaEst,
        fecha_asignacion: new Date().toISOString().split('T')[0]
      })
    });

    const data = await res.json();
    if (data.success) {
      alert('✅ Tutor asignado correctamente');
      await cargarEstudiantesConTutores();
      await cargarEstudiantesParaAsignar();
      await cargarActividadesEstudiantes();
    } else {
      alert('❌ Error al asignar tutor: ' + (data.message || 'desconocido'));
    }
  } catch (err) {
    console.error('❌ Error en la asignación:', err);
    alert('Error al asignar tutor.');
  }
}

// Cargar actividades de todos los estudiantes
async function cargarActividadesEstudiantes() {
  try {
    const res = await fetch('/api/auth/actividades-estudiantes');
    if (!res.ok) throw new Error(`Error HTTP: ${res.status}`);
    const data = await res.json();
    if (!data.success) throw new Error(data.message);

    const tabla = document.getElementById('tablaActividadesEstudiantes');
    tabla.innerHTML = '';

    data.actividades.forEach(act => {
      const fila = document.createElement('tr');
      fila.innerHTML = `
        <td>${act.estudiante || ''}</td>
        <td>${act.tutor_empresarial || ''}</td>
        <td>${act.fecha || ''}</td>
        <td>${act.descripcion || ''}</td>
        <td>${act.horas || ''}</td>
        <td>${act.estado_validacion || ''}</td>
        <td>${act.comentarios || ''}</td>
      `;
      tabla.appendChild(fila);
    });
  } catch (err) {
    console.error('Error al cargar actividades:', err);
  }
}

// Logout
function logout() {
  fetch('/api/auth/logout', { method: 'POST' })
    .then(() => window.location.href = '/')
    .catch(err => console.error('Error al cerrar sesión:', err));
}

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
  obtenerUsuario();
  cargarEstudiantesConTutores();
  cargarTutores();
  cargarEstudiantesParaAsignar();
  cargarActividadesEstudiantes();

  document.getElementById('btnAsignarTutor')?.addEventListener('click', (e) => {
    e.preventDefault();
    asignarTutor();
  });

  document.getElementById('logoutBtn')?.addEventListener('click', (e) => {
    e.preventDefault();
    logout();
  });
});
