document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('registroForm');

  let mensajeElem = document.createElement('div');
  mensajeElem.id = 'mensajeRegistro';
  mensajeElem.style.marginTop = '10px';
  mensajeElem.style.fontWeight = 'bold';
  form.insertAdjacentElement('afterend', mensajeElem);

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    mensajeElem.style.color = 'black';
    mensajeElem.textContent = 'Procesando registro...';

    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    // Validaciones detalladas

    // Nombre: mínimo 3 caracteres, solo letras y espacios
    if (!data.nombre || data.nombre.trim().length < 3 || !/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(data.nombre.trim())) {
      alert('Por favor, ingresa un nombre válido de al menos 3 letras y sin números ni símbolos.');
      mensajeElem.style.color = 'red';
      mensajeElem.textContent = 'Nombre inválido.';
      return;
    }

    // Correo: formato estándar
    if (!data.correo || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.correo)) {
      alert('Por favor, ingresa un correo electrónico válido.');
      mensajeElem.style.color = 'red';
      mensajeElem.textContent = 'Correo inválido.';
      return;
    }

    // Contraseña: mínimo 6 caracteres, al menos una mayúscula, una minúscula, un número y un símbolo, sin espacios
    if (!data.contraseña || data.contraseña.length < 6) {
      alert('La contraseña debe tener al menos 6 caracteres.');
      mensajeElem.style.color = 'red';
      mensajeElem.textContent = 'Contraseña inválida.';
      return;
    }
    if (!/[A-Z]/.test(data.contraseña)) {
      alert('La contraseña debe contener al menos una letra mayúscula.');
      mensajeElem.style.color = 'red';
      mensajeElem.textContent = 'Contraseña inválida.';
      return;
    }
    if (!/[a-z]/.test(data.contraseña)) {
      alert('La contraseña debe contener al menos una letra minúscula.');
      mensajeElem.style.color = 'red';
      mensajeElem.textContent = 'Contraseña inválida.';
      return;
    }
    if (!/[0-9]/.test(data.contraseña)) {
      alert('La contraseña debe contener al menos un número.');
      mensajeElem.style.color = 'red';
      mensajeElem.textContent = 'Contraseña inválida.';
      return;
    }
    if (!/[\W_]/.test(data.contraseña)) {
      alert('La contraseña debe contener al menos un símbolo especial.');
      mensajeElem.style.color = 'red';
      mensajeElem.textContent = 'Contraseña inválida.';
      return;
    }
    if (/\s/.test(data.contraseña)) {
      alert('La contraseña no debe contener espacios.');
      mensajeElem.style.color = 'red';
      mensajeElem.textContent = 'Contraseña inválida.';
      return;
    }

    // Rol: debe ser uno de los válidos
    if (!data.rol || !['estudiante', 'tutor_academico', 'tutor_empresarial'].includes(data.rol)) {
      alert('Selecciona un rol válido.');
      mensajeElem.style.color = 'red';
      mensajeElem.textContent = 'Rol inválido.';
      return;
    }

    // Cédula: mínimo 5 caracteres, solo números, guiones o letras mayúsculas (por si es formato tipo X-XXX-XXXX)
    if (!data.cedula || data.cedula.trim().length < 5 || !/^[A-Z0-9\-]+$/.test(data.cedula.trim().toUpperCase())) {
      alert('Por favor, ingresa una cédula válida (solo números, guiones o letras mayúsculas).');
      mensajeElem.style.color = 'red';
      mensajeElem.textContent = 'Cédula inválida.';
      return;
    }

    try {
      const res = await fetch('/api/auth/sign-up', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      const result = await res.json();

      if (res.ok && result.success) {
        mensajeElem.style.color = 'green';
        mensajeElem.textContent = result.message || 'Registrado con éxito';
        alert('Registro exitoso.');
        form.reset();
      } else {
        mensajeElem.style.color = 'red';
        mensajeElem.textContent = result.message || 'No se pudo completar el registro. Por favor verifica tus datos.';
        alert(result.message || 'No se pudo completar el registro. Por favor verifica tus datos.');
      }
    } catch (err) {
      mensajeElem.style.color = 'red';
      mensajeElem.textContent = 'En este momento no es posible procesar tu solicitud. Intenta más tarde.';
      alert('En este momento no es posible procesar tu solicitud. Intenta más tarde.');
      console.error(err);
    }
  });
});
