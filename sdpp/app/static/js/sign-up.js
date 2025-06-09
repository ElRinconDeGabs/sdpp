document.getElementById('registroForm').addEventListener('submit', async function (e) {
  e.preventDefault();

  const formData = new FormData(e.target);
  const data = Object.fromEntries(formData.entries());

  try {
    const res = await fetch('/api/auth/sign-up', { // ← Cambia la ruta aquí
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    const result = await res.json();
    alert(result.message || (result.success ? 'Registrado con éxito' : 'Error al registrar'));
  } catch (err) {
    alert('Error al conectar con el servidor');
    console.error(err);
  }
});