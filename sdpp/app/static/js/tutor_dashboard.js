// Obtener el nombre del tutor
async function obtenerUsuario() {
  try {
    const res = await fetch('/api/auth/usuario');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    if (data.success) {
      document.getElementById('nombreTutor').textContent = `Bienvenido, ${data.nombre}`;
    } else {
      console.warn('No se obtuvo información válida del usuario');
    }
  } catch (err) {
    console.error('Error al obtener usuario:', err);
    // Mensaje amigable para el usuario
    alert('No fue posible obtener tu información en este momento. Por favor, inténtalo más tarde.');
  }
}

// Cargar actividades pendientes de validación
async function cargarActividades() {
  try {
    const res = await fetch('/api/auth/actividades-por-validar');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (!data.success) throw new Error(data.message);

    const tabla = document.getElementById('tablaActividades');
    tabla.innerHTML = '';

    data.actividades.forEach((act) => {
      // Validaciones simples de datos para evitar mostrar "undefined" o datos inválidos
      const nombreEstudiante = act.nombre_estudiante?.trim() || 'Desconocido';
      const fecha = act.fecha || 'No disponible';
      const descripcion = act.descripcion?.trim() || 'Sin descripción';
      const horas = (typeof act.horas === 'number' && act.horas >= 0) ? act.horas : 'N/A';
      const archivoAdjunto = act.archivo_adjunto?.trim() || null;
      const idActividad = act.id_actividad;

      const fila = document.createElement('tr');
      fila.innerHTML = `
        <td>${nombreEstudiante}</td>
        <td>${fecha}</td>
        <td>${descripcion}</td>
        <td>${horas}</td>
        <td>${archivoAdjunto ? `<a href="${archivoAdjunto}" target="_blank">Descargar</a>` : 'Sin archivo'}</td>
        <td><textarea class="comentario" data-id="${idActividad}" placeholder="Comentario..."></textarea></td>
        <td>
          <button class="btn-aprobar" data-id="${idActividad}">Aprobar</button>
          <button class="btn-rechazar" data-id="${idActividad}">Rechazar</button>
        </td>
      `;
      tabla.appendChild(fila);
    });

    // Vincular eventos a los botones después de crear la tabla
    document.querySelectorAll('.btn-aprobar').forEach(btn => {
      btn.addEventListener('click', () => validarActividad(btn.dataset.id, 'aprobada'));
    });
    document.querySelectorAll('.btn-rechazar').forEach(btn => {
      btn.addEventListener('click', () => validarActividad(btn.dataset.id, 'rechazada'));
    });
  } catch (err) {
    console.error('❌ Error al cargar actividades:', err);
    alert('No fue posible cargar las actividades en este momento. Por favor, inténtalo más tarde.');
  }
}

// Validar (aprobar/rechazar) una actividad
async function validarActividad(idActividad, estado) {
  const textarea = document.querySelector(`textarea[data-id="${idActividad}"]`);
  const comentario = textarea?.value.trim() || '';

  // Validaciones previas
  if (!idActividad || !['aprobada', 'rechazada'].includes(estado)) {
    alert('Datos inválidos para la validación de la actividad.');
    return;
  }
  if (estado === 'rechazada' && comentario.length < 5) {
    alert('Por favor, proporciona un comentario de al menos 5 caracteres para rechazar una actividad.');
    textarea?.focus();
    return;
  }

  if (!confirm(`¿Estás seguro de ${estado === 'aprobada' ? 'aprobar' : 'rechazar'} esta actividad?`)) {
    return;
  }

  try {
    const res = await fetch('/api/auth/validar-actividad', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id_actividad: parseInt(idActividad, 10),
        estado,
        comentario,
      }),
    });

    if (!res.ok) {
      alert('No fue posible procesar la validación en este momento. Por favor, inténtalo más tarde.');
      return;
    }

    const data = await res.json();
    if (data.success) {
      alert(`✅ Actividad ${estado}`);
      cargarActividades(); // Refrescar tabla
    } else {
      alert(`❌ Error: ${data.message || 'No se pudo completar la acción.'}`);
    }
  } catch (err) {
    console.error('❌ Error al validar actividad:', err);
    alert('No fue posible completar la validación. Por favor, inténtalo más tarde.');
  }
}

// Cerrar sesión
function logout() {
  fetch('/api/auth/logout', { method: 'POST' })
    .then(() => window.location.href = '/')
    .catch(err => {
      console.error('Error al cerrar sesión:', err);
      alert('No fue posible cerrar sesión en este momento. Inténtalo más tarde.');
    });
}

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
  obtenerUsuario();
  cargarActividades();

  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', (e) => {
      e.preventDefault();
      logout();
    });
  }
});
