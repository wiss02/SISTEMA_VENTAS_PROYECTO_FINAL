# Sistema de Gestión Inmobiliaria - TEM742

Este documento sirve como el plano de arquitectura, manual de desarrollo y plan de entrega del **Sistema de Gestión Inmobiliaria (TEM742)**. Ha sido diseñado y codificado según los lineamientos del Analista de Sistemas para dar cumplimiento a los Requisitos Técnicos de la materia.

Cualquier nuevo desarrollador o agente de Inteligencia Artificial que continúe este proyecto puede utilizar esta guía como punto de partida y contexto absoluto.

---

## 📁 1. Estructura de Directorios del Proyecto
La arquitectura del proyecto está modularizada mediante el patrón **Application Factory** y **Blueprints** en Flask:

```
inmobiliaria_tem742/
│
├── config.py               # Capa de Configuración (Variables de entorno, SQLite)
├── requirements.txt        # Gestión de Dependencias (Librerías congeladas)
├── run.py                  # Bootstrapper y sembrador automático de base de datos
│
└── app/                    # Núcleo de la Aplicación
    ├── __init__.py         # Inicializador y manejadores de error (403, 404)
    ├── models.py           # Capa de Datos (8 Tablas en 3FN con SQLAlchemy)
    │
    ├── modulos/            # Capa de Lógica de Negocio
    │   ├── __init__.py
    │   ├── auth/           # Módulo 1: Autenticación con Roles (RBAC)
    │   │   ├── __init__.py
    │   │   └── routes.py
    │   ├── propiedades/    # Módulo 2: Catálogo e Inmuebles (CRUD Principal)
    │   │   ├── __init__.py
    │   │   └── routes.py
    │   └── dashboard/      # Módulo 3: Analíticas y Métricas (Agregación SQL)
    │       ├── __init__.py
    │       └── routes.py
    │
    ├── static/             # Archivos Estáticos
    │   ├── css/            # Estilos centralizados en styles.css (Cero inline style)
    │   └── js/             # Gráficos dinámicos con Chart.js en dashboard.js
    │
    └── templates/          # Capa de Presentación (Frontend DRY con Bootstrap)
        ├── base.html       # Layout Maestro (Navbar, Sidebar y Mensajes Flash)
        ├── auth/           # Pantallas de Login y Registro
        ├── propiedades/    # Vistas CRUD de inmuebles (Index, Crear, Editar, Detalle)
        ├── dashboard/      # Panel de métricas e indicadores de rendimiento
        └── errors/         # Pantallas elegantes de error 403 (Acceso Denegado) y 404
```

---

## 🗄️ 2. Capa de Datos: Modelo Relacional (3FN)
La base de datos está normalizada en **Tercera Forma Normal (3FN)** para garantizar la integridad referencial y eliminar redundancias.

1. **`roles`**: Niveles de acceso de seguridad.
   - `id` (PK), `nombre_rol` (Unique, Not Null), `descripcion` (Nullable).
2. **`usuarios`**: Personal y Clientes. Contraseñas cifradas con `werkzeug.security`.
   - `id` (PK), `username` (Unique), `password_hash`, `nombre_completo`, `correo` (Unique), `rol_id` (FK -> `roles.id`).
3. **`tipos_propiedad`**: Clasificación de inmuebles.
   - `id` (PK), `nombre_tipo` (Unique).
4. **`estados_propiedad`**: Ciclo de vida del inmueble.
   - `id` (PK), `nombre_estado` (Unique).
5. **`propietarios`**: Dueños legales de los inmuebles.
   - `id` (PK), `nombre`, `telefono`, `correo` (Nullable), `ci_nit` (Unique).
6. **`propiedades`**: Núcleo del catálogo relacional.
   - `id` (PK), `titulo`, `descripcion`, `precio` (Float), `direccion`, `accion` (Venta/Alquiler), `fecha_registro`.
   - Llaves Foráneas: `tipo_id` (FK), `estado_id` (FK), `propietario_id` (FK), `agente_id` (FK).
7. **`visitas`**: Agenda transaccional de citas.
   - `id` (PK), `fecha_hora`, `estado_visita` (Programada, Realizada, Cancelada), `observaciones`.
   - Llaves Foráneas: `propiedad_id` (FK), `cliente_id` (FK -> `usuarios.id`).
8. **`contratos`**: Cierre económico y formalización del negocio.
   - `id` (PK), `fecha_firma`, `monto_final`, `clausulas`, `tipo_contrato` (Compraventa/Arrendamiento).
   - Llaves Foráneas: `propiedad_id` (FK), `cliente_id` (FK -> `usuarios.id`).

---

## 🔒 3. Control de Acceso (RBAC) y Seguridad
- **Cifrado de Credenciales**: Se utiliza `werkzeug.security` para el cifrado mediante hash en registro y comprobación segura en inicio de sesión.
- **Filtro de Roles**: Las vistas administrativas están protegidas mediante el decorador `@roles_permitidos(['Administrador', 'Agente'])`.
- **Restricción 403**: Si un usuario con rol "Cliente" intenta ingresar manualmente a rutas de administración, es interceptado y redirigido a una página de Bootstrap estilizada que informa la denegación de privilegios (`errors/403.html`).

---

## 📊 4. Optimización de Base de Datos y Frontend
- **Cálculo Directo (SQL Aggregations)**: Las consultas del Dashboard se delegan directamente a SQLite/PostgreSQL usando funciones de agregación (`func.count`, `func.sum`, `func.avg`, `group_by`). Está prohibido procesar bucles `for` en memoria de Python.
- **Cero Estilos Inline**: Las vistas no contienen ningún atributo `style="..."`. Todas las reglas se encuentran en `/static/css/styles.css`.
- **Diseño DRY**: Todas las sub-plantillas heredan de `base.html`.
- **Baja Crítica Segura (Modal)**: Los botones de borrado en el CRUD no llaman a rutas directamente. Disparan un modal de confirmación en JavaScript/Bootstrap, que envía un formulario seguro por el método **POST**.

---

## 🔑 5. Credenciales de Prueba Sembradas

| Rol | Usuario (`username`) | Contraseña | Privilegios |
| :--- | :--- | :--- | :--- |
| **Administrador** | `wilson` | **`admin123`** | **Amo y Señor** (wilsonrenelp@gmail.com) |
| **Agente** | `carlos.agente` | **`agente123`** | CRUD de catálogo y visualización de analíticas |
| **Cliente** | `ana.cliente` | **`cliente123`** | Consulta pública de inmuebles en catálogo |

---

## ⚙️ 6. Instrucciones para Arrancar el Proyecto

1. Instalar dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```
2. Ejecutar la aplicación (inicializará y sembrará la BD automáticamente en la primera corrida):
   ```bash
   python run.py
   ```
3. Abrir la URL en el navegador:
   `http://127.0.0.1:5000/`

---

## ✅ 7. Estado del Proyecto
* **Módulo de Visitas**: Completado (CRUD, filtros, cambio de estados).
* **Módulo de Contratos**: Completado (Registro, detalle, resumen estadístico).
* **Módulo de Propietarios**: Completado (Gestión de dueños de inmuebles, validación CI/NIT).
* **Dashboard Analítico**: Completado (Múltiples métricas, gráficos con Chart.js y actividad reciente).
* **API REST**: Completada (Endpoints JSON protegidos con RBAC y página de documentación).
* **Migración a Producción**: Pendiente cambiar la configuración en `config.py` de SQLite a PostgreSQL para el despliegue final en la nube (Render).
