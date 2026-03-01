# API REST - Clase 3 Programación Distribuida

API REST desarrollada con FastAPI que implementa un CRUD básico para gestión de clientes con focus en conceptos de programación distribuida.

## 🚀 Características

- ✅ CRUD completo (Create, Read, Update, Delete)
- ✅ Validación de datos (nombres no vacíos)
- ✅ Contador global de clientes creados
- ✅ Simulación de delay asíncrono (3 segundos)
- ✅ Endpoints funcionales y documentados

## 📋 Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Mensaje de bienvenida |
| GET | `/clientes` | Obtener lista de clientes |
| POST | `/clientes` | Crear nuevo cliente |
| GET | `/clientes/{cliente_id}` | Obtener cliente por ID |
| PUT | `/clientes/{cliente_id}` | Actualizar cliente |
| DELETE | `/clientes/{cliente_id}` | Eliminar cliente |

## 🔧 Instalación y Uso

### Requisitos
- Python 3.8+
- FastAPI
- Uvicorn

### Instalación
```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install fastapi uvicorn
```

### Ejecutar servidor
```bash
uvicorn main:app --host 127.0.0.1 --port 9000 --reload
```

El servidor estará disponible en: `http://localhost:9000`
Documentación interactiva: `http://localhost:9000/docs`

## 💡 Preguntas Clave de Programación Distribuida

### ❓ 1. ¿Es seguro usar variable global?

**Respuesta corta**: ❌ NO es totalmente seguro en entornos concurrentes (múltiples solicitudes simultáneas).

**Explicación detallada**:

```python
contador_clientes_creados = 0  # Variable global compartida
```

**El problema**: En FastAPI, cada solicitud HTTP se procesa potencialmente en **paralelo**. Si dos clientes envían requests simultáneamente, pueden ocurrir **race conditions**:

```
Tiempo | Thread 1 | Thread 2 | Variable
-------|----------|----------|----------
t1     | Lee: 0   |          | contador = 0
t2     |          | Lee: 0   | contador = 0
t3     | Suma: 1  |          | contador = ?
t4     |          | Suma: 1  | contador = ?
t5     | Guarda 1 |          | contador = 1
t6     |          | Guarda 1 | contador = 1  ← ¡ERROR! Debería ser 2
```

En nuestro pequeño proyecto está "relativamente seguro" porque:
- Es una demostración educativa
- El incremento es simple (una línea)
- Uvicorn en desarrollo usa un solo worker

**Pero en producción**: ⚠️ **Absolutamente inseguro** si tienes múltiples workers o reutilizas procesos.

---

### ❓ 2. ¿Dónde aparece el recurso compartido?

**Respuesta**: En **3 lugarse**:

#### 1️⃣ **Variable Global: `contador_clientes_creados`**
```python
contador_clientes_creados = 0  # ← Recurso compartido entre requests
```
- **Problema**: Todos los requests acceden y modifican esta misma variable
- **Acceso**: Lectura y escritura sin sincronización
- **Riesgo**: Race conditions si dos requests incrementan simultáneamente

#### 2️⃣ **Lista Global: `clientes`**
```python
clientes = []  # ← Recurso compartido entre requests
```
- **Problema**: Múltiples requests pueden leer/escribir simultáneamente
- **Operaciones**:
  - `clientes.append()` en POST
  - `clientes.remove()` en DELETE
  - `for cliente in clientes:` en GET
- **Riesgo**: Modificaciones durante iteración, elementos perdidos, corrupción de datos

#### 3️⃣ **Variable de sesión en el servidor**
```
[Request 1 - Cliente A] ─→ Modifica 'clientes'
                         ↓
                   Lista compartida
                         ↓
[Request 2 - Cliente B] ─→ Lee 'clientes'  ← Puede ver datos inconsistentes
```

---

### ❓ 3. ¿Se debería usar lock en producción?

**Respuesta**: ✅ **SÍ, absolutamente**.

#### Solución 1: Usar `threading.Lock()` (Básico)

```python
import threading
from fastapi import FastAPI

app = FastAPI()
clientes = []
contador = 0
lock = threading.Lock()  # ← Mutex/Lock para sincronización

@app.post("/clientes")
async def crear_cliente(nombre: str):
    global contador
    
    if not nombre or nombre.strip() == "":
        return {"error": "Nombre vacío"}
    
    await asyncio.sleep(3)  # Simulación
    
    with lock:  # ← Sección crítica protegida
        contador += 1
        cliente = {
            "id": len(clientes) + 1,
            "nombre": nombre.strip(),
            "numero_cliente_creado": contador
        }
        clientes.append(cliente)
    
    return cliente
```

**Ventajas**:
- ✅ Simple de implementar
- ✅ Protege acceso exclusivo

**Desventajas**:
- ❌ Reduce concurrencia (solo 1 request accede al lock)
- ❌ Riesgo de deadlock
- ❌ No es escalable con múltiples procesos

---

#### Solución 2: Usar Base de Datos (Recomendado para Producción) 📊

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Las BD manejan sincronización automáticamente
# Las transacciones garantizan consistencia
```

**Ventajas**:
- ✅ Sincronización automática
- ✅ Escalable con múltiples workers
- ✅ Persistencia de datos
- ✅ Soporte para transacciones ACID

**Desventajas**:
- ❌ Mayor complejidad
- ❌ Overhead de BD

---

#### Solución 3: Usar `asyncio.Lock()` (AsyncIO)

```python
import asyncio

app = FastAPI()
async_lock = asyncio.Lock()

@app.post("/clientes")
async def crear_cliente(nombre: str):
    async with async_lock:
        # Sección crítica protegida
        contador += 1
```

**Ventajas**:
- ✅ Mejor que threading.Lock() para async
- ✅ Evita bloqueos del event loop

**Desventajas**:
- ❌ Solo funciona en un solo proceso

---

#### Solución 4: Usar `RWLock` (Lectura/Escritura)

Para nuestro caso, hay más lecturas (GET) que escrituras (POST/PUT/DELETE):

```python
from fastapi import FastAPI
import asyncio

class RWLock:
    def __init__(self):
        self._read_ready = asyncio.Event()
        self._readers = 0
        self._writers = 0
        self._lock = asyncio.Lock()
    
    async def read(self):
        async with self._lock:
            self._readers += 1
        # Leer datos
    
    async def write(self):
        async with self._lock:
            self._writers += 1
        # Escribir datos
```

**Ventajas**:
- ✅ Múltiples lectores simultáneos
- ✅ Escritores exclusivos

---

## 📊 Comparativa de Soluciones

| Solución | Segura | Escalable | Compleja | Caso de Uso |
|----------|--------|-----------|----------|------------|
| Variable Global | ❌ No | ❌ No | ✅ Simple | ❌ Nunca en Prod |
| `threading.Lock()` | ✅ Sí | ⚠️ Limitado | ⚠️ Medio | ✅ Proyectos pequeños |
| Base de Datos | ✅ Sí | ✅ Sí | ⚠️ Más alto | ✅ **Producción** |
| `asyncio.Lock()` | ✅ Sí | ⚠️ 1 proceso | ⚠️ Medio | ✅ Un solo worker |
| `RWLock` | ✅ Sí | ✅ Parcial | ❌ Complejo | ✅ Muchas lecturas |

---

## 🎯 Recomendación para Producción

```python
# ✅ OPCIÓN RECOMENDADA: PostgreSQL + SQLAlchemy + FastAPI

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, Session
from fastapi import Depends

DATABASE_URL = "postgresql://user:password@localhost/banco_db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()

class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    contador_secuencial = Column(Integer, autoincrement=True)

@app.post("/clientes")
async def crear_cliente(nombre: str, db: Session = Depends(get_db)):
    # La BD maneja sincronización
    nuevo_cliente = Cliente(nombre=nombre)
    db.add(nuevo_cliente)
    db.commit()
    return nuevo_cliente
```

---

## 📝 Conclusiones

### Para esta Clase (Educativa):
- El código **funciona** sin locks
- Demostramos **dónde** está el recurso compartido
- Mostramos **por qué** es importante

### Para Producción:
- **Nunca** usar variables globales para datos compartidos
- **Siempre** usar una base de datos
- **Evitar** locks en favor de BD con transacciones ACID
- **Monitorear** race conditions con herramientas de testing

---

## 🔗 Referencias
- [FastAPI - Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [Python Threading](https://docs.python.org/3/library/threading.html)
- [AsyncIO](https://docs.python.org/3/library/asyncio.html)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)

---

**Autor**: Estudiante Clase 3 - Programación Distribuida  
**Fecha**: Marzo 2026
