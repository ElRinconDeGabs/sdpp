document.getElementById('login-form').addEventListener('submit', async (e) => {
  e.preventDefault();

  const correoInput = document.getElementById('username');
  const passInput = document.getElementById('pass');
  const msgEl = document.getElementById('msg-mistake');

  const correo = correoInput.value.trim();
  const contraseña = passInput.value.trim();

  // Validaciones detalladas
  if (!correo) {
    msgEl.textContent = 'El correo es obligatorio.';
    msgEl.style.color = 'red';
    correoInput.focus();
    return;
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(correo)) {
    msgEl.textContent = 'Ingresa un correo válido.';
    msgEl.style.color = 'red';
    correoInput.focus();
    return;
  }

  if (!contraseña) {
    msgEl.textContent = 'La contraseña es obligatoria.';
    msgEl.style.color = 'red';
    passInput.focus();
    return;
  }

  if (contraseña.length < 6) {
    msgEl.textContent = 'La contraseña debe tener al menos 6 caracteres.';
    msgEl.style.color = 'red';
    passInput.focus();
    return;
  }

  const invalidChars = /[\s]/;
  if (invalidChars.test(contraseña)) {
    msgEl.textContent = 'La contraseña no debe contener espacios.';
    msgEl.style.color = 'red';
    passInput.focus();
    return;
  }

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ correo, contraseña }),
    });

    if (!res.ok) {
      msgEl.textContent = 'Actualmente no podemos procesar tu solicitud. Por favor, inténtalo más tarde.';
      msgEl.style.color = 'red';
      return;
    }

    const data = await res.json();

    if (data.success) {
      msgEl.textContent = `Bienvenido, ${data.nombre}`;
      msgEl.style.color = 'green';

      switch (data.rol) {
        case 'estudiante':
          window.location.href = '/estudiante/dashboard';
          break;
        case 'tutor_academico':
          window.location.href = '/tutor_academico/dashboard';
          break;
        case 'tutor_empresarial':
          window.location.href = '/tutor_empresarial/dashboard';
          break;
        default:
          msgEl.textContent = 'Rol no reconocido';
          msgEl.style.color = 'red';
      }
    } else {
      msgEl.textContent = data.message || 'Credenciales inválidas';
      msgEl.style.color = 'red';
    }
  } catch (err) {
    msgEl.textContent = 'Actualmente no podemos procesar tu solicitud. Por favor, inténtalo más tarde.';
    msgEl.style.color = 'red';
    console.error(err);
  }
});
