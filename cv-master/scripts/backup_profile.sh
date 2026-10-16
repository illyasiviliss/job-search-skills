#!/usr/bin/env bash
# 备份简历母版。写入母版前必须先跑一次。
# 用法: backup_profile.sh [母版路径]
set -euo pipefail

ROOT="${CV_MASTER_ROOT:-$HOME/Documents/Career}"
PROFILE="${1:-$ROOT/母版.md}"
BACKUP_DIR="$ROOT/.backups"
KEEP=10

if [[ ! -f "$PROFILE" ]]; then
  echo "ERROR: 找不到母版文件: $PROFILE" >&2
  exit 1
fi

mkdir -p "$BACKUP_DIR"
STAMP="$(date +%Y%m%d-%H%M%S)"
DEST="$BACKUP_DIR/母版-$STAMP.md"
cp "$PROFILE" "$DEST"
echo "已备份: $DEST"

# 只保留最近 $KEEP 份
ls -1t "$BACKUP_DIR"/母版-*.md 2>/dev/null | tail -n +$((KEEP + 1)) | while read -r old; do
  rm -f "$old"
  echo "已清理旧备份: $old"
done
