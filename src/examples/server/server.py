from pathlib import Path

from pyotr.server import Application

SPEC_PATH = Path(__file__).parent.parent / 'petstore.yaml'
ENDPOINT_BASE = 'examples.server.pets'

app = Application.from_file(
    SPEC_PATH, endpoint_base=ENDPOINT_BASE, debug=True
)
