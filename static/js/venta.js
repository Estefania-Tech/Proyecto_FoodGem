console.log('venta.js cargado');



// Ejecutar inmediatamente si los elementos existen, o esperar al DOM
function initVenta() {
    // Verificar que estamos en la página correcta
    if (!document.getElementById('codigoInput')) {
        return;
    }
    let productoSeleccionado = null;
    let productosEnTabla = [];

    const codigoInput = document.getElementById('codigoInput');
    const nombreInput = document.getElementById('nombreInput');
    const cantidadInput = document.getElementById('cantidadInput');
    const btnAgregar = document.getElementById('btnAgregar');
    const productosListCodigo = document.getElementById('productosListCodigo');
    const productosListNombre = document.getElementById('productosListNombre');
    const tablaProductos = document.getElementById('tablaProductos');
    const lowStockSection = document.getElementById('lowStockSection');
    const lowStockBody = document.getElementById('lowStockBody');
    const initialLowStock = window.initialLowStock || [];

    function actualizarLowStock(lowStock) {
        if (!lowStock || lowStock.length === 0) {
            if (lowStockSection) {
                lowStockSection.style.display = 'none';
            }
            return;
        }

        if (lowStockSection) {
            lowStockSection.style.display = 'block';
        }

        if (!lowStockBody) {
            return;
        }

        lowStockBody.innerHTML = '';
        lowStock.forEach(producto => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${producto.codigo}</td>
                <td>${producto.nombre}</td>
                <td>${producto.cantidad}</td>
            `;
            lowStockBody.appendChild(row);
        });
    }

    actualizarLowStock(initialLowStock);

    // Función para mostrar resultados de búsqueda
    function mostrarProductos(productos, listaElement) {
        if (productos.length > 0) {
            listaElement.innerHTML = '';
            productos.forEach(producto => {
                const div = document.createElement('div');
                div.className = 'producto-item';
                div.innerHTML = `<strong>${producto.codigo}</strong> - ${producto.nombre} (Stock: ${producto.cantidad}) - $${producto.precio}`;
                div.addEventListener('click', function() {
                    seleccionarProducto(producto);
                });
                listaElement.appendChild(div);
            });
            listaElement.style.display = 'block';
        } else {
            listaElement.innerHTML = '<div class="producto-item">No se encontraron productos</div>';
            listaElement.style.display = 'block';
        }
    }

    // Función para seleccionar un producto
    function seleccionarProducto(producto) {
        productoSeleccionado = producto;
        codigoInput.value = producto.codigo;
        nombreInput.value = producto.nombre;
        productosListCodigo.style.display = 'none';
        productosListNombre.style.display = 'none';
        cantidadInput.focus();
    }

    // Buscar por código
    codigoInput.addEventListener('input', async function() {
        console.log("Buscando por código:");
        const codigo = this.value.trim();
        
        if (codigo.length < 1) {
            productosListCodigo.style.display = 'none';
            return;
        }

        try {
            const response = await fetch(`/buscar_producto?search=${encodeURIComponent(codigo)}`);
            const data = await response.json();
            mostrarProductos(data.productos, productosListCodigo);
        } catch (error) {
            console.error('Error:', error);
            productosListCodigo.innerHTML = '<div class="producto-item">Error al buscar</div>';
            productosListCodigo.style.display = 'block';
        }
    });

    // Buscar por nombre
    nombreInput.addEventListener('input', async function() {
        const nombre = this.value.trim();
        
        if (nombre.length < 1) {
            productosListNombre.style.display = 'none';
            return;
        }

        try {
            const response = await fetch(`/buscar_producto?search=${encodeURIComponent(nombre)}`);
            const data = await response.json();
            mostrarProductos(data.productos, productosListNombre);
        } catch (error) {
            console.error('Error:', error);
            productosListNombre.innerHTML = '<div class="producto-item">Error al buscar</div>';
            productosListNombre.style.display = 'block';
        }
    });

    async function registrarVenta(codigo, cantidad) {
        console.log("DATOS A ENVIAR:", {
            codigo: codigoInput.value,
            cantidad: cantidadInput.value
        });
        const response = await fetch('/venta_add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                codigo: codigoInput.value.trim(),
                cantidad: cantidad
            })
        });

        const data = await response.json();
        console.log("RESPUESTA:", data);

        return data;
    }
    
    // Cerrar listas al hacer clic fuera
    document.addEventListener('click', function(e) {
        if (e.target !== codigoInput && e.target !== nombreInput) {
            productosListCodigo.style.display = 'none';
            productosListNombre.style.display = 'none';
        }
    });

    // Agregar producto a la tabla
    btnAgregar.addEventListener('click', function() {
        const cantidad = parseInt(cantidadInput.value);

        if (isNaN(cantidad) || cantidad <= 0) {
            alert("Cantidad inválida");
            return;
        }

        if (!productoSeleccionado) {
            alert('Por favor selecciona un producto');
            return;
        }

        if (cantidad > productoSeleccionado.cantidad) {
            alert(`Solo hay ${productoSeleccionado.cantidad} unidades disponibles`);
            return;
        }

        registrarVenta(productoSeleccionado.codigo, cantidad)
            .then(result => {
                console.log("RESPUESTA DEL SERVIDOR:", result);
                if (!result || !result.success) {
                    alert(result?.error || 'Error al registrar la venta');
                    return;
                }

                productoSeleccionado.cantidad = result.producto.cantidad;
                const subtotal = cantidad * productoSeleccionado.precio;
                const fila = document.createElement('tr');
                fila.innerHTML = `
                    <td>${productoSeleccionado.codigo}</td>
                    <td>${productoSeleccionado.nombre}</td>
                    <td>${cantidad}</td>
                    <td>$${parseFloat(productoSeleccionado.precio)}</td>
                    <td>$${subtotal}</td>
                    <td>
                        <button class="btn btn-sm btn-danger btn-eliminar">Eliminar</button>
                        <button class="btn btn-sm btn-warning btn-editar">Editar</button>
                    </td>
                `;

                    productosEnTabla.push({
                        codigo: productoSeleccionado.codigo,
                        nombre: productoSeleccionado.nombre,
                        cantidad: cantidad,
                        precio: productoSeleccionado.precio,
                        subtotal: subtotal
                });

                tablaProductos.appendChild(fila);

                // Evento para eliminar

                fila.querySelector('.btn-eliminar').addEventListener('click', function() {
                    const index = productosEnTabla.findIndex(p => 
                        p.codigo === productoSeleccionado.codigo && p.cantidad === cantidad
                    );
                    if (index > -1) {
                        productosEnTabla.splice(index, 1);
                    }
                    fila.remove();
                    calcularTotal();
                });

                // Evento para editar (puede abrir un modal o permitir edición inline)
                fila.querySelector('.btn-editar').addEventListener('click', function() {
                    const nuevoCantidad = prompt('Ingrese la nueva cantidad:', cantidad);
                    if (nuevoCantidad === null || isNaN(nuevoCantidad)|| nuevoCantidad <= 0){
                        alert('Cantidad inválida');
                        return;
                    } 
                    const cantidadActualizada = parseInt(nuevoCantidad);
                    fila.children[2].textContent = cantidadActualizada;
                    const nuevoSubtotal = cantidadActualizada * productoSeleccionado.precio;
                    fila.children[4].textContent = `$${nuevoSubtotal}`;
                    const producto = productosEnTabla.find(p => p.codigo === productoSeleccionado.codigo);

                    if (producto) {
                        producto.cantidad = cantidadActualizada;
                        producto.subtotal = nuevoSubtotal;
                    }

                    calcularTotal();
                });

                // Actualizar sección de stock bajo
                actualizarLowStock(result.low_stock);

                // Limpiar campos
                codigoInput.value = '';
                nombreInput.value = '';
                cantidadInput.value = '';
                productoSeleccionado = null;
                codigoInput.focus();

                // Recalcular total
                calcularTotal();
            })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al registrar la venta');
        });
    });


    // Permitir agregar con Enter en cantidad
    cantidadInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            btnAgregar.click();
        }
    });

    /*Funcion para finalizar venta*/
    const btnFacturar = document.getElementById('btnFacturar');
    const modalFactura = document.getElementById('modalFactura');
    const totalPagar = document.getElementById('totalPagar');
    const btnHecho = document.getElementById('btnHecho');
    const cantidadProductos = document.getElementById('cantidadProductos');
    console.log("Productos en tablaa");
    btnFacturar.addEventListener('click', function() {
        modalFactura.style.display = 'flex';
        cantidadProductos.textContent = productosEnTabla.length;
        let total = 0;
        productosEnTabla.forEach(producto => {
            total += producto.subtotal;
        });
        totalPagar.textContent = total.toFixed(2);
    });

    //Calcular cambio
    const pagoInput = document.getElementById('pagoInput');
    const cambio = document.getElementById('cambio');
    pagoInput.addEventListener('input', function() {
        const efectivo = parseFloat(this.value) || 0;
        let total = 0;
        productosEnTabla.forEach(producto => {
            total += producto.subtotal;
        });
        const cambioValor = efetcivo - total;
        cambio.textContent = `$${cambioValor.toFixed(2)}`;
    }); 

    /*Guardar venta en historial*/
    btnHecho.addEventListener('click', async() => {
        const total = productosEnTabla.reduce((acc, p) => acc + p.subtotal, 0);
        const efectivo = parseFloat(pagoInput.value);
        const cambioValor = efectivo - total;
        const response = await fetch('/guardar_factura', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                productos: productosEnTabla,
                total: total,
                efectivo: efectivo,
                cambio: cambioValor
            })
        });
        const result = await response.json();
        if (result.success) {
            alert('Venta registrada exitosamente');
            modalFactura.style.display = 'none';
            location.reload();
        }
    }); 

    // Calcular total
    function calcularTotal() {
        const total = productosEnTabla.reduce((sum, producto) => sum + producto.subtotal, 0);
        document.getElementById('totalPagar').textContent = total;
    } 
   
}

// Intentar inicializar inmediatamente, o esperar al DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initVenta);
    } else {
        initVenta();
    } 

    