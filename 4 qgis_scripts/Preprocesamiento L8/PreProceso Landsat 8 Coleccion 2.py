import os
import shutil

# autor: Pablo Mandolesi
# Dada la carpeta "C:\\Preprocesamiento L8\\coleccion2\\", en la que estan las carpetas de las escenas descomprimidas de Landsat8(coleccion2),
# levanta las bandas y las guarda en formato Geotiff en "C:\\Preprocesamiento L8\\Descomprimida\\" en carpetas individuales por escena, 
# para que puedan alimentar el procesador_L8_v3 de ENVI.


workpath="C:\\Preprocesamiento L8\\Coleccion 2\\"
listacarpetas=os.listdir(workpath) #Lista de carpetas de escenas descomprimidas de la coleccion2
print(listacarpetas)
for carpeta in listacarpetas: # para cada carpeta:
        print(f'Procesando escena:  {carpeta}')
        listaarchivos=os.listdir(workpath+f'{carpeta}') # lista de archivos en cada escena
#        print(listaarchivos)

        for file in listaarchivos: #para cada archivo:
                if file.endswith("QA_PIXEL.TIF"): # si el archivo termina en "QA_PIXEL.TIF" Lo levanto y lo guardo cambiandole el nombre para igualarlo a coleccion1
                                                  # en la carpeta destino
                        path_to_tif = workpath+carpeta+'\\'+file
                        
                        print(f'{file}')
                        rlayer = QgsRasterLayer(path_to_tif,f'{file}')
                        os.makedirs(f'C:\\Preprocesamiento L8\\Descomprimida\\{file[0:40]}', exist_ok=True)
                        processing.run("gdal:translate", {'INPUT':f'{path_to_tif}','TARGET_CRS':None,'NODATA':None,'COPY_SUBDATASETS':False,'OPTIONS':'','DATA_TYPE':0,'OUTPUT':f'C:\\Preprocesamiento L8\\Descomprimida\\{file[0:40]}\\{file[0:40]}_BQA.TIF'})
                #        print(f'C:\\Preprocesamiento L8\\Descomprimida\\{file[0:40]}\\{file}')
                        if not rlayer.isValid():
                            print("Layer failed to load!")
                #        else:
                #            QgsProject.instance().addMapLayer(rlayer)
                if file.endswith(".TIF") and not file.endswith("QA_PIXEL.TIF"): # Si el archivo termina en .TIF, lo levanto y lo guardo en la carpeta destino
                        path_to_tif = workpath+carpeta+'\\'+file
#                        print(path_to_tif)
                        print(f'{file}')
                        rlayer = QgsRasterLayer(path_to_tif,f'{file}')
                        os.makedirs(f'C:\\Preprocesamiento L8\\Descomprimida\\{file[0:40]}', exist_ok=True)
                        processing.run("gdal:translate", {'INPUT':f'{path_to_tif}','TARGET_CRS':None,'NODATA':None,'COPY_SUBDATASETS':False,'OPTIONS':'','DATA_TYPE':0,'OUTPUT':f'C:\\Preprocesamiento L8\\Descomprimida\\{file[0:40]}\\{file}'})
                #        print(f'C:\\Preprocesamiento L8\\Descomprimida\\{file[0:40]}\\{file}')
                        if not rlayer.isValid():
                            print("Layer failed to load!")
                #        else:
                #            QgsProject.instance().addMapLayer(rlayer)
                
                if file.endswith(".txt"): # Si el archivo termina en .txt, lo copio a la carpeta destino
                        path_to_file = workpath+carpeta+'\\'+file
                        print(file)
                        os.makedirs(f'C:\\Preprocesamiento L8\\Descomprimida\\{file[0:40]}', exist_ok=True)
                        shutil.copy(path_to_file, f'C:\\Preprocesamiento L8\\Descomprimida\\{file[0:40]}\\{file}')


print("Script corrido")