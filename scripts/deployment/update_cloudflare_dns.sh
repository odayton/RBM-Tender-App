#!/bin/bash

# Cloudflare DNS Update Script
# This script updates Cloudflare DNS when your IP changes

# Configuration
# Set these environment variables on your server:
# export CLOUDFLARE_ZONE_ID="your_zone_id_here"
# export CLOUDFLARE_RECORD_ID="your_record_id_here" 
# export CLOUDFLARE_API_TOKEN="your_api_token_here"
# export CLOUDFLARE_DOMAIN="rbm-intranet.com"

ZONE_ID="${CLOUDFLARE_ZONE_ID:-9e19719769fc43d5aa95815ecb8ffa48}"
RECORD_ID="${CLOUDFLARE_RECORD_ID:-b6acf708ea91e583512ea00e192ef344}"
API_TOKEN="${CLOUDFLARE_API_TOKEN}"
DOMAIN="${CLOUDFLARE_DOMAIN:-rbm-intranet.com}"

# Validate required environment variables
if [ -z "$API_TOKEN" ]; then
    echo "Error: CLOUDFLARE_API_TOKEN environment variable is not set"
    echo "Please set it with: export CLOUDFLARE_API_TOKEN='your_token_here'"
    exit 1
fi

# Get current public IP
CURRENT_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || curl -s ifconfig.me)

if [ -z "$CURRENT_IP" ]; then
    echo "Failed to get current IP"
    exit 1
fi

echo "Current IP: $CURRENT_IP"

# Get the current DNS record
CURRENT_DNS_IP=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records/$RECORD_ID" \
    -H "Authorization: Bearer $API_TOKEN" \
    -H "Content-Type: application/json" | jq -r '.result.content')

echo "Current DNS IP: $CURRENT_DNS_IP"

# Check if IP has changed
if [ "$CURRENT_IP" = "$CURRENT_DNS_IP" ]; then
    echo "IP hasn't changed, no update needed"
    exit 0
fi

# Update the DNS record
echo "Updating DNS record..."
RESPONSE=$(curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records/$RECORD_ID" \
    -H "Authorization: Bearer $API_TOKEN" \
    -H "Content-Type: application/json" \
    --data "{
        \"type\": \"A\",
        \"name\": \"$DOMAIN\",
        \"content\": \"$CURRENT_IP\",
        \"ttl\": 300,
        \"proxied\": false
    }")

# Check if update was successful
if echo "$RESPONSE" | jq -e '.success' > /dev/null; then
    echo "DNS updated successfully to $CURRENT_IP"
else
    echo "Failed to update DNS: $(echo "$RESPONSE" | jq -r '.errors[0].message')"
    exit 1
fi 