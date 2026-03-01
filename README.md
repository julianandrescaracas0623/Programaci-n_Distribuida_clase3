# Clase 3 Porgramacion Distribuida API Banco - FastAPI

## Descripción

API básica desarrollada con FastAPI que permite gestionar clientes en memoria.  
Incluye operaciones CRUD (crear, listar, obtener, actualizar y eliminar clientes).

La aplicación utiliza variables globales como almacenamiento simulado en lugar de una base de datos real.

---

## Preguntas 

### 1. ¿Es seguro usar variable global?

No es seguro en producción.  
Las variables globales pueden generar problemas de concurrencia cuando múltiples peticiones acceden o modifican los datos al mismo tiempo.

En este proyecto, `contador_clientes_creados` puede verse afectado por condiciones de carrera.

---

### 2. ¿Dónde aparece el recurso compartido?

El recurso compartido aparece en las variables globales:

- `clientes`
- `contador_clientes_creados`

Estas variables son accesibles y modificables por todas las peticiones que recibe el servidor.

---

### 3. ¿Se debería usar lock en producción?

Sí.  
Si se mantienen datos en memoria y se modifican concurrentemente, se debería usar un mecanismo de bloqueo (`Lock`) para evitar condiciones de carrera.

Sin embargo, en producción lo recomendable es utilizar una base de datos en lugar de variables globales.

---

## Recomendación Final

Para entornos reales:

- Evitar variables globales para almacenamiento.
- Usar una base de datos (PostgreSQL, MySQL, etc.).
- Implementar control de concurrencia adecuado.
