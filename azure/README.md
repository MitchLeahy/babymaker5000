# Azure Infrastructure for Baby Maker 5000

This directory contains Azure infrastructure-as-code templates and deployment scripts for the Baby Maker 5000 application.

## Directory Structure

```
azure/
├── README.md                   # This file - documentation
├── blob/                      # Azure Blob Storage infrastructure
│   ├── storage-account.json   # ARM template for storage account
│   ├── blob-manager.json      # ARM template for lifecycle management
│   └── deploy.sh              # Blob storage deployment script
└── app-service/               # Azure App Service infrastructure
    ├── app-service-plan.json  # ARM template for App Service Plan
    ├── web-app.json           # ARM template for Web App
    └── deploy.sh              # App Service deployment script
```

## Components

### Blob Storage (`blob/`)
Handles image storage for parent photos and generated baby/family images.

- **`storage-account.json`** - Creates Azure Storage Account with:
  - 4 containers: parent-photos, generated-babies, generated-families, temp-uploads
  - Security settings (HTTPS-only, no public access)
  - CORS configuration for web access
  - Encryption enabled

- **`blob-manager.json`** - Manages storage lifecycle:
  - Auto-deletes temp files after 1 day
  - Archives generated images after 30 days
  - Deletes parent photos after 7 days
  - Cost optimization through tiered storage

- **`deploy.sh`** - Automated deployment script:
  - Creates resource group and storage account
  - Deploys both ARM templates
  - Generates `.env.azure` configuration file
  - Provides cost estimates and management info

### App Service (`app-service/`)
Hosts the Streamlit web application with the cheapest viable configuration.

- **`app-service-plan.json`** - Creates App Service Plan with:
  - Basic B1 tier (~$13.14/month) - cheapest with SSL support
  - Linux container support for Python
  - Single instance for cost optimization
  - Auto-scaling disabled to control costs

- **`web-app.json`** - Creates Web App with:
  - Python 3.12 runtime
  - Streamlit-optimized configuration
  - Environment variables for API tokens
  - Application Insights for monitoring
  - HTTPS-only access
  - Proper startup command configuration

- **`deploy.sh`** - Complete App Service deployment:
  - Deploys both App Service Plan and Web App
  - Configures environment variables securely
  - Sets up Application Insights
  - Provides deployment instructions
  - Generates `.env.appservice` configuration

## Usage

### 1. Deploy Blob Storage (Required First)
```bash
cd azure/blob
chmod +x deploy.sh
./deploy.sh
```

### 2. Deploy App Service
```bash
# First, make sure your .env file contains:
# REPLICATE_API_TOKEN=your_replicate_token_here
# AZURE_STORAGE_CONNECTION_STRING=your_azure_storage_connection_string

cd azure/app-service
chmod +x deploy.sh
./deploy.sh
```
*Note: The script will automatically read your API keys from the .env file*

### 3. Deploy Your Application Code
```bash
# Option A: Quick deployment with Azure CLI
az webapp up --name <your-web-app-name> --resource-group babymaker5000-rg

# Option B: Git deployment (continuous)
az webapp deployment source config \
    --name <your-web-app-name> \
    --resource-group babymaker5000-rg \
    --repo-url <your-git-repo> \
    --branch main \
    --manual-integration
```

### 4. Configure Application
The deployment script automatically configures:
- `REPLICATE_API_TOKEN` - For AI image generation
- `AZURE_STORAGE_CONNECTION_STRING` - For blob storage
- `STREAMLIT_*` - Server configuration
- Application Insights monitoring

## Cost Breakdown (Monthly)

### Cheapest Configuration:
- **Blob Storage**: ~$2-5/month (depending on usage)
- **App Service Plan (B1)**: ~$13.14/month
- **Application Insights**: ~$2.30/GB ingested
- **Total**: ~$15-20/month

### Cost Optimization Features:
- ✅ **B1 Basic tier** - Cheapest with SSL and custom domains
- ✅ **Single instance** - No auto-scaling to control costs
- ✅ **Lifecycle policies** - Auto-cleanup of old files
- ✅ **LRS storage** - Cheapest replication option
- ✅ **Linux containers** - Lower cost than Windows

## Security Features

- ✅ **No public blob access** - Uses SAS URLs for secure, time-limited access
- ✅ **HTTPS-only** - All traffic encrypted in transit
- ✅ **Secure secrets** - API tokens stored as secure parameters
- ✅ **Automatic cleanup** - Prevents data accumulation
- ✅ **Application Insights** - Security monitoring and alerts

## Monitoring & Management

### View Application:
- **Web App**: `https://<your-app-name>.azurewebsites.net`
- **Azure Portal**: Resource group `babymaker5000-rg`
- **Application Insights**: Performance and error monitoring

### Management Commands:
```bash
# View real-time logs
az webapp log tail --name <web-app-name> --resource-group babymaker5000-rg

# Restart application
az webapp restart --name <web-app-name> --resource-group babymaker5000-rg

# Scale up (if needed)
az appservice plan update --name <plan-name> --resource-group babymaker5000-rg --sku S1
```

## Deployment Order

**Important**: Deploy in this order for proper dependencies:

1. **Blob Storage** (`azure/blob/deploy.sh`) - Creates storage account
2. **App Service** (`azure/app-service/deploy.sh`) - Creates web hosting
3. **Application Code** - Deploy your Streamlit app

## Clean Up

```bash
# Delete all Azure resources
az group delete --name babymaker5000-rg --yes --no-wait
```

## Future Extensions

This directory structure allows for easy addition of other Azure services:

```
azure/
├── blob/              # Blob storage (current)
├── app-service/       # App Service (current)
├── functions/         # Azure Functions (future)
├── cognitive/         # Cognitive Services (future)
├── database/          # CosmosDB or SQL (future)
└── networking/        # VNet, Load Balancer (future)
```

## Troubleshooting

### Common Issues:
1. **App won't start**: Check `startup.sh` is executable and in project root
2. **Missing dependencies**: Ensure `requirements.txt` includes all packages
3. **Environment variables**: Verify secrets are properly configured
4. **Storage errors**: Confirm blob storage is deployed first
5. **High costs**: Monitor usage in Azure Portal cost management 