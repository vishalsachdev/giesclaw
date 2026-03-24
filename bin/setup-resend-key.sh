#!/bin/bash
# Add Resend API key to VPS. Run locally:
#   bash bin/setup-resend-key.sh

read -sp "Paste your Resend API key: " KEY
echo
ssh vps "echo 'RESEND_API_KEY=$KEY' | sudo tee -a /opt/giesclaw/platform/.env.local > /dev/null"
ssh vps "echo 'RESEND_FROM_EMAIL=SOS <sos@giesclaw.illinihunt.org>' | sudo tee -a /opt/giesclaw/platform/.env.local > /dev/null"
echo "Done. Key added to VPS."
