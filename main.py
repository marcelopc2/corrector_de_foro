import streamlit as st
import requests
from decouple import config

# Configuración de la API de Canvas
API_URL = 'https://canvas.uautonoma.cl/api/v1/'
API_TOKEN = config("TOKEN")
HEADERS = {"Authorization": f"Bearer {API_TOKEN}","Content-Type": "application/json"}

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
def disable_threaded_replies(course_id, forum_id):
    url = f"{API_URL}/courses/{course_id}/discussion_topics/{forum_id}"
    data = {"discussion_type": "threaded", "peer_reviews":False}  # La otra opcion -> not_threaded
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
            if disable_threaded_replies(course_id, forum_id):
                successful_updates += 1
            else:
                failed_updates += 1

        processed_courses += 1
        progress_bar.progress(processed_courses / total_courses)

    # Resultado final
    st.write(f"Se procesaron {total_courses} cursos.")
    st.success(f"Foros actualizados exitosamente: {successful_updates}")
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
