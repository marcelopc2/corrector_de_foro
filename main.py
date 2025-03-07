import streamlit as st
import requests
from decouple import config
import unicodedata
import re

# Configuración de la API de Canvas
API_URL = 'https://canvas.uautonoma.cl/api/v1/'
API_TOKEN = config("TOKEN")
HEADERS = {"Authorization": f"Bearer {API_TOKEN}","Content-Type": "application/json"}

def clean_string(input_string: str) -> str:
    cleaned = input_string.strip().lower()
    cleaned = unicodedata.normalize('NFD', cleaned)
    cleaned = re.sub(r'[^\w\s.,!?-]', '', cleaned)
    cleaned = re.sub(r'[\u0300-\u036f]', '', cleaned)
    return cleaned
# Función para obtener los foros de un curso
def get_course_forums(course_id):
    url = f"{API_URL}/courses/{course_id}/discussion_topics"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error al obtener foros del curso {course_id}: {response.status_code} - {response.text}")
        return []

# Función para desactivar respuestas hilvanadas en un foro
def disable_threaded_replies(course_id, forum_id, data):
    url = f"{API_URL}/courses/{course_id}/discussion_topics/{forum_id}"
    response = requests.put(url, headers=HEADERS, json=data)  # Usa `json=data` para enviar el cuerpo en formato JSON
    if response.status_code == 200:
        #st.success(f"Respuestas hilvanadas desactivadas en el foro {forum_id} del curso {course_id}")
        return True
    else:
        st.error(f"Error al actualizar el foro {forum_id} del curso {course_id}: {response.status_code} - {response.text}")
        return False

# Función para procesar todos los cursos
def process_courses(course_ids):
    total_courses = len(course_ids)
    processed_courses = 0
    successful_updates = 0
    failed_updates = 0

    # Barra de progreso
    progress_bar = st.progress(0)

    for course_id in course_ids:
        st.write(f"Procesando curso: {course_id}")
        forums = get_course_forums(course_id)

        for forum in forums:
            forum_id = forum.get("id")
            forum_name = forum.get("title")
            if clean_string(forum_name) == "foro academico":
                data = {"discussion_type": "threaded", "assignment": {"peer_reviews": False}}
            else:
                data = {"discussion_type": "threaded"}
            if disable_threaded_replies(course_id, forum_id, data):
                successful_updates += 1
            else:
                failed_updates += 1

        processed_courses += 1
        progress_bar.progress(processed_courses / total_courses)

    # Resultado final
    st.write(f"Se procesaron {total_courses} cursos.")
    st.success(f"{successful_updates} foros actualizados exitosament - Respuestas hilvanadas y revision entre pares DESACTIVADAS.")
    if failed_updates > 0:
        st.error(f"Errores en la actualización: {failed_updates}")

# Interfaz de usuario de Streamlit
st.title("Gestión de Foros en Canvas")
st.write("Ingrese los IDs de los cursos para desactivar las respuestas hilvanadas en todos los foros.")
st.info("Se ha agregado de la desactivación de las revisiones entre pares. 07/03/2025")

course_ids_input = st.text_area(
    "IDs de cursos (separados por comas, espacios o saltos de línea)",
    placeholder="Ejemplo: 12345, 67890\n12345 67890"
)

if st.button("Actualizar Foros"):
    if course_ids_input:
        course_ids = [course.strip() for course in course_ids_input.replace(",", " ").replace("\n", " ").split() if course.strip()]
        if course_ids:
            process_courses(course_ids)
        else:
            st.warning("Por favor, ingrese al menos un ID de curso válido.")
    else:
        st.warning("Por favor, ingrese los IDs de los cursos.")
