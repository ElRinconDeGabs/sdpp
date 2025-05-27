// public/static/js/login.js
document
  .getElementById('login-form')
  .addEventListener('submit', async (e) => {
    e.preventDefault();

    // ↳ Los IDs vienen del HTML
    const correo = document.getElementById('username').value.trim();
    const contraseña = document.getElementById('pass').value.trim();

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ correo, contraseña }), // ← el backend espera estos nombres
      });

      const msgEl = document.getElementById('msg-mistake');

      if (!res.ok) {
        // Error de red o 5xx
        msgEl.textContent =
          'Error del servidor. Intenta de nuevo en unos instantes.';
        msgEl.style.color = 'red';
        return;
      }

      const data = await res.json();

      if (data.success) {
        msgEl.textContent = `Bienvenido, ${data.nombre}`;
        msgEl.style.color = 'green';
        // window.location.href = '/dashboard.html';  // o la ruta que necesites
      } else {
        msgEl.textContent = data.message;
        msgEl.style.color = 'red';
      }
    } catch (err) {
      // Fallo de conexión o JSON inválido
      const msgEl = document.getElementById('msg-mistake');
      msgEl.textContent = 'No se pudo conectar con el servidor.';
      msgEl.style.color = 'red';
      console.error(err);
    }
  });
