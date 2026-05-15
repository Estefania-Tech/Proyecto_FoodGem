document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('editModal');
    if (!modal) {
        return;
    }

    const closeBtn = modal.querySelector('.close');
    const editForm = document.getElementById('editForm');
    const cancelBtn = modal.querySelector('.btn-cancel');

    // Abrir modal al hacer click en editar en Inventario
    document.querySelectorAll('.btn-edit').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            const productId = this.href.split('/').pop();

            try {
                const response = await fetch(`/get_product/${productId}`);
                const data = await response.json();

                document.getElementById('productId').value = data.id;
                document.getElementById('producto_codigo').value = data.codigo;
                document.getElementById('nombre_producto').value = data.nombre;
                document.getElementById('precio_producto').value = data.precio;
                document.getElementById('categoria_producto').value = data.categoria;
                document.getElementById('cantidad_producto').value = data.cantidad;

                modal.style.display = 'block';
            } catch (error) {
                console.error('Error:', error);
                alert('Error al cargar el producto');
            }
        });
    });

    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            modal.style.display = 'none';
        });
    }

    if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
            modal.style.display = 'none';
        });
    }

    // Cerrar modal al hacer click fuera
    window.addEventListener('click', (e) => {
        if (modal && e.target === modal) {
            modal.style.display = 'none';
        }
    });

    if (editForm) {
        editForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const productId = document.getElementById('productId').value;

            const formData = new FormData(this);
            const data = {
                codigo_producto: document.getElementById('producto_codigo').value,
                nombre_producto: formData.get('nombre_producto'),
                precio_producto: formData.get('precio_producto'),
                categoria_producto: formData.get('categoria_producto'),
                cantidad_producto: formData.get('cantidad_producto')
            };

            try {
                const response = await fetch(`/edit_product/${productId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    modal.style.display = 'none';
                    location.reload();
                } else {
                    alert('Error al actualizar el producto');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error al actualizar el producto');
            }
        });
    }
});