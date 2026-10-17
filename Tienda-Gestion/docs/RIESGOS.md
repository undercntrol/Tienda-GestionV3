# Gestión de riesgos — Tienda Gestión

Exigida desde el Sprint 3. Se revisa en cada Sprint Planning y en cada
retrospectiva: se actualiza la probabilidad, el impacto y el estado.

**Escala:** Probabilidad (P) e Impacto (I) de 1 (bajo) a 3 (alto).
**Exposición = P × I.** 6–9 alta (atender ya) · 3–4 media (vigilar) · 1–2 baja.

| ID | Riesgo (causa → efecto) | P | I | Exp. | Estrategia | Respuesta concreta | Responsable | Estado |
|---|---|:---:|:---:|:---:|---|---|---|---|
| R1 | El proyecto parte de un programa que ya existía (hecho fuera del curso) → no todo el equipo lo conoce y no puede sostenerlo ni explicarlo | 3 | 3 | **9** | Mitigar | Reorganizado en módulos pequeños; cada integrante es dueño de una pestaña y su servicio y la explica en la review | Todo el equipo | Abierto |
| R2 | La clave de licencia del programa que vende la tienda queda en un repositorio público (Sprint 6) → cualquiera podría generar licencias | 2 | 3 | **6** | Evitar | En el repositorio la clave NO va en el código: se lee de un archivo local excluido por `.gitignore`. La clave real nunca se sube | [Integrante] | Abierto |
| R3 | El historial de commits queda concentrado en una persona o en pocos commits grandes → el docente no ve trabajo distribuido | 3 | 2 | **6** | Mitigar | Una rama por historia y commits desde la cuenta de cada autor | Scrum Master | Abierto |
| R4 | El programa no corre el día de la sustentación (versión de Python, falta `tkinter`) → no se califica | 2 | 3 | **6** | Mitigar | Verificar la noche anterior en el computador de la presentación: `python --version` ≥ 3.10, pruebas y abrir el programa | [Integrante] | Abierto |
| R5 | Se pierde o se daña la base de datos de la tienda → se pierden las cuentas de los clientes | 2 | 3 | **6** | Mitigar | HU-13 (respaldo automático al cerrar) en el Sprint 4. Mientras tanto, copiar `datos/tienda.db` a una USB | [Integrante] | Abierto |
| R6 | El administrador olvida su clave → nadie entra a Configuración | 2 | 3 | **6** | Mitigar | HU-14 (recuperar la clave) en el Sprint 5. Mientras tanto, tener un segundo administrador | [Integrante] | Abierto |
| R7 | Uso de IA sin revisar → código que el equipo no entiende | 2 | 3 | **6** | Mitigar | Registrar en la bitácora qué se pidió, qué se aceptó y qué se rechazó; nadie sube código que no pueda explicar | Todo el equipo | Abierto |
| R8 | El repositorio y el programa de la tienda se separan (datos incompatibles) → la tienda no puede usar lo que construye el equipo | 2 | 2 | 4 | Mitigar | Mismo esquema de base de datos que el programa de la tienda; probado en ambos sentidos | [Integrante] | Mitigado |
| R9 | Se fía a un cliente equivocado o se cobra mal → conflicto con el vecino | 2 | 2 | 4 | Mitigar | Autocompletar para no duplicar clientes, movimientos visibles y comprobante; el administrador puede corregir la venta | [Integrante] | Mitigado parcialmente |
| R10 | Entran funciones que no están en el backlog → no se terminan las comprometidas | 2 | 2 | 4 | Evitar | Nada entra al sprint si no se acordó en el Planning | Product Owner | Abierto |
| R11 | La lista del proveedor llega en otro formato → la importación no sirve | 2 | 1 | 2 | Aceptar | El importador informa línea por línea; hay formato documentado y archivo de ejemplo | [Integrante] | Mitigado |

## Riesgos materializados

| Fecha | Riesgo | Qué pasó | Qué se hizo |
|---|---|---|---|
| [dd/mm] | | | |

## Riesgos cerrados

| Riesgo | Motivo del cierre |
|---|---|
| Incumplir la condición 3 (integración externa) | Cerrado en el Sprint 3 con HU-10 |
| Incumplir la condición 4 (consulta con filtrado) | Cerrado con HU-02 y HU-09 |
