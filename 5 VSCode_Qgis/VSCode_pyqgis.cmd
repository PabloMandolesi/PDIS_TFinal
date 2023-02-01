    @REM @echo off
    SET OSGEO4W_ROOT=C:\OSGeo4W

    for %%f in ("%OSGEO4W_ROOT%\etc\ini\*.bat") do call "%%f"
    call "%OSGEO4W_ROOT%\bin\o4w_env.bat"
    call "%OSGEO4W_ROOT%\etc\ini\qt5_env.bat"
    call "%OSGEO4W_ROOT%\etc\ini\python3_env.bat"
    call "%OSGEO4W_ROOT%\apps\grass\grass82\etc\env.bat"


    @REM @REM @echo off
    path %PATH%;%OSGEO4W_ROOT%\bin
    path %PATH%;%OSGEO4W_ROOT%\apps\qgis-ltr\bin
    path %PATH%;%OSGEO4W_ROOT%\apps\qgis-ltr\python
    path %PATH%;%OSGEO4W_ROOT%\apps\qgis-ltr\python\plugins
    path %PATH%;%OSGEO4W_ROOT%\apps\qgis-ltr\qtplugins
    path %PATH%;%OSGEO4W_ROOT%\apps\Python39\Scripts
    path %PATH%;%OSGEO4W_ROOT%\apps\qt5\bin
    path %PATH%;%OSGEO4W_ROOT%\apps\qt5\plugins
    path %PATH%;%OSGEO4W_ROOT%\apps\grass\grass82\lib
    path %PATH%;%OSGEO4W_ROOT%\apps\grass\grass82\bin


    @REM Este es mi agregado de valor. Las diferencias entre os.path y sys.path. Este ultimo es creado
    @REM por el interprete de python al inciarse. a partir de path y pythonpath. Aca logre iniciar directamente con 
    @REM las variables bien definidas desde el inicio. Para hacer append en PYTHONPATH hay que repetir el nombre al 
    @REM final de la oracion; e incluir el separador ; 
    @REM fuente: https://exchangetuts.com/difference-between-path-syspath-and-osenviron-1640090403544654
    set PYTHONPATH=%OSGEO4W_ROOT%\apps\qgis-ltr\python
    set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\qgis-ltr\python\plugins
    set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\grass\grass82\etc\python

    @REM set PYTHONPATH=%OSGEO4W_ROOT%\apps\Python39\lib\site-packages;%PYTHONPATH%



    set PYTHONHOME=%OSGEO4W_ROOT%\apps\Python39
    set PYTHONUTF8=1
    set PATH=C:\Program Files\Git\bin;%PATH%    

    set QGIS_PREFIX_PATH=%OSGEO4W_ROOT:\=/%/apps/qgis-ltr
    set GDAL_PAM_ENABLED=NO
    set GDAL_FILENAME_IS_UTF8=YES
    set VSI_CACHE=TRUE
    set VSI_CACHE_SIZE=1000000
    set QT_PLUGIN_PATH=%OSGEO4W_ROOT%\apps\qgis-ltr\qtplugins;%OSGEO4W_ROOT%\apps\qt5\plugins
    
    @REM call VSCode
    start "VisualStudioCode for PyQGIS" /B "C:\Users\pablo.mandolesi\AppData\Local\Programs\Microsoft VS Code\Code.exe"%*