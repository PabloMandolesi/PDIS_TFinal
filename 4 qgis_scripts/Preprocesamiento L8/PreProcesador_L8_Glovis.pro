;.FULL_RESET_SESSION
;.compile 'F:\!L8\Pasapera\Procesador_L8_v3.pro'
;SAVE, /ROUTINES, FILENAME='F:\!L8\Pasapera\Procesador_L8_v3.sav'

;PRO procesador_L8_v3,event   ;version1.0
;autor: Mario Lanfri
;version para windows
;Crea el directorio REFL
;Crea el directorio NDVI
;Crea el directorio LST

;En C:\Program Files\ITT\IDL\IDL80\products\envi48\menu esta en archivo -> envi.men
; hay que editarlo y agregar en la seccion de
;preprocessing calibration utilitiesRadar) lo siguiente 2 {Landsat 8} {open procesador_L8}  {not used}


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;; MODIFICAR LAS SIGUIENTES CARPETAS:;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

dir_desc= "C:\Preprocesamiento L8\Descomprimida\" ;directorio donde estan los archivos con las imagenes descomprimidas

cd,dir_desc
dirin_1="C:\Preprocesamiento L8\PreProcesadas\" ; donde voy a guardar las carpetas de resultados
dir_reproyect="C:\Preprocesamiento L8\ReproyectadaBase\" ; carpeta donde esta el archivo "im_reproyectada.hdr"

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
files=FILE_SEARCH('L*', count=nfiles)
for k1=0,nfiles-1 do begin

;agarro cada carpeta y empiezo el analisis:   guardo los stack en una carpeta y guardo los ndvi en otra carpeta
  CD, files[k1]
  CD, CURRENT=curr & PRINT, curr
  mtdata=FILE_SEARCH('*_MTL.txt')

  compile_opt IDL2
  ENVI, /restore_base_save_files
  ENVI_INIT, /batch_mode
  ;metaname= envi_pickfile(title='Seleccione el archivo de metadatos (*_MTL.txt) de los datos Landsat 8)')
  ;metaname="E:\CAEARTE\LucasL8\L8\LC82290822013266LGN00_MTL.txt" 
  metaname=[curr+"\"+mtdata]
  posdir= STRSPLIT(metaname, "\", COUNT=count)  ;separa en COUNT pedazos, en posdir estan los largos de esos pedazos

  last=posdir[count-1]                        ; por ej. last=22
  directorio=STRMID(metaname,0,last)          ;tiene el \ del final  i.e.  E:\CAEARTE\LucasL8\L8\
  metafilename=STRMID(metaname,last)
  prefijo=STRMID(metafilename,0,41)             ;LC82290822013266LGN00_          LC08_L1TP_227085_20180416_20180501_01_T1_B5   (41 caracteres antes del B5)

  bandnames=[prefijo+"BQA.TIF",prefijo+"B1.TIF",prefijo+"B2.TIF",prefijo+"B3.TIF",prefijo+"B4.TIF",prefijo+"B5.TIF",prefijo+"B6.TIF",prefijo+"B7.TIF",$
  prefijo+"B8.TIF",prefijo+"B9.TIF",prefijo+"B10.TIF",prefijo+"B11.TIF"]

  ;Lectura de los metadatos
  metadatafile=directorio+prefijo+"MTL.txt"
  openr,1,metadatafile; ;LC82290822013266LGN00_MTL.txt
  fila1=""          ;aca pone la fila 0
  metadata=""
  while(not eof(1)) do begin
    readf,1,fila1
    metadata=[metadata,[fila1]]
  endwhile
  close,1     ;termino de leer los metadatos
  dimmeta=size(metadata)
  ;auxmeta=strarr(dimmeta[1])

  for i=0,dimmeta[1]-1 do begin
  auxmeta=metadata[i]
  IF(STRPOS(auxmeta, ' SPACECRAFT_ID') NE -1) then SPACECRAFT_ID_line=i
  IF(STRPOS(auxmeta, ' SENSOR_ID') NE -1) then SENSOR_ID_line=i
  IF(STRPOS(auxmeta, ' WRS_PATH') NE -1) then WRS_PATH_line=i
  IF(STRPOS(auxmeta, ' WRS_ROW') NE -1) then WRS_ROW_line=i
  IF(STRPOS(auxmeta, ' DATE_ACQUIRED') NE -1) then DATE_ACQUIRED_line=i

  IF(STRPOS(auxmeta, ' REFLECTIVE_LINES') NE -1) then REFLECTIVE_LINES_line=i
  IF(STRPOS(auxmeta, ' REFLECTIVE_SAMPLES') NE -1) then REFLECTIVE_SAMPLES_line=i

  IF(STRPOS(auxmeta, ' REFLECTANCE_MULT_BAND_1') NE -1) then REFLECTANCE_MULT_BAND_1_line=i
  IF(STRPOS(auxmeta, ' REFLECTANCE_MULT_BAND_2') NE -1) then REFLECTANCE_MULT_BAND_2_line=i
  IF(STRPOS(auxmeta, ' REFLECTANCE_MULT_BAND_3') NE -1) then REFLECTANCE_MULT_BAND_3_line=i
  IF(STRPOS(auxmeta, ' REFLECTANCE_MULT_BAND_4') NE -1) then REFLECTANCE_MULT_BAND_4_line=i
  IF(STRPOS(auxmeta, ' REFLECTANCE_MULT_BAND_5') NE -1) then REFLECTANCE_MULT_BAND_5_line=i
  IF(STRPOS(auxmeta, ' REFLECTANCE_MULT_BAND_6') NE -1) then REFLECTANCE_MULT_BAND_6_line=i
  IF(STRPOS(auxmeta, ' REFLECTANCE_MULT_BAND_7') NE -1) then REFLECTANCE_MULT_BAND_7_line=i
  IF(STRPOS(auxmeta, ' REFLECTANCE_MULT_BAND_8') NE -1) then REFLECTANCE_MULT_BAND_8_line=i
  IF(STRPOS(auxmeta, ' REFLECTANCE_MULT_BAND_9') NE -1) then REFLECTANCE_MULT_BAND_9_line=i

  IF(STRPOS(auxmeta, ' REFLECTANCE_ADD_BAND_1') NE -1) then REFLECTANCE_ADD_BAND_1_line=i
  IF(STRPOS(auxmeta, ' REFLECTANCE_ADD_BAND_2') NE -1) then REFLECTANCE_ADD_BAND_2_line=i
  IF(STRPOS(auxmeta, ' REFLECTANCE_ADD_BAND_3') NE -1) then REFLECTANCE_ADD_BAND_3_line=i
  IF(STRPOS(auxmeta, ' REFLECTANCE_ADD_BAND_4') NE -1) then REFLECTANCE_ADD_BAND_4_line=i
  IF(STRPOS(auxmeta, ' REFLECTANCE_ADD_BAND_5') NE -1) then REFLECTANCE_ADD_BAND_5_line=i
  IF(STRPOS(auxmeta, ' REFLECTANCE_ADD_BAND_6') NE -1) then REFLECTANCE_ADD_BAND_6_line=i
  IF(STRPOS(auxmeta, ' REFLECTANCE_ADD_BAND_7') NE -1) then REFLECTANCE_ADD_BAND_7_line=i
  IF(STRPOS(auxmeta, ' REFLECTANCE_ADD_BAND_8') NE -1) then REFLECTANCE_ADD_BAND_8_line=i
  IF(STRPOS(auxmeta, ' REFLECTANCE_ADD_BAND_9') NE -1) then REFLECTANCE_ADD_BAND_9_line=i

  IF(STRPOS(auxmeta, ' K1_CONSTANT_BAND_10') NE -1) then K1_CONSTANT_BAND_10_line=i
  IF(STRPOS(auxmeta, ' K1_CONSTANT_BAND_11') NE -1) then K1_CONSTANT_BAND_11_line=i
  IF(STRPOS(auxmeta, ' K2_CONSTANT_BAND_10') NE -1) then K2_CONSTANT_BAND_10_line=i
  IF(STRPOS(auxmeta, ' K2_CONSTANT_BAND_11') NE -1) then K2_CONSTANT_BAND_11_line=i


  IF(STRPOS(auxmeta, ' RADIANCE_MULT_BAND_10') NE -1) then RADIANCE_MULT_BAND_10_line=i
  IF(STRPOS(auxmeta, ' RADIANCE_ADD_BAND_10') NE -1) then RADIANCE_ADD_BAND_10_line=i

  IF(STRPOS(auxmeta, ' RADIANCE_MULT_BAND_11') NE -1) then RADIANCE_MULT_BAND_11_line=i
  IF(STRPOS(auxmeta, ' RADIANCE_ADD_BAND_11') NE -1) then RADIANCE_ADD_BAND_11_line=i

  endfor
  


  ;texto =[metadata[SPACECRAFT_ID_line], metadata[SENSOR_ID_line], metadata[WRS_PATH_line], metadata[WRS_ROW_line], metadata[DATE_ACQUIRED_line], $
  ;"Procesador_L8.v3 ","Mario Lanfri - 2014", "CAEARTE - CONAE"]
  ;metadata14= SPACECRAFT_ID = "LANDSAT_8"
  ;metadata15= SENSOR_ID = "OLI"
  ;metadata16= WRS_PATH = 226
  ;metadata17= WRS_ROW = 85
  ;metadata21= DATE_ACQUIRED = 2014-08-04

  ;Result = DIALOG_MESSAGE(texto,/information,title="Caracteristicas de la imagen")
  path=STRMID(metadata[WRS_PATH_line],15)
  row=STRMID(metadata[WRS_ROW_line],14)
  y1=STRMID(metadata[DATE_ACQUIRED_line],20,4)
  m1=STRMID(metadata[DATE_ACQUIRED_line],25,2)
  d1=STRMID(metadata[DATE_ACQUIRED_line],28,2)
 nome1=['P',path, '-R0', row,'-', y1,m1,d1,'-L8-L1I']
 nome_ndvi=strjoin(nome1)
 
 nome2=['P',path, '-R0', row,'-', y1,m1,d1,'-L8-L1T']
 nome_stack=strjoin(nome2)


  lineasref=STRMID(metadata[REFLECTIVE_LINES_line], STRLEN(metadata[REFLECTIVE_LINES_line])-5, 5)
  columnasref=STRMID(metadata[REFLECTIVE_SAMPLES_line], STRLEN(metadata[REFLECTIVE_SAMPLES_line])-5, 5)   ;aca estaba mal... decia lo siguiente: columnasref=STRMID(metadata[42], STRLEN(metadata[41])-5, 5)

  gralout=STRMID(prefijo,0,16)          ;L8_2290822013266 generico para las salidas

  ;calibracion bandas

  out_fids = intarr(12)
  dims= [-1, 0, columnasref-1, 0, lineasref-1]         ;por aqui da el error Type conversion error: Unable to convert given STRING to Long.

  ;FILE_MKDIR, dirin_1+'imagenRGB'
  FILE_MKDIR, dirin_1+'DELETE'
  FILE_MKDIR, dirin_1+'NDVIs'
  FILE_MKDIR, dirin_1+'STACKs'

  ;dirout_rgb=dirin_1+"imagenRGB\"
  dirout_delete=dirin_1+'DELETE\'
  dirout_ndvi=dirin_1+'NDVIs\'
  dirout_stack=dirin_1+'STACKs\'

  aux15=STRSPLIT(metadata[SENSOR_ID_line],"=")            ;esta es la linea que dice si el sensor es OLI o OLI_TIRS
  MULT15=STRMID(metadata[SENSOR_ID_line],aux15[1])

; CALCULO REFLECTANCIA PARA DESPUES CALCULAR NDVI
  k=[4,5]
  for j=0,1 do begin
      i=k[j]
      fname =directorio+bandnames[i]
      envi_open_data_file, fname, /tif, r_fid=fid
      if (fid eq -1) then return

      out_proj = envi_get_projection(fid=fid,pixel_size=out_ps)

     if(strlen(mult15)le 6) then begin      ;caso OLI     (ETC)
         aux1=STRSPLIT(metadata[REFLECTANCE_MULT_BAND_1_line],"=")
         MULT1=STRMID(metadata[REFLECTANCE_MULT_BAND_1_line],aux1[1])
         aux2=STRSPLIT(metadata[REFLECTANCE_ADD_BAND_1_line],"=")
         ADD1=STRMID(metadata[REFLECTANCE_ADD_BAND_1_line],aux2[1])
      endif else begin                   ;caso OLI_TIRS   (USGS)
         aux1=STRSPLIT(metadata[REFLECTANCE_MULT_BAND_1_line],"=")
         MULT1=STRMID(metadata[REFLECTANCE_MULT_BAND_1_line],aux1[1])
         aux2=STRSPLIT(metadata[REFLECTANCE_ADD_BAND_1_line],"=")
         ADD1=STRMID(metadata[REFLECTANCE_ADD_BAND_1_line],aux2[1])
      endelse

     MULTasc=string(MULT1)
     ADDasc=string(ADD1)
     envi_file_query, fid, ns=ns, nl=nl

     ;if(i eq 8 ) then dims8 = [-1, 0, ns-1, 0, nl-1]
     dims = [-1, 0, ns-1, 0, nl-1]
     pos  = [0]

     exp1 = ADDasc + " + (" + MULTasc+") * b"+strtrim(string(i),1)        ;exp1 = 'ADD + MULT * b1'
     print,exp1
     out_name = dirout_delete+gralout+'_B'+strtrim(string(i),1)+"_ref"
     envi_doit, 'math_doit', fid=fid, pos=pos, dims=dims, exp=exp1, out_name=out_name, r_fid=out_fid
     out_fids[i]=out_fid
     ENVI_FILE_MNG, id=fid, /REMOVE
  endfor

;CALCULO EL NDVI
  expndvi='(float(b2)-float(b1))/(float(b2)+float(b1))'
  ;dir_out=dirout_delete
  outname_ndvi=dirout_delete+gralout+'_NDVI'
  fidndvi=[out_fids[4],out_fids[5]]
  envi_doit, 'math_doit', fid=fidndvi, pos=[0,0], dims=dims, exp=expndvi, out_name=outname_ndvi, r_fid=out_ndvi

;PARA ARMAR EL STACK
  fids= MAKE_ARRAY(9, 1, /INTEGER)
  k=[0,1,2,3,4,5,6,7,9]
  c=0
  dimension = lonarr(5,9,/NOZERO)
  for j=0,8 do begin
      i=k[j]
      fname =directorio+bandnames[i]
      envi_open_data_file, fname, /tif, r_fid=fid
      fids[c]=fid
      envi_file_query, fid, ns=t_ns, nl=t_nl
      dims =[-1,0,t_ns-1,0,t_nl-1]
      dimension[0:4,c]=dims
      c=c+1
  endfor

;hacemos el stack
  nameout=strmid(prefijo,0,16)
  out_proj=ENVI_GET_PROJECTION(FID=fids[2], PIXEL_SIZE=out_ps)
  pos = lonarr(9)
  out_name=[dirout_delete+nameout+"_Stack"]
  fid_out=[fids[1:8],fids[0]]
  band_names_out=[[nameout+"_B1"],[nameout+"_B2"],[nameout+"_B3"],[nameout+"_B4"],[nameout+"_B5"],[nameout+"_B6"],[nameout+"_B7"],[nameout+"_B9"],[nameout+"_BQA"]]
  ENVI_DOIT,'ENVI_LAYER_STACKING_DOIT',DIMS=dimension, FID=fid_out, INTERP=0,OUT_DT=12, OUT_NAME=out_name, OUT_PROJ=out_proj, OUT_PS=out_ps,OUT_BNAME=band_names_out, POS=pos, R_FID=fid_s; este tendria que quedar en memoria /MEMORY


;reproyectar: crear la proyeccion (no es lo ideal)

  ENVI_OPEN_FILE,dir_reproyect+"im_reproyectada",R_FID=fid1
  o_proj = ENVI_GET_PROJECTION(FID = fid1)

;reproyecto stack
  OUT_NAME=[dirout_stack+gralout+"_Stack_POSGAR94_z5"]
  OUT_BNAME=[[nameout+"_B1"],[nameout+"_B2"],[nameout+"_B3"],[nameout+"_B4"],[nameout+"_B5"],[nameout+"_B6"],[nameout+"_B7"],[nameout+"_B9"],[nameout+"_BQA"]]
  ENVI_CONVERT_FILE_MAP_PROJECTION, BACKGROUND=0, DIMS=dims, FID=fid_s, GCP_NAME="warp_points", O_PROJ=o_proj , OUT_NAME=[dirout_stack+nome_stack], OUT_BNAME=OUT_BNAME, POS=[0,1,2,3,4,5,6,7,8], R_FID=fid_r, RESAMPLING=0, WARP_METHOD=2

;reproyecto ndvi
  ENVI_CONVERT_FILE_MAP_PROJECTION, BACKGROUND=0, DIMS=dims, FID=out_ndvi, GCP_NAME="warp_points", O_PROJ=o_proj , OUT_NAME=[dirout_ndvi+nome_ndvi], POS=[0], R_FID=fid_r_ndvi, RESAMPLING=0, WARP_METHOD=2

cd, dir_desc

endfor

FILE_DELETE, dirin_1+"DELETE", /RECURSIVE

end