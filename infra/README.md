# Infraestructura y Deployment BackendBot

Este directorio contiene toda la infraestructura como código (IaC) y scripts de deployment para BackendBot usando Azure Container Apps.

## 📁 Estructura

```
infra/
├── main.bicep                 # Template principal de Azure
├── main.parameters.json       # Parámetros de deployment
└── README.md                  # Esta documentación

scripts/
├── validate_predeploy.ps1     # Validación de pre-deployment
├── deploy_backendbot.ps1      # Script completo de deployment
└── README.md                  # Documentación de scripts
```

## 🚀 Deployment Rápido

### Prerrequisitos

1. **Azure CLI instalado y autenticado**
   ```bash
   az login
   az account set --subscription "YOUR_SUBSCRIPTION_ID"
   ```

2. **Azure CLI con extensiones necesarias**
   ```bash
   az extension add --name containerapp
   az extension add --name application-insights
   ```

3. **PowerShell (para scripts de validación)**
   - Windows: PowerShell incluido
   - Linux/Mac: Instalar PowerShell Core

### Deployment Paso a Paso

1. **Validar pre-deployment**
   ```powershell
   .\scripts\validate_predeploy.ps1 -EnvironmentName "backendbot-dev" -Location "eastus"
   ```

2. **Ejecutar deployment completo**
   ```powershell
   .\scripts\deploy_backendbot.ps1 -EnvironmentName "backendbot-dev" -Location "eastus"
   ```

## 🔧 Configuración

### Variables de Entorno

Edita `infra/main.parameters.json` para configurar:

- `environmentName`: Nombre del entorno (dev, staging, prod)
- `location`: Región de Azure (eastus, westeurope, etc.)
- `containerImage`: Imagen Docker a usar
- `containerRegistryName`: Nombre del Azure Container Registry

### Recursos Creados

El deployment crea automáticamente:

- **Grupo de Recursos**: Contenedor de todos los recursos
- **Container App Environment**: Entorno para Container Apps
- **Container App**: La aplicación BackendBot
- **Managed Identity**: Identidad para acceso seguro
- **Container Registry**: Para imágenes Docker
- **Log Analytics**: Para monitoreo y logs
- **Storage Account**: Para datos persistentes

## 📊 Monitoreo

### Logs de Aplicación
```bash
# Ver logs en tiempo real
az containerapp logs show --name backendbot-app --resource-group backendbot-dev-rg --follow

# Ver logs históricos
az monitor diagnostic-settings list --resource /subscriptions/.../resourceGroups/backendbot-dev-rg/providers/Microsoft.App/containerApps/backendbot-app
```

### Métricas
```bash
# Ver métricas de Container App
az monitor metrics list --resource /subscriptions/.../resourceGroups/backendbot-dev-rg/providers/Microsoft.App/containerApps/backendbot-app --metric "Requests"
```

## 🔄 Actualizaciones

### Actualizar Imagen
```powershell
# Construir nueva imagen
docker build -t backendbot:latest .

# Push a registry
az acr login --name backendbotacr
docker tag backendbot:latest backendbotacr.azurecr.io/backendbot:latest
docker push backendbotacr.azurecr.io/backendbot:latest

# Actualizar Container App
az containerapp update --name backendbot-app --resource-group backendbot-dev-rg --image backendbotacr.azurecr.io/backendbot:latest
```

### Escalar Recursos
```bash
# Escalar manualmente
az containerapp update --name backendbot-app --resource-group backendbot-dev-rg --min-replicas 1 --max-replicas 10

# Configurar auto-scaling
az containerapp update --name backendbot-app --resource-group backendbot-dev-rg --scale-rule-name "cpu-scaling" --scale-rule-type "cpu" --scale-rule-value "70"
```

## 🛠 Troubleshooting

### Problemas Comunes

1. **Error de autenticación**
   ```bash
   az login
   az account set --subscription "YOUR_SUBSCRIPTION_ID"
   ```

2. **Quota excedida**
   ```bash
   az quota show --scope /subscriptions/YOUR_SUBSCRIPTION_ID/providers/Microsoft.App/locations/eastus --quota Microsoft.App
   ```

3. **Imagen no encontrada**
   ```bash
   az acr repository list --name backendbotacr --output table
   ```

4. **Deployment fallido**
   ```bash
   az deployment group show --resource-group backendbot-dev-rg --name main --query "properties.error"
   ```

### Logs de Debug

```powershell
# Ejecutar validación con verbose
.\scripts\validate_predeploy.ps1 -Verbose

# Ejecutar deployment con verbose
.\scripts\deploy_backendbot.ps1 -Verbose
```

## 🔒 Seguridad

### Managed Identity

La infraestructura usa Managed Identity para acceso seguro a recursos de Azure:

- **System-assigned**: Para Container App
- **User-assigned**: Para acceso a otros servicios

### Secrets Management

- Variables de entorno sensibles se almacenan en Azure Key Vault
- Container App tiene acceso controlado a secrets
- Logs no contienen información sensible

## 📈 Costos

### Estimación Mensual (Desarrollo)

- **Container App**: ~$10-20/mes
- **Container Registry**: ~$5/mes
- **Log Analytics**: ~$5-10/mes
- **Storage Account**: ~$1/mes
- **Total**: ~$21-36/mes

### Optimizaciones de Costo

1. **Escalado automático**: Configurar min-replicas=0
2. **Tier de Log Analytics**: Usar Basic en desarrollo
3. **Storage**: Usar LRS (Locally Redundant)

## 🔄 CI/CD

### GitHub Actions

Ejemplo de workflow para deployment automático:

```yaml
name: Deploy BackendBot
on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    - name: Deploy
      run: |
        cd scripts
        pwsh ./deploy_backendbot.ps1 -EnvironmentName "backendbot-prod"
```

## 📞 Soporte

Para problemas específicos:

1. Revisar logs de Azure Portal
2. Verificar configuración en `main.parameters.json`
3. Ejecutar validación con `-Verbose`
4. Consultar documentación de Azure Container Apps

---

**Nota**: Esta infraestructura está optimizada para desarrollo y puede requerir ajustes para producción (VNET, backup, etc.).