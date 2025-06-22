#!/bin/bash

# Baby Maker 5000 - Azure App Service Deployment Script
# This script deploys the complete App Service infrastructure

set -e

# Configuration
RESOURCE_GROUP_NAME="babymaker5000-rg"
LOCATION="eastus"
APP_SERVICE_PLAN_NAME="babymaker-plan-$(date +%s)"
WEB_APP_NAME="babymaker-app-$(date +%s)"
DEPLOYMENT_NAME="babymaker-appservice-$(date +%Y%m%d-%H%M%S)"
SKU="B1"  # Basic B1 - cheapest with SSL support (~$13.14/month)

# Alternative regions to try if quota is exceeded
REGIONS=("eastus" "westus2" "centralus" "westeurope" "southeastasia")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${BLUE}🍼 Baby Maker 5000 - Azure App Service Deployment${NC}"
echo "============================================================"

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

# Check if resource group exists, create if not
if ! az group show --name "$RESOURCE_GROUP_NAME" &> /dev/null; then
    echo -e "${YELLOW}📁 Creating resource group: ${RESOURCE_GROUP_NAME}${NC}"
    az group create \
        --name "$RESOURCE_GROUP_NAME" \
        --location "$LOCATION" \
        --output table
else
    echo -e "${GREEN}📁 Resource group already exists: ${RESOURCE_GROUP_NAME}${NC}"
fi

# Load environment variables from .env file
echo -e "${PURPLE}🔐 Loading secrets from .env file...${NC}"
if [ -f "../../.env" ]; then
    # Load environment variables from .env file
    export $(grep -v '^#' ../../.env | xargs)
    echo -e "${GREEN}✅ .env file found and loaded${NC}"
else
    echo -e "${RED}❌ .env file not found in project root!${NC}"
    echo "Please create a .env file with:"
    echo "REPLICATE_API_TOKEN=your_replicate_token_here"
    echo "AZURE_STORAGE_CONNECTION_STRING=your_azure_storage_connection_string"
    exit 1
fi

# Validate required environment variables
if [ -z "$REPLICATE_API_TOKEN" ]; then
    echo -e "${RED}❌ REPLICATE_API_TOKEN not found in .env file!${NC}"
    exit 1
else
    echo -e "${GREEN}✅ REPLICATE_API_TOKEN loaded from .env${NC}"
fi

if [ -z "$AZURE_STORAGE_CONNECTION_STRING" ]; then
    echo -e "${RED}❌ AZURE_STORAGE_CONNECTION_STRING not found in .env file!${NC}"
    echo "Make sure you've deployed blob storage first and copied the connection string to .env"
    exit 1
else
    echo -e "${GREEN}✅ AZURE_STORAGE_CONNECTION_STRING loaded from .env${NC}"
fi

# Function to deploy App Service Plan with quota retry logic
deploy_app_service_plan() {
    local region=$1
    local attempt=$2
    
    echo -e "${YELLOW}🏗️  Deploying App Service Plan in $region (attempt $attempt)...${NC}"
    
    # Capture both stdout and stderr, but separate them
    local temp_file=$(mktemp)
    local error_file=$(mktemp)
    
    az deployment group create \
        --resource-group "$RESOURCE_GROUP_NAME" \
        --template-file "app-service-plan.json" \
        --parameters appServicePlanName="$APP_SERVICE_PLAN_NAME" \
        --parameters location="$region" \
        --parameters sku="$SKU" \
        --parameters skuCapacity=1 \
        --name "${DEPLOYMENT_NAME}-plan-${region}" \
        --output json > "$temp_file" 2> "$error_file"
    
    local exit_code=$?
    local error_output=$(cat "$error_file")
    
    # Check for quota error in stderr
    if echo "$error_output" | grep -q "SubscriptionIsOverQuotaForSku"; then
        echo -e "${YELLOW}⚠️  Quota exceeded in $region, trying next region...${NC}"
        rm "$temp_file" "$error_file"
        return 1
    elif [ $exit_code -ne 0 ]; then
        echo -e "${RED}❌ Deployment failed in $region${NC}"
        echo "$error_output"
        rm "$temp_file" "$error_file"
        return 1
    else
        # Success - save the JSON output
        PLAN_DEPLOYMENT=$(cat "$temp_file")
        echo -e "${GREEN}✅ App Service Plan deployed successfully in $region${NC}"
        CURRENT_LOCATION="$region"
        rm "$temp_file" "$error_file"
        return 0
    fi
}

# Try deploying in different regions until successful
PLAN_DEPLOYMENT=""
CURRENT_LOCATION=""
for i in "${!REGIONS[@]}"; do
    region="${REGIONS[$i]}"
    if deploy_app_service_plan "$region" "$((i+1))"; then
        break
    fi
    
    if [ $i -eq $((${#REGIONS[@]}-1)) ]; then
        echo -e "${RED}❌ Failed to deploy in all regions. Please try:${NC}"
        echo "1. Use a different Azure subscription"
        echo "2. Request quota increase: https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade"
        echo "3. Try B1 tier in a different region manually"
        exit 1
    fi
done

# Deploy Web App
echo -e "${YELLOW}🌐 Deploying Web App in $CURRENT_LOCATION...${NC}"

# Extract App Service Plan details from successful deployment
PLAN_ID=$(echo "$PLAN_DEPLOYMENT" | jq -r '.properties.outputs.appServicePlanId.value')
ACTUAL_PLAN_NAME=$(echo "$PLAN_DEPLOYMENT" | jq -r '.properties.outputs.appServicePlanName.value')

echo -e "${GREEN}✅ App Service Plan deployed: ${ACTUAL_PLAN_NAME} in ${CURRENT_LOCATION}${NC}"

WEB_APP_DEPLOYMENT=$(az deployment group create \
    --resource-group "$RESOURCE_GROUP_NAME" \
    --template-file "web-app.json" \
    --parameters webAppName="$WEB_APP_NAME" \
    --parameters appServicePlanId="$PLAN_ID" \
    --parameters location="$CURRENT_LOCATION" \
    --parameters pythonVersion="3.12" \
    --parameters replicateApiToken="$REPLICATE_API_TOKEN" \
    --parameters azureStorageConnectionString="$AZURE_STORAGE_CONNECTION_STRING" \
    --parameters enableApplicationInsights=true \
    --name "${DEPLOYMENT_NAME}-webapp" \
    --output json)

# Extract Web App details
ACTUAL_WEB_APP_NAME=$(echo "$WEB_APP_DEPLOYMENT" | jq -r '.properties.outputs.webAppName.value')
WEB_APP_URL=$(echo "$WEB_APP_DEPLOYMENT" | jq -r '.properties.outputs.webAppUrl.value')
APP_INSIGHTS_KEY=$(echo "$WEB_APP_DEPLOYMENT" | jq -r '.properties.outputs.applicationInsightsInstrumentationKey.value')

echo -e "${GREEN}✅ Web App deployed: ${ACTUAL_WEB_APP_NAME}${NC}"

# Configure startup command
echo -e "${YELLOW}⚙️  Configuring startup command...${NC}"
az webapp config set \
    --resource-group "$RESOURCE_GROUP_NAME" \
    --name "$ACTUAL_WEB_APP_NAME" \
    --startup-file "startup.sh" \
    --output none

echo -e "${GREEN}✅ Startup command configured${NC}"

# Create deployment configuration file
echo -e "${YELLOW}📝 Creating deployment configuration...${NC}"
cat > "../../.env.appservice" << EOF
# Azure App Service Configuration for Baby Maker 5000
# Generated on $(date)

# App Service Details
AZURE_RESOURCE_GROUP=${RESOURCE_GROUP_NAME}
AZURE_APP_SERVICE_PLAN=${ACTUAL_PLAN_NAME}
AZURE_WEB_APP_NAME=${ACTUAL_WEB_APP_NAME}
AZURE_WEB_APP_URL=${WEB_APP_URL}

# Application Insights
AZURE_APPLICATION_INSIGHTS_KEY=${APP_INSIGHTS_KEY}

# Deployment Info
AZURE_LOCATION=${CURRENT_LOCATION}
AZURE_SKU=${SKU}
DEPLOYMENT_DATE=$(date)

# Git Deployment (for future use)
# Run this to set up continuous deployment:
# az webapp deployment source config --name ${ACTUAL_WEB_APP_NAME} --resource-group ${RESOURCE_GROUP_NAME} --repo-url <your-git-repo> --branch main --manual-integration
EOF

echo -e "${GREEN}✅ Configuration saved to .env.appservice${NC}"

# Display summary
echo ""
echo -e "${BLUE}🎉 App Service Deployment Complete!${NC}"
echo "============================================================"
echo -e "${GREEN}Resource Group:${NC} $RESOURCE_GROUP_NAME"
echo -e "${GREEN}App Service Plan:${NC} $ACTUAL_PLAN_NAME ($SKU)"
echo -e "${GREEN}Web App:${NC} $ACTUAL_WEB_APP_NAME"
echo -e "${GREEN}URL:${NC} $WEB_APP_URL"
echo -e "${GREEN}Location:${NC} $CURRENT_LOCATION"
echo ""
echo -e "${YELLOW}📋 Next Steps:${NC}"
echo "1. Deploy your code to the App Service:"
echo "   - Option A: Use Azure CLI: az webapp up --name $ACTUAL_WEB_APP_NAME --resource-group $RESOURCE_GROUP_NAME"
echo "   - Option B: Set up Git deployment (see .env.appservice file)"
echo "   - Option C: Use VS Code Azure extension"
echo "   - Option D: Upload via Azure Portal"
echo ""
echo "2. Make sure your code includes:"
echo "   - startup.sh (already created in project root)"
echo "   - requirements.txt with all dependencies"
echo "   - app.py as the main entry point"
echo ""
echo "3. Your .env file is already configured with the required secrets"
echo ""
echo "4. Monitor your application:"
echo "   - App Service: https://portal.azure.com/#@/resource/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP_NAME/providers/Microsoft.Web/sites/$ACTUAL_WEB_APP_NAME"
echo "   - Application Insights: https://portal.azure.com/#blade/AppInsightsExtension/ApplicationDashboard"
echo ""
echo -e "${BLUE}💰 Cost Estimate (Monthly):${NC}"
echo "- App Service Plan (B1): ~$13.14/month"
echo "- Application Insights: ~$2.30/GB ingested"
echo "- Total estimated: ~$15-20/month"
echo ""
echo -e "${GREEN}🔧 Management Commands:${NC}"
echo "- View logs: az webapp log tail --name $ACTUAL_WEB_APP_NAME --resource-group $RESOURCE_GROUP_NAME"
echo "- Restart app: az webapp restart --name $ACTUAL_WEB_APP_NAME --resource-group $RESOURCE_GROUP_NAME"
echo "- Scale up: az appservice plan update --name $ACTUAL_PLAN_NAME --resource-group $RESOURCE_GROUP_NAME --sku S1"
echo ""
echo -e "${BLUE}🗑️  Cleanup (when done):${NC}"
echo "az group delete --name $RESOURCE_GROUP_NAME --yes --no-wait"
echo ""
echo -e "${PURPLE}🚀 Your Baby Maker 5000 is ready to deploy!${NC}" 