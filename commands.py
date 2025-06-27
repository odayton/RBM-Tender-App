# commands.py

import click
import io
from PIL import Image
from app.__init__ import create_app
from app.utils.file_utils import storage_manager

# This creates an instance of the app for our script to use
app = create_app()

def create_dummy_image():
    """Creates a simple black square PNG image in memory."""
    img = Image.new('RGB', (100, 100), 'black')
    byte_io = io.BytesIO()
    img.save(byte_io, 'PNG')
    byte_io.seek(0)
    return byte_io.read()

@click.command(name='test-storage')
def test_storage_command():
    """
    Runs a test to save a dummy image using the StorageManager
    and generate its public URL.
    """
    # The 'with app.app_context()' is crucial because url_for() needs it to work.
    with app.app_context():
        click.echo("--- Running Storage Manager Test ---")
        
        image_data = create_dummy_image()
        filename = "test_graph.png"
        
        click.echo(f"Attempting to save '{filename}'...")
        saved_path = storage_manager.save_graph(image_data, filename)
        click.echo(f"File saved locally to: {saved_path}")

        url = storage_manager.get_graph_url(filename)
        click.echo(f"SUCCESS: URL for browser access is: {url}")
        click.echo("---------------------------------")