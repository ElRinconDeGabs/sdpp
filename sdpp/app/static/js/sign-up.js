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
        form.reset();
      } else {
        mensajeElem.style.color = 'red';
        mensajeElem.textContent = result.message || 'Error al registrar';
      }
    } catch (err) {
      mensajeElem.style.color = 'red';
      mensajeElem.textContent = 'Error al conectar con el servidor';
      console.error(err);
    }
  });
});
