from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
from typing import List

app = FastAPI()

# Configuración de CORS (Para que React pueda hablar con Python)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Puerto por defecto de Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELOS DE DATOS (Lo que esperamos recibir del Front) ---
class DatosUsuario(BaseModel):
    edad: int
    peso: float
    estatura: float
    genero: str
    objetivo: str  # bajar_grasa, subir_masa, mantenimiento
    nivel: str     # principiante, intermedio, experto
    dias_disponibles: int
    equipo_disponible: List[str] # ["dumbbell", "cable", "body weight"]

# --- LÓGICA DEL SISTEMA EXPERTO (REGLAS) ---
def determinar_distribucion(dias: int, nivel: str):
    """Regla para decidir el tipo de split (distribución)"""
    if dias <= 3 or nivel == "principiante":
        return "Full Body"
    elif dias == 4:
        return "Upper / Lower"
    elif dias >= 5:
        return "Push / Pull / Legs"
    return "Full Body" # Default

# --- ENDPOINT PRINCIPAL ---
# Nota cómo esto ya está pegado al margen izquierdo
@app.post("/generar-rutina")
async def generar_rutina(datos: DatosUsuario):
    
    # 1. Aplicar Reglas de Inferencia (Tu Sistema Experto)
    distribucion = determinar_distribucion(datos.dias_disponibles, datos.nivel)
    
    # 2. Conectar con ExerciseDB de verdad
    url = "https://exercisedb.p.rapidapi.com/exercises"
    
    headers = {
        "X-RapidAPI-Key": "be5bf0bfd9msh4943414be429511p1e3b6djsnc493f2b9dac9", # Tu llave
        "X-RapidAPI-Host": "exercisedb.p.rapidapi.com"
    }
    
    try:
        # Hacemos la petición a la API
        response = requests.get(url, headers=headers)
        response.raise_for_status() 
        todos_los_ejercicios = response.json()
        
        # CHISMOSO 1: Ver qué tipo de dato nos llegó
        print("Tipo de dato recibido:", type(todos_los_ejercicios))
        
        # CHISMOSO 2: Imprimir un pedacito de lo que llegó para revisarlo
        if isinstance(todos_los_ejercicios, list):
            print("Total de ejercicios recibidos:", len(todos_los_ejercicios))
        else:
            print("La API respondió con este mensaje:", todos_los_ejercicios)
        
        # 3. QUITAR EL FILTRO TEMPORALMENTE
        # Solo tomaremos los primeros 5 ejercicios directos de la API
        ejercicios_filtrados = todos_los_ejercicios[:5] 

        # 4. Estructurar la respuesta final
        rutina_generada = {
            "mensaje": f"Rutina generada exitosamente para objetivo: {datos.objetivo}",
            "tipo_rutina": distribucion,
            "ejercicios_recomendados": ejercicios_filtrados
        }
        
        return rutina_generada

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con la API: {str(e)}")