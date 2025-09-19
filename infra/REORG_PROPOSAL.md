# Propuesta de Reorganización Modular - BackendBot (Resumida)

Objetivo: Reducir acoplamiento, aplicar principios SOLID y facilitar migración a producción.

1) Estructura propuesta (alta nivel)

- `backendbot/` (paquete raíz) ya existente
  - `core/` -> lógica core, interfaces (nueva), servicios básicos
  - `services/` -> adaptadores concretos (db, logger, config)
  - `bots/` -> implementaciones de bots (stateless y testables)
  - `ui/` -> UI (PyQt) con capas de adaptador
  - `api/` -> FastAPI app y routers
  - `packages/` -> código utilitario reutilizable

2) Pasos inmediatos (fase 1 refactor)

- Añadir `backendbot/core/interfaces.py` con Protocols (hecho)
- Identificar adaptadores concretos que implementan esas interfaces
- Inyectar dependencias vía `core/di/container.py` referenciando Protocols
- Mover utilidades de `utils/` a `packages/` o `services/` según corresponda
- Mantener tests y crear adaptadores de test con las Protocols

3) Riesgos y mitigaciones

- Cambios extensos en imports: usar alias y `from .interfaces import ILogger` para compatibilidad
- Rompimiento de tests: ejecutar tests por fase y mantener compatibilidad temporal

4) Tareas inmediatas

- Crear interfaces (hecho)
- Generar grafo de dependencias (hecho)
- Crear ticket/PR para introducir `interfaces.py` y ajustar DI
- Implementar un adaptador `services/logger_service.py` y `services/config_service.py` que implementen Protocols

---

Siguiente paso: crear adaptadores iniciales y actualizar `core/di/container.py` para usar Protocols en lugar de concretos. ¿Procedo creando `backendbot/services/logger_service.py` y parcheando el `container.py` para inyectar la nueva abstracción (en una rama o con commits locales)?
