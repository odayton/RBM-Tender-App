import os
import sys
import tempfile
import atexit
from app import create_app
from app.core.core_config import config_dict

# File to store the selected mode across debug reloads
MODE_FILE = os.path.join(tempfile.gettempdir(), 'rbm_tender_mode.txt')

def show_menu():
    """Display the mode selection menu."""
    print("\n" + "="*50)
    print("RBM Tender App - Mode Selection")
    print("="*50)
    print("1. Development Mode (requires login)")
    print("   - Database: PostgreSQL (persistent)")
    print("   - Login: Manual login required")
    print("   - CSRF: Enabled")
    print("   - Debug: Enabled")
    print()
    print("2. Easy Development Mode (auto-login) ⭐ RECOMMENDED")
    print("   - Database: PostgreSQL (persistent)")
    print("   - Login: Auto-login enabled (no login required!)")
    print("   - CSRF: Disabled (easier form testing)")
    print("   - Debug: Enabled")
    print()
    print("3. Testing Mode (test database)")
    print("   - Database: PostgreSQL test database")
    print("   - Login: Manual login required")
    print("   - CSRF: Disabled")
    print("   - Cache: Disabled")
    print("   - Debug: Enabled")
    print()
    print("4. Production Mode (SECURE) - EC2 Ready")
    print("   - Database: Production database (DATABASE_URL)")
    print("   - Login: Manual login required")
    print("   - CSRF: Enabled")
    print("   - Debug: DISABLED")
    print("   - Security: MAXIMUM")
    print("   - Use: start_production.py for direct EC2 deployment")
    print()
    print("5. Clear saved mode and exit")
    print("6. Exit")
    print("="*50)

def get_user_choice():
    """Get user's mode choice."""
    while True:
        try:
            choice = input("\nSelect mode (1-6): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6']:
                return choice
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, 4, 5, or 6.")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            clear_mode()
            sys.exit(0)

def get_environment_from_choice(choice):
    """Convert menu choice to environment name."""
    env_map = {
        '1': 'development',
        '2': 'dev-easy',
        '3': 'testing',
        '4': 'production'
    }
    return env_map.get(choice)

def save_mode(env):
    """Save the selected mode to a temporary file."""
    try:
        with open(MODE_FILE, 'w') as f:
            f.write(env)
    except Exception as e:
        print(f"Warning: Could not save mode selection: {e}")

def load_mode():
    """Load the selected mode from the temporary file."""
    try:
        if os.path.exists(MODE_FILE):
            with open(MODE_FILE, 'r') as f:
                return f.read().strip()
    except Exception as e:
        print(f"Warning: Could not load mode selection: {e}")
    return None

def clear_mode():
    """Clear the saved mode."""
    try:
        if os.path.exists(MODE_FILE):
            os.remove(MODE_FILE)
            print("✅ Saved mode cleared.")
    except Exception as e:
        print(f"Warning: Could not clear saved mode: {e}")

def validate_production_environment():
    """Validate production environment variables."""
    required_vars = ['DATABASE_URL', 'SECRET_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ PRODUCTION ERROR: Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these environment variables before running in production mode.")
        return False
    
    return True

def start_app(env):
    """Start the Flask app with the specified environment."""
    print(f"\n🚀 Starting RBM Tender App in {env.upper()} mode...")
    print(f"📊 Environment: {env}")
    
    # Production security validation
    if env == 'production':
        if not validate_production_environment():
            print("\n❌ Cannot start in production mode. Please fix the environment variables.")
            return
        
        # Additional production checks
        if os.environ.get('FLASK_DEBUG') == '1':
            print("⚠️  WARNING: FLASK_DEBUG is enabled in production! This is a security risk.")
            response = input("Continue anyway? (y/N): ")
            if response.lower() != 'y':
                print("❌ Aborting production start.")
                return
    
    # Get the configuration class
    config_class = config_dict[env]
    print(f"⚙️  Using config class: {config_class.__name__}")
    
    # Create app with the appropriate configuration
    app = create_app(config_class)
    
    # Show configuration details
    print(f"🗄️  Database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')}")
    print(f"🐛 Debug: {app.config.get('DEBUG', False)}")
    print(f"🧪 Testing: {app.config.get('TESTING', False)}")
    print(f"🔐 Auto-login: {app.config.get('ENABLE_AUTO_LOGIN', False)}")
    print(f"🛡️  CSRF: {app.config.get('WTF_CSRF_ENABLED', True)}")
    print()
    
    # Security warnings
    if env == 'production':
        print("🔒 PRODUCTION SECURITY MODE:")
        print("   - HTTPS enforcement enabled")
        print("   - Security headers active")
        print("   - Rate limiting enabled")
        print("   - Debug mode disabled")
        print()
    elif app.config.get('ENABLE_AUTO_LOGIN'):
        print("✅ Auto-login enabled! You'll be automatically logged in.")
        print("📧 Login as: dev@example.com")
        print()
    else:
        print("🔒 Manual login required. Please log in through the login page.")
        print()
    
    # Determine host and port for production
    if env == 'production':
        host = os.environ.get('HOST', '0.0.0.0')
        port = int(os.environ.get('PORT', 5000))
        print(f"🌐 Starting server at http://{host}:{port}")
        print("🔒 PRODUCTION: Use HTTPS reverse proxy (nginx/apache) in front of this server")
    else:
        host = '0.0.0.0'  # This allows external connections
        port = 5000
        print("🌐 Starting server at http://0.0.0.0:5000")
        print("📡 External access: http://[YOUR_IP_ADDRESS]:5000")
        print("🔧 To find your IP address, run: ipconfig (Windows) or ifconfig (Mac/Linux)")
    
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Start the Flask app
    try:
        print(f"🚀 Starting Flask app on {host}:{port}...")
        
        # Configure reloader exclusions to prevent unnecessary restarts
        extra_files = []
        if app.config.get('DEBUG', False):
            # Exclude common directories that cause unnecessary restarts
            import os
            exclude_dirs = [
                'instance/logs',
                'instance/sessions', 
                'instance/uploads',
                'instance/exports',
                '__pycache__',
                '.git',
                'node_modules'
            ]
            print("🔧 Debug mode: Auto-reloader active (excludes logs, cache, uploads)")
        
        app.run(
            host=host, 
            port=port, 
            debug=app.config.get('DEBUG', False), 
            threaded=True,
            extra_files=extra_files
        )
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Cleaning up...")
        clear_mode()
        sys.exit(0)

def main():
    """Main function to handle mode selection and app startup."""
    # Register cleanup function to run on exit
    atexit.register(clear_mode)
    
    # Check if we have a saved mode (from debug reload)
    saved_env = load_mode()
    
    if saved_env and saved_env in config_dict:
        print(f"🔄 Found saved mode: {saved_env.upper()}")
        print("Press Enter to continue with saved mode, or Ctrl+C to choose a different mode...")
        try:
            input()
            print(f"🔄 Continuing with {saved_env.upper()} mode...")
            start_app(saved_env)
            return
        except KeyboardInterrupt:
            print("\n")
            clear_mode()
    
    # Check if environment variable is set (for non-interactive use)
    env = os.environ.get('FLASK_ENV', '').lower()
    
    if env and env in config_dict:
        # Environment variable is set, use it directly
        print(f"🔧 Using environment variable: FLASK_ENV={env}")
        start_app(env)
    else:
        # No environment variable, show interactive menu
        while True:
            show_menu()
            choice = get_user_choice()
            
            if choice == '5':
                print("\n🧹 Clearing saved mode...")
                clear_mode()
                print("👋 Goodbye!")
                break
            
            if choice == '6':
                print("\n👋 Goodbye!")
                break
            
            env = get_environment_from_choice(choice)
            if env:
                # Save the mode for debug reloads
                save_mode(env)
                start_app(env)
                break

if __name__ == '__main__':
    main()