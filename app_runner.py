from app import create_app

# Create the application instance using the modern factory
app = create_app()

if __name__ == '__main__':
    # Set host to '0.0.0.0' to make it accessible from the network
    # Debug mode should ideally be loaded from the config, but this is fine for local dev
    app.run(host='0.0.0.0', port=5000, debug=True)