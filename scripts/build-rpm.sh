#!/bin/bash
set -euo pipefail

SRCDIR="$(cd "$(dirname "$0")/.." && pwd)"
VER=$(sed -n 's/^__version__ = "\(.*\)"/\1/p' "$SRCDIR/src/linguaedit/__init__.py")
PKG="linguaedit"
SERVER="192.168.2.2"
USER="yeager"

SSH_PASS=$(security find-generic-password -s "ssh-${SERVER}" -w)
SSH="sshpass -p $SSH_PASS ssh -o StrictHostKeyChecking=no ${USER}@${SERVER}"
SCP="sshpass -p $SSH_PASS scp -o StrictHostKeyChecking=no"

echo "Building ${PKG}-${VER} RPM on ${SERVER}..."

# Pre-compress man page for the spec
gzip -9cn "$SRCDIR/man/linguaedit-gui.1" > "/tmp/linguaedit-gui.1.gz"

# Create tarball
TARDIR="/tmp/${PKG}-${VER}"
rm -rf "$TARDIR"
mkdir -p "$TARDIR"/{src,scripts,data/icons,man}
cp -r "$SRCDIR/src/linguaedit" "$TARDIR/src/"
find "$TARDIR" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Create launcher script
cat > "$TARDIR/scripts/linguaedit-gui" <<'EOF'
#!/usr/bin/python3
from linguaedit.__main__ import main
main()
EOF
chmod 755 "$TARDIR/scripts/linguaedit-gui"

cp "$SRCDIR/data/io.github.yeager.linguaedit.desktop" "$TARDIR/data/"
cp "$SRCDIR/data/io.github.yeager.linguaedit.xml" "$TARDIR/data/"
cp "$SRCDIR/data/icons/io.github.yeager.linguaedit.svg" "$TARDIR/data/icons/"
cp /tmp/linguaedit-gui.1.gz "$TARDIR/man/"
cp "$SRCDIR/README.md" "$SRCDIR/CHANGELOG.md" "$SRCDIR/LICENSE" "$TARDIR/"

cd /tmp
tar czf "${PKG}-${VER}.tar.gz" "${PKG}-${VER}"

# Ensure rpmbuild is installed
$SSH "which rpmbuild >/dev/null 2>&1 || sudo apt-get install -y rpm" || true

# Setup rpmbuild dirs on server
$SSH "mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}"

# Upload
$SCP "/tmp/${PKG}-${VER}.tar.gz" "${USER}@${SERVER}:~/rpmbuild/SOURCES/"
$SCP "$SRCDIR/scripts/linguaedit.spec" "${USER}@${SERVER}:~/rpmbuild/SPECS/"

# Build
$SSH "cd ~/rpmbuild/SOURCES && tar xzf ${PKG}-${VER}.tar.gz && cd ${PKG}-${VER} && rpmbuild -bb ~/rpmbuild/SPECS/linguaedit.spec --define '_topdir /home/${USER}/rpmbuild'"

# Fetch result
RPM_PATH=$($SSH "find ~/rpmbuild/RPMS -name '${PKG}-${VER}*.rpm' -type f | head -1")
if [ -n "$RPM_PATH" ]; then
    $SCP "${USER}@${SERVER}:${RPM_PATH}" "/tmp/"
    echo "Built: /tmp/$(basename "$RPM_PATH")"
else
    echo "ERROR: RPM not found on server"
    exit 1
fi
