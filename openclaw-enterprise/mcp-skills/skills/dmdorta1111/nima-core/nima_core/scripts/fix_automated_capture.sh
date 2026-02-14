#!/bin/bash
# Fix NIMA Automated Capture - Heartbeat & Hook Setup
# Run this to enable automatic memory capture

echo "======================================"
echo "NIMA Automated Capture Setup"
echo "======================================"
echo ""

# 1. Check if hooks are properly linked
echo "[1/4] Checking OpenClaw hooks..."
HOOK_DIR="$HOME/.openclaw/extensions/nima-core/hooks"

if [ -d "$HOOK_DIR" ]; then
    echo "✓ Hook directory exists"
    ls -la "$HOOK_DIR"
else
    echo "✗ Hook directory not found!"
    echo "→ Creating hook directory..."
    mkdir -p "$HOOK_DIR"
fi

echo ""

# 2. Check OpenClaw configuration
echo "[2/4] Checking OpenClaw config..."
OPENCLAW_CONFIG="$HOME/.openclaw/config.json"

if [ -f "$OPENCLAW_CONFIG" ]; then
    echo "✓ OpenClaw config exists"
    # Check if nima-core is in extensions
    if grep -q "nima-core" "$OPENCLAW_CONFIG" 2>/dev/null; then
        echo "✓ nima-core found in config"
    else
        echo "⚠️  nima-core not in OpenClaw config"
        echo "→ Add this to your config:"
        echo '{"extensions": ["nima-core"]}'
    fi
else
    echo "⚠️  No OpenClaw config found"
fi

echo ""

# 3. Test hook trigger manually
echo "[3/4] Testing hook trigger..."
echo "→ You should see hook events fire on:"
echo "   - agent:bootstrap (when you start chatting)"
echo "   - command:* (when commands run)"
echo ""
echo "To enable capture on every message:"
echo ""

# 4. Create capture-on-message hook
echo "[4/4] Creating message capture hook..."

cat > "$HOOK_DIR/message-capture.sh" << 'EOF'
#!/bin/bash
# Auto-capture messages to NIMA
# Place this in: ~/.openclaw/extensions/nima-core/hooks/

# Get message from stdin
MESSAGE=$(cat)

# Run NIMA capture
python3 << PYTHON
import sys
sys.path.insert(0, '/usr/local/lib/python3.11/dist-packages')  # Adjust path as needed

from nima_core import NimaCore

nima = NimaCore()
result = nima.capture(
    who="user",
    what="""${MESSAGE}""",
    importance=0.7
)
print(f"Captured: {result}")
PYTHON
EOF

chmod +x "$HOOK_DIR/message-capture.sh"
echo "✓ Created message-capture.sh"

echo ""
echo "======================================"
echo "Next Steps:"
echo "======================================"
echo ""
echo "1. Restart OpenClaw gateway:"
echo "   openclaw gateway restart"
echo ""
echo "2. Test by sending a message - it should auto-capture!"
echo ""
echo "3. Check memory count:"
echo "   python3 -c \"from nima_core import NimaCore; n=NimaCore(); print(len(n.episodic.memories))\""
echo ""
echo "If capture still doesn't auto-trigger:"
echo "→ Check OpenClaw logs: openclaw logs"
echo "→ Verify hook is registered: openclaw hooks list"
echo ""
