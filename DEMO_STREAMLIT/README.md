# Geoportal para Streamlit: demostracion sin datos reales

Esta carpeta es independiente del visor local y no necesita GDB, Excel,
GeoPackage ni servidor de consultas. Todos los rectangulos, codigos, direcciones,
areas y clasificaciones son inventados para probar la interfaz.
No representan la cartografia ni el inventario real de Neiva.

## Ejecutar localmente

```powershell
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

## Publicar la demostracion privada

1. Subir la carpeta DEMO_STREAMLIT al repositorio privado del Geoportal.
2. Entrar en https://share.streamlit.io/ con la cuenta autorizada.
3. Seleccionar Create app y el repositorio geoportal-neiva-pruebas.
4. Seleccionar la rama real del repositorio.
5. Entry point: DEMO_STREAMLIT/streamlit_app.py
6. Elegir Python 3.13 en los ajustes de despliegue.
7. Elegir un subdominio disponible y desplegar.
8. Revisar Settings > Sharing > Only specific people can view this app.
9. Invitar los correos autorizados desde Share. Comprobar desde una sesion
   no autorizada que el mapa no queda accesible.

La URL solo existe despues de que el despliegue termine correctamente.
La autenticacion la gestiona Streamlit Community Cloud, no esta aplicacion.
Segun su documentacion, Community Cloud permite una aplicacion privada a la vez;
si ese cupo ya esta ocupado, no cambiar otra aplicacion a publica para liberarlo.
Resolverlo con el administrador antes de continuar.

No sustituir estos ejemplos por datos institucionales sin autorizar previamente
el alojamiento, tratamiento y acceso. El codigo no implementa administracion
propia de usuarios. La configuracion de invitaciones y sus permisos debe ser
revisada por el responsable del espacio de trabajo.

Los mapas base externos solicitan teselas a OpenStreetMap/Esri y revelan al
proveedor la extension visualizada, no las consultas de los predios ficticios.
Los recursos OpenLayers conservan su licencia en resources/LICENSE-OpenLayers.txt.
