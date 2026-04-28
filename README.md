# 📊 Diagnóstico de Ofertas Loyalty

Aplicación desarrollada en **Python + Streamlit** para analizar ofertas de productos de manera dinámica, sin necesidad de modificar código.

Permite:
- Aplicar filtros por fechas, productos, montos mínimos, ciudad, segmento, categoría y negocio
- Calcular KPIs clave (clientes, transacciones, ventas, variación)
- Analizar Pareto 80/20 de productos
- Exportar resultados a Excel

---

## 🚀 Requisitos

- Python 3.9 o superior  
- Conexión a internet para instalar dependencias  

---

## 📂 Estructura del proyecto


Entrega_Prueba_Tecnica_Loyalty/
├── app/
│ ├── init.py
│ ├── app.py # Interfaz principal (Streamlit)
│ ├── load_data.py # Carga de datos
│ ├── filters.py # Lógica de filtros
│ ├── metrics.py # KPIs y cálculos
│ ├── exports.py # Exportación a Excel
│ └── utils.py # Funciones auxiliares
├── data/
│ ├── Clientes.csv
│ ├── Productos.csv
│ ├── Negocios.csv
│ ├── Calendario.csv
│ └── Ventas.csv
├── requirements.txt
└── README.md


---


## ⚙️ Instalación

1. Descargar y descomprimir el proyecto  
2. Abrir la carpeta en tu editor (VS Code recomendado)  
3. Abrir una terminal en la ruta del proyecto  ( preferiblemente cmd)

otros pasos
RUTA = es la del usuario del pc puede ser admin o nombre del usuario
"C:\Users\RUTA\anaconda3\python.exe" --version
"C:\Users\Hermanos Ferrucho\anaconda3\python.exe" -m venv .venv

.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app/app.py

###  IMPORTANTE  Crear entorno virtual
Crear entorno virtual de python ( recomendado  con 
python -m venv venv )
instalar paquetes claves   python -m pip install streamlit pandas xlsxwriter openpyxl



###  Instalar las dependencias


pip install -r requirements.txt


### Ejecutar la aplicación


streamlit run app/app.py



Se abrirá automáticamente una ventana en tu navegador predeterminado (generalmente http://localhost:8501)



### Exportar requerimientos
python -m pip freeze > requirements.txt


# Notas de la solución
La aplicación está diseñada con enfoque en la capa de visualización (VIEW)
El script se limita a la carga de datos, manteniendo la lógica en la interfaz
Permite segmentación dinámica y análisis flexible para usuarios no técnicos
Estructura modular para facilitar mantenimiento y escalabilidad



# Funcionalidades principales

Filtros dinámicos (fecha, productos, montos, segmentación)
KPIs en tiempo real
Pareto de productos (80/20)
Tablas de resumen y detalle
Exportación a Excel por tabla seleccionada