# src/travel_crew_backend/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse
import os
import re

# Usamos una importación relativa porque 'crew.py' está en el mismo directorio.
from .crew import TravelCrew

# Inicializar la aplicación FastAPI
app = FastAPI(
    title="API del Asistente de Viajes",
    description="Una API para planificar itinerarios de viaje personalizados usando un equipo de agentes de IA (CrewAI).",
    version="1.0.0"
)

class TripRequest(BaseModel):
    prompt: str 

# --- Función de Validación ---
def validate_trip_request(prompt: str) -> bool:
    """
    Valida si el prompt contiene información suficiente para planificar un viaje.
    """
    # Lista de palabras clave que indican una solicitud de viaje válida
    travel_keywords = [
        'viaje', 'viajar', 'trip', 'travel', 'vacaciones', 'turismo',
        'días', 'semanas', 'meses', 'presupuesto', 'budget',
        'destino', 'destination', 'país', 'ciudad', 'lugar',
        'hotel', 'alojamiento', 'vuelo', 'transporte',
        'comida', 'gastronomía', 'cultura', 'aventura',
        'playa', 'montaña', 'museo', 'restaurante'
    ]
    
    # Lista de saludos comunes que NO son solicitudes de viaje
    greetings = [
        'hola', 'hello', 'hi', 'hey', 'buenos días', 'buenas tardes',
        'buenas noches', 'saludos', 'qué tal', 'cómo estás',
        'good morning', 'good afternoon', 'good evening'
    ]
    
    prompt_lower = prompt.lower().strip()
    
    # Si es solo un saludo, no es válido
    if prompt_lower in greetings or len(prompt_lower.split()) <= 2:
        return False
    
    # Verificar si contiene al menos una palabra clave de viaje
    contains_travel_keyword = any(keyword in prompt_lower for keyword in travel_keywords)
    
    # Verificar longitud mínima
    min_length_check = len(prompt.strip()) >= 15
    
    return contains_travel_keyword and min_length_check

# --- Función de Limpieza ---
def clean_llm_output(text: str) -> str:
    """Limpia artefactos comunes del LLM"""
    cleaned_text = text.replace("∗", "").replace("ˊ", "")
    return cleaned_text

@app.post("/plan-trip")
async def plan_trip_endpoint(request: TripRequest):
    """
    Recibe una petición de viaje y devuelve un itinerario generado por el Crew de IA,
    listo para mostrarse en el chat y para ser descargado.
    """
    try:
        # Validar que sea una solicitud de viaje válida
        if not validate_trip_request(request.prompt):
            return JSONResponse(
                status_code=400,
                content={
                    "chat_response": """
                    ¡Hola! 👋 
                    
                    Para ayudarte a planificar tu viaje, necesito más información específica. 
                    
                    Por favor, describe tu viaje ideal incluyendo:
                    - 🌍 **Destino** que te interesa
                    - 📅 **Duración** del viaje (días/semanas)
                    - 💰 **Presupuesto** aproximado (opcional)
                    - 🎯 **Tipo de experiencia** (cultura, gastronomía, aventura, etc.)
                    
                    **Ejemplos:**
                    - "Un viaje de 10 días por Italia enfocado en gastronomía"
                    - "Aventura de 2 semanas en Costa Rica con presupuesto moderado"
                    - "¿Qué puedo hacer en 5 días en Tokio?"
                    """,
                    "download_content": None,
                    "download_filename": None
                }
            )

        inputs = {'trip_request': request.prompt}
        
        print(f"🚀 Ejecutando el crew para la petición: {request.prompt}")
        travel_crew = TravelCrew()
        result = travel_crew.crew().kickoff(inputs=inputs)
        print(f"✅ Crew finalizado. Procesando resultado.")

        # 1. Obtener el resultado final y limpiarlo para el chat
        final_chat_response = clean_llm_output(result.raw)

        # 2. Leer el contenido del archivo .md para la descarga
        download_content = ""
        filename = "itinerary.md"
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                download_content = f.read()
        except FileNotFoundError:
            print(f"⚠️  Advertencia: No se encontró el archivo '{filename}'. La descarga no estará disponible.")
            download_content = final_chat_response # Como fallback, usamos la respuesta del chat

        # 3. Construir la respuesta JSON estructurada
        structured_response = {
            "chat_response": final_chat_response,
            "download_content": download_content,
            "download_filename": filename
        }
        
        return structured_response

    except Exception as e:
        print(f"❌ Error durante la ejecución del crew: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "chat_response": "Lo siento, hubo un problema interno al procesar tu solicitud. Por favor, intenta nuevamente en unos momentos.",
                "download_content": None,
                "download_filename": None
            }
        )

@app.get("/")
def read_root():
    return {"status": "El servidor del Asistente de Viajes IA está funcionando correctamente."}

@app.get("/health")
def health_check():
    """Endpoint para verificar el estado del servicio"""
    return {"status": "healthy", "service": "travel-assistant-ai"}