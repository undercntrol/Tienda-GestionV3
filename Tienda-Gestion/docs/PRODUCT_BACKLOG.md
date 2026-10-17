# Product Backlog — Tienda Gestión

**Product Goal:** lograr que la cigarrería lleve digitalmente sus ventas y
cuentas por cobrar, de modo que al cierre de cada día el tendero conozca el
total vendido por método de pago y el saldo exacto de cada cliente,
reduciendo el tiempo de cuadre diario de 20 a menos de 5 minutos y
eliminando las deudas no registradas, dentro de las 16 semanas del semestre.

**Origen:** la observación en la cigarrería y el programa de escritorio que ya
usa la tienda. Cada historia corresponde a algo que ese programa hace; el
repositorio lo construye por partes, sprint a sprint, con pruebas y documentación.

**Fuente oficial:** las historias completas, con el formato del curso, están en
`docs/FRSFormato_HU.docx`. Este archivo es el resumen y debe coincidir con él.

**Estimación:** puntos Fibonacci (1, 2, 3, 5, 8); en Planner van como texto en
el título de la tarjeta, por ejemplo `HU-09 [5 pts]`.
> Los puntos son una propuesta: el equipo los revisa y corrige antes de la
> sustentación.

## Resumen por sprint

| Sprint | Historia | Pts | Responsable | Estado |
|:---:|---|:---:|---|---|
| 1 | HU-01 Registrar una venta | 3 | Juan Nicolas Rodríguez Castro | Terminada (0.3.0) |
| 1 | HU-02 Consultar las ventas ya registradas | 2 | Nicolas Benitez Velasco | Terminada (0.3.0) |
| 1 | HU-03 Consultar el total vendido en una fecha determinada | 2 | Nicolas Benitez Velasco | Terminada (0.3.0) |
| 2 | HU-04 Desarrollo de tablas de usuarios de aplicación | 3 | Juan Nicolas Rodríguez Castro | Terminada (0.3.0) |
| 2 | HU-05 Asociar compras a un cliente (fiado) | 5 | Nicolas Benitez Velasco | Terminada (0.3.0) |
| 2 | HU-06 Consultar saldo de cliente | 3 | Cristian Camilo Mora González | Terminada (0.3.0) |
| 3 | HU-07 Iniciar sesión con roles | 5 | [Asignar] | Terminada (0.3.0) |
| 3 | HU-08 Cobrar la cuenta de un cliente con comprobante | 3 | [Asignar] | Terminada (0.3.0) |
| 3 | HU-09 Reporte de ingresos por día, semana o mes | 5 | [Asignar] | Terminada (0.3.0) |
| 3 | HU-10 Administrar productos e importar la lista de precios | 3 | [Asignar] | Terminada (0.3.0) |
| 4 | HU-11 Métodos de pago y nombre del negocio | 3 | [Asignar] | Por hacer |
| 4 | HU-12 Recibo de venta imprimible | 2 | [Asignar] | Por hacer |
| 4 | HU-13 Respaldo automático y manual | 3 | [Asignar] | Por hacer |
| 5 | HU-14 Recuperar la clave | 5 | [Asignar] | Por hacer |
| 5 | HU-15 Gestión completa de usuarios | 3 | [Asignar] | Por hacer |
| 5 | HU-16 Tema claro y oscuro | 2 | [Asignar] | Por hacer |
| 6 | HU-17 Licencia por equipo | 5 | [Asignar] | Por hacer |
| 6 | HU-18 Release versionado y empaquetado | 3 | [Asignar] | Por hacer |

**Velocidad (puntos terminados):** S1 = 7 · S2 = 11 · S3 = 16.

---

## Sprint 1

### HU-01 · Registrar una venta — 3 pts · prioridad Alta

> Como cajero o administrador de la tienda, quiero registrar cada venta con el producto, el valor y el método de pago, para que quede guardada sin tener que anotarla en la libreta y facilitar el cierre del día.

**Criterios de aceptación**

1. El sistema debe permitir registrar una venta con producto, monto, método de pago y fecha; la fecha es la de hoy por defecto y se puede cambiar con el calendario.
2. Si el producto no existe, se crea con ese valor como precio; si existe y tiene precio, el monto se autocompleta. Mientras se escribe aparecen coincidencias para no duplicar productos.
3. La venta debe quedar guardada, aparecer en la lista de ventas y conservarse al cerrar y volver a abrir el programa.
4. Sin producto, con monto en cero o, en una venta de contado, sin método de pago, la venta no se registra y se muestra un mensaje que explica por qué.

**Validaciones**

- El monto debe ser un número mayor a cero; se acepta escrito como 2500, 2.500 o $2.500.
- Cada venta de contado debe tener producto, monto, método de pago y fecha; si se escribe un método de pago nuevo, se crea.

**Reglas de negocio**

- Registrar ventas: administrador y cajero.
- Editar o eliminar una venta ya registrada: solo el administrador (HU-07).

_Cambio en la versión 1.1: la venta se registra por monto y no por cantidad × precio unitario, porque así anota el tendero._

### HU-02 · Consultar las ventas ya registradas — 2 pts · prioridad Media

> Como cajero o administrador de la tienda, quiero consultar las ventas ya registradas filtrando por fechas, producto, método de pago o cliente, para revisar qué se ha vendido sin tener que buscarlo en la libreta.

**Criterios de aceptación**

1. El sistema debe mostrar las ventas registradas con fecha, día de la semana, producto, cliente, método de pago, estado (Pagada o Fiada) y monto, ordenadas por fecha.
2. Se debe poder filtrar por rango de fechas (con calendario), producto, método de pago y cliente, combinando los filtros; el botón «Hoy» vuelve a las ventas del día.
3. Debajo de la lista se muestran el total vendido y el número de ventas de lo filtrado; la lista incluye ventas de sesiones anteriores y una venta eliminada no aparece.
4. Si no hay ventas con esos filtros, la lista queda vacía, el total en $0 y el programa no falla.

**Validaciones**

- Las fechas deben tener el formato AAAA-MM-DD; si no son válidas se avisa y se vuelve al día de hoy; si vienen al revés, se intercambian.
- Las ventas fiadas se muestran en color ámbar y sin método de pago hasta que se cobran.

**Reglas de negocio**

- Consultar las ventas: administrador y cajero.
- Editar o eliminar desde la lista: solo el administrador; al cajero esos botones le aparecen deshabilitados.

_Cambio en la versión 1.1: se agregaron los filtros y el estado Pagada/Fiada; la cantidad ya no se muestra porque la venta se registra por monto._

### HU-03 · Consultar el total vendido en una fecha determinada — 2 pts · prioridad Alta

> Como administrador de la tienda, quiero consultar el total que entró en una fecha determinada, para cuadrar la caja de ese día sin hacer las cuentas de memoria.

**Criterios de aceptación**

1. El sistema debe permitir elegir una fecha con el calendario y mostrar el total que entró ese día, el número de ventas y el desglose por método de pago y por producto.
2. La suma del desglose por método de pago debe coincidir con el total.
3. Una venta fiada no suma el día en que se fía sino el día en que se cobra, porque es cuando entra la plata a la caja.
4. Si en la fecha elegida no hay ventas, el total aparece en $0 con el mensaje «Sin ventas en el período» y la pantalla no falla.

**Validaciones**

- La fecha debe ser válida (AAAA-MM-DD); si no lo es, se avisa y se vuelve al día de hoy.
- El total es la suma de las ventas pagadas cuya fecha de pago es la elegida; las ventas eliminadas no cuentan.

**Reglas de negocio**

- Consultar los totales: administrador y cajero.
- Nadie puede modificar los totales desde este apartado.

_Cambio en la versión 1.1: el total cuenta lo que entró a la caja (ventas pagadas por fecha de pago), y la consulta quedó en el apartado Reportes, que en el Sprint 3 se amplía a semana y mes (HU-09)._

---

## Sprint 2

### HU-04 · Desarrollo de tablas de usuarios de aplicación — 3 pts · prioridad Alta

> Como administrador, quiero que el sistema guarde los datos de las personas que usan el programa (usuario, clave y rol), para que cada una pueda iniciar sesión y el sistema sepa qué puede hacer.

**Criterios de aceptación**

1. La base de datos debe tener una tabla de usuarios con identificador único, nombre de usuario único, clave protegida y rol (administrador o cajero).
2. La primera vez que se abre el programa se pide crear el usuario administrador.
3. El administrador puede crear usuarios con su rol y eliminarlos desde Configuración → Usuarios.

**Validaciones**

- El nombre de usuario es obligatorio y no se puede repetir; la clave debe tener al menos 4 caracteres (y confirmarse al crear el primer administrador).
- La clave nunca se guarda en texto: se guarda como hash con sal (PBKDF2).

**Reglas de negocio**

- Crear y eliminar usuarios: solo el administrador.
- Nadie puede eliminar su propio usuario y siempre debe quedar al menos un administrador.

_Cambio en la versión 1.1: el título estaba intercambiado con el de HU-05 y se corrigió. Se aclara que «usuarios» son quienes usan el programa y «clientes» son a quienes se les vende (HU-05)._

### HU-05 · Asociar compras a un cliente (fiado) — 5 pts · prioridad Media

> Como cajero o administrador, quiero asociar una venta a un cliente cuando se la fío, para saber qué compró cada cliente y cuánto debe.

**Criterios de aceptación**

1. Por defecto la venta es a «Cliente general» (de contado). Al elegir o escribir otro cliente, la venta queda fiada: pendiente de pago y sin método de pago.
2. El cliente se busca por su nombre mientras se escribe; si no existe, se crea como «pasajero». En Cuentas se registran clientes «fijos» con nombre y teléfono.
3. La asociación se conserva y se ve en la lista de ventas (columna Cliente y estado Fiada) y en los movimientos del cliente.

**Validaciones**

- El nombre del cliente es obligatorio y no se puede repetir; «Cliente general» es un nombre reservado para las ventas de contado.
- Cada venta tiene cliente: «Cliente general» o un cliente registrado.

**Reglas de negocio**

- Fiar y registrar clientes: administrador y cajero.
- Un cliente que debe no se puede quitar; si tiene historial, se oculta pero sus ventas se conservan.

_Cambio en la versión 1.1: el título estaba intercambiado con el de HU-04 y se corrigió._

### HU-06 · Consultar saldo de cliente — 3 pts · prioridad Media

> Como cajero o administrador, quiero consultar cuánto debe cada cliente y qué compras tiene pendientes, para cobrarle el valor exacto.

**Criterios de aceptación**

1. El usuario debe ver cada cliente con su teléfono, tipo (fijo o pasajero), número de compras pendientes y saldo.
2. Puede abrir los movimientos de un cliente: fecha, producto, estado (Pagada o Pendiente) y monto, con el saldo pendiente.
3. Se muestra el total por cobrar de la tienda, y los saldos se actualizan apenas se registra una venta fiada o se cobra una cuenta.

**Validaciones**

- El saldo es la suma de las compras pendientes del cliente; se calcula y no se guarda aparte, para que nunca quede desactualizado.
- Un cliente sin compras pendientes tiene saldo $0.

**Reglas de negocio**

- Consultar saldos: administrador y cajero.
- El estado de una compra solo cambia de Pendiente a Pagada al cobrar la cuenta (HU-08).

_Cambio en la versión 1.1: el cliente no usa el programa; quien consulta es el usuario de la tienda. Se quitaron los abonos y los datos bancarios porque la tienda no los maneja: el cobro es de la cuenta completa (HU-08)._

---

## Sprint 3

### HU-07 · Iniciar sesión con roles — 5 pts · prioridad Alta

> Como dueño de la tienda, quiero que cada persona entre con su usuario y clave, para que el cajero no pueda corregir ventas ni cambiar la configuración.

**Criterios de aceptación**

1. Sin iniciar sesión no se ve ninguna pantalla; con datos incorrectos aparece «Usuario o clave incorrectos» (el mismo mensaje si el usuario no existe).
2. El administrador ve Ventas, Cuentas, Reportes y Configuración; el cajero ve Ventas, Cuentas y Reportes.
3. Solo el administrador puede editar o eliminar una venta; al cajero esos botones le aparecen deshabilitados.
4. «Cerrar sesión» vuelve a la pantalla de ingreso, y el encabezado muestra el nombre y el rol de quien está usando el programa.

**Validaciones**

- Usuario y clave son obligatorios; la clave se compara contra el hash guardado.
- Eliminar una venta pide confirmación; al editar una venta de contado, su fecha de pago se mueve con la fecha de la venta.

**Reglas de negocio**

- Los permisos de cada rol están definidos en una sola tabla del programa.
- Editar, eliminar ventas y entrar a Configuración: solo el administrador.

### HU-08 · Cobrar la cuenta de un cliente con comprobante — 3 pts · prioridad Alta

> Como cajero o administrador, quiero cobrarle la cuenta a un cliente y entregarle un comprobante, para que quede constancia de lo que pagó.

**Criterios de aceptación**

1. Desde Cuentas se elige el cliente, el método de pago y la fecha del pago.
2. Se salda todo lo pendiente del cliente, que queda con saldo $0.
3. Se abre un comprobante imprimible con el nombre del negocio, el cliente, la fecha, el método, el detalle de las compras y el total pagado.
4. Lo cobrado cuenta como ingreso en la fecha del pago y aparece ese día en los reportes.

**Validaciones**

- No se puede cobrar a un cliente sin saldo pendiente.
- El método de pago es obligatorio y la fecha del pago debe ser válida.

**Reglas de negocio**

- Cobrar cuentas: administrador y cajero.
- Se cobra la cuenta completa; no se manejan abonos parciales.

### HU-09 · Reporte de ingresos por día, semana o mes — 5 pts · prioridad Alta

> Como administrador, quiero ver cuánto entró en un día, una semana o un mes, por producto y por método de pago, para saber qué se vende más y cuánta plata tengo.

**Criterios de aceptación**

1. Se elige el período: Día, Semana (de lunes a domingo) o Mes (respetando febrero y los años bisiestos), con filtros por producto y por método de pago.
2. Se muestran el total por producto (de mayor a menor), el total por día, el total por método y los ingresos totales del período.
3. El reporte se exporta a HTML imprimible y a Excel (.xlsx con 5 hojas) sin instalar programas adicionales.
4. Si no hay ventas en el período, las tablas quedan vacías con el mensaje «Sin ventas en el período» y el programa no falla.

**Validaciones**

- La fecha, el mes y el año del período deben ser válidos.
- Si el archivo de Excel está abierto, se avisa que se cierre en lugar de fallar.

**Reglas de negocio**

- Ver reportes: administrador y cajero.
- El reporte cuenta solo ventas pagadas, por su fecha de pago.

### HU-10 · Administrar productos e importar la lista de precios — 3 pts · prioridad Media

> Como administrador, quiero administrar mis productos y cargar la lista de precios que me manda el proveedor, para no digitar producto por producto cuando suben los precios.

**Criterios de aceptación**

1. El administrador agrega, edita y elimina productos; el precio es opcional y las ventas de un producto eliminado se conservan como «(eliminado)».
2. Se importa un archivo CSV con nombre y precio, con o sin encabezado, separado por «;» o «,»: los productos nuevos se crean y los existentes actualizan su precio.
3. Una línea con error no detiene la importación: al final se informa cuántos productos se crearon, cuántos se actualizaron y qué líneas fallaron y por qué.

**Validaciones**

- No se permiten dos productos con el mismo nombre; el precio debe ser un número (mayor que cero en el archivo CSV).
- Se aceptan archivos guardados por Excel antiguo (codificación latin-1); un archivo vacío o inexistente se informa.

**Reglas de negocio**

- Administrar productos e importar precios: solo el administrador.
- Un producto se identifica por su nombre, sin importar mayúsculas.

---

## Sprints 4 a 6 (por hacer)

### HU-11 · Métodos de pago y nombre del negocio — 3 pts
> Como dueño quiero administrar las formas de pago y poner el nombre de mi negocio, para que aparezca en la pantalla, los reportes y los comprobantes.

### HU-12 · Recibo de venta imprimible — 2 pts
> Como tendero quiero imprimir el recibo de una venta, para dárselo al cliente que lo pida.

### HU-13 · Respaldo automático y manual — 3 pts
> Como dueño quiero que se guarde una copia de los datos al cerrar el programa (y poder hacerla cuando quiera), para no perder las cuentas si se daña el computador.

### HU-14 · Recuperar la clave — 5 pts
> Como usuario quiero recuperar mi clave con una pregunta de seguridad o con un código que me da el proveedor, para no quedarme por fuera del programa.

### HU-15 · Gestión completa de usuarios — 3 pts
> Como administrador quiero cambiar la clave de un usuario y configurar su pregunta de seguridad.

### HU-16 · Tema claro y oscuro — 2 pts
> Como tendero quiero cambiar a colores oscuros, para cansar menos la vista en la noche.

### HU-17 · Licencia por equipo — 5 pts
> Como proveedor quiero que el programa se active con un código único por computador, para que no se copie sin licencia.

### HU-18 · Release versionado y empaquetado — 3 pts
> Como dueño quiero instalar el programa con un solo archivo, sin instalar Python.
