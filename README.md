# Converter — Documentación del Proyecto

Conversor de código Java a diagramas UML (clases, casos de uso y flujo de control).

**Repositorios:**
- Backend: [`service-converter`](https://github.com/Isaacjbar/service-converter)
- Frontend: [`converter-web-app`](https://github.com/Isaacjbar/converter-web-app)
- Documentación: [`converter-docs`](https://github.com/Isaacjbar/converter-docs)

---

## Requisitos del Sistema

| Herramienta | Versión mínima |
|---|---|
| Python | 3.11+ |
| pip | 23+ |
| Node.js | 18+ |
| npm | 9+ |
| Git | 2.40+ |

> El backend usa SQLite por defecto (incluido con Python). No se requiere instalar un motor de base de datos adicional para desarrollo local.

---

## Configuración del Backend (`service-converter`)

### 1. Clonar el repositorio

```bash
git clone https://github.com/Isaacjbar/service-converter.git
cd service-converter
```

### 2. Crear y activar el entorno virtual

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (cmd):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

Dependencias incluidas:

| Paquete | Función |
|---|---|
| `django>=5.1` | Framework web principal |
| `djangorestframework>=3.15` | API REST |
| `djangorestframework-simplejwt>=5.3` | Autenticación JWT |
| `django-cors-headers>=4.4` | Configuración CORS para el frontend |
| `javalang>=0.13.0` | Parser del AST de Java |
| `Pillow>=10.4` | Procesamiento de imágenes |

### 4. Aplicar migraciones

```bash
python manage.py migrate
```

### 5. Poblar la base de datos con datos de prueba

#### Crear superusuario administrador

```bash
python manage.py createsuperuser
```

Ingresar cuando se solicite:
- **Email:** `admin@converter.local`
- **Username:** `admin`
- **Password:** (mínimo 8 caracteres)

#### Crear usuarios de prueba desde la shell de Django

```bash
python manage.py shell
```

```python
from apps.accounts.models import User

# Usuario analista de prueba
User.objects.create_user(
    username='analista01',
    email='analista01@converter.local',
    password='analista123',
    role='analyst'
)

# Segundo usuario analista
User.objects.create_user(
    username='analista02',
    email='analista02@converter.local',
    password='analista123',
    role='analyst'
)

print("Usuarios creados correctamente.")
exit()
```

#### Cargar historial de conversiones de prueba

```bash
python manage.py shell
```

```python
from apps.accounts.models import User
from apps.history.models import DiagramHistory

user = User.objects.get(email='analista01@converter.local')

DiagramHistory.objects.create(
    user=user,
    filename='Vehiculo.java',
    source_code='public class Vehiculo { private String marca; }',
    class_diagram='@startuml\nclass Vehiculo {\n  -marca: String\n}\n@enduml',
    usecase_diagram='@startuml\nactor Usuario\n@enduml',
    flow_diagram='@startuml\nstart\nstop\n@enduml',
)

DiagramHistory.objects.create(
    user=user,
    filename='Vehiculo.java',
    source_code='public class Vehiculo { private String marca; private int anio; }',
    class_diagram='@startuml\nclass Vehiculo {\n  -marca: String\n  -anio: int\n}\n@enduml',
    usecase_diagram='@startuml\nactor Usuario\n@enduml',
    flow_diagram='@startuml\nstart\nstop\n@enduml',
)

print("Historial de prueba creado.")
exit()
```

### 6. Levantar el servidor de desarrollo

```bash
python manage.py runserver
```

El backend quedará disponible en: `http://127.0.0.1:8000`

---

## Configuración del Frontend (`converter-web-app`)

### 1. Clonar el repositorio

```bash
git clone https://github.com/Isaacjbar/converter-web-app.git
cd converter-web-app
```

### 2. Instalar dependencias

```bash
npm install
```

### 3. Levantar el servidor de desarrollo

```bash
npm run dev
```

El frontend quedará disponible en: `http://localhost:5173`

---

## Estructura de la Documentación

```
converter-docs/
├── README.md                        # Este archivo
├── epicas/
│   ├── hu-autenticacion.md          # HU-01 a HU-05
│   ├── hu-conversion.md             # HU-06 a HU-11
│   ├── hu-visualizacion.md          # HU-12 a HU-15
│   ├── hu-historial.md              # HU-16 a HU-19
│   └── hu-administracion.md         # HU-20 a HU-23
├── minutas/
│   ├── minuta-01_2026-02-27.md
│   ├── minuta-02_2026-03-13.md
│   └── minuta-03_2026-03-27.md
└── docs/
    └── db-requisitos.md             # Eventos, triggers, vistas, índices y backups
```

---

## Equipo de Desarrollo

| Nombre | Rol |
|---|---|
| Negrete Juárez Vanesa | Desarrollo |
| Canchola Aguilar Alan | Desarrollo |
| Pérez Bosques Laura | Desarrollo |
| Ramírez López Alicia | Desarrollo |
| Apaez Sotelo Alexis Jesús | Desarrollo |
| Jiménez Barcelata Isaac | Desarrollo |
