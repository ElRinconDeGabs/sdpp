// Cargar nombre del estudiante
async function cargarNombreEstudiante() {
  try {
    const response = await fetch('/api/auth/usuario');
    if (!response.ok) throw new Error('Error HTTP al obtener nombre');
    const data = await response.json();
    if (data.success) {
      document.getElementById('nombreUsuario').textContent = `Bienvenido, ${data.nombre}`;
    } else {
      console.error('No autorizado o sin sesión');
    }
  } catch (error) {
    console.error('❌ Error al cargar nombre del estudiante:', error);
  }
}

// Cargar actividades registradas por el estudiante
async function cargarActividadesEstudiante() {
  try {
    const response = await fetch('/api/auth/actividades/mias');
    if (!response.ok) throw new Error('Error HTTP al obtener actividades');
    const data = await response.json();
    if (data.success) {
      const tabla = document.getElementById('tablaActividades');
      tabla.innerHTML = '';
      data.actividades.forEach((actividad) => {
        const fila = document.createElement('tr');
        fila.innerHTML = `
          <td>${actividad.fecha}</td>
          <td>${actividad.descripcion}</td>
          <td>${actividad.horas}</td>
          <td>${actividad.estado_validacion || 'Pendiente'}</td>
          <td>${actividad.comentarios || ''}</td>
        `;
        tabla.appendChild(fila);
      });
    } else {
      console.error('No autorizado o sin sesión');
    }
  } catch (error) {
    console.error('❌ Error al cargar actividades del estudiante:', error);
  }
}

// Cargar resumen (avance y horas semanales)
async function cargarResumen() {
  try {
    const response = await fetch('/api/auth/actividades/resumen');
    if (!response.ok) throw new Error('Error HTTP al obtener resumen');
    const data = await response.json();
    if (data.success) {
      document.getElementById('avanceGeneral').textContent = `${data.porcentaje}% completado`;
      document.getElementById('horasSemana').textContent = `${data.horas_semana} horas`;
    } else {
      console.error('No autorizado o sin sesión');
    }
  } catch (error) {
    console.error('❌ Error al cargar resumen:', error);
  }
}

// Enviar formulario de nueva actividad
document.getElementById('actividadForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  try {
    const response = await fetch('/api/auth/actividades/registrar', {
      method: 'POST',
      body: formData,
    });
    const data = await response.json();
    if (data.success) {
      alert('Actividad registrada con éxito.');
      e.target.reset();
      await cargarActividadesEstudiante();
      await cargarResumen();
    } else {
      alert('Error al registrar actividad.');
    }
  } catch (error) {
    console.error('❌ Error al registrar actividad:', error);
  }
});

// Al cargar la página
document.addEventListener('DOMContentLoaded', async () => {
  await cargarNombreEstudiante();
  await cargarActividadesEstudiante();
  await cargarResumen();
});
