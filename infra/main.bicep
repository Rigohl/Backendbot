// Infraestructura BackendBot - Bicep Template
// Reemplaza la validación problemática de azure_check_predeploy

@description('Nombre del entorno')
param environmentName string = 'backendbot-dev'

@description('Ubicación de los recursos')
param location string = 'eastus'

@description('Imagen del contenedor')
param containerImage string = 'backendbot:latest'

@description('Nombre del Container Registry')
param containerRegistryName string = 'backendbotacr'

@description('Nombre del Container App')
param containerAppName string = 'backendbot-app'

@description('Nombre de la Managed Identity')
param managedIdentityName string = 'backendbot-identity'

@description('Nombre del Storage Account')
param storageAccountName string = 'backendbotstorage'

@description('Tags para los recursos')
param tags object = {
  Environment: 'Development'
  Project: 'BackendBot'
  Owner: 'DevTeam'
}

// User Assigned Managed Identity
resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: '${managedIdentityName}-${environmentName}'
  location: location
  tags: tags
}

// Container Registry
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: '${containerRegistryName}${uniqueString(resourceGroup().id)}'
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: false
  }
  tags: tags
}

// Log Analytics Workspace
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2020-08-01' = {
  name: 'backendbotlogs${uniqueString(resourceGroup().id)}'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
  tags: tags
}

// Storage Account
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: '${storageAccountName}${uniqueString(resourceGroup().id)}'
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
  tags: tags
}

// Container Apps Environment
resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: 'backendbot-env-${environmentName}'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
  tags: tags
}

// Container App
resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: '${containerAppName}-${environmentName}'
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentity.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      ingress: {
        external: true
        targetPort: 80
        transport: 'http'
      }
      registries: [
        {
          server: containerRegistry.properties.loginServer
          identity: managedIdentity.id
        }
      ]
    }
    template: {
      containers: [
        {
          image: containerImage
          name: 'backendbot'
          resources: {
            cpu: 1
            memory: '1.0Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 10
        rules: [
          {
            name: 'http-scaling'
            http: {
              metadata: {
                concurrentRequests: '10'
              }
            }
          }
        ]
      }
    }
  }
  tags: tags
}

// Outputs
output containerAppUrl string = 'https://${containerApp.properties.configuration.ingress.fqdn}'
output containerRegistryName string = containerRegistry.name
output managedIdentityClientId string = managedIdentity.properties.clientId
output storageAccountName string = storageAccount.name
output logAnalyticsWorkspaceId string = logAnalytics.id
