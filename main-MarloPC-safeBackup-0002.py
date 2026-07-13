import fetcher
from misc import *
from material import Material
from dataclasses import asdict
from json import dumps
from enum import Enum
from PyQt6.QtWidgets import QApplication, QWidget

material_fetcher = fetcher.MaterialFetcher()
reaction_fetcher = fetcher.ReactionFetcher()

materials = []
reactions = []



def fetch_data():
    materials = material_fetcher.fetch()
    reactions = reaction_fetcher.fetch(materials)

fetch_data()

def json_default(o):
    if isinstance(o, Material):
        return o.toJSON()
    if isinstance(o, Enum):
        return o.toJSON() if hasattr(o, "toJSON") else o.name
    return o.__dict__


app = QApplication([])
window = QWidget()
window.show()

app.exec()