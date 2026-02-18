#!/bin/bash
# ============================================
# Strategic Dashboard - Build Package Script
# macOS上で実行し、配布用フォルダを生成する
# ============================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DIST="$SCRIPT_DIR/StrategicDashboard"

echo "============================================"
echo "  Building StrategicDashboard package..."
echo "============================================"

# --- Clean previous build ---
if [ -d "$DIST" ]; then
    echo "Removing previous build..."
    rm -rf "$DIST"
fi

mkdir -p "$DIST"

# --- Copy launcher scripts ---
echo "Copying launcher scripts..."
cp "$SCRIPT_DIR/START.vbs"        "$DIST/"
cp "$SCRIPT_DIR/start.bat"        "$DIST/"
cp "$SCRIPT_DIR/setup.bat"        "$DIST/"
cp "$SCRIPT_DIR/stop.bat"         "$DIST/"
cp "$SCRIPT_DIR/requirements.txt" "$DIST/"

# --- Copy main app ---
echo "Copying application..."
cp "$SCRIPT_DIR/app_new.py" "$DIST/"
cp "$SCRIPT_DIR/main_desktop.py" "$DIST/"
cp "$SCRIPT_DIR/build_exe.bat" "$DIST/"
[ -f "$SCRIPT_DIR/SETUP_GUIDE.txt" ] && cp "$SCRIPT_DIR/SETUP_GUIDE.txt" "$DIST/"

# --- Copy splash/logo images ---
echo "Copying images..."
[ -f "$SCRIPT_DIR/opening.png" ] && cp "$SCRIPT_DIR/opening.png" "$DIST/"
[ -f "$SCRIPT_DIR/back.png" ]    && cp "$SCRIPT_DIR/back.png"    "$DIST/"

# --- Copy assets (from ~/Pictures/kddi_cockpit) ---
echo "Copying assets..."
ASSET_SRC="$HOME/Pictures/kddi_cockpit"
mkdir -p "$DIST/assets"
if [ -d "$ASSET_SRC" ]; then
    cp "$ASSET_SRC"/*.png "$DIST/assets/" 2>/dev/null || true
    echo "  Copied from $ASSET_SRC"
else
    echo "  [WARN] $ASSET_SRC not found — assets/ will be empty"
fi

# --- Copy dashboard_modules ---
echo "Copying dashboard_modules..."
cp -r "$SCRIPT_DIR/dashboard_modules" "$DIST/dashboard_modules"
# Remove pycache
find "$DIST/dashboard_modules" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# --- Create empty directories ---
mkdir -p "$DIST/context"
mkdir -p "$DIST/static"

# --- Summary ---
echo ""
echo "============================================"
echo "  Build complete!"
echo "  Output: $DIST"
echo "============================================"
echo ""
echo "Contents:"
ls -la "$DIST/"
echo ""
echo "Next steps (EXE build):"
echo "  1. Copy StrategicDashboard/ folder to pip が使える Windows PC"
echo "  2. build_exe.bat を実行 → dist/StrategicDashboard/ が生成される"
echo "  3. dist/StrategicDashboard/ を会社PCにコピー"
echo "  4. StrategicDashboard.exe をダブルクリックで起動"
