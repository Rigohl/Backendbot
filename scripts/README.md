# Scripts de BackendBot

Scripts de PowerShell para validación y deployment de BackendBot en Azure.

## 📋 Scripts Disponibles

### `validate_predeploy.ps1`
**Propósito**: Validación completa de pre-deployment que reemplaza la función `azure_check_predeploy` problemática.

**Uso**:
```powershell
.\validate_predeploy.ps1 [parámetros]
```

**Parámetros**:
- `-EnvironmentName`: Nombre del entorno (default: "backendbot-dev")
- `-Location`: Región de Azure (default: "eastus")
- `-SkipQuotaCheck`: Omitir verificación de quotas
- `-Verbose`: Salida detallada

**Validaciones realizadas**:
- ✅ Autenticación en Azure
- ✅ Existencia de archivos de infraestructura
- ✅ Sintaxis de Bicep/Terraform
- ✅ Providers de Azure registrados
- ✅ Recursos disponibles en la región
- ✅ Quotas de servicios (opcional)

### `deploy_backendbot.ps1`
**Propósito**: Deployment completo de BackendBot incluyendo validación automática.

**Uso**:
```powershell
.\deploy_backendbot.ps1 [parámetros]
```

**Parámetros**:
- `-EnvironmentName`: Nombre del entorno (default: "backendbot-dev")
- `-Location`: Región de Azure (default: "eastus")
- `-SkipValidation`: Omitir validación de pre-deployment
- `-SkipQuotaCheck`: Omitir verificación de quotas
- `-Verbose`: Salida detallada

**Proceso de deployment**:
1. 🔍 Validación de pre-deployment (opcional)
2. 📁 Creación/verificación de grupo de recursos
3. 🚀 Deployment de infraestructura via Bicep
4. 📋 Mostrar outputs y URLs de acceso

## 🚀 Uso Rápido

### Deployment Básico
```powershell
# Desde el directorio raíz del proyecto
.\scripts\deploy_backendbot.ps1
```

### Deployment con Parámetros Personalizados
```powershell
.\scripts\deploy_backendbot.ps1 -EnvironmentName "backendbot-staging" -Location "westeurope" -Verbose
```

### Solo Validación
```powershell
.\scripts\validate_predeploy.ps1 -EnvironmentName "backendbot-prod" -SkipQuotaCheck
```

## 📋 Requisitos

### Sistema Operativo
- ✅ Windows con PowerShell 5.1+
- ✅ Windows/Linux/Mac con PowerShell Core 7+

### Azure CLI
```bash
# Instalar Azure CLI
# Windows: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows
# Linux/Mac: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

# Autenticación
az login

# Extensiones necesarias
az extension add --name containerapp
az extension add --name application-insights
```

### Permisos de Azure
La cuenta debe tener permisos para:
- Crear grupos de recursos
- Deployar recursos via ARM/Bicep
- Gestionar Container Apps
- Acceder a Container Registry

## 🔧 Configuración

### Variables de Entorno
Los scripts usan las siguientes variables de entorno de Azure CLI:

- `AZURE_SUBSCRIPTION_ID`: ID de suscripción (automático)
- `AZURE_TENANT_ID`: ID de tenant (automático)
- `AZURE_CONFIG_DIR`: Directorio de configuración (opcional)

### Configuración Regional
Por defecto usa `eastus`. Para cambiar:
```powershell
# Configurar región por defecto
az configure --defaults location=westeurope

# O especificar en cada comando
.\scripts\deploy_backendbot.ps1 -Location "westeurope"
```

## 📊 Salida y Logging

### Niveles de Verbose
- **Normal**: Solo progreso y resultados principales
- **Verbose**: Detalles completos de comandos ejecutados

### Códigos de Salida
- `0`: Éxito
- `1`: Error de validación o deployment
- `2`: Error de configuración

### Logs
Los scripts generan logs detallados que incluyen:
- Timestamp de cada operación
- Comandos ejecutados
- Resultados de Azure CLI
- Mensajes de error específicos

## 🛠 Troubleshooting

### Problemas Comunes

1. **Error de autenticación**
   ```
   ❌ No estás autenticado en Azure
   Solución: az login
   ```

2. **Directorio infra no encontrado**
   ```
   ❌ No se encuentra directorio 'infra'
   Solución: Ejecutar desde directorio raíz del proyecto
   ```

3. **Error de sintaxis en Bicep**
   ```
   ❌ Error en sintaxis de Bicep
   Solución: Revisar main.bicep y corregir errores
   ```

4. **Provider no registrado**
   ```
   ❌ Provider Microsoft.App no registrado
   Solución: az provider register --namespace Microsoft.App
   ```

### Debug Mode
```powershell
# Ejecutar con máxima verbosidad
.\scripts\deploy_backendbot.ps1 -Verbose

# Solo validación con debug
.\scripts\validate_predeploy.ps1 -Verbose -SkipQuotaCheck
```

### Verificar Estado
```powershell
# Ver deployments activos
az deployment group list --resource-group backendbot-dev-rg --output table

# Ver estado de Container App
az containerapp show --name backendbot-app --resource-group backendbot-dev-rg --output table
```

## 🔄 Integración con CI/CD

### GitHub Actions
```yaml
- name: Validate Pre-deployment
  run: |
    cd scripts
    pwsh ./validate_predeploy.ps1 -EnvironmentName "backendbot-prod"

- name: Deploy BackendBot
  run: |
    cd scripts
    pwsh ./deploy_backendbot.ps1 -EnvironmentName "backendbot-prod" -SkipValidation
```

### Azure DevOps
```yaml
- task: PowerShell@2
  inputs:
    targetType: 'inline'
    script: |
      cd scripts
      .\deploy_backendbot.ps1 -EnvironmentName "$(EnvironmentName)" -Location "$(AzureLocation)"
```

## 📈 Métricas y Monitoreo

### Métricas de Deployment
Los scripts rastrean:
- ⏱️ Tiempo total de deployment
- ✅/❌ Estado de cada paso
- 📊 Recursos creados
- 🔗 URLs generadas

### Logs Centralizados
- Azure Activity Logs
- Container App logs
- Deployment logs

## 🔒 Seguridad

### Mejores Prácticas
- ✅ No almacena credenciales en texto plano
- ✅ Usa autenticación de Azure CLI
- ✅ Valida permisos antes de deployment
- ✅ Manejo seguro de errores

### Variables Sensibles
- Nunca incluir secrets en parámetros
- Usar Azure Key Vault para configuración sensible
- Managed Identity para acceso a recursos

## 📞 Soporte

### Documentación Relacionada
- [Azure Container Apps](https://docs.microsoft.com/en-us/azure/container-apps/)
- [Azure Bicep](https://docs.microsoft.com/en-us/azure/azure-resource-manager/bicep/)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/)

### Reportar Problemas
1. Ejecutar con `-Verbose` para detalles completos
2. Incluir salida completa del error
3. Especificar versión de Azure CLI: `az version`
4. Incluir configuración regional y de suscripción

---

**Nota**: Estos scripts están diseñados para ser idempotentes y seguros para múltiples ejecuciones.