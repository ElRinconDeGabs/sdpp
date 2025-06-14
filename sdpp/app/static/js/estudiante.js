document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("actividadForm");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(form);

    try {
      const response = await fetch("/api/actividades/registrar", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      if (result.success) {
        alert("Actividad registrada con éxito");
        form.reset();
        cargarActividades(); // Refresca la tabla
      } else {
        alert(result.message || "Ocurrió un error");
      }
    } catch (error) {
      console.error("Error al enviar:", error);
      alert("Error de conexión con el servidor");
    }
  });
});

async function cargarActividades() {
  try {
    const res = await fetch("/api/actividades/mias");
    const data = await res.json();

    const tbody = document.getElementById("tablaActividades");
    tbody.innerHTML = "";

    data.actividades.forEach((act) => {
      const tr = document.createElement("tr");

      tr.innerHTML = `
        <td>${act.fecha}</td>
        <td>${act.descripcion}</td>
        <td>${act.horas}</td>
        <td>${act.estado_validacion}</td>
        <td>${act.comentarios || "-"}</td>
      `;

      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Error al cargar actividades:", err);
  }
}

// Ejecutar al cargar la página
document.addEventListener("DOMContentLoaded", cargarActividades);
