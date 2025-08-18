#!/usr/bin/env python3
"""
Production startup script for RBM Tender App on EC2
This bypasses the interactive menu and goes straight to production mode

NOTE: For production deployment, use Gunicorn instead of this script:
    gunicorn --workers 1 --bind 0.0.0.0:5000 app:create_app()
"""

import os
import sys
from app import create_app
from app.core.core_config import ProductionConfig

def main():
    """Start the app in production mode."""
    print("🚀 Starting RBM Tender App in PRODUCTION mode...")
    print("⚠️  WARNING: This uses Flask's development server. Use Gunicorn for production!")
    print()
    
    # Validate environment
    required_vars = ['DATABASE_URL', 'SECRET_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ ERROR: Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these in your .env file or environment.")
        print("Expected files: .env, .env.production, or environment variables")
        sys.exit(1)
    
    # Create app with production config
    try:
        app = create_app(ProductionConfig)
    except Exception as e:
        print(f"❌ ERROR: Failed to create app: {e}")
        print("Check your configuration and database connection.")
        sys.exit(1)
    
    # Get configuration
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    
    print(f"🌐 Starting production server at http://{host}:{port}")
    print(f"🗄️  Database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')}")
    print(f"🔒 Security: MAXIMUM")
    print(f"🐛 Debug: DISABLED")
    print()
    print("📋 Production Deployment Notes:")
    print("   - Use Gunicorn for production: gunicorn --workers 1 --bind 0.0.0.0:5000 app:create_app()")
    print("   - Nginx handles static files and reverse proxy")
    print("   - Cloudflare handles HTTPS termination")
    print("   - Database: PostgreSQL (not SQLite)")
    print()
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        app.run(host=host, port=port, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped.")
        sys.exit(0)

if __name__ == '__main__':
    main()

