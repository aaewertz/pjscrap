# Instalación #

* Descargar e Instalar python3 desde https://www.python.org/downloads/

* Abrir terminal o cmd y clonar Repositorio
```
git clone https://foretama@bitbucket.org/foretama/identificar_fallos_cortesuprema.git
```
* Crear tu virtual enviroment
```python
python -m venv venv
```
* Activar el virtual enviroment

```python
venv\Scripts\activate
```
* Actualizar pip
```python
python -m pip install --upgrade pip
```
* Instalar los paquetes con pip y requirements.txt
```python
pip install -r requirements.txt
```
* Descargar chromedriver para la version de chrome que tienes y sistema operativo
    * En Chrome Browser ir a: 3 puntos (botón abajo de la X) -> Ayuda -> Acerca de Google Chrome -> Obtener version
    * https://chromedriver.storage.googleapis.com/index.html -> Descargar chromedriver de acuerdo a la version de tu Chrome y de tu OS.
    * Guardar chromedriver en la carpeta code

# Uso #

En la carpeta "code", hay 2 scripts:

* 01_descarga_fallos.py
* 02_filtrar_fallos_cortos

## 01_descarga_fallos

Con el script **01_descarga_fallos** podrás descargar los fallos de un día escogido.

Los fallos descargados son guardados en la carpeta **code\downloads\FECHA\pdfs**, donde FECHA es la fecha escogida. Un ejemplo de ruta sería **code\downloads\2020_04_17\pdfs**

Los archivos se guardarán con nombres con el formato **FECHA&NÚMERO_DE_FALLO&NÚMERO_DEL_DOCUMENTO.pdf**, donde FECHA es la fecha escogida, el NÚMERO_DE_INGRESO es el número de ingreso del fallo y el NÚMERO_DEL_DOCUMENTO es el número del documento dado que puede haber más de 1 documento adjunto al fallo. Un ejemplo del nombre de los archivos guardados es **2020_04_17&1567-2020&1.pdf**

Para correr el script:
```python
python 01_descarga_fallos.py
```

## 02_filtrar_fallos_cortos

Con el script **02_filtrar_fallos_cortos** se busca todos los archivos descargados de la carpeta escogida que tengan igual o mas de **N** páginas, donde **N** es la cantidad de paginas a filtrar ingresada.

Para correr el script:
```python
python 02_filtrar_fallos_cortos.py
```