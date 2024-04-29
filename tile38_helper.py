from contextlib import contextmanager
import os
from pyle38 import Tile38

class Tile38Helper:
    def __init__(self):
        self._conn = None

    def get_conn_str(self):
        # Initialisation
        conn_str = "redis://localhost:9851"
        if "TILE38_URL" in os.environ:
            conn_str = f"redis://{os.getenv('TILE38_URL')}"

        return conn_str

    def initialize_connection(self):
        conn_str = self.get_conn_str()
        self._conn = Tile38(url=conn_str)

    @contextmanager
    def get_resource(self):
        if self._conn is None:
            self.initialize_connection()
        yield self._conn


tile38_helper = Tile38Helper()