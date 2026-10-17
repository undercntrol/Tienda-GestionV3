# Cambios por versión

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/);
versiones según [SemVer](https://semver.org/lang/es/). Cada sprint cierra con
una versión; en el Sprint 6 se publica como *release* de GitHub (1.0.0).

## [0.3.0] — Sprints 2 y 3 · 2026-10-17

El código del Sprint 2 entra al repositorio en esta versión, junto con el
del Sprint 3, reorganizado para seguir el programa que ya usa la tienda.

### Agregado
- **HU-04** Tabla de usuarios con clave protegida (hash con sal) y rol; usuarios en Configuración.
- **HU-05** Ventas fiadas: cualquier cliente distinto de "Cliente general";
  clientes fijos y pasajeros.
- **HU-06** Pestaña Cuentas con saldos, compras pendientes, movimientos y total por cobrar.
- **HU-07** Inicio de sesión con roles administrador y cajero; editar y eliminar
  ventas solo para el administrador.
- **HU-08** Cobro de la cuenta completa con método y fecha de pago; comprobante HTML.
- **HU-09** Pestaña Reportes: ingresos por día, semana o mes, por producto, día
  y método; exportación a HTML imprimible y a Excel (.xlsx sin librerías).
- **HU-10** Administración de productos e importación de la lista de precios desde CSV.
- **HU-02** Filtros por fechas, producto, pago y cliente; estado Pagada/Fiada.
- **HU-03** Total de una fecha en Reportes, por fecha de pago.
- Calendario para elegir fechas, autocompletar de productos y clientes, caja de dinero `$2.500`.
- 50 pruebas automáticas.
- Documentación: historias de usuario actualizadas (`docs/FRSFormato_HU.docx`),
  backlog de 6 sprints, Sprint 3, riesgos, retrospectiva. `.gitignore`.

### Cambiado
- **HU-01** La venta se registra por **monto** (como anota el tendero), no por
  cantidad × precio unitario. Productos, métodos de pago y clientes nuevos se
  crean solos al vender.
- Fechas de venta sin hora (la base 0.1 se migra sola).
- Esquema de base de datos igual al del programa de la tienda.
- Interfaz con el tema verde y las pestañas del programa de la tienda.
- Product Goal y Definition of Done unificados.

### Quitado
- `__pycache__/` y `datos/tienda.db` del repositorio.

## [0.1.0] — Sprint 1 · 2026-09-12

### Agregado
- Registro de ventas con persistencia en SQLite (HU-01).
- Cierre del día con desglose por método de pago (HU-03).
- Catálogo de productos con búsqueda.
- 22 pruebas automáticas.
