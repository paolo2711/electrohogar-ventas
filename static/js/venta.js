// Atajos de la pantalla de venta (ver docs/identidad-visual.md):
//   /      lleva el cursor a la búsqueda
//   Enter  en la búsqueda ya hecha, agrega el primer producto de la lista
//   F9     cobra la venta
(() => {
  const buscar = document.getElementById('q');
  const cobrar = document.getElementById('cobrar');

  document.addEventListener('keydown', (e) => {
    if (e.key === '/' && document.activeElement !== buscar) {
      e.preventDefault();
      buscar.focus();
      buscar.select();
    }
    if (e.key === 'F9') {
      e.preventDefault();
      const boton = cobrar.querySelector('button');
      if (!boton.disabled) cobrar.requestSubmit();
    }
  });

  // Si el texto no cambió desde la última búsqueda, Enter agrega el primero que salió.
  buscar.addEventListener('keydown', (e) => {
    if (e.key !== 'Enter' || buscar.value.trim() === '' || buscar.value !== buscar.dataset.buscado) return;
    const primero = document.querySelector('.agregar:not([disabled])');
    if (primero) {
      e.preventDefault();
      primero.form.requestSubmit();
    }
  });
})();
