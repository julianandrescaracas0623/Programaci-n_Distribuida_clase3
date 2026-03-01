from fastapi import FastAPI # import  propio del framework FastAPI
from typing import List # import estandar de python para tipado
import asyncio # import para manejo de operaciones asíncronas

###########################
# Creación de la aplicación
###########################

app = FastAPI() # se crea una instancia de la clase FastAPI, que es la aplicación web

########################
# Base de datos simulada
########################

clientes = [] # lista vacía que simula una base de datos de clientes en memoria
contador_clientes_creados = 0 # contador global de clientes creados

@app.get("/") # Decorador que define una ruta GET para la raíz del sitio
def home():
    return {"message": "Bienvenido a la API del Banco Funcionando"} # Devuelve un mensaje de bienvenida en formato JSON


# Endpoint para crear un nuevo cliente
@app.post("/clientes") # Decorador para el método POST en la ruta /clientes
async def crear_cliente(nombre: str): # Parametro recibido por query
    global contador_clientes_creados # Accede a la variable global
    
    # Validación: no permitir nombre vacío
    if not nombre or nombre.strip() == "":
        return {"error": "El nombre del cliente no puede estar vacío"}
    
    # Simulación de delay asíncrono de 3 segundos
    await asyncio.sleep(3)
    
    contador_clientes_creados += 1 # Incrementa el contador de clientes creados
    cliente = {
        "id": len(clientes) + 1, # Asigna un ID único basado en la longitud de la lista de clientes
        "nombre": nombre.strip(), # Asigna el nombre del cliente al valor recibido (sin espacios extras)
        "numero_cliente_creado": contador_clientes_creados # Número secuencial de clientes creados
    }
    clientes.append(cliente) # Agrega el cliente a la lista de clientes
    return cliente # Devuelve el cliente recién creado en formato JSON


# Endpoint para obtener la lista de clientes
@app.get("/clientes")# Decorador para el método GET en la ruta /clientes
def listar_clientes():
    return clientes # Devuelve la lista de clientes en formato JSON

# Endpoint para obtener un cliente por ID
@app.get("/clientes/{cliente_id}")# Decorador para el método GET en la ruta /clientes/{cliente_id}, donde {cliente_id} es un parámetro de ruta que representa el ID del cliente
def obtener_cliente(cliente_id: int):
    for cliente in clientes:
        if cliente["id"] == cliente_id: # Compara el ID del cliente con el ID recibido
            return cliente # Devuelve el cliente encontrado en formato JSON
    return {"error": "Cliente no encontrado"} # Devuelve un mensaje de error si no se encuentra el cliente

# Endpoint para eliminar un cliente por ID
@app.delete("/clientes/{cliente_id}") # Decorador para el método DELETE en la ruta /clientes/{cliente_id}, donde {cliente_id} es un parámetro de ruta que representa el ID
def eliminar_cliente(cliente_id: int):
    for cliente in clientes: # Itera sobre la lista de clientes
        if cliente["id"] == cliente_id: # Compara el ID del cliente con el ID recibido
            clientes.remove(cliente) # Elimina el cliente de la lista de clientes
            return {"message": "Cliente eliminado"} # Devuelve un mensaje de éxito en formato JSON
    return {"error": "Cliente no encontrado"} # Devuelve un mensaje de error si no se encuentra el cliente

@app.put("/clientes/{cliente_id}") # Decorador para el método PUT en la ruta /clientes/{cliente_id}, donde {cliente_id} es un parámetro de ruta que representa el ID del cliente
def actualizar_cliente(cliente_id: int, nombre: str): # Parámetros recibidos por query
    for cliente in clientes: # Itera sobre la lista de clientes
        if cliente["id"] == cliente_id: # Compara el ID del cliente con el ID recibido
            cliente["nombre"] = nombre # Actualiza el nombre del cliente con el valor recibido
            return cliente # Devuelve el cliente actualizado en formato JSON
    return {"error": "Cliente no encontrado"} # Devuelve un mensaje de error si no se encuentra el cliente





    