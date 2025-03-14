#!/bin/bash

CONTAINER_NAME="ghl_lead_notes_etc_creation-flask-app-1"

SLACK_WEBHOOK_URL="https://hooks.slack.com/services/....." # Set ur value .env not working


while true; do
    # Check if the health endpoint is accessible
    STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME")

    if [[ "$STATUS" == "unhealthy" ]]; then
        curl -X POST -H 'Content-type: application/json' --data \
        '{"text":"🚨 *Alert:* Container '"$CONTAINER_NAME"' is *UNHEALTHY*! Restarting now..."}' \
        "$SLACK_WEBHOOK_URL"

        # Restart the container
        docker restart "$CONTAINER_NAME"
    fi

    sleep 45  # Check every 45 seconds
done
