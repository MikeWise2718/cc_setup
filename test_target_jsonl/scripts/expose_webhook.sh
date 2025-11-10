#!/bin/bash

# Webhook Tunnel Exposure Script (TEMPLATE - OPTIONAL)
# This script exposes a local webhook server to the public internet.
#
# This is OPTIONAL infrastructure. Only needed if:
# - You're using GitHub webhooks for automation
# - You need external services to reach your local development server
#
# CUSTOMIZATION REQUIRED:
# 1. Choose your tunnel provider (Cloudflare, ngrok, localtunnel, etc.)
# 2. Configure authentication/tokens for your chosen provider
# 3. Update the tunnel command below
# 4. Remove this script if you don't need webhook exposure
#
# See store/CUSTOMIZATION_GUIDE.md for more details

# Example: Cloudflare Tunnel
# Requires: cloudflared CLI installed and CLOUDFLARED_TUNNEL_TOKEN in .env
if [ -f .env ]; then
    export CLOUDFLARED_TUNNEL_TOKEN=$(grep CLOUDFLARED_TUNNEL_TOKEN .env | cut -d '=' -f2)
fi

# TODO: Customize this command for your tunnel provider
cloudflared tunnel run --token $CLOUDFLARED_TUNNEL_TOKEN

# Alternative Examples (uncomment and customize as needed):
#
# ngrok (popular alternative):
# ngrok http 8001
#
# localtunnel:
# npx localtunnel --port 8001
#
# SSH tunnel (if you have a server):
# ssh -R 80:localhost:8001 serveo.net