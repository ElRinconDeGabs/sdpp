document.getElementById('login-form').addEventListener('submit', async (e) => {
  e.preventDefault();

  const correo = document.getElementById('username').value.trim();
  const contraseña = document.getElementById('pass').value.trim();
  const msgEl = document.getElementById('msg-mistake');

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ correo, contraseña }),
    });

    if (!res.ok) {
      msgEl.textContent = 'Error del servidor. Intenta de nuevo en unos instantes.';
      msgEl.style.color = 'red';
      return;
    }

    const data = await res.json();

    if (data.success) {
      msgEl.textContent = `Bienvenido, ${data.nombre}`;
      msgEl.style.color = 'green';

      // Redirige al dashboard según el rol
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
    msgEl.textContent = 'No se pudo conectar con el servidor.';
    msgEl.style.color = 'red';
    console.error(err);
  }
});
