#!/bin/bash

# Baby Maker 5000 - Azure Deployment Script
# This script deploys the Azure Blob Storage infrastructure

set -e

# Configuration
RESOURCE_GROUP_NAME="babymaker5000-rg"
LOCATION="eastus"
STORAGE_ACCOUNT_NAME="babymaker$(date +%s)"
DEPLOYMENT_NAME="babymaker-deployment-$(date +%Y%m%d-%H%M%S)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🍼 Baby Maker 5000 - Azure Deployment${NC}"
echo "=================================================="

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}❌ Azure CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not logged in to Azure. Please login first.${NC}"
    az login
fi

# Get current subscription
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
echo -e "${BLUE}📋 Current subscription: ${SUBSCRIPTION_ID}${NC}"

# Create resource group
echo -e "${YELLOW}📁 Creating resource group: ${RESOURCE_GROUP_NAME}${NC}"
az group create \
    --name "$RESOURCE_GROUP_NAME" \
    --location "$LOCATION" \
    --output table

# Deploy storage account
echo -e "${YELLOW}☁️  Deploying storage account...${NC}"
STORAGE_DEPLOYMENT=$(az deployment group create \
    --resource-group "$RESOURCE_GROUP_NAME" \
    --template-file "storage-account.json" \
    --parameters storageAccountName="$STORAGE_ACCOUNT_NAME" \
    --parameters location="$LOCATION" \
    --name "${DEPLOYMENT_NAME}-storage" \
    --output json)

# Extract storage account name from deployment
ACTUAL_STORAGE_NAME=$(echo "$STORAGE_DEPLOYMENT" | jq -r '.properties.outputs.storageAccountName.value')
CONNECTION_STRING=$(echo "$STORAGE_DEPLOYMENT" | jq -r '.properties.outputs.connectionString.value')
BLOB_ENDPOINT=$(echo "$STORAGE_DEPLOYMENT" | jq -r '.properties.outputs.blobEndpoint.value')

echo -e "${GREEN}✅ Storage account deployed: ${ACTUAL_STORAGE_NAME}${NC}"

# Deploy blob manager
echo -e "${YELLOW}🔧 Deploying blob manager...${NC}"
BLOB_DEPLOYMENT=$(az deployment group create \
    --resource-group "$RESOURCE_GROUP_NAME" \
    --template-file "blob-manager.json" \
    --parameters storageAccountName="$ACTUAL_STORAGE_NAME" \
    --parameters enableLifecycleManagement=true \
    --parameters tempFilesRetentionDays=1 \
    --parameters generatedFilesRetentionDays=30 \
    --name "${DEPLOYMENT_NAME}-blob" \
    --output json)

echo -e "${GREEN}✅ Blob manager deployed${NC}"

# Extract outputs
PARENT_PHOTOS_ENDPOINT=$(echo "$BLOB_DEPLOYMENT" | jq -r '.properties.outputs.blobEndpoints.value.parentPhotos')
GENERATED_BABIES_ENDPOINT=$(echo "$BLOB_DEPLOYMENT" | jq -r '.properties.outputs.blobEndpoints.value.generatedBabies')
GENERATED_FAMILIES_ENDPOINT=$(echo "$BLOB_DEPLOYMENT" | jq -r '.properties.outputs.blobEndpoints.value.generatedFamilies')

# Create .env configuration
echo -e "${YELLOW}📝 Creating .env configuration...${NC}"
cat > "../.env.azure" << EOF
# Azure Blob Storage Configuration for Baby Maker 5000
# Generated on $(date)

# Azure Storage Connection String
AZURE_STORAGE_CONNECTION_STRING="${CONNECTION_STRING}"

# Azure Container Name (optional, defaults to 'babymaker-images')
AZURE_CONTAINER_NAME=babymaker-images

# Blob Endpoints
AZURE_BLOB_ENDPOINT=${BLOB_ENDPOINT}
AZURE_PARENT_PHOTOS_ENDPOINT=${PARENT_PHOTOS_ENDPOINT}
AZURE_GENERATED_BABIES_ENDPOINT=${GENERATED_BABIES_ENDPOINT}
AZURE_GENERATED_FAMILIES_ENDPOINT=${GENERATED_FAMILIES_ENDPOINT}

# Replicate API Token (add your token here)
REPLICATE_API_TOKEN=your_replicate_api_token_here

# OpenAI API Key (optional - only needed if using DALL-E instead of Replicate)
# OPENAI_API_KEY=your_openai_api_key_here
EOF

echo -e "${GREEN}✅ Configuration saved to .env.azure${NC}"

# Display summary
echo ""
echo -e "${BLUE}🎉 Deployment Complete!${NC}"
echo "=================================================="
echo -e "${GREEN}Resource Group:${NC} $RESOURCE_GROUP_NAME"
echo -e "${GREEN}Storage Account:${NC} $ACTUAL_STORAGE_NAME"
echo -e "${GREEN}Location:${NC} $LOCATION"
echo -e "${GREEN}Blob Endpoint:${NC} $BLOB_ENDPOINT"
echo ""
echo -e "${YELLOW}📋 Next Steps:${NC}"
echo "1. Copy .env.azure to .env"
echo "2. Add your REPLICATE_API_TOKEN to the .env file"
echo "3. Update requirements.txt to include Azure dependencies:"
echo "   - Uncomment the Azure lines in requirements.txt"
echo "   - Run: pip install -r requirements.txt"
echo "4. Run your Baby Maker 5000 app: streamlit run app.py"
echo ""
echo -e "${BLUE}💰 Cost Estimate:${NC}"
echo "- Storage Account: ~$0.02/GB/month"
echo "- Blob Storage: ~$0.0184/GB/month"
echo "- Transactions: ~$0.0004/10,000 transactions"
echo ""
echo -e "${GREEN}🔧 Management:${NC}"
echo "- View in Azure Portal: https://portal.azure.com/#@/resource/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP_NAME"
echo "- Monitor costs: https://portal.azure.com/#blade/Microsoft_Azure_CostManagement/Menu/overview"
echo ""
echo -e "${BLUE}🗑️  Cleanup (when done):${NC}"
echo "az group delete --name $RESOURCE_GROUP_NAME --yes --no-wait" 