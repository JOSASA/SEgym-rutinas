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
@app.post("/generar-rutina")
async def generar_rutina(datos: DatosUsuario):

    # 1. Aplicar Reglas de Inferencia
    distribucion = determinar_distribucion(datos.dias_disponibles, datos.nivel)

    # 2. Conectar con ExerciseDB (Ejemplo simplificado)
    # NOTA: Necesitas registrarte en RapidAPI para obtener tu 'X-RapidAPI-Key'
    # url = "https://exercisedb.p.rapidapi.com/exercises"
    # headers = {
    # 	"X-RapidAPI-Key": "TU_API_KEY_AQUI",
    # 	"X-RapidAPI-Host": "exercisedb.p.rapidapi.com"
    # }
    # response = requests.get(url, headers=headers)
    # data = response.json()

    # POR AHORA: Retornamos datos simulados para probar la conexión
    rutina_generada = {
        "mensaje": f"Rutina generada para objetivo {datos.objetivo}",
        "tipo_rutina": distribucion,
        "ejercicios_recomendados": [
            {"nombre": "Sentadilla", "equipo": "barbell", "series": 4, "reps": 10},
            {"nombre": "Press Banca", "equipo": "barbell", "series": 3, "reps": 12}
        ]
    }

    return rutina_generada

# Para correr el server: uvicorn main:app --reload