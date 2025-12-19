#!/bin/bash

###############################################################################
# Image Optimization Script
#
# Converts images to WebP format and ensures they are under 200KB.
# Processes all images in static/img/ directory.
#
# Requirements:
# - ImageMagick or cwebp (for WebP conversion)
#
# Usage: bash scripts/optimize-images.sh
###############################################################################

set -e

STATIC_IMG_DIR="static/img"
MAX_SIZE_KB=200
QUALITY=85

echo "🖼️  Image Optimization Script"
echo "================================"
echo ""

# Check if static/img directory exists
if [ ! -d "$STATIC_IMG_DIR" ]; then
    echo "ℹ️  Directory $STATIC_IMG_DIR does not exist yet - skipping optimization"
    exit 0
fi

# Check for image files
IMAGE_COUNT=$(find "$STATIC_IMG_DIR" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) | wc -l)

if [ "$IMAGE_COUNT" -eq 0 ]; then
    echo "ℹ️  No images found in $STATIC_IMG_DIR - skipping optimization"
    exit 0
fi

echo "📊 Found $IMAGE_COUNT image(s) to process"
echo ""

# Check for ImageMagick or cwebp
if command -v convert &> /dev/null; then
    CONVERTER="imagemagick"
    echo "✓ Using ImageMagick for conversion"
elif command -v cwebp &> /dev/null; then
    CONVERTER="cwebp"
    echo "✓ Using cwebp for conversion"
else
    echo "⚠️  Neither ImageMagick nor cwebp found"
    echo "   Install one of:"
    echo "   - ImageMagick: sudo apt-get install imagemagick"
    echo "   - cwebp: sudo apt-get install webp"
    echo ""
    echo "   Skipping image optimization..."
    exit 0
fi

echo ""

PROCESSED=0
CONVERTED=0
OVERSIZED=0

# Process each image
find "$STATIC_IMG_DIR" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) | while read -r img; do
    BASENAME=$(basename "$img")
    DIRNAME=$(dirname "$img")
    FILENAME="${BASENAME%.*}"
    EXT="${BASENAME##*.}"

    # Convert to WebP if not already
    if [ ! -f "$DIRNAME/$FILENAME.webp" ]; then
        echo "🔄 Converting: $BASENAME → $FILENAME.webp"

        if [ "$CONVERTER" = "imagemagick" ]; then
            convert "$img" -quality $QUALITY "$DIRNAME/$FILENAME.webp"
        else
            cwebp -q $QUALITY "$img" -o "$DIRNAME/$FILENAME.webp"
        fi

        CONVERTED=$((CONVERTED + 1))
    fi

    # Check WebP file size
    WEBP_FILE="$DIRNAME/$FILENAME.webp"
    if [ -f "$WEBP_FILE" ]; then
        SIZE_KB=$(du -k "$WEBP_FILE" | cut -f1)

        if [ "$SIZE_KB" -gt "$MAX_SIZE_KB" ]; then
            echo "   ⚠️  Warning: $FILENAME.webp is ${SIZE_KB}KB (exceeds ${MAX_SIZE_KB}KB limit)"
            echo "      Consider resizing or further compressing this image"
            OVERSIZED=$((OVERSIZED + 1))
        else
            echo "   ✓ $FILENAME.webp: ${SIZE_KB}KB"
        fi
    fi

    PROCESSED=$((PROCESSED + 1))
done

echo ""
echo "================================"
echo "✅ Optimization complete"
echo "   Processed: $PROCESSED image(s)"
echo "   Converted: $CONVERTED to WebP"

if [ "$OVERSIZED" -gt 0 ]; then
    echo "   ⚠️  $OVERSIZED image(s) exceed ${MAX_SIZE_KB}KB limit"
    exit 1
else
    echo "   ✓ All images within ${MAX_SIZE_KB}KB limit"
fi
