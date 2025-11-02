#!/bin/bash

# Application Stop Script (TEMPLATE)
# This script stops all application services
#
# CUSTOMIZATION REQUIRED:
# 1. Update PORTS list to match your application's ports
# 2. Add/remove process names to kill
# 3. Customize webhook server process name if applicable
#
# See store/CUSTOMIZATION_GUIDE.md for more details

# TODO: Customize these port numbers to match your application
PORTS="8000,5173,8001"  # Comma-separated list of ports to kill

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Stopping Application...${NC}"

# Kill any running start.sh processes
echo -e "${GREEN}Killing start.sh processes...${NC}"
pkill -f "start.sh" 2>/dev/null

# Kill webhook server (optional - remove if not using webhooks)
echo -e "${GREEN}Killing webhook server (if running)...${NC}"
pkill -f "trigger_webhook.py" 2>/dev/null

# TODO: Add any other process names you need to kill
# Examples:
# pkill -f "your-app-name" 2>/dev/null
# pkill -f "node.*server" 2>/dev/null

# Kill processes on specific ports
echo -e "${GREEN}Killing processes on ports $PORTS...${NC}"
lsof -ti:$PORTS | xargs kill -9 2>/dev/null

echo -e "${GREEN}✓ Services stopped successfully!${NC}"