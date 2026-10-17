# Bitácora — Sprint 3

Registro exigido por los numerales 8 y 9 del enunciado. El tablero está en
Planner (Teams); los puntos van como texto en cada tarjeta.

> **Para el equipo:** las filas vacías o con `[ ]` se llenan con lo que
> **realmente** pasó.

## Sprint Goal

Que cada persona entre con su usuario y rol, que el tendero pueda cobrar las
cuentas fiadas con comprobante, ver cuánta plata entró por día, semana o mes
(y llevarlo a Excel), y cargar la lista de precios del proveedor desde un archivo.

## Daily Scrum

| Fecha | Quién | Qué hice | Qué voy a hacer | Impedimentos |
|---|---|---|---|---|
| [dd/mm] | [Integrante 1] | | | |
| [dd/mm] | [Integrante 2] | | | |
| [dd/mm] | [Integrante 3] | | | |
| [dd/mm] | [Integrante 4] | | | |

## Burndown (en tareas, no en puntos)

Total de tareas del sprint: **16** (lista en `docs/SPRINT3.md`).
*Ideal* baja en línea recta; *Real* = tarjetas que no están en "Terminado" al
final de cada día en Planner.

| Día | Fecha | Ideal (pendientes) | Real (pendientes) | Terminadas ese día |
|:---:|---|:---:|:---:|:---:|
| 0 | [inicio] | 16 | 16 | 0 |
| 1 | | 14 | | |
| 2 | | 11 | | |
| 3 | | 9 | | |
| 4 | | 7 | | |
| 5 | | 5 | | |
| 6 | | 2 | | |
| 7 | 17/10 | 0 | | |

Lectura del burndown (al cierre): ¿la línea real quedó por encima o por debajo
de la ideal? ¿En qué días se estancó y por qué?

## Historias y tareas

| Historia | Pts | Tareas | Responsable |
|---|:---:|---|---|
| HU-07 Iniciar sesión con roles | 5 | T1–T3 | |
| HU-08 Cobrar la cuenta con comprobante | 3 | T4–T5 | |
| HU-09 Reporte de ingresos por día, semana o mes | 5 | T6–T9 | |
| HU-10 Productos e importar lista de precios | 3 | T10–T11 | |
| Pruebas | — | T12 | |
| Transversales | — | T13–T16 | |

## Registro de uso de IA

El enunciado evalúa sobre todo la última columna: qué se descartó y con qué criterio.

| Fecha | Qué le pedimos | Qué aceptamos | Qué rechazamos y por qué |
|---|---|---|---|
| 17/10 | A Claude (Anthropic): reorganizar en módulos la lógica del programa de la tienda para las historias de los Sprints 1 a 3, con pruebas, y armar la documentación del Sprint 3 | [lo que el equipo revisó y conservó] | [lo que el equipo cambió o descartó, con su razón] |
| 17/10 | (Propuesta de Claude, no pedida) una historia de "recordatorio de cobro por WhatsApp" como integración externa | — | La quitamos del backlog: no salió de la observación, y abrir un enlace de WhatsApp no es consumir una API (no se envía ni se recibe información). La condición 3 se cumple con el CSV del proveedor |
| [dd/mm] | | | |

### Decisiones del código para revisar

Al reorganizar el código se tomaron estas decisiones. El equipo debe
revisarlas: las que no comparta se cambian y se registran arriba como rechazadas.

| Decisión | Alternativa descartada y por qué | Dónde se ve |
|---|---|---|
| Separar pantallas, reglas (servicios) y SQL (repositorios) | Un solo archivo de 2.700 líneas: difícil de repartir entre 4 personas y de probar | `app/` |
| Mismo esquema de base de datos que el programa de la tienda | Un esquema "más limpio" (p. ej. tabla de abonos): rompería la compatibilidad con los datos reales de la tienda | `app/db.py` |
| Cobrar la cuenta completa, no abonos parciales | Abonos parciales: así no trabaja la tienda y complica el saldo | `servicios_cuentas.cobrar` |
| Reportes por fecha de pago, no de venta | Por fecha de venta: contaría lo fiado como plata recibida | `repositorios.ingresos` |
| Excel escrito a mano (ZIP + XML) | openpyxl: obliga a instalar librerías en el computador de la tienda | `app/exportar_xlsx.py` |
| Permisos en una tabla única | `if es_admin` repartidos por las pantallas: fácil olvidar uno | `app/permisos.py` |
| Mismo mensaje si el usuario no existe o la clave está mal | Mensajes distintos: le dicen a un extraño qué usuarios existen | `servicios_usuarios.autenticar` |
| Al migrar una base vieja, las ventas de contado reciben fecha de pago | Dejarla vacía: esas ventas desaparecerían de los reportes de ingresos | `db._migrar` |

## Review (llenar al cierre)

- Historias terminadas según la DoD: [ ] HU-07 · [ ] HU-08 · [ ] HU-09 · [ ] HU-10
- Qué opinó el docente / el tendero:
- Qué entra al Product Backlog a raíz de la review:
