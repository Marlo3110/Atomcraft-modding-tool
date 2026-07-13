import fetcher
from misc import *
from material import Material
from reaction import Reaction
from dataclasses import asdict
from json import dumps
from enum import Enum
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLineEdit,
                             QGridLayout, QWidget, QListWidget, QListWidgetItem,
                              QToolBar, QSplitter, QMenu, QTabWidget, QVBoxLayout,
                              QLabel, QComboBox, QSpinBox, QCompleter, QScrollArea)
from PyQt6.QtGui import QIcon, QPixmap, QColor
from gui_utils import CollapsibleSection

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

selected_item = None # the item that is selected currently
editing_material:Material = None # item that is currently being added
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
        
        # material editor
        self.material_editor_container = QScrollArea()
        self.material_editor_container.setWidgetResizable(True)
        self.material_editor = QWidget()
        self.material_name = QLineEdit()

        self.material_color = QLabel()
        self.material_color.setStyleSheet("background-color: rgba(255,0,0,0); margin:5px; border:2px solid rgb(255, 255, 255); ")

        self.material_description = QLineEdit("description")

        self.material_state = QComboBox()
        self.material_state.addItems([state.name for state in State])
        
        self.material_proton_number = QSpinBox()
        self.material_proton_number.setMinimum(0)
        self.material_proton_number.setMaximum(999)
        self.material_proton_number.setMinimumWidth(125)
        self.material_proton_number.setMaximumWidth(125)
        self.material_proton_number.setPrefix("Protons: ")

        self.material_neutron_number = QSpinBox()
        self.material_neutron_number.setMinimum(0)
        self.material_neutron_number.setMaximum(999)
        self.material_neutron_number.setMinimumWidth(125)
        self.material_neutron_number.setMaximumWidth(125)
        self.material_neutron_number.setPrefix("Neutrons: ")


        self.material_turns_into_from_alpha_particle_impact_label = QLabel("Turns into on alpha particle impact: ")
        self.material_turns_into_from_alpha_particle_impact = QComboBox()
        self.material_turns_into_from_alpha_particle_impact.addItem("None")
        self.material_turns_into_from_alpha_particle_impact.addItems([mat.Name for mat in materials])
        self.material_turns_into_from_alpha_particle_impact.setEditable(True)
        self.material_turns_into_from_alpha_particle_impact.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.material_turns_into_from_alpha_particle_impact.completer().setCompletionMode(QCompleter.CompletionMode.InlineCompletion)
        self.material_turns_into_from_alpha_particle_impact.completer().setModelSorting(QCompleter.ModelSorting.CaseInsensitivelySortedModel)

        self.material_turns_into_from_proton_impact_label = QLabel("Turns into on proton impact: ")
        self.material_turns_into_from_proton_impact = QComboBox()
        self.material_turns_into_from_proton_impact.addItem("None")
        self.material_turns_into_from_proton_impact.addItems([mat.Name for mat in materials])
        self.material_turns_into_from_proton_impact.setEditable(True)
        self.material_turns_into_from_proton_impact.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.material_turns_into_from_proton_impact.completer().setCompletionMode(QCompleter.CompletionMode.InlineCompletion)
        self.material_turns_into_from_proton_impact.completer().setModelSorting(QCompleter.ModelSorting.CaseInsensitivelySortedModel)

        self.material_turns_into_from_neutron_impact_label = QLabel("Turns into on neutron impact: ")
        self.material_turns_into_from_neutron_impact = QComboBox()
        self.material_turns_into_from_neutron_impact.addItem("None")
        self.material_turns_into_from_neutron_impact.addItems([mat.Name for mat in materials])
        self.material_turns_into_from_neutron_impact.setEditable(True)
        self.material_turns_into_from_neutron_impact.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.material_turns_into_from_neutron_impact.completer().setCompletionMode(QCompleter.CompletionMode.InlineCompletion)
        self.material_turns_into_from_neutron_impact.completer().setModelSorting(QCompleter.ModelSorting.CaseInsensitivelySortedModel)

        # decay settings here yeah




        #
        self.material_picks_up_into_label = QLabel("Picks up into: ")
        self.material_picks_up_into = QComboBox()
        self.material_picks_up_into.addItem("None")
        self.material_picks_up_into.addItems([mat.Name for mat in materials])
        self.material_picks_up_into.setEditable(True)
        self.material_picks_up_into.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.material_picks_up_into.completer().setCompletionMode(QCompleter.CompletionMode.InlineCompletion)
        self.material_picks_up_into.completer().setModelSorting(QCompleter.ModelSorting.CaseInsensitivelySortedModel)

        self.material_mines_into_label = QLabel("Mines into: ")
        self.material_mines_into = QComboBox()
        self.material_mines_into.addItem("None")
        self.material_mines_into.addItems([mat.Name for mat in materials])
        self.material_mines_into.setEditable(True)
        self.material_mines_into.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.material_mines_into.completer().setCompletionMode(QCompleter.CompletionMode.InlineCompletion)
        self.material_mines_into.completer().setModelSorting(QCompleter.ModelSorting.CaseInsensitivelySortedModel)

        self.material_builds_into_label = QLabel("builds into: ")
        self.material_builds_into = QComboBox()
        self.material_builds_into.addItem("None")
        self.material_builds_into.addItems([mat.Name for mat in materials])
        self.material_builds_into.setEditable(True)
        self.material_builds_into.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.material_builds_into.completer().setCompletionMode(QCompleter.CompletionMode.InlineCompletion)
        self.material_builds_into.completer().setModelSorting(QCompleter.ModelSorting.CaseInsensitivelySortedModel)




        self.material_editor_container.setWidget(self.material_editor)
        self.material_editor_layout = QGridLayout(self.material_editor)
        
        self.material_editor_layout.addWidget(self.material_name, 0, 0)
        self.material_editor_layout.addWidget(self.material_color, 0, 1)
        self.material_editor_layout.addWidget(self.material_description, 1, 0, 1, 2)
        self.material_editor_layout.addWidget(self.material_state, 2, 0)
        self.material_editor_layout.addWidget(self.material_proton_number, 3, 0)
        self.material_editor_layout.addWidget(self.material_neutron_number, 3, 1)

        self.material_editor_layout.addWidget(self.material_turns_into_from_alpha_particle_impact_label, 4, 0)
        self.material_editor_layout.addWidget(self.material_turns_into_from_alpha_particle_impact, 4, 1)
        self.material_editor_layout.addWidget(self.material_turns_into_from_proton_impact_label, 5, 0)
        self.material_editor_layout.addWidget(self.material_turns_into_from_proton_impact, 5, 1)
        self.material_editor_layout.addWidget(self.material_turns_into_from_neutron_impact_label, 6, 0)
        self.material_editor_layout.addWidget(self.material_turns_into_from_neutron_impact, 6, 1)
        self.material_editor_layout.setRowMinimumHeight(7, 20)
        self.material_editor_layout.addWidget(self.material_picks_up_into_label, 8, 0)
        self.material_editor_layout.addWidget(self.material_picks_up_into, 8, 1)
        self.material_editor_layout.addWidget(self.material_mines_into_label, 9, 0)
        self.material_editor_layout.addWidget(self.material_mines_into, 9, 1)
        self.material_editor_layout.addWidget(self.material_builds_into_label, 10, 0)
        self.material_editor_layout.addWidget(self.material_builds_into, 10, 1)

        


        self.material_editor.setLayout(self.material_editor_layout)
        self.update_material_editor()


        # reaction editor
        self.reaction_editor = QWidget()
        self.update_reaction_editor()

        editor = QTabWidget()
        editor.setMinimumWidth(300)
        editor.setLayout(editor_layout)
        editor.addTab(self.material_editor_container, "material editor")
        editor.addTab(self.reaction_editor, "reaction editor")

        # Container
        #container_layout = QGridLayout()
        

        container = QSplitter()
        container.addWidget(editor)
        container.addWidget(sidebar)
        #container.setLayout(container_layout)


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
        global selected_item, editing_material, editing_reaction
        if selected_item != None:

            if selected_item.text().endswith(" | material"):
                txt = selected_item.text().removesuffix(" | material")
                material = find_material_in_materials(txt)
                editing_material = material
                self.update_material_editor()

            elif selected_item.text().endswith(" | reaction"):
                txt = selected_item.text().removesuffix(" | reaction")
                reaction = find_reaction_in_reactions(txt)
                editing_reaction = reaction
                self.update_reaction_editor()

            selected_item = None


    def update_material_editor(self):
        colorPixmap = QPixmap(30, 30)
        if editing_material == None:
            self.material_name.setText("test")

            colorPixmap.fill(QColor.fromRgb(0, 0, 0))
            self.material_color.setPixmap(colorPixmap)

            self.material_description.setText("test description")

            return
        
        self.material_name.setText(editing_material.Name)
        colorPixmap.fill(editing_material.Color.toQColor())
        self.material_color.setPixmap(colorPixmap)

        self.material_description.setText(editing_material.Description)

    def update_reaction_editor(self):
        if editing_reaction == None:
            return



        

app = QApplication([])
window = MainWindow()
window.show()

app.exec()