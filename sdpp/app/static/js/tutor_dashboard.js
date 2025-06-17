// Función para cargar el nombre del tutor desde el backend
async function cargarNombreTutor() {
  try {
    const response = await fetch('/api/auth/tutor/usuario')  // en lugar de /auth/tutor/usuario
    if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);

    const data = await response.json();

    if (data.success && data.nombre) {
      const nombreTutorElem = document.getElementById('nombreTutor');
      if (nombreTutorElem) {
        nombreTutorElem.textContent = `Bienvenido, ${data.nombre}`;
      } else {
        console.warn('Elemento con ID "nombreTutor" no encontrado.');
      }
    } else {
      console.warn('Respuesta exitosa pero no se encontró el nombre del tutor.');
    }
  } catch (error) {
    console.error("❌ Error al cargar nombre del tutor:", error);
  }
}

// Función para cargar actividades pendientes
async function cargarActividadesPendientes() {
  try {
    const response = await fetch('/api/auth/tutor/usuario')  // en lugar de /auth/tutor/usuario
    if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);

    const data = await response.json();

    if (!data.success) throw new Error(data.message || 'Error al obtener actividades');

    const tabla = document.getElementById('tablaActividades');
    if (!tabla) throw new Error('Elemento con ID "tablaActividades" no encontrado.');

    // Limpiar contenido previo
    tabla.innerHTML = '';

    const actividades = data.data || data.actividades || [];

    if (actividades.length === 0) {
      tabla.innerHTML = '<tr><td colspan="6">No hay actividades pendientes.</td></tr>';
      return;
    }

    actividades.forEach(act => {
      const fila = document.createElement('tr');

      fila.innerHTML = `
        <td>${act.nombre_estudiante || act.estudiante || ''}</td>
        <td>${act.fecha || ''}</td>
        <td>${act.descripcion || ''}</td>
        <td>${act.horas || ''}</td>
        <td>
          ${
            act.archivo_adjunto
              ? `<a href="/auth/tutor/actividades/${act.id_actividad}/evidencia" target="_blank" rel="noopener noreferrer">Ver evidencia</a>`
              : 'Sin evidencia'
          }
        </td>
        <td>
          <button type="button" onclick="validarActividad(${act.id_actividad}, 'aprobada')">Aprobar</button>
          <button type="button" onclick="validarActividad(${act.id_actividad}, 'rechazada')">Rechazar</button>
        </td>
      `;

      tabla.appendChild(fila);
    });
  } catch (error) {
    console.error("❌ Error cargando actividades:", error);
  }
}

// Función para validar una actividad (aprobar o rechazar)
async function validarActividad(idActividad, estado) {
  try {
    const comentarios = prompt(`Comentarios para marcar como "${estado}":`)?.trim() || '';

    const response = await fetch('/auth/tutor/actividades/validar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id_actividad: idActividad,
        estado_validacion: estado,
        comentario: comentarios
      })
    });

    if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);

    const data = await response.json();

    if (data.success) {
      alert('✅ Actividad validada correctamente');
      await cargarActividadesPendientes(); // Recargar tabla después de validar
    } else {
      alert('❌ Error al validar actividad: ' + (data.message || 'Desconocido'));
    }
  } catch (error) {
    console.error("❌ Error al validar actividad:", error);
    alert('❌ Error al validar actividad, revise la consola para más detalles.');
  }
}

// Función principal que se ejecuta al cargar el DOM
async function cargarDatosTutor() {
  await cargarNombreTutor();
  await cargarActividadesPendientes();
}

// Evento para cargar los datos cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', cargarDatosTutor);
