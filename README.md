# GESPRO_E2_G2_2
Tec en Burgos RETURN


# GESPRO_G2_E2_2 – Gestor de Tareas

Proyecto desarrollado para las sesiones prácticas de la asignatura,
siguiendo la metodología Scrum.

El objetivo del proyecto no es la complejidad técnica, sino el uso
correcto de Scrum, la organización del trabajo y la colaboración en equipo.

## Funcionalidades
- Backend mínimo en Python (Flask)
- Endpoint de prueba `/health`
- Gestión de tareas con atributos:
  - id
  - título
  - estado (TODO, IN_PROGRESS, DONE)
- Listado de tareas (GET /tasks)
- Creación de tareas (POST /tasks)
- Persistencia básica en memoria
- Frontend HTML simple conectado al backend

## Estructura del proyecto
GESPRO_G2_E2/
├── backend/
│ └── app.py
├── frontend/
│ └── index.html
├── docs/
└── README.md
## Requisitos
- Anaconda / Miniconda
- Python 3.13
- Flask
- flask-cors

## Ejecución en local

1. Activar entorno:
conda activate GesPro
2. Ejecutar backend:
cd backend
python app.py
3. Abrir el frontend:
- Abrir el archivo `frontend/index.html` en el navegador

## Metodología de trabajo
El proyecto se ha desarrollado siguiendo Scrum, organizando el trabajo
en sprints cortos con planificación, desarrollo, revisión y retrospectiva.
