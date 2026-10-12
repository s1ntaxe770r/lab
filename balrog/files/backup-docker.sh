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
CONTAINER_BACKUP_DIR="/mnt/thomas/containers"
MEDIA_SOURCE="/root/media"
MEDIA_BACKUP_DIR="/mnt/thomas/media"
MIN_SIZE_BYTES=$((100 * 1024 * 1024))  # 100MB in bytes
BACKUP_DATE=$(date +%Y-%m-%d_%H-%M-%S)

log_info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_step()    { echo -e "${CYAN}[STEP]${NC} $1"; }

IMAGES_SAVED=0
IMAGES_SKIPPED=0
ERRORS=0

# ====== DOCKER IMAGE BACKUP ======

log_step "Creating container backup directory..."
mkdir -p "${CONTAINER_BACKUP_DIR}"

log_step "Scanning Docker images..."

while IFS= read -r image_id; do
    # Get full name (repo:tag) and size in bytes
    image_info=$(docker image inspect "${image_id}" --format '{{index .RepoTags 0}} {{.Size}}' 2>/dev/null)
    image_name=$(echo "${image_info}" | awk '{print $1}')
    image_size=$(echo "${image_info}" | awk '{print $2}')

    # Skip untagged images
    if [ -z "${image_name}" ] || [ "${image_name}" = "<none>:<none>" ]; then
        log_warning "Skipping untagged image ${image_id}"
        continue
    fi

    if [ "${image_size}" -lt "${MIN_SIZE_BYTES}" ]; then
        size_mb=$(( image_size / 1024 / 1024 ))
        log_info "Skipping ${image_name} (${size_mb}MB < 100MB)"
        IMAGES_SKIPPED=$((IMAGES_SKIPPED + 1))
        continue
    fi

    # Sanitize name for filename: replace / and : with _
    safe_name=$(echo "${image_name}" | tr '/: ' '___')
    output_file="${CONTAINER_BACKUP_DIR}/${safe_name}.tar"

    size_mb=$(( image_size / 1024 / 1024 ))
    log_step "Saving ${image_name} (${size_mb}MB) -> ${output_file}"

    if docker save -o "${output_file}" "${image_name}"; then
        log_success "Saved ${image_name}"
        IMAGES_SAVED=$((IMAGES_SAVED + 1))
    else
        log_error "Failed to save ${image_name}"
        rm -f "${output_file}"
        ERRORS=$((ERRORS + 1))
    fi

done < <(docker images -q | sort -u)

# ====== MEDIA BACKUP ======

log_step "Starting media backup: ${MEDIA_SOURCE} -> ${MEDIA_BACKUP_DIR}"
mkdir -p "${MEDIA_BACKUP_DIR}"

if [ ! -d "${MEDIA_SOURCE}" ]; then
    log_error "Media source ${MEDIA_SOURCE} does not exist!"
    ERRORS=$((ERRORS + 1))
else
    if rsync -av --progress --delete "${MEDIA_SOURCE}/" "${MEDIA_BACKUP_DIR}/" 2>&1 | while read line; do
        echo -e "${MAGENTA}[RSYNC]${NC} ${line}"
    done; [ ${PIPESTATUS[0]} -eq 0 ]; then
        log_success "Media backup completed"
    else
        log_error "Media backup failed"
        ERRORS=$((ERRORS + 1))
    fi
fi

# ====== SUMMARY ======

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${NC}  Backup run: ${BACKUP_DATE}"
echo -e "${GREEN}║${NC}  Docker images saved:   ${IMAGES_SAVED}"
echo -e "${GREEN}║${NC}  Docker images skipped: ${IMAGES_SKIPPED} (< 100MB)"
echo -e "${GREEN}║${NC}  Errors:                ${ERRORS}"
echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"
echo ""

[ "${ERRORS}" -eq 0 ] && exit 0 || exit 1
