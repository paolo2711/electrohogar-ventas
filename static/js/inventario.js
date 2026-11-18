// Productos y stock: "/" lleva a la búsqueda, y los rótulos del formulario
// cambian según se registre un ingreso o un ajuste por conteo.
(() => {
  const buscar = document.getElementById('q');
  document.addEventListener('keydown', (e) => {
    if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
      e.preventDefault();
      buscar.focus();
      buscar.select();
    }
  });

  const form = document.getElementById('registrar');
  if (!form) return;
  form.addEventListener('change', (e) => {
    if (e.target.name !== 'tipo') return;
    form.querySelectorAll('label[data-ingreso]').forEach((l) => { l.textContent = l.dataset[e.target.value]; });
  });
})();
