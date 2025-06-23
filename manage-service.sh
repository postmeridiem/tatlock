#!/usr/bin/env bash
# manage-service.sh
# Interactive CLI for managing the Tatlock service.

# --- Color and Style Definitions ---
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# --- OS Detection and Command Configuration ---
SERVICE_NAME="tatlock"
OS="$(uname)"
PLIST_PATH="$HOME/Library/LaunchAgents/com.tatlock.plist"

case "$OS" in
  'Linux')
    IS_SYSTEMD=$(ps --no-headers -o comm 1)
    if [ "$IS_SYSTEMD" != "systemd" ]; then
        echo -e "${RED}Error: This script requires systemd for service management on Linux.${NC}"
        exit 1
    fi
    STATUS_CMD="sudo systemctl is-active $SERVICE_NAME"
    START_CMD="sudo systemctl start $SERVICE_NAME"
    STOP_CMD="sudo systemctl stop $SERVICE_NAME"
    RESTART_CMD="sudo systemctl restart $SERVICE_NAME"
    LOGS_CMD="sudo journalctl -u $SERVICE_NAME -f -n 50 --no-pager"
    ;;
  'Darwin')
    STATUS_CMD="launchctl list | grep $SERVICE_NAME > /dev/null 2>&1"
    START_CMD="launchctl load $PLIST_PATH"
    STOP_CMD="launchctl unload $PLIST_PATH"
    RESTART_CMD="launchctl unload $PLIST_PATH && sleep 1 && launchctl load $PLIST_PATH"
    LOG_FILE="/tmp/tatlock.log"
    LOGS_CMD="tail -f $LOG_FILE"
    ;;
  *)
    echo -e "${RED}Error: Unsupported operating system '$OS'.${NC}"
    exit 1
    ;;
esac

# --- Functions ---

# Function to display current service status
show_status() {
    echo -e "${CYAN}──────────────────────────────────────────────────${NC}"
    echo -en "${BOLD}Tatlock Service Status: "
    
    if [[ "$OS" == "Linux" ]]; then
        status=$($STATUS_CMD)
        if [ "$status" == "active" ]; then
            echo -e "${GREEN}● Running${NC}"
        else
            echo -e "${RED}● Stopped${NC}"
        fi
    elif [[ "$OS" == "Darwin" ]]; then
        if $STATUS_CMD; then
            echo -e "${GREEN}● Running${NC}"
        else
            echo -e "${RED}● Stopped${NC}"
        fi
    fi
    echo -e "${CYAN}──────────────────────────────────────────────────${NC}"
}

# Function to start the service
start_service() {
    echo -e "\n${YELLOW}Attempting to start the Tatlock service...${NC}"
    if eval $START_CMD; then
        echo -e "${GREEN}Service started successfully.${NC}"
    else
        echo -e "${RED}Error: Failed to start the service.${NC}"
        if [[ "$OS" == "Darwin" ]] && [ ! -f "$PLIST_PATH" ]; then
             echo -e "${RED}LaunchAgent plist not found at $PLIST_PATH. Was the service installed?${NC}"
        fi
    fi
    sleep 1
}

# Function to stop the service
stop_service() {
    echo -e "\n${YELLOW}Attempting to stop the Tatlock service...${NC}"
    if eval $STOP_CMD; then
        echo -e "${GREEN}Service stopped successfully.${NC}"
    else
        # This can fail if the service isn't running, which is not a critical error.
        echo -e "${YELLOW}Could not stop the service (it may not have been running).${NC}"
    fi
    sleep 1
}

# Function to restart the service
restart_service() {
    echo -e "\n${YELLOW}Attempting to restart the Tatlock service...${NC}"
    if eval $RESTART_CMD; then
        echo -e "${GREEN}Service restarted successfully.${NC}"
    else
        echo -e "${RED}Error: Failed to restart the service.${NC}"
    fi
    sleep 1
}

# Function to tail logs
tail_logs() {
    echo -e "\n${YELLOW}Showing live logs for Tatlock... (Press Ctrl+C to exit)${NC}"
    echo -e "${CYAN}──────────────────────────────────────────────────${NC}"
    eval $LOGS_CMD
}

# --- Main Menu Loop ---
while true; do
    clear
    echo -e "${BOLD}${CYAN}"
    echo "══════════════════════════════════════════════════"
    echo "            Tatlock Service Manager"
    echo "══════════════════════════════════════════════════"
    echo -e "${NC}"
    
    show_status
    
    echo -e "\n${BOLD}Please choose an option:${NC}"
    echo "  ${GREEN}1.${NC} Start Service"
    echo "  ${GREEN}2.${NC} Stop Service"
    echo "  ${GREEN}3.${NC} Restart Service"
    echo "  ${YELLOW}4.${NC} View Live Logs"
    echo "  ${RED}5.${NC} Exit"
    echo ""
    read -p "Enter your choice [1-5]: " choice
    
    case $choice in
        1)
            start_service
            read -p "Press Enter to return to the menu..."
            ;;
        2)
            stop_service
            read -p "Press Enter to return to the menu..."
            ;;
        3)
            restart_service
            read -p "Press Enter to return to the menu..."
            ;;
        4)
            tail_logs
            # This command runs until Ctrl+C, so the pause is implicit.
            echo -e "\n${YELLOW}Log view finished. Press Enter to return to the menu...${NC}"
            read
            ;;
        5)
            echo -e "\n${BLUE}Exiting Service Manager. Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "\n${RED}Invalid option. Please try again.${NC}"
            sleep 2
            ;;
    esac
done 