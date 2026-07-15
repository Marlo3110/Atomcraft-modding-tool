import fetcher
from misc import *
from material import Material
from reaction import Reaction
from dataclasses import asdict
from json import dumps
from enum import Enum
from PyQt6.QtCore import QSize, Qt, QMargins
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLineEdit,
                             QGridLayout, QWidget, QListWidget, QListWidgetItem,
                              QToolBar, QSplitter, QMenu, QTabWidget, QVBoxLayout,
                              QLabel, QComboBox, QSpinBox, QCompleter, QScrollArea,
                              QSizePolicy)
from PyQt6.QtGui import QIcon, QPixmap, QColor
from material_editor import MaterialEditor

material_fetcher = fetcher.MaterialFetcher()
reaction_fetcher = fetcher.ReactionFetcher()

materials = []
reactions = []


def fetch_data():
    global materials, reactions
    materials = material_fetcher.fetch()
    reactions = reaction_fetcher.fetch(materials)

fetch_data()

def json_default(o):
    if isinstance(o, Material):
        return o.toJSON()
    if isinstance(o, Enum):
        return o.toJSON() if hasattr(o, "toJSON") else o.name
    return o.__dict__

def find_material_in_materials(name:str) -> Material:
    global materials
    for i in materials:
        if i.Name == name:
            return i
    return None

def find_reaction_in_reactions(name:str) -> Reaction:
    global reactions
    for i in reactions:
        if i.Name == name:
            return i
    return None

selected_item = None  # the item that is selected currently
editing_reaction:Reaction = None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Atomcraft modding tool")
        self.setMinimumSize(QSize(700,400))

        # Search sidebar

        # context menu
        self.context_menu = QMenu("", self)
        self.edit = self.context_menu.addAction("edit")

        self.search_bar = QLineEdit()
        self.search_bar.textChanged.connect(self.refresh_elements_list)

        self.elements = QListWidget()
        self.elements.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.elements.customContextMenuRequested.connect(self.open_context_menu)

        self.new_element = QPushButton()
        self.new_element.setText("New")
        layout = QGridLayout()
        layout.addWidget(self.search_bar, 0, 0)
        layout.addWidget(self.new_element, 0, 1)
        layout.addWidget(self.elements, 1, 0, 1, 2)

        sidebar = QWidget()
        sidebar.setLayout(layout)

        # Editor
        editor_layout = QGridLayout()

        # material editor — now its own class
        self.material_editor_container = MaterialEditor(materials)

        # reaction editor
        self.reaction_editor = QWidget()
        self.update_reaction_editor()

        editor = QTabWidget()
        editor.setMinimumWidth(300)
        editor.setLayout(editor_layout)
        editor.addTab(self.material_editor_container, "material editor")
        editor.addTab(self.reaction_editor, "reaction editor")

        # Container
        container = QSplitter()
        container.addWidget(editor)
        container.addWidget(sidebar)

        # Toolbar
        toolbar = QToolBar("Toolbar")
        toolbar.setMinimumSize(QSize(25,25))

        self.addToolBar(toolbar)
        self.setCentralWidget(container)
        self.refresh_elements_list("")

    def refresh_elements_list(self, text:str):
        self.elements.clear()
        pixmap = QPixmap(25,25)

        if text == "":
            for i in materials:
                pixmap.fill(i.Color.toQColor())
                icon = QIcon(pixmap)
                widget = QListWidgetItem(icon, f"{i.Name} | material", self.elements)
            for i in reactions:
                if len(i.Outputs) > 0:
                        if i.Outputs[0] == None:
                            continue
                        if i.Outputs[0].MaterialName == None:
                            continue
                        pixmap.fill(i.Outputs[0].MaterialName.Color.toQColor())
                        icon = QIcon(pixmap)
                        widget = QListWidgetItem(icon, f"{i.Name} | reaction", self.elements)
                else:
                    pixmap.fill(QColor.black)
                    icon = QIcon(pixmap)
                    widget = QListWidgetItem(icon, f"{i.Name} | reaction", self.elements)
        else:
            for i in materials:
                if text.lower() in i.Name.lower():
                    pixmap.fill(i.Color.toQColor())
                    icon = QIcon(pixmap)
                    widget = QListWidgetItem(icon, f"{i.Name} | material", self.elements)
            for i in reactions:
                if text.lower() in i.Name.lower():
                    if len(i.Outputs) > 0:
                        if i.Outputs[0] == None:
                            continue
                        if i.Outputs[0].MaterialName == None:
                            continue
                        pixmap.fill(i.Outputs[0].MaterialName.Color.toQColor())
                        icon = QIcon(pixmap)
                        widget = QListWidgetItem(icon, f"{i.Name} | reaction", self.elements)
                    else:
                        pixmap.fill(QColor.black)
                        icon = QIcon(pixmap)
                        widget = QListWidgetItem(icon, f"{i.Name} | reaction", self.elements)

        self.elements.sortItems(Qt.SortOrder.AscendingOrder)

    def open_context_menu(self, position):
        item = self.elements.itemAt(position)
        if item is None:
            return  # right-clicked on empty space

        action = self.context_menu.exec(self.elements.mapToGlobal(position))

        if action == self.edit:
            global selected_item
            print("item:", item.text(), "pressed")
            selected_item = item
            self.edit_element(item)

    def edit_element(self, item):
        global selected_item, editing_reaction
        if selected_item != None:

            if selected_item.text().endswith(" | material"):
                txt = selected_item.text().removesuffix(" | material")
                material = find_material_in_materials(txt)
                self.material_editor_container.set_material(material)

            elif selected_item.text().endswith(" | reaction"):
                txt = selected_item.text().removesuffix(" | reaction")
                reaction = find_reaction_in_reactions(txt)
                editing_reaction = reaction
                self.update_reaction_editor()

            selected_item = None

    def update_reaction_editor(self):
        if editing_reaction == None:
            return


app = QApplication([])
window = MainWindow()
window.show()

app.exec()