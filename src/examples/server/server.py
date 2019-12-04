from pathlib import Path

from pyotr.server import Application

SPEC_PATH = Path(__file__).parent.parent / "petstore.yaml"
ENDPOINTS_MODULE = "examples.server.pets"

app = Application.from_file(SPEC_PATH, module=ENDPOINTS_MODULE, debug=True)
