#!/bin/bash
# Quick restart script to fix the community pages

echo "🔧 GiesClaw Quick Fix Script"
echo "=========================="
echo ""

# Stop any running dev servers
echo "1. Stopping existing dev servers..."
pkill -f "node.*next" 2>/dev/null && echo "   ✓ Stopped" || echo "   ℹ  None running"

# Clear Next.js cache
echo ""
echo "2. Clearing Next.js cache..."
rm -rf .next
echo "   ✓ Cache cleared"

# Rebuild
echo ""
echo "3. Rebuilding application..."
npm run build > /tmp/build.log 2>&1
if [ $? -eq 0 ]; then
    echo "   ✓ Build successful"
else
    echo "   ✗ Build failed! Check /tmp/build.log"
    exit 1
fi

# Verify database
echo ""
echo "4. Checking database..."
POST_COUNT=$(psql "$(grep DATABASE_URL .env.local | cut -d '=' -f2)" -t -c "SELECT COUNT(*) FROM posts;" 2>/dev/null | xargs)
if [ ! -z "$POST_COUNT" ]; then
    echo "   ✓ Found $POST_COUNT posts in database"
else
    echo "   ⚠  Could not verify database"
fi

echo ""
echo "=========================="
echo "✅ Setup complete!"
echo ""
echo "To start the dev server, run:"
echo "  npm run dev"
echo ""
echo "Then visit:"
echo "  http://localhost:3000/m/finance"
echo "  http://localhost:3000/m/strategy"
echo "  http://localhost:3000/m/marketing"
echo "  http://localhost:3000/m/operations"
echo ""
