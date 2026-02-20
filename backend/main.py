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

def determinar_series_reps(objetivo: str, nivel: str):
    """Reglas de inferencia para determinar el volumen de entrenamiento"""
    if objetivo == "subir_masa":
        if nivel == "principiante":
            return {"series": 3, "reps": "8-10"}
        else:
            return {"series": 4, "reps": "8-12"}
            
    elif objetivo == "bajar_grasa":
        return {"series": 3, "reps": "12-15"}
        
    else: # mantenimiento
        return {"series": 3, "reps": "10-12"}


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

def determinar_series_reps(objetivo: str, nivel: str):
    """Reglas de inferencia para determinar el volumen de entrenamiento"""
    if objetivo == "subir_masa":
        if nivel == "principiante":
            return {"series": 3, "reps": "8-10"}
        else:
            return {"series": 4, "reps": "8-12"}
            
    elif objetivo == "bajar_grasa":
        return {"series": 3, "reps": "12-15"}
        
    else: # mantenimiento
        return {"series": 3, "reps": "10-12"}


# --- ENDPOINT PRINCIPAL ---
@app.post("/generar-rutina")
async def generar_rutina(datos: DatosUsuario):
    
    print("\n--- 🔍 INTENTO 3: ARQUITECTURA PROFESIONAL ---")
    
    distribucion = determinar_distribucion(datos.dias_disponibles, datos.nivel)
    volumen = determinar_series_reps(datos.objetivo, datos.nivel)
    
    headers = {
        "X-RapidAPI-Key": "be5bf0bfd9msh4943414be429511p1e3b6djsnc493f2b9dac9", # Tu llave
        "X-RapidAPI-Host": "exercisedb.p.rapidapi.com"
    }
    
    try:
        ejercicios_filtrados = []
        
        # 1. Consultar la API *por equipo* en lugar de pedir toda la base de datos
        print(f"✅ 1. Buscando ejercicios exclusivamente para: {datos.equipo_disponible}")
        for equipo in datos.equipo_disponible:
            # Reemplazamos espacios por %20 para que la URL sea válida (ej. "body weight" -> "body%20weight")
            equipo_url = equipo.replace(" ", "%20")
            url = f"https://exercisedb.p.rapidapi.com/exercises/equipment/{equipo_url}?limit=50"
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                ejercicios_filtrados.extend(response.json())
                print(f"   -> Se descargaron ejercicios para: {equipo}")
                
        print(f"✅ 2. Total de ejercicios recolectados: {len(ejercicios_filtrados)}")
        
        # 2. SISTEMA EXPERTO: SELECCIÓN MUSCULAR
        ejercicios_seleccionados = []
        if distribucion == "Full Body":
            musculos_requeridos = ["pectorals", "lats", "quads", "hamstrings", "delts"]
            print(f"✅ 3. Buscando estos músculos: {musculos_requeridos}")
            
            for musculo in musculos_requeridos:
                # Buscamos en nuestra nueva lista pre-filtrada
                ejercicio_encontrado = next(
                    (ej for ej in ejercicios_filtrados if ej.get("target") == musculo), 
                    None
                )
                if ejercicio_encontrado:
                    ejercicios_seleccionados.append(ejercicio_encontrado)
                    print(f"   -> Encontrado para {musculo}: {ejercicio_encontrado['name']}")
                else:
                    print(f"   -> ❌ NO se encontró para: {musculo}")

        # Si por alguna razón no se armó la rutina completa, rellenamos
        if len(ejercicios_seleccionados) == 0:
             print("⚠️ No se seleccionó nada con la regla principal, tomando 5 al azar...")
             ejercicios_seleccionados = ejercicios_filtrados[:5]

        # 3. Construimos la lista final con series y reps integradas
        rutina_final = []
        for ej in ejercicios_seleccionados: 
            rutina_final.append({
                "name": ej["name"],
                "target": ej["target"],
                "equipment": ej["equipment"],
                "series": volumen["series"],
                "reps": volumen["reps"]
            })

        rutina_generada = {
            "mensaje": f"Rutina generada exitosamente para objetivo: {datos.objetivo}",
            "tipo_rutina": distribucion,
            "ejercicios_recomendados": rutina_final
        }
        
        return rutina_generada

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de API: {e}")
        raise HTTPException(status_code=500, detail=f"Error al conectar con la API: {str(e)}")