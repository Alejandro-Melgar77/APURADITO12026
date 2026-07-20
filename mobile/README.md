# Apuradito Mobile

Cliente Flutter para pasajeros y conductores. La app no contiene URLs de
desarrollo o producción fijas: se configuran al compilar con `--dart-define`.

## Ejecutar localmente

Para el emulador Android, con el backend en el puerto 8000:

```powershell
flutter pub get
flutter run
```

El valor local por defecto es `http://10.0.2.2:8000`, que representa el
localhost de la computadora anfitriona desde el emulador Android.

Para un teléfono físico, usa la IP privada de la computadora, siempre que
ambos estén en la misma red:

```powershell
flutter run --dart-define=API_BASE_URL=http://192.168.1.50:8000
```

En iOS, usa un túnel HTTPS para el backend local (por ejemplo, Cloudflare
Tunnel), porque iOS bloquea HTTP sin cifrar por seguridad.

## Ejecutar contra producción

Reemplaza la URL por la URL HTTPS del Web Service de Render. El WebSocket se
deriva automáticamente como `wss://.../ws/viajes`.

```powershell
flutter run --dart-define=API_BASE_URL=https://apuradito-backend.onrender.com
```

Si el WebSocket usa un host o ruta diferente, indícalo explícitamente:

```powershell
flutter run --dart-define=API_BASE_URL=https://apuradito-backend.onrender.com --dart-define=WS_VIAJES_URL=wss://apuradito-backend.onrender.com/ws/viajes
```

Para generar un APK de producción:

```powershell
.\build_apk.ps1 -ApiBaseUrl "https://apuradito-backend.onrender.com"
```

## Verificación

```powershell
flutter analyze
flutter test
```
## Generar APK APURADITO

Desde la carpeta `mobile`, ejecuta:

```powershell
.\build_apk.ps1 -ApiBaseUrl "https://TU-BACKEND.onrender.com"
```

El archivo final quedará en:

```text
build\app\outputs\flutter-apk\APURADITO.apk
```

Para generar APKs separados por arquitectura:

```powershell
.\build_apk.ps1 -SplitPerAbi
```

El nombre visible de la aplicación en Android e iOS es `APURADITO`. Si cambias el logo, vuelve a generar los iconos nativos con:

```powershell
dart run flutter_launcher_icons
```

## Versión PWA instalable y sin conexión

La carpeta `web/` ya incluye el manifiesto de APURADITO y un service worker
propio. Después de abrirla una vez con internet, la PWA conserva la interfaz y
los recursos de la app para volver a abrirse sin red; las rutas, billetera y
viajes muestran el último dato guardado. Las publicaciones de ruta y las
calificaciones no financieras se sincronizan al recuperar conexión. Reservas,
cancelaciones y operaciones con Coins siempre requieren conexión para evitar
cobros o asientos duplicados.

Para generar la PWA apuntando al backend publicado:

```powershell
flutter build web --release --dart-define=API_BASE_URL=https://TU-BACKEND.onrender.com
```

Publica el contenido de `build\web` detrás de HTTPS (por ejemplo, un Static
Site de Render). En Chrome/Edge para Android y en navegadores de escritorio se
podrá instalar desde el botón de instalación del navegador.

### Nota para Windows

Flutter necesita que Windows permita enlaces simbólicos para compilar plugins.
Si `flutter pub get`, `flutter analyze` o el build muestra ese aviso, abre una
terminal y ejecuta `start ms-settings:developers`; activa **Modo de
desarrollador** y vuelve a abrir la terminal.
