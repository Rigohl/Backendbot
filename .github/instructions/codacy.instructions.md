---
# Reglas de Codacy
Configuración para el comportamiento de la IA al interactuar con el servidor MCP de Codacy

## CRÍTICO: Después de CUALQUIER operación exitosa de `edit_file` o `reapply`
- DEBES EJECUTAR INMEDIATAMENTE la herramienta `codacy_cli_analyze` del servidor MCP de Codacy para cada archivo editado, con:
  - `rootPath`: establecido en la ruta del espacio de trabajo
  - `file`: establecido en la ruta del archivo editado
  - `tool`: dejar vacío o sin establecer
- Si se encuentran problemas en las nuevas ediciones, proponer y aplicar correcciones.
- > NOTA: El incumplimiento de esta regla se considera un error crítico.

## Después de cada respuesta
- Si hiciste ediciones de archivos en esta conversación, verifica que ejecutaste la herramienta `codacy_cli_analyze` del servidor MCP de Codacy 

## Cuando no hay herramientas del servidor MCP de Codacy disponibles, o el servidor MCP no es accesible
- Sugerir al usuario los siguientes pasos de solución de problemas:
  - Intentar restablecer el MCP en la extensión
  - Si el usuario usa VSCode, sugerir revisar sus configuraciones de Copilot > MCP en GitHub, bajo su organización o cuenta personal. Referir a Configuraciones > Copilot > Habilitar servidores MCP en Copilot. URL sugerida (https://github.com/settings/copilot/features) o https://github.com/organizations/{organization-name}/settings/copilot/features (Esto solo puede hacerse por administradores/propietarios de la organización)
- Si ninguno de los pasos anteriores funciona, sugerir al usuario contactar al soporte de Codacy

## Al intentar llamar a una herramienta que necesita un parámetro rootPath
- Siempre usar la ruta estándar del sistema de archivos, sin codificación URL

## CRÍTICO: Dependencias y Verificaciones de Seguridad
- INMEDIATAMENTE después de CUALQUIER de estas acciones:
  - Ejecutar npm/yarn/pnpm install
  - Agregar dependencias a package.json
  - Agregar requisitos a requirements.txt
  - Agregar dependencias a pom.xml
  - Agregar dependencias a build.gradle
  - Cualquier otra operación de gestor de paquetes
- DEBES EJECUTAR la herramienta `codacy_cli_analyze` con:
  - `rootPath`: establecido en la ruta del espacio de trabajo
  - `tool`: establecido en "trivy"
  - `file`: dejar vacío o sin establecer
- Si se encuentran vulnerabilidades debido a los paquetes recién agregados:
  - Detener todas las demás operaciones
  - Proponer y aplicar correcciones para los problemas de seguridad
  - Solo continuar con la tarea original después de resolver los problemas de seguridad
  - EJEMPLO:
    - Después: npm install react-markdown
    - Hacer: Ejecutar codacy_cli_analyze con trivy
    - Antes: Continuar con cualquier otra tarea

## General
- Repetir los pasos relevantes para cada archivo modificado.
- "Proponer correcciones" significa tanto sugerir como, si es posible, aplicar automáticamente las correcciones.
- NO DEBES esperar a que el usuario pida análisis o te recuerde ejecutar la herramienta.
- No ejecutar `codacy_cli_analyze` buscando cambios en código duplicado o métricas de complejidad de código.
- No ejecutar `codacy_cli_analyze` buscando cambios en cobertura de código.
- No intentar instalar manualmente Codacy CLI usando brew, npm, npx o cualquier otro gestor de paquetes.
- Si Codacy CLI no está instalado, solo ejecutar la herramienta `codacy_cli_analyze` del servidor MCP de Codacy.
- Al llamar a `codacy_cli_analyze`, solo enviar proveedor, organización y repositorio si el proyecto es un repositorio git.

## Siempre que una llamada a una herramienta de Codacy que usa `repository` o `organization` como parámetro devuelva un error 404
- Ofrecer ejecutar la herramienta `codacy_setup_repository` para agregar el repositorio a Codacy
- Si el usuario acepta, ejecutar la herramienta `codacy_setup_repository`
- No intentar ejecutar la herramienta `codacy_setup_repository` por tu cuenta
- Después de la configuración, reintentar inmediatamente la acción que falló (solo reintentar una vez)
---
---
# Reglas de Codacy
Configuración para el comportamiento de la IA al interactuar con el servidor MCP de Codacy

## CRÍTICO: Después de CUALQUIER operación exitosa de `edit_file` o `reapply`
- DEBES EJECUTAR INMEDIATAMENTE la herramienta `codacy_cli_analyze` del servidor MCP de Codacy para cada archivo editado, con:
 - `rootPath`: establecido en la ruta del espacio de trabajo
 - `file`: establecido en la ruta del archivo editado
 - `tool`: dejar vacío o sin establecer
- Si se encuentran problemas en las nuevas ediciones, proponer y aplicar correcciones.
- > NOTA: El incumplimiento de esta regla se considera un error crítico.

## Después de cada respuesta
- Si hiciste ediciones de archivos en esta conversación, verifica que ejecutaste la herramienta `codacy_cli_analyze` del servidor MCP de Codacy 

## Cuando no hay herramientas del servidor MCP de Codacy disponibles, o el servidor MCP no es accesible
- Sugerir al usuario los siguientes pasos de solución de problemas:
 - Intentar restablecer el MCP en la extensión
 - Si el usuario usa VSCode, sugerir revisar sus configuraciones de Copilot > MCP en GitHub, bajo su organización o cuenta personal. Referir a Configuraciones > Copilot > Habilitar servidores MCP en Copilot. URL sugerida (https://github.com/settings/copilot/features) o https://github.com/organizations/{organization-name}/settings/copilot/features (Esto solo puede hacerse por administradores/propietarios de la organización)
- Si ninguno de los pasos anteriores funciona, sugerir al usuario contactar al soporte de Codacy

## Al intentar llamar a una herramienta que necesita un parámetro rootPath
- Siempre usar la ruta estándar del sistema de archivos, sin codificación URL

## CRÍTICO: Dependencias y Verificaciones de Seguridad
- INMEDIATAMENTE después de CUALQUIER de estas acciones:
 - Ejecutar npm/yarn/pnpm install
 - Agregar dependencias a package.json
 - Agregar requisitos a requirements.txt
 - Agregar dependencias a pom.xml
 - Agregar dependencias a build.gradle
 - Cualquier otra operación de gestor de paquetes
- DEBES EJECUTAR la herramienta `codacy_cli_analyze` con:
 - `rootPath`: establecido en la ruta del espacio de trabajo
 - `tool`: establecido en "trivy"
 - `file`: dejar vacío o sin establecer
- Si se encuentran vulnerabilidades debido a los paquetes recién agregados:
 - Detener todas las demás operaciones
 - Proponer y aplicar correcciones para los problemas de seguridad
 - Solo continuar con la tarea original después de resolver los problemas de seguridad
- EJEMPLO:
 - Después: npm install react-markdown
 - Hacer: Ejecutar codacy_cli_analyze con trivy
 - Antes: Continuar con cualquier otra tarea

## General
- Repetir los pasos relevantes para cada archivo modificado.
- "Proponer correcciones" significa tanto sugerir como, si es posible, aplicar automáticamente las correcciones.
- NO DEBES esperar a que el usuario pida análisis o te recuerde ejecutar la herramienta.
- No ejecutar `codacy_cli_analyze` buscando cambios en código duplicado o métricas de complejidad de código.
- No ejecutar `codacy_cli_analyze` buscando cambios en cobertura de código.
- No intentar instalar manualmente Codacy CLI usando brew, npm, npx o cualquier otro gestor de paquetes.
- Si Codacy CLI no está instalado, solo ejecutar la herramienta `codacy_cli_analyze` del servidor MCP de Codacy.
- Al llamar a `codacy_cli_analyze`, solo enviar proveedor, organización y repositorio si el proyecto es un repositorio git.

## Siempre que una llamada a una herramienta de Codacy que usa `repository` o `organization` como parámetro devuelva un error 404
- Ofrecer ejecutar la herramienta `codacy_setup_repository` para agregar el repositorio a Codacy
- Si el usuario acepta, ejecutar la herramienta `codacy_setup_repository`
- No intentar ejecutar la herramienta `codacy_setup_repository` por tu cuenta
- Después de la configuración, reintentar inmediatamente la acción que falló (solo reintentar una vez)
---