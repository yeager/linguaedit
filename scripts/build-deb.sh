#!/bin/bash
set -euo pipefail

SRCDIR="$(cd "$(dirname "$0")/.." && pwd)"
VER=$(sed -n 's/^__version__ = "\(.*\)"/\1/p' "$SRCDIR/src/linguaedit/__init__.py")
DEST="/tmp/linguaedit_${VER}_build"
PKG="linguaedit"

echo "Building ${PKG} ${VER}..."

rm -rf "$DEST"
mkdir -p "$DEST/DEBIAN"
mkdir -p "$DEST/usr/bin"
mkdir -p "$DEST/usr/lib/python3/dist-packages"
mkdir -p "$DEST/usr/share/applications"
mkdir -p "$DEST/usr/share/mime/packages"
mkdir -p "$DEST/usr/share/icons/hicolor/scalable/apps"
mkdir -p "$DEST/usr/share/doc/$PKG"
mkdir -p "$DEST/usr/share/man/man1"
mkdir -p "$DEST/usr/share/metainfo"

# Control file
cat > "$DEST/DEBIAN/control" <<EOF
Package: $PKG
Version: $VER
Section: editors
Priority: optional
Architecture: all
Depends: python3 (>= 3.10)
Recommends: ffmpeg, hunspell, python3-polib, python3-yaml
Maintainer: Daniel Nylander <daniel@danielnylander.se>
Homepage: https://github.com/yeager/linguaedit
Description: Professional translation editor
 A PySide6/Qt6 translation editor supporting 17+ file formats with
 translation memory, glossary, AI review, linting, Zen mode, and more.
 PySide6 must be installed via pip: pip install PySide6
EOF

# postinst / prerm
install -m 755 "$SRCDIR/debian/postinst" "$DEST/DEBIAN/postinst"
install -m 755 "$SRCDIR/debian/prerm" "$DEST/DEBIAN/prerm"

# Binary
cat > "$DEST/usr/bin/linguaedit-gui" <<'EOF'
#!/usr/bin/python3
from linguaedit.__main__ import main
main()
EOF
chmod 755 "$DEST/usr/bin/linguaedit-gui"

# Python package
cp -r "$SRCDIR/src/linguaedit" "$DEST/usr/lib/python3/dist-packages/"

# Remove __pycache__
find "$DEST" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Desktop file
install -m 644 "$SRCDIR/data/io.github.yeager.linguaedit.desktop" "$DEST/usr/share/applications/"

# MIME type
install -m 644 "$SRCDIR/data/io.github.yeager.linguaedit.xml" "$DEST/usr/share/mime/packages/"

# Icon
install -m 644 "$SRCDIR/data/icons/io.github.yeager.linguaedit.svg" "$DEST/usr/share/icons/hicolor/scalable/apps/"

# Metainfo
if [ -f "$SRCDIR/io.github.yeager.linguaedit.metainfo.xml" ]; then
    install -m 644 "$SRCDIR/io.github.yeager.linguaedit.metainfo.xml" "$DEST/usr/share/metainfo/"
fi

# Copyright (DEP-5)
install -m 644 "$SRCDIR/debian/copyright" "$DEST/usr/share/doc/$PKG/copyright"

# Changelog
gzip -9cn "$SRCDIR/debian/changelog" > "$DEST/usr/share/doc/$PKG/changelog.Debian.gz"

# Man page
gzip -9cn "$SRCDIR/man/linguaedit-gui.1" > "$DEST/usr/share/man/man1/linguaedit-gui.1.gz"

# Build
OUTPUT="/tmp/${PKG}_${VER}_all.deb"
dpkg-deb --root-owner-group --build "$DEST" "$OUTPUT"

echo "Built: $OUTPUT"
echo "Size: $(du -h "$OUTPUT" | cut -f1)"

# Verify
echo ""
echo "=== Lintian-style checks ==="
echo -n "copyright: "; [ -f "$DEST/usr/share/doc/$PKG/copyright" ] && echo "OK" || echo "MISSING"
echo -n "changelog: "; [ -f "$DEST/usr/share/doc/$PKG/changelog.Debian.gz" ] && echo "OK" || echo "MISSING"
echo -n "manpage: "; [ -f "$DEST/usr/share/man/man1/linguaedit-gui.1.gz" ] && echo "OK" || echo "MISSING"
echo -n "__pycache__: "; find "$DEST" -name __pycache__ -type d | grep -q . && echo "FOUND (BAD)" || echo "clean"
echo -n "postinst: "; [ -f "$DEST/DEBIAN/postinst" ] && echo "OK" || echo "MISSING"

rm -rf "$DEST"
