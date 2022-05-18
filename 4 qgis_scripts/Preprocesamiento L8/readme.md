Diciembre de 2021. El lanzamiento de la Colección 2 de Landsat había inutilizado el script (IDL) de preprocesamiento de imágenes que se usa en mi trabajo. Hacía solo un par de días, yo acababa de presentar el trabajo final de un curso de posgrado del Instituto Gulich sobre procesamiento digital de imágenes satelitales en Python. Esta fue mi oportunidad para probar lo aprendido en una aplicación real en un ambiente de trabajo. Felicidad porque se presentara tan rápido.

En la Colección 2 de Landsat se modificaba el formato de las imágenes, que cambió de geotiffs a COG (Cloud Optimized Geotiff). Este cambio no debería haber causado ningún problema, pero en nuestro caso, inutilizó el script de preproceso ya que la versión de ENVI que teníamos no reconocía este nuevo formato.

Buscando una manera de sortear este inconveniente, descubrimos que si levantábamos las COGs en qgis y usábamos "Guardar como..." para guardarlas como nuevos geotiffs, lográbamos que ENVI las reconozca y así poder seguir usando el script de IDL que teníamos. Esta solución resultaba en agregar un paso manual y repetitivo al procedimiento normal, que sumado al hecho de que la cantidad de imágenes que se procesan periódicamente es considerablemente alta, se transformaba en una carga engorrosa y pesada para el equipo de trabajo, tornándola inviable.

En mi mente resonaba el título de un libro: "automate the boring stuff with Python". Como leí hace poco en un blog, un programador es demasiado vago para hacer una tarea repetitiva durante una semana, pero va a trabajar apasionadamente durante una semana para automatizar esa tarea.

Y así es como escribí dos versiones del mismo script para automatizar esta tarea. El primero usando "Gdal:translate" y el segundo usando "QgsRasterFileWriter". 

La primer versión (la que usa Gdal:translate) tenía un desvío en su funcionamiento, generaba un archivo ".IMD" acompañando a cada tiff. No era ningún problema, pero no me gustaba el hecho de que el script resultara en algo que no era específicamente lo deseado. Me puse a estudiar la configuración del comando y los drivers de gtiffs de gdal, a ver si se podía modificar algo que corrigiera este efecto indeseado. Fue un callejón sin salida.

Mientras, encontré que existía otro comando que podía utilizar para la misma tarea "QgsRasterFileWriter", el cual realizaba la misma tarea, pero esta vez sin generar los archivos acompañantes indeseados.

De todas maneras, para cuando mandé la segunda versión, la primera ya estaba siendo usada y funcionando. Equipo que gana no se toca. La segunda versión fue solo por la satisfacción por perfeccionar el código.
