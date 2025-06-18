// Cargar nombre del tutor académico
async function cargarNombreTutorAcademico() {
  try {
    const response = await fetch('/auth/tutor-academico/usuario');
    if (!response.ok) throw new Error('Error HTTP al obtener tutor académico');
    const data = await response.json();
    if (data.success && data.nombre) {
      document.getElementById('nombreTutorAcademico').textContent = `Bienvenido, ${data.nombre}`;
    }
  } catch (error) {
    console.error('❌ Error al obtener nombre del tutor académico:', error);
  }
}

// Cargar lista de estudiantes para el formulario
async function cargarEstudiantes() {
  try {
    const response = await fetch('/auth/tutor-academico/estudiantes');
    const data = await response.json();
    const select = document.getElementById('estudiante');
    select.innerHTML = '';

    data.estudiantes.forEach(est => {
      const option = document.createElement('option');
      option.value = est.id;
      option.textContent = est.nombre;
      select.appendChild(option);
    });
  } catch (error) {
    console.error('❌ Error al cargar estudiantes:', error);
  }
}

// Cargar lista de tutores empresariales para el formulario
async function cargarTutoresEmpresariales() {
  try {
    const response = await fetch('/auth/tutor-academico/tutores-empresariales');
    const data = await response.json();
    const select = document.getElementById('tutorEmpresarial');
    select.innerHTML = '';

    data.tutores.forEach(tutor => {
      const option = document.createElement('option');
      option.value = tutor.id;
      option.textContent = tutor.nombre;
      select.appendChild(option);
    });
  } catch (error) {
    console.error('❌ Error al cargar tutores empresariales:', error);
  }
}

// Manejar envío del formulario de asignación
document.getElementById('formAsignacion').addEventListener('submit', async (e) => {
  e.preventDefault();
  const estudianteId = document.getElementById('estudiante').value;
  const tutorId = document.getElementById('tutorEmpresarial').value;

  try {
    const response = await fetch('/auth/tutor-academico/asignar-tutor', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id_estudiante: estudianteId,
        id_tutor_empresarial: tutorId
      })
    });

    const data = await response.json();
    const mensaje = document.getElementById('asignacionMensaje');
    if (data.success) {
      mensaje.textContent = '✅ Tutor asignado correctamente';
      mensaje.style.color = 'green';
    } else {
      mensaje.textContent = '❌ Error al asignar tutor';
      mensaje.style.color = 'red';
    }
  } catch (error) {
    console.error('❌ Error al enviar asignación:', error);
  }
});

// Cargar actividades de los estudiantes
async function cargarActividadesEstudiantes() {
  try {
    const response = await fetch('/auth/tutor-academico/actividades');
    const data = await response.json();
    const tabla = document.getElementById('tablaActividadesEstudiantes');
    tabla.innerHTML = '';

    data.actividades.forEach(act => {
      const fila = document.createElement('tr');
      fila.innerHTML = `
        <td>${act.nombre_estudiante}</td>
        <td>${act.fecha}</td>
        <td>${act.descripcion}</td>
        <td>${act.horas}</td>
        <td>${act.estado_validacion}</td>
        <td>${act.comentario || ''}</td>
      `;
      tabla.appendChild(fila);
    });
  } catch (error) {
    console.error('❌ Error al cargar actividades de estudiantes:', error);
  }
}

// Función principal
async function cargarDashboardTutorAcademico() {
  await cargarNombreTutorAcademico();
  await cargarEstudiantes();
  await cargarTutoresEmpresariales();
  await cargarActividadesEstudiantes();
}

// Ejecutar al cargar el DOM
document.addEventListener('DOMContentLoaded', cargarDashboardTutorAcademico);
