from app import app, db, Producto

with app.app_context():
    # Crear tablas si no existen
    db.create_all()

    # Verificar si ya hay productos
    productos_existentes = Producto.query.count()
    print(f"Productos existentes: {productos_existentes}")

    if productos_existentes == 0:
        # Agregar productos de prueba
        productos_prueba = [
            Producto(codigo='001', nombre='Producto A', precio=10.50, categoria='Categoria 1', cantidad=100),
            Producto(codigo='002', nombre='Producto B', precio=25.00, categoria='Categoria 1', cantidad=50),
            Producto(codigo='003', nombre='Producto C', precio=15.75, categoria='Categoria 2', cantidad=75),
            Producto(codigo='004', nombre='Producto D', precio=8.99, categoria='Categoria 2', cantidad=200),
        ]

        for producto in productos_prueba:
            db.session.add(producto)

        db.session.commit()
        print("Productos de prueba agregados exitosamente")
    else:
        print("Ya hay productos en la base de datos")

    # Mostrar productos
    productos = Producto.query.all()
    for p in productos:
        print(f"Código: {p.codigo}, Nombre: {p.nombre}, Precio: {p.precio}, Cantidad: {p.cantidad}")