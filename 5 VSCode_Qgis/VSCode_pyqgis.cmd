    @echo off
    SET OSGEO4W_ROOT=C:\OSGeo4W
    call "%OSGEO4W_ROOT%"\bin\o4w_env.bat
    call "%OSGEO4W_ROOT%"\bin\qt5_env.bat
    call "%OSGEO4W_ROOT%"\bin\py3_env.bat
    call "%OSGEO4W_ROOT%"\apps\grass\grass78\etc\env.bat

    @echo off
    path %PATH%;%OSGEO4W_ROOT%\bin
    path %PATH%;%OSGEO4W_ROOT%\apps\qgis-ltr\bin
    path %PATH%;%OSGEO4W_ROOT%\\apps\\qgis-ltr\\python\\plugins
    path %PATH%;%OSGEO4W_ROOT%\apps\grass\grass78\lib
    path %PATH%;%OSGEO4W_ROOT%\apps\grass\grass78\bin
    path %PATH%;C:\OSGeo4W\apps\Qt5\bin
    path %PATH%;C:\OSGeo4W\apps\Python39\Scripts
    path %PATH%;%OSGEO4W_ROOT%\apps\qgis-ltr\qtplugins
    path %PATH%;%OSGEO4W_ROOT%\apps\qt5\plugins



    set PYTHONPATH=%OSGEO4W_ROOT%\apps\qgis-ltr\python
    set PYTHONHOME=%OSGEO4W_ROOT%\apps\Python39
    set PYTHONPATH=%OSGEO4W_ROOT%\apps\Python39\lib\site-packages;%PYTHONPATH%

    set PATH=C:\Program Files\Git\bin;%PATH%
    

    set QGIS_PREFIX_PATH=%OSGEO4W_ROOT:\=/%/apps/qgis-ltr
    set GDAL_FILENAME_IS_UTF8=YES
    set QT_PLUGIN_PATH=%OSGEO4W_ROOT%\apps\qgis-ltr\qtplugins;%OSGEO4W_ROOT%\apps\qt5\plugins
    
    start "VisualStudioCode for PyQGIS" /B "C:\Microsoft VS Code\Code.exe"%*