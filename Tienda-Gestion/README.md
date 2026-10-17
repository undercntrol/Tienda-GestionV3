# Tienda Gestión

Sistema de ventas, fiado y reportes para una cigarrería de barrio.
Proyecto Integrador — Práctica Aplicada · TIC42695 · Ingeniería de Sistemas · Semestre 2026-2

**Versión:** 0.3.0 (cierre del Sprint 3 de 6)
**Equipo:** Fabrizio Stefano Saganome Cardenas · Laura Sofía Castellanos Manrique · Juan Nicolas Rodríguez Castro · Willintong Ignacio Castro Caro · Nicolas Benitez Velasco · Cristian Camilo Mora González
**Repositorio:** https://github.com/undercntrol/Tienda-Gestion

---

## El problema

En la cigarrería las ventas y lo que se le fía a cada vecino se anotan en una
libreta. Al final del día el tendero cuadra la caja sumando a mano, no sabe
con certeza cuánto le debe cada cliente y no distingue lo que vendió de lo que
de verdad entró a la caja (lo fiado se vende pero se cobra después).

## Product Goal

Lograr que la cigarrería lleve digitalmente sus ventas y cuentas por cobrar,
de modo que al cierre de cada día el tendero conozca el total vendido por
método de pago y el saldo exacto de cada cliente, reduciendo el tiempo de
cuadre diario de 20 a menos de 5 minutos y eliminando las deudas no
registradas, dentro de las 16 semanas del semestre.

## Cómo ejecutarlo

Requiere **Python 3.10 o superior**. Sin dependencias externas: solo la
librería estándar (`tkinter`, `sqlite3`, `csv`, `hashlib`, `zipfile`).

```bash
python main.py
```

- **Primera vez:** pide crear el usuario administrador. Después, el
  administrador crea a los cajeros en **Configuración → Usuarios**.
- **Datos:** se crean solos en `datos/tienda.db` (no se suben al repositorio).
- **Reportes y comprobantes:** se guardan en `salidas/` y se abren en el navegador.
- **Ejemplo para la demo:** `docs/ejemplos/lista_precios_ejemplo.csv` se
  importa desde **Configuración → Importar lista de precios (CSV)**.

Pruebas automáticas (50, corren sin abrir la ventana):

```bash
python -m unittest discover -s tests -v
```

## Qué hace el programa hoy (versión 0.3.0)

| Pestaña | Qué se hace | Administrador | Cajero |
|---|---|:---:|:---:|
| 🛒 Ventas | Registrar ventas de contado o fiadas · lista con filtros · editar/eliminar | ✓ | ✓ (sin editar/eliminar) |
| 👥 Cuentas | Clientes, lo que debe cada uno, movimientos, cobrar con comprobante | ✓ | ✓ |
| 📄 Reportes | Ingresos por día, semana o mes · HTML imprimible · Excel | ✓ | ✓ |
| ⚙ Configuración | Productos · importar lista de precios · usuarios | ✓ | — |

Los permisos están en una sola tabla: `app/permisos.py`.

## Historias por sprint

Historias completas en el formato del curso: `docs/FRSFormato_HU.docx`.
Resumen con puntos y criterios: `docs/PRODUCT_BACKLOG.md`.

| Sprint | Historias | Estado |
|:---:|---|---|
| 1 | HU-01 Registrar una venta · HU-02 Consultar las ventas registradas · HU-03 Total vendido en una fecha | Terminado |
| 2 | HU-04 Tablas de usuarios · HU-05 Asociar compras a un cliente (fiado) · HU-06 Consultar saldo de cliente | Terminado |
| 3 | HU-07 Iniciar sesión con roles · HU-08 Cobrar la cuenta con comprobante · HU-09 Reporte de ingresos por día/semana/mes · HU-10 Productos e importar lista de precios | **Terminado** |
| 4 | HU-11 Métodos de pago y nombre del negocio · HU-12 Recibo de venta · HU-13 Respaldo automático | Por hacer |
| 5 | HU-14 Recuperar la clave · HU-15 Gestión completa de usuarios · HU-16 Tema claro/oscuro | Por hacer |
| 6 | HU-17 Licencia por equipo · HU-18 Release empaquetado (.exe) | Por hacer |

## Reglas del negocio que salieron de la observación

- El tendero anota el **valor** de la venta, no cantidad × precio.
- Los productos, métodos de pago y clientes nuevos se crean solos al vender:
  la tienda funciona desde el minuto uno sin cargar nada.
- **"Cliente general" = contado.** Cualquier otro cliente = **fiado**: queda
  pendiente y el método de pago se define cuando paga.
- **Lo fiado no es plata que entró.** Los reportes cuentan ingresos por
  **fecha de pago**: lo fiado aparece el día en que se cobra.
- Al cobrar una cuenta se salda todo lo pendiente del cliente.
- No se quita a un cliente que debe; si tiene historial, se oculta y no se borra.
- El cajero no corrige ventas: solo el administrador edita o elimina.

## Definition of Done del equipo

Una historia está terminada cuando:

- [ ] Cumple todos sus criterios de aceptación, probados a mano en el programa corriendo.
- [ ] Tiene pruebas automáticas de sus reglas y `python -m unittest discover -s tests` pasa completo.
- [ ] El código está en una rama propia (`hu-XX-descripcion`), revisado por otro
      integrante y mezclado a `main` por pull request.
- [ ] Los errores posibles muestran un mensaje que el tendero entiende.
- [ ] La documentación quedó actualizada (README, backlog y bitácora del sprint).
- [ ] El uso de IA quedó registrado en la bitácora del sprint.

## Estructura del proyecto

```
Tienda-Gestion/
├── main.py                    punto de entrada: base de datos → login → ventana
├── app/
│   ├── config.py              rutas, reglas fijas (Cliente general, roles) y colores
│   ├── formato.py             dinero $2.500 y fechas en español
│   ├── errores.py             errores que el usuario puede corregir
│   ├── db.py                  esquema SQLite y migraciones
│   ├── repositorios.py        TODO el SQL del proyecto
│   ├── modelos.py             objetos que viajan entre capas
│   ├── permisos.py            qué puede hacer cada rol              (HU-07)
│   ├── servicios_catalogo.py  productos e importación CSV          (HU-10)
│   ├── servicios_ventas.py    registrar, fiar, consultar, corregir (HU-01, 02, 05, 07)
│   ├── servicios_cuentas.py   clientes, saldos, cobro              (HU-05, 06, 08)
│   ├── servicios_reportes.py  periodos, ingresos, HTML y Excel     (HU-03, 09)
│   ├── servicios_usuarios.py  usuarios y login                     (HU-04, 07)
│   ├── exportar_xlsx.py       Excel sin librerías externas         (HU-09)
│   └── ui/
│       ├── aplicacion.py      encabezado y pestañas según el rol
│       ├── login.py           inicio de sesión
│       ├── tab_ventas.py      🛒 Ventas
│       ├── tab_cuentas.py     👥 Cuentas
│       ├── tab_reportes.py    📄 Reportes
│       ├── tab_config.py      ⚙ Configuración
│       ├── widgets.py         calendario, caja de dinero, autocompletar, diálogos
│       └── estilo.py          tema verde y tablas con filas alternadas
├── tests/                     test_ventas · test_usuarios_y_cuentas · test_consultas_y_reportes
├── docs/                      historias (Word), backlog, sprint 3, riesgos, retrospectiva, ejemplos
└── datos/                     aquí se crea tienda.db
```

**Capas.** Las pantallas (`ui/`) no validan ni escriben SQL: llaman a un
servicio y muestran el mensaje del error que reciban. Los servicios tienen las
reglas; los repositorios, el SQL. Así las reglas se prueban sin abrir la
ventana y cada sprint agrega archivos sin romper lo anterior.

## Modelo de datos

```
productos      (id, nombre único, precio)
metodos_pago   (id, nombre único)                   ← Efectivo, Nequi, Daviplata, Tarjeta
transacciones  (id, producto_id, metodo_id, monto, fecha,
                cliente_id, pagada, fecha_pago)      ← cliente_id NULL = Cliente general
clientes       (id, nombre único, telefono, tipo fijo|pasajero, activo)
usuarios       (id, nombre único, password 'sal$hash', rol administrador|cajero)
```

El esquema es el mismo del producto de escritorio que ya usa la tienda: una
base creada por cualquiera de los dos la abre el otro. `db.MIGRACIONES` agrega
columnas sin perder datos (una base de la versión 0.1 se migra sola; hay prueba).

## Condiciones técnicas del enunciado — estado al cerrar el Sprint 3

| # | Condición | Estado | Dónde se ve |
|---|---|---|---|
| 1 | Persistencia real | **Cumplida** | SQLite en archivo. Prueba `test_los_datos_siguen_ahi_despues_de_cerrar` |
| 2 | Sesión o control de acceso | **Cumplida** | HU-04 y HU-07: login, roles administrador/cajero, pestañas y botones según el rol |
| 3 | Integración externa | **Cumplida** | HU-10: importa la lista de precios desde un archivo CSV externo |
| 4 | Consulta con filtrado | **Cumplida** | HU-02: lista de ventas con filtros combinables · HU-09: reportes por periodo, producto y pago |
| 5 | Manejo de errores visible | **Cumplida** | Avisos claros en cada validación; ventana "Ocurrió un problema" para errores inesperados |
| 6 | Repositorio en GitHub | **Cumplida** | Este repositorio |
| 7 | Documentación versionada | **Cumplida** | README, `docs/` y `CHANGELOG.md` |

## Documentación

| Documento | Contenido |
|---|---|
| `docs/FRSFormato_HU.docx` | Historias de usuario en el formato del curso (fuente oficial) |
| `docs/PRODUCT_BACKLOG.md` | Resumen del backlog de los 6 sprints con puntos |
| `docs/SPRINT3.md` | Sprint Goal, Sprint Backlog, tareas, WIP y guion de la demo |
| `docs/RIESGOS.md` | Matriz de riesgos (exigida desde el Sprint 3) |
| `docs/RETROSPECTIVA_SPRINT3.md` | Formato de la retrospectiva y acciones de mejora |
| `BITACORA_SPRINT1.md`, `BITACORA_SPRINT3.md` | Daily, burndown en tareas y uso de IA |
| `CHANGELOG.md` | Qué cambió en cada versión |
