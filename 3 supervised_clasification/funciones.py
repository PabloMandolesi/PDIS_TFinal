
import os
from os import listdir
from os.path import isfile, join
import numpy as np
import geopandas as gpd
import pandas as pd
from osgeo import gdal
from xml.etree import ElementTree as ET
import rasterio
from rasterio.mask import mask
from rasterio.plot import show
from rasterio.plot import show_hist

from shapely.geometry import box
from shapely.geometry import mapping
from shapely.geometry.polygon import Polygon

from datetime import datetime
from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
import seaborn as sns


def get_fechas(dir_in, ext='tif', verbose=True):
    
    '''
    extrae la lista ordenada de fechas de los archivos MODIS 
    de una carpeta dada por dir_in.
    El resultado es una lista de objetos tipo datetime.
    '''
    
    files = os.listdir(dir_in) #Listado
    # Filtrar únicamente los formatos de datos que me interesan
    files_with_ext = [f for f in files if f.lower().endswith(ext.lower())]
    files_with_ext.sort() #Organizar en orden ascendente
    sfechas = [f.split('doy')[1].split('_')[0] for f in files_with_ext] #Extraer las fechas
    fechas = [datetime.strptime(f, '%Y%j') for f in sfechas] #Fechas a formato datetime
    
    if verbose: print(f'Recolecté {len(fechas)} fechas entre {fechas[0]} y {fechas[-1]}.')
    
    return fechas

def subset_img (ds, ul_x, ul_y, lr_x, lr_y):
    '''toma un raster gdal y retorna un array recortado a partir de las coordenadas de un bounding box'''
    # extraigo datos del geotransform
    geoTs = ds.GetGeoTransform()
    ulx = geoTs[0]
    uly = geoTs[3]
    p_size_x = geoTs[1]
    p_size_y = geoTs[5]
    # pixel upper-left
    p_xul = round((ul_x - ulx)/p_size_x)
    p_yul = round((ul_y - uly)/p_size_y)
    # pixel lower-right
    p_lrx = round((lr_x - ulx)/p_size_x)
    p_lry = round((lr_y - uly)/p_size_y)
    # offsets
    x_off = p_xul
    y_off = p_yul
    # win size
    win_xsize = p_lrx-p_xul
    win_ysize = p_lry-p_yul
    # subset
    subset = ds.ReadAsArray(x_off, y_off, win_xsize, win_ysize)
    return subset

def mostrar_indice(array, nodata=None, p=0, vmin=None, vmax=None, cmap='Greys_r', title=""):
    '''
    plotear una imagen definiendo un percentil para valores min y max del estiramiento
    '''
    if not vmin:
        vmin = np.percentile(array[array!=nodata],p)
    if not vmax:
        vmax = np.percentile(array[array!=nodata],100-p)

    print(f'vmin={vmin} vmax={vmax}')
    plt.imshow(array, cmap, vmin=vmin, vmax=vmax)
    plt.colorbar()
    plt.tight_layout()
    plt.title(title)
    plt.show()

def scale(array, p=0, nodata=None, vmin=None, vmax=None):
    ''' toma un array, estira a percentil p y escala entre 0 y 1'''    
    vmin = np.percentile(array[array!=nodata], p)
    vmax = np.percentile(array[array!=nodata], 100-p)
    arraycopy = array.copy() # crea array virtual para que no modifique al array original    
    scaled = (arraycopy-vmin)/(vmax-vmin)
    scaled[scaled > 1] = 1
    scaled[scaled < 0] = 0
    return scaled

def nequalize(array,p=0,nodata=0):
    """
    normalize and equalize a single band image
    """
    if len(array.shape)==2:
        vmin=np.percentile(array[array!=nodata],p)
        vmax=np.percentile(array[array!=nodata],100-p)
        eq_array = (array-vmin)/(vmax-vmin)
        eq_array[eq_array>1]=1
        eq_array[eq_array<0]=0
    elif len(array.shape)==3:
        eq_array = array.copy()
        for i in range(array.shape[0]):
            eq_array[i]=nequalize(eq_array[i])
    return eq_array

def get_rgb(array, band_list=[], p = 0, nodata=None):
    '''toma un array 3D, a cada banda la estira a percentil p y escala entre 0 y 1'''
    r = scale(array[band_list[0]-1,:,:],p, nodata=nodata)
    g = scale(array[band_list[1]-1,:,:],p, nodata=nodata)
    b = scale(array[band_list[2]-1,:,:],p, nodata=nodata)
    stacked = np.dstack((r,g,b))
    return stacked

def plot_rgb(array, band_list=[], p = 0, nodata=None, figsize=(10,10)):
    '''toma un array 3D, a cada banda la estira a percentil p y escala entre 0 y 1, y lo plotea en rgb'''
    stacked = get_rgb(array, band_list, p, nodata=nodata)
    plt.figure(figsize=figsize)
    plt.title(f'Combinación {band_list[0]}, {band_list[1]}, {band_list[2]}, (estirado al {p}%)', size = 15)
    plt.imshow(stacked)

def write_raster_gdal(array, path, fname, fdriver, dtype, gt, src, nband = 1):
    ''' Toma un array y lo escribe a un archivo en formato gdal.
    Esta función está pensada para arreglos o matrices de 2 o 3 dimensiones, donde:
    Para 3 dimensiones:
    a.shape[0] = Numero de bandas
    a.shape[1] = Numero de filas
    a.shape[2] = Numero de columnas
    
    Para 2 dimensiones:
    a.shape[0] = Numero de filas
    a.shape[1] = Numero de columnas
    '''
    shape = array.shape
    driver  = gdal.GetDriverByName(fdriver)
    if len(array.shape) == 2:
        out_image = driver.Create(os.path.join(path,fname ),shape[1],shape[0],nband,dtype)
    else:
        out_image = driver.Create(os.path.join(path,fname ),shape[2],shape[1],nband,dtype)
    out_image.SetGeoTransform(gt)
    out_image.SetProjection(src)
    
    if nband == 1:
        out_image.GetRasterBand(1).WriteArray(array)
    
    else:
        for i in range(nband):
            out_image.GetRasterBand(i+1).WriteArray(array[i,:,:])
    del out_image

def extraer_muestras(indir,raster, vector, outdir, columna, nodata=None):
    '''Dado un archivo vectorial con muestras y una imagen de entrada, construye los diagramas de caja
     para cada muestra y para cada banda, reflejando su comportamiento espectral.'''
    rasterf = rasterio.open(indir+raster)
    rasterf_crs = rasterf.crs
    vectorf = gpd.read_file(indir+vector)
    vectorf = vectorf.to_crs(rasterf_crs)
    lista_clases = np.unique(vectorf[columna])

    for i, clase in enumerate(lista_clases):
        mascara_clase = vectorf[vectorf[columna] == clase]
        recorte_clase =  mask(dataset=rasterf, shapes = mascara_clase.geometry, crop = True, nodata=nodata)[0]
        l = [band[band!=nodata].ravel() for band in recorte_clase]
        # plt.figure(figsize=(8,6))
        
        sns.boxplot(data=l)
        plt.xlabel('Banda')
        plt.title(f'Clase {clase}')
        plt.xticks(ticks = list(np.arange(len(l))), labels = list(np.arange(len(l))+1))
        plt.ylim(0,4000)
        if outdir is not None:
            nombre = f'Boxplot_{clase}.png'
            ruta_out = outdir
            outfile = os.path.join(ruta_out,nombre)
            plt.savefig(outfile)
        plt.show()

def guardar_GTiff(filename, crs, transform, array, nodata = 0):
    '''guardar un array en un archivo GTiff'''
    # cuento las bandas
    if len(array.shape)==2:
        count=1
    else:
        count=array.shape[0]
    #respeto el type, evitando el float64
    if array.dtype == np.float64:
        dtype = np.float32
    else:
        dtype=array.dtype
    with rasterio.open(
        filename,
        'w',
        driver='GTiff',
        height=array.shape[-2],
        width=array.shape[-1],
        count=count,
        dtype=dtype,
        nodata = nodata,
        crs=crs,
        transform=transform) as dataset:
        if len(array.shape)==2:
            dataset.write(array, 1)
        else:
            for b in range(0,count):
                dataset.write(array[b], b+1)

def extraer_raster(indir,raster, vector, outdir, columna, modo = 'mask', nodata=None):
    rasterf = rasterio.open(indir+raster)
    rasterf_crs = rasterf.crs
    vectorf = gpd.read_file(indir+vector)
    vectorf = vectorf.to_crs(rasterf_crs)

    for i in vectorf[columna]:
        vector = vectorf[vectorf[columna] == i]
        if modo =='mask':
            recorte,transform =  mask(dataset=rasterf,shapes = vector.geometry, crop = True)
        else:
            minx = float(vector.bounds.minx)
            miny = float(vector.bounds.miny)
            maxx = float(vector.bounds.maxx)
            maxy = float(vector.bounds.maxy)
            extent = box(minx,miny,maxx,maxy)
            bbox = gpd.GeoDataFrame({'geometry': extent}, index=[0], crs=rasterf_crs)
            recorte,transform =  mask(dataset=rasterf,shapes = bbox.geometry, crop = True)
        ruta_out = outdir
        nombre = f'{raster[:-4]}_{i}.tif'
        outfile = os.path.join(ruta_out,nombre)
        guardar_GTiff(outfile,rasterf_crs,transform,recorte, nodata=nodata)

def compute_mbb(fn, snap_to_grid = True, grid_step = 10):
    """dado un poligono en un shp, 
    calcula el mínimo rectángulo que lo contenga
    con vértices en una grilla de paso dado"""

    shapefile = gpd.read_file(fn)
    geoms_sh = shapefile.geometry.values
    
    while type(geoms_sh)!=Polygon: #miro solo el primer polígono del archivo
        geoms_sh = geoms_sh[0]     #me voy metiendo hasta que llego al nivel polygono

    geom0_GJSON = mapping(geoms_sh) #transformo de geometria a geojson
    
    Cx=[c[0] for c in geom0_GJSON['coordinates'][0]]
    Cy=[c[1] for c in geom0_GJSON['coordinates'][0]]
    
    mX = min(Cx)
    MX = max(Cx)
    mY = min(Cy)
    MY = max(Cy)
    
    if snap_to_grid:
        mX = grid_step*(np.floor(mX/grid_step)) # divide por step, redondea para bajo y vuelve a multiplicar por step
        MX = grid_step*(np.ceil(MX/grid_step)) # divide por step, redondea para arriba y vuelve a multiplicar por step
        mY = grid_step*(np.floor(mY/grid_step))
        MY = grid_step*(np.ceil(MY/grid_step))

    mbb = [{'type': 'Polygon',
            'coordinates': (((mX, MY),
                             (MX, MY),
                             (MX, mY),
                             (mX, mY),
                             (mX, MY)),)}]
    return mbb

def stack_dir(dir_in, fn_out = None, ext = '', verbose = True):
    '''crea un stack con todas las imágenes (de una banda)
    en un directorio. Las ordena alfabéticamente por nombre de archivo.
    Si se le pasa un nombre de archivo fn_out graba el stack ahí.'''
    files = [f for f in listdir(dir_in) if isfile(join(dir_in, f))]
    files_with_ext = [f for f in files if f.lower().endswith(ext.lower())]
    files_with_ext.sort()
    list_of_arrays = []
    for fn in files_with_ext:
        if verbose: print(fn)
        with rasterio.open(join(dir_in,fn)) as src:
            transform = src.transform
            crs=src.crs #recuerdo el sistema de referencia para poder grabar
            array = src.read()
        list_of_arrays.append(array)
    stack = np.vstack(list_of_arrays)
    if verbose: print(f'Recolecté {len(list_of_arrays)} rasters.')
    if fn_out:
        if verbose: print(f'Guardando el stack en {fn}.')
        guardar_GTiff(fn_out, crs, transform, stack)
   
    return stack



def extract_10m_bands_Sentinel2(img_data_dir, mbb=None, compute_ndvi = True, verbose = True):
    """dado un directorio con las bandas de una Sentinel 2
    extrae las 4 bandas de 10m de resolucion (2, 3, 4 y 8) y computa el NDVI.
    Si se le pasa un polígono mbb en formato GJSON lo usa para recortar 
    la imagen, sino extrae la imagen completa.
    
    Devuelve la matriz con los datos extraídos, el crs y 
    la geotransformacion correspodientes"""
    
    ls = os.listdir(img_data_dir)
    band_names = ['B02.','B03.', 'B04.', 'B08.'] 
    bands = []
    for b in band_names:
        try:
            fn = [fn for fn in ls if b in fn][0]
        except:
            print(f"Banda {b} no encontrada en {img_data_dir}.")
        if verbose: print(f"Leyendo {fn}.")
        
        fn = os.path.join(img_data_dir,fn)
        with rasterio.open(fn) as src:
            crs=src.crs #recuerdo el sistema de referencia para poder grabar
            if mbb: #si hay mbb hago un clip
                array, out_transform = mask(src, mbb, crop=True)
            else: #si no, uso la imagen entera
                array = src.read()
                out_transform = src.transform
        bands.append(np.true_divide(array[0], 10000, dtype=np.float32))
    if compute_ndvi:
        if verbose: print(f"Computando NDVI.")
        bands.append((bands[3]-bands[2])/(bands[3]+bands[2]))
    return np.stack(bands), crs, out_transform

def extract_10m_bands_Sentinel2_ZIP(zipfilename, mbb=None, compute_ndvi = True, verbose = True):
    """dado un zip de una Sentinel 2
    extrae las 4 bandas de 10m de resolucion (2, 3, 4 y 8) y computa el NDVI.
    Si se le pasa un polígono mbb en formato GJSON lo usa para recortar 
    la imagen, sino extrae la imagen completa.
    
    Devuelve la matriz con los datos extraídos, el crs y 
    la geotransformacion correspodientes"""
    
    from zipfile import ZipFile
    import re
    import os

    ## vsizip bugfix
    os.environ['CPL_ZIP_ENCODING'] = 'UTF-8'

    ## look for 10m resolution bands: 02, 03, 04 and 08
    tileREXP = re.compile(r'.*_B(02|03|04|08).jp2$')
    if verbose: print(f'Leyendo ZIP {zipfilename}')

    bands = []
    with ZipFile(zipfilename,'r') as zfile:
        bandfns = [x for x in zfile.namelist() if re.match(tileREXP,x)]
        bandfns.sort()
        for bandfn in bandfns:
            fn = f'/vsizip/{zipfilename}/{bandfn}'
            if verbose: print(f'Leyendo {os.path.basename(fn)}.')
            with rasterio.open(fn) as src:
                crs=src.crs #recuerdo el sistema de referencia para poder grabar
                if mbb: #si hay mbb hago un clip
                    array, out_transform = mask(src, mbb, crop=True)
                else: #si no, uso la imagen entera
                    array = src.read()
                    out_transform = src.transform
            bands.append(np.true_divide(array[0], 10000, dtype=np.float32)) # bands es una lista, las bandas las va generando en "array"
    if compute_ndvi:
        if verbose: print(f'Computando NDVI.')
        bands.append((bands[3]-bands[2])/(bands[3]+bands[2]))
    return np.stack(bands), crs, out_transform




def calibrar_spot(spot_path, xml_spot_path):
    with open(xml_spot_path) as f:
        tree =  ET.parse(f)
        root =  tree.getroot()

    #Localizamos el nodo Radiometric_Data:
    radiometric_data = root.findall('Radiometric_Data')
    # Localizamos el sub-nodo Radiometric_Calibration:
    radiometric_calibration = [item.findall('Radiometric_Calibration') for item in radiometric_data][0]
    # sin el [0] nos daria una lista de 1 elemento, que es ese que imprimimos ahi.

    # Localizamos el sub-nodo Instrument_Calibration:
    instrument_calibration = [item.findall('Instrument_Calibration') for item in radiometric_calibration][0]
    # Localizamos el sub-nodo Band_Measurement_List:
    band_measurement_list = [item.findall('Band_Measurement_List') for item in instrument_calibration][0]
    # Localizamos el sub-nodo Band_Radiance:
    band_radiance = [item.findall('Band_Radiance') for item in band_measurement_list][0]
    #Finalmente, construimos nuestras listas de GAIN y BIAS mirando la información de cada nodo Band_Radiance:
    gain = [item.find('GAIN').text for item in band_radiance]
    bias = [item.find('BIAS').text for item in band_radiance]
    band_id = [item.find('BAND_ID').text for item in band_radiance]

    ## Cálculo de la reflectancia:
    #Localizamos Dataset_Sources:
    dataset_sources = root.findall('Dataset_Sources')
    #Localizamos Source_Identification:
    source_identification = [item.findall('Source_Identification') for item in dataset_sources][0]
    #Localizamos Strip_Source:
    strip_source = [item.findall('Strip_Source') for item in source_identification][0]
    #Localizamos IMAGING_DATE
    imaging_date = [item.find('IMAGING_DATE').text for item in strip_source][0]
    # Interpretar como objeto datetime y convertir formato a juliano
    
    dt = datetime.strptime(imaging_date,'%Y-%m-%d')
    day = dt.strftime('%j')
    # usamos la fecha para calcular la distancia tierra-sol
    earth_sun_d = 1-0.0167*np.cos(2*np.pi*(int(day)-3)/365)
    # calculamos el ángulo de elevación solar
    #Localizamos Geometric_Data:
    geometric_data = root.findall('Geometric_Data')
    #Localizamos Use_Area:
    use_area = [item.findall('Use_Area') for item in geometric_data][0]
    #Localizamos Located_Geometric_Values
    located_geometric_values = [item.findall('Located_Geometric_Values') for item in use_area][0]
    #Localizamos Solar_Incidences
    solar_incidences = [item.find('Solar_Incidences') for item in located_geometric_values]
    #Localizamos SUN_ELEVATION
    sun_elevation = [float(item.find('SUN_ELEVATION').text) for item in solar_incidences]
    #Calculamos el ángulo de elevación solar promedio:
    mean_sun_elevation = np.mean(sun_elevation)
    # irradiancia solar o exoatmosférica para cada banda
    #Localizamos Band_Solar_Irradiance
    band_solar_irradiance = [item.findall('Band_Solar_Irradiance') for item in band_measurement_list][0]
    #Localizamos las entradas 'VALUE' dentro de Band_Solar_Irradiance
    e0 = [float(item.find('VALUE').text) for item in band_solar_irradiance]

    # abrimos el raster y cargamos las bandas as nparrays
    
    spot_apilada = gdal.Open(spot_path)
    gt = spot_apilada.GetGeoTransform()
    src = spot_apilada.GetProjection()
    spot_apilada = spot_apilada.ReadAsArray()

    if len(band_id) == 1:
        pan_band=spot_apilada
        gain_pan = float(gain[0])
        bias_pan = float(bias[0])
        pan_L = pan_band / gain_pan + bias_pan
        e0_pan = e0[0]

        pan_p = (np.pi*pan_L*(earth_sun_d)**2)/(e0_pan*np.sin(mean_sun_elevation*np.pi/180))
        spot_P = pan_p
        
    else:
        # B2 corresponde al Rojo, B1 al Verde, B0 al Azul y B3 al Infrarrojo Cercano, y que ocupan las posiciones 1,2,3 y 4
        # levantamos las bandas
        red_band = spot_apilada[0,:,:]
        green_band = spot_apilada[1,:,:]
        blue_band = spot_apilada[2,:,:]
        NIR_band = spot_apilada[3,:,:]
        #Leemos los factores aditivos y multiplicativos:
        gain_red = float(gain[0])
        bias_red = float(bias[0])
        gain_green = float(gain[1])
        bias_green = float(bias[1])
        gain_blue = float(gain[2])
        bias_blue = float(bias[2])
        gain_NIR = float(gain[3])
        bias_NIR = float(bias[3])
        #Calculamos la radiancia:
        red_L = red_band / gain_red + bias_red
        green_L = green_band / gain_green + bias_green
        blue_L = blue_band / gain_blue + bias_blue
        nir_L = NIR_band / gain_NIR + bias_NIR

        # irradiancia solar o exoatmosférica para cada banda       
        e0_red = e0[0]
        e0_green = e0[1]
        e0_blue = e0[2]
        e0_nir = e0[3]

        #Calculamos la reflectancia
        # Atención: Cuando usamos la función seno o coseno, el ángulo debe estar expresado en radianes
        red_p = (np.pi*red_L*(earth_sun_d)**2)/(e0_red*np.sin(mean_sun_elevation*np.pi/180))
        green_p = (np.pi*green_L*(earth_sun_d)**2)/(e0_green*np.sin(mean_sun_elevation*np.pi/180))
        blue_p = (np.pi*blue_L*(earth_sun_d)**2)/(e0_blue*np.sin(mean_sun_elevation*np.pi/180))
        nir_p = (np.pi*nir_L*(earth_sun_d)**2)/(e0_nir*np.sin(mean_sun_elevation*np.pi/180))

        spot_P = np.stack((blue_p,green_p,red_p,nir_p))

    return spot_P
