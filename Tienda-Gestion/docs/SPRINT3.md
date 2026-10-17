# Sprint 3 — Tienda Gestión

**Cierre:** sábado 17/10/2026 · Sprint Review, sustentación y retrospectiva
**Versión entregada:** 0.3.0

## Sprint Goal

Que cada persona entre con su usuario y rol, que el tendero pueda cobrar las
cuentas fiadas con comprobante, ver cuánta plata entró por día, semana o mes
(y llevarlo a Excel), y cargar la lista de precios del proveedor desde un archivo.

Con este sprint quedan cumplidas las condiciones técnicas 2 (control de acceso),
3 (archivo externo) y 4 (consulta con filtrado).

## Sprint Backlog

| Historia | Pts | Responsable |
|---|:---:|---|
| HU-07 Iniciar sesión con roles | 5 | [Asignar] |
| HU-08 Cobrar la cuenta de un cliente con comprobante | 3 | [Asignar] |
| HU-09 Reporte de ingresos por día, semana o mes (HTML y Excel) | 5 | [Asignar] |
| HU-10 Administrar productos e importar la lista de precios | 3 | [Asignar] |
| **Total comprometido** | **16** | |

Criterios de aceptación en `docs/FRSFormato_HU.docx` (y resumen en `docs/PRODUCT_BACKLOG.md`).

## Tareas

Cada tarea es una tarjeta en Planner dentro del depósito de su historia. El
burndown de la bitácora cuenta estas tarjetas.

| # | Tarea | Historia | Archivo principal | Responsable |
|:---:|---|---|---|---|
| T1 | Pantalla de inicio de sesión y verificación de la clave | HU-07 | `ui/login.py`, `servicios_usuarios.py` | |
| T2 | Tabla de permisos y pestañas/botones según el rol | HU-07 | `permisos.py`, `ui/aplicacion.py` | |
| T3 | Editar y eliminar venta solo para administrador | HU-07 | `servicios_ventas.py`, `ui/tab_ventas.py` | |
| T4 | Cobro de la cuenta completa con método y fecha de pago | HU-08 | `servicios_cuentas.py` → `cobrar` | |
| T5 | Comprobante HTML imprimible | HU-08 | `servicios_cuentas.py`, `ui/tab_cuentas.py` | |
| T6 | Cálculo del periodo Día / Semana / Mes | HU-09 | `servicios_reportes.py` → `periodo` | |
| T7 | Ingresos por fecha de pago: por producto, día y método | HU-09 | `repositorios.py` → `ingresos` | |
| T8 | Pestaña Reportes | HU-09 | `ui/tab_reportes.py` | |
| T9 | Exportar a HTML imprimible y a Excel sin librerías | HU-09 | `servicios_reportes.py`, `exportar_xlsx.py` | |
| T10 | Productos: agregar, editar, eliminar | HU-10 | `servicios_catalogo.py`, `ui/tab_config.py` | |
| T11 | Leer el CSV (separador, codificación, errores por línea) y resumen | HU-10 | `servicios_catalogo.py` → `importar_csv` | |
| T12 | Pruebas automáticas de HU-07 a HU-10 y archivo de ejemplo | Todas | `tests/`, `docs/ejemplos/` | |
| T13 | Organizar el código en módulos y dejar la base compatible con el producto de la tienda | — | `app/` | |
| T14 | Matriz de riesgos | — | `docs/RIESGOS.md` | |
| T15 | Historias en el formato del curso, README, backlog, changelog, `.gitignore` | — | `docs/FRSFormato_HU.docx`, raíz | |
| T16 | Bitácora: Daily, burndown y registro de IA | — | `BITACORA_SPRINT3.md` | |

**Total: 16 tareas.**

## Tablero en Planner

Depósitos: **Product Backlog · Sprint Backlog · En curso · En revisión · Terminado**

**WIP:** máximo **4 tarjetas en "En curso"** (una por integrante) y **2 en
"En revisión"**. Si una columna está llena, nadie empieza otra tarea: primero
se ayuda a sacar lo que está trabado. Una tarjeta pasa a "Terminado" solo si
cumple la Definition of Done.

## Incremento entregado (0.3.0)

- Inicio de sesión con roles administrador y cajero; editar y eliminar ventas solo para el administrador.
- Cobro de la cuenta completa con comprobante imprimible.
- Pestaña Reportes: ingresos por día, semana o mes, por producto, día y
  método; exportación a HTML y a Excel.
- Productos e importación de la lista de precios desde CSV con reporte de líneas con error.
- 50 pruebas automáticas, todas pasan.

## Guion sugerido para la demo (≈ 8 min)

1. Abrir el programa y entrar como **administrador**.
2. **Configuración → Importar lista de precios (CSV)** con
   `docs/ejemplos/lista_precios_ejemplo.csv`. La última línea tiene un precio
   inválido: se informa y no detiene el resto.
3. **Ventas:** una de contado (el monto se autocompleta), una con producto
   nuevo escrito a mano y una **fiada** a un cliente nuevo (se crea como pasajero).
4. Filtrar la lista por cliente y por pago; **editar** el monto de una venta.
5. **Cuentas:** ver movimientos y **cobrar** la cuenta → comprobante en el navegador.
6. **Reportes → Mes:** mostrar que lo fiado aparece el día del cobro. Abrir el
   HTML y el Excel.
7. **Cerrar sesión** y entrar como **cajero**: no ve Configuración y los
   botones de editar/eliminar están deshabilitados.
8. Correr `python -m unittest discover -s tests`.
