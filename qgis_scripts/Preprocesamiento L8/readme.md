En mi trabajo, se usa uns script de ENVI para hacer un preproceso en las landsat 8. En Diciembre de 2021, luego de terminar el curso de posgrado 
sobre procesamiento digital de imagenes satelitales en python, se lanzo la coleccion 2 de Landsat la cual modificaba el formato de las imagenes a Geotiff.
Este cambio inutilizó el script de ENVI. Descubrimos que si levantabamos las tiffs en qgis y usando "Guardar como..." podiamos solucionar este inconveniente.
Dado el gran numero de archivos que teniamos que, de ahora en más, modificar para poder incorporar a nuestro procesamiento estandar, teniendo en mente el
termino de "automate the boring stuff with Python", me dispuse a automatizar esta tarea. Como leí hace poco, un programador es demasiado vago para hacer una tarea repetitiva durando una semana,
pero va a trabajar apasionadamente durante una semana para automatizar esa tarea. Y así es como escribi dos versiones del mismo script, uno usando ... y otro usando ...