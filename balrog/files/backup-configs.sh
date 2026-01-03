#!/bin/bash

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
BACKUP_SOURCE="${HOME}/configs"
BACKUP_DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_FILENAME="homelab-configs-backup-${BACKUP_DATE}.tar.gz"
BACKUP_TEMP_DIR="/tmp/backups"
BACKUP_TEMP_PATH="${BACKUP_TEMP_DIR}/${BACKUP_FILENAME}"
RCLONE_REMOTE="r2"
RCLONE_DEST="${RCLONE_REMOTE}:backups"

# Function to log messages with colors
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# Create backup directory if it doesn't exist
log_step "Creating temporary backup directory..."
mkdir -p "${BACKUP_TEMP_DIR}"

# Check if source directory exists
if [ ! -d "${BACKUP_SOURCE}" ]; then
    log_error "Source directory ${BACKUP_SOURCE} does not exist!"
    exit 1
fi

log_info "Starting backup process..."
log_info "Source: ${BACKUP_SOURCE}"
log_info "Backup file: ${BACKUP_FILENAME}"

# Create tarball
log_step "Creating compressed tarball..."
if tar czf "${BACKUP_TEMP_PATH}" \
    --exclude='.git' \
    --exclude='.gitignore' \
    --exclude='node_modules' \
    --exclude='*.log' \
    --exclude='*.tmp' \
    --exclude='.cache' \
    --exclude='cache' \
    --exclude='.DS_Store' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    -C "$(dirname ${BACKUP_SOURCE})" "$(basename ${BACKUP_SOURCE})"; then
    BACKUP_SIZE=$(du -h "${BACKUP_TEMP_PATH}" | cut -f1)
    log_success "Tarball created successfully (Size: ${BACKUP_SIZE})"
else
    log_error "Failed to create tarball"
    exit 1
fi

# Upload to R2
log_step "Uploading to Cloudflare R2..."
if rclone copy "${BACKUP_TEMP_PATH}" "${RCLONE_DEST}" --progress --s3-upload-cutoff=100M --s3-chunk-size=100M  2>&1 | while read line; do
    echo -e "${MAGENTA}[UPLOAD]${NC} ${line}"
done; [ ${PIPESTATUS[0]} -eq 0 ]; then
    log_success "Backup uploaded successfully to ${RCLONE_DEST}/${BACKUP_FILENAME}"
else
    log_error "Failed to upload backup to R2"
    rm -f "${BACKUP_TEMP_PATH}"
    exit 1
fi

# Clean up local backup
log_step "Cleaning up temporary files..."
rm -f "${BACKUP_TEMP_PATH}"
log_success "Temporary files cleaned up"

# Final success message
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${NC}  ${GREEN}✓${NC} Backup completed successfully!                  ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}  Backup: ${BACKUP_FILENAME}                        "
echo -e "${GREEN}║${NC}  Destination: ${RCLONE_DEST}                       "
echo -e "${GREEN}║${NC}  Date: ${BACKUP_DATE}                              "
echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"
echo ""

exit 0
