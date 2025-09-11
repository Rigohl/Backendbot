# 🖥️ BackendBot – Supervisor Autónomo de Procesos

**BackendBot** es un sistema local y cloud-ready que mantiene tu backend siempre en ejecución, optimiza recursos y te da control desde la bandeja del sistema o dashboard web. Soporta almacenamiento local (SQLite) y remoto (Neon/Postgres).

---

## 🖼️ Ejemplo de Dashboard
![Dashboard ejemplo](../dashboard/dashboard_ejemplo.png)

El dashboard muestra:
- Estado del backend (RAM, CPU, uptime, modo actual)
- Gráficos de uso de RAM y CPU en tiempo real
- Lista de procesos y acciones rápidas
- Historial de optimizaciones y eventos recientes
- Selector de modo y cambio instantáneo

## 🕹️ Modos de Operación
Cada modo (Diario, Editor, Videojuego, Streaming, Multimedia, Focus) ajusta la política de suspensión y priorización de procesos. Puedes cambiar el modo desde la bandeja, dashboard o API (`/set-modo/{modo}`).

## ⚙️ Personalización
- Edita `config.py` para definir procesos importantes, umbrales y modos personalizados.
- Puedes agregar/quitar procesos hibernables y ajustar los límites de RAM/CPU.

## ❓ FAQ y Mejores Prácticas
- **¿Qué pasa si Neon falla?** Se usa SQLite local automáticamente.
- **¿Cómo restauro procesos importantes?** Usa el botón en la bandeja o el endpoint `/restore-important`.
- **¿Cómo optimizo RAM?** Usa el botón del dashboard o `/optimize`.
- **¿Cómo agrego un modo nuevo?** Edita la lista en `config.py` y reinicia el backend.

## 🏆 Recomendaciones
- Mantén actualizados los umbrales según tu uso.
- Revisa el historial para identificar procesos problemáticos.
- Usa el dashboard para monitoreo en tiempo real y acciones rápidas.

---

## 📋 Características

- Monitoreo en tiempo real de procesos y recursos del sistema.
- Optimización automática de RAM suspendiendo/cerrando procesos hibernables.
- Watchdog inteligente con aprendizaje basado en decisiones previas.
- Dashboard web y API para visualizar procesos, métricas y reportes.
- Icono en bandeja del sistema para control rápido y cambio de modos.
- Soporte para despliegue local y en la nube (Railway, Fly.io, Neon).
- Historial y reportes guardados en Neon/Postgres o SQLite.

## 🛠️ Instalación y Despliegue

### Local (Windows/Linux)
1. Clona o descarga el repositorio.
2. Instala dependencias (incluye soporte Neon/Postgres):
   ```
   pip install -r requirements.txt
   # requirements.txt incluye psycopg2-binary para Neon/Postgres
   ```
3. Ejecuta el backend:
   ```
   python -m src.backendbot.main
   ```
4. Usa los scripts y el dashboard como antes.

### Railway / Fly.io / Neon
1. Sube el proyecto a Railway/Fly.io.
2. Configura la variable de entorno `DATABASE_URL` con la URL de Neon/Postgres. Ejemplo:
   ```
   DATABASE_URL=postgresql://usuario:contraseña@ep-neon-db.neon.tech:5432/backendbot
   ```
   Si no se define, se usará SQLite local automáticamente.
3. El backend se inicia automáticamente con:
   ```
   web: uvicorn src.backendbot.main:app --host 0.0.0.0 --port 8000
   ```
   (Procfile ya incluido)
4. Accede al dashboard/API en la URL pública del servicio.

## ⚙️ Configuración

- Umbrales: CPU >80%, RAM >4000 MB por 60s.
- Procesos hibernables y modos configurables en `config.py`.
- Historial y reportes en Neon/Postgres si `DATABASE_URL` está definido, o SQLite local.

## 🗄️ Base de datos
- **Local:** SQLite (`data/backend_data.db`) (fallback automático si no hay `DATABASE_URL`)
- **Cloud:** Neon/Postgres (`DATABASE_URL`)
- Tablas: `process_history`, `optimization_events`, `watchdog_decisions`

## 🚀 Modos de Operación
- Diario, Editor, Videojuego, Streaming, Multimedia, Focus.
- Cambia modos desde la bandeja o API `/set-modo/{modo}`.

## 📚 API Endpoints
- `/procesos`, `/apagar/{pid}`, `/resume/{pid}`, `/kill/{pid}`, `/optimize`, `/set-modo/{modo}`, `/restore-important`, `/self`, `/memoria`, `/reset-memoria`.

## 🗑️ Sugerencias de Desinstalación
- (Ver recomendaciones previas)


## 🧪 Pruebas y Cobertura
- Tests unitarios en `tests/` para módulos principales (`utils`, `api_routes`, etc).
- Ejecuta los tests con:
   ```
   pytest tests/
   ```

## 🚀 Próximas Mejoras y Hoja de Ruta
- Dashboard avanzado, suspensión inteligente, gestión dinámica, integración GPU, reportes exportables, etc.


## ☁️ Despliegue No Local (Opciones de Backend Remoto)

## 🛠️ Troubleshooting Railway/Fly.io/Neon
- Verifica que `DATABASE_URL` esté correctamente configurada.
- Revisa los logs del servicio para errores de conexión.
- Asegúrate de que `psycopg2-binary` esté instalado (ver `requirements.txt`).
- Si falla la conexión Neon, el sistema usará SQLite local automáticamente.
- Railway, Fly.io, Neon/Postgres, Render.com, Docker.

---

## 📊 Dashboard Web

El dashboard es una interfaz web moderna construida con HTML5, Tailwind CSS y Chart.js para monitoreo en tiempo real.

### Características del Frontend
- **Estado del Backend**: Muestra PID, RAM, CPU, uptime y modo actual.
- **Gráficos en Tiempo Real**: RAM y CPU con Chart.js, actualizados cada 5 segundos.
- **Lista de Procesos**: Tabla con PID, nombre, RAM y botón para cerrar procesos.
- **Historial de Optimizaciones**: Lista de eventos de liberación de RAM.
- **Selector de Modo**: Cambia entre modos predefinidos (diario, editor, etc.).
- **Acciones Rápidas**: Optimizar RAM, resetear memoria.
- **Logs en Tiempo Real**: Muestra las últimas entradas del log del backend.
- **Configuración**: Permite cambiar URL del backend y API Key.

### APIs Utilizadas
- `GET /self`: Estado del backend.
- `GET /procesos`: Lista de procesos activos.
- `POST /apagar/{pid}`: Cerrar un proceso.
- `POST /optimize`: Optimizar RAM.
- `POST /reset-memoria`: Resetear memoria de decisiones.
- `GET /modos`: Lista de modos disponibles.
- `POST /set-modo/{modo}`: Cambiar modo.
- `GET /history/optimizations`: Historial de optimizaciones.
- `GET /logs`: Últimas entradas del log.

### Configuración
- **URL del Backend**: Por defecto `http://127.0.0.1:8000`.
- **API Key**: Por defecto `your-super-secret-api-key` (cambiar en `config.py`).

### Mejoras Recientes
- Autenticación con API Key en lugar de Basic Auth.
- Manejo de errores mejorado en todas las requests.
- Actualización de endpoints para coincidir con el backend.
- Interfaz responsiva y moderna.

### Tests del Frontend
Para probar el frontend, abrir `dashboard/index.html` en un navegador y verificar:
- Conexión al backend.
- Carga de datos sin errores.
- Funcionalidad de botones.
- Actualización en tiempo real.

Para tests automatizados, se recomienda integrar Jest o similar para funciones JS.

Ejemplo de instalación:
```bash
npm init -y
npm install --save-dev jest
```

Crear `tests/dashboard_tests.js`:
```javascript
const { apiRequest } = require('../dashboard/index.html'); // Nota: Requiere extraer JS a archivo separado

test('apiRequest adds API key header', () => {
  // Mock fetch
  global.fetch = jest.fn();
  apiRequest('/test');
  expect(fetch).toHaveBeenCalledWith('http://127.0.0.1:8000/test', {
    headers: { 'X-API-Key': 'your-super-secret-api-key', 'Content-Type': 'application/json' }
  });
});
```

Ejecutar con `npx jest`.

---

**Para dudas o soporte, consulta la documentación o abre un issue.**