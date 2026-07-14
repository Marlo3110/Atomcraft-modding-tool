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
from gui_utils import   ( 
                        QCollapsibleSection,
                        QIntegerInputLabel,
                        MaterialSelector,
                        QBooleanInputLabel,
                        QEnumSelector,
                        )

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
        self.material_color.setStyleSheet("background-color: rgba(0,0,0,0); margin:1px; border:2px solid rgb(255, 255, 255); ")
        self.material_color.setMaximumSize(QSize(50,50))

        self.material_description = QLineEdit("description")

        self.material_state = QComboBox()
        self.material_state.addItems([state.name for state in State])
        
        material_title_container_layout = QGridLayout()
        material_title_container_layout.addWidget(self.material_name, 0, 0)
        material_title_container_layout.addWidget(self.material_color, 0, 1)
        material_title_container_layout.addWidget(self.material_description, 1, 0)
        material_title_container_layout.addWidget(self.material_state, 1, 1)
        self.material_title_container = QWidget()
        self.material_title_container.setLayout(material_title_container_layout)
        self.material_title_container.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )


        # atomic info
        self.material_proton_number = QIntegerInputLabel("Protons: ", "")
        self.material_neutron_number = QIntegerInputLabel("Neutrons: ", "")

        self.material_atomic_info_container = QCollapsibleSection("Atomic info")
        self.material_atomic_info_container.addWidget(self.material_proton_number)
        self.material_atomic_info_container.addWidget(self.material_neutron_number)

        #turns into
        self.material_turns_into_from_alpha_particle = MaterialSelector("Turns into from alpha particle impact: ", mats=materials)
        self.material_turns_into_from_proton_impact = MaterialSelector("Turns into from proton impact: ", mats=materials)
        self.material_turns_into_from_neutron_impact = MaterialSelector("Turns into from neutron impact: ", mats=materials)

        self.material_picks_up_into = MaterialSelector("Picks up into: ", mats=materials)
        self.material_mines_into = MaterialSelector("Mines into: ", mats=materials)
        self.material_builds_into = MaterialSelector("Builds into: ", mats=materials)

        self.material_turns_right_into = MaterialSelector("Rotates right into: ", mats=materials)
        self.material_turns_left_into = MaterialSelector("Rotates left into: ", mats=materials)
        self.material_grows_into = MaterialSelector("Grows into: ", mats=materials)

        self.material_turns_into_container = QCollapsibleSection("Turns into ... from ...")
        self.material_turns_into_container.addWidget(self.material_turns_into_from_alpha_particle)
        self.material_turns_into_container.addWidget(self.material_turns_into_from_proton_impact)
        self.material_turns_into_container.addWidget(self.material_turns_into_from_neutron_impact)

        self.material_turns_into_container.addWidget(self.material_picks_up_into)
        self.material_turns_into_container.addWidget(self.material_mines_into)
        self.material_turns_into_container.addWidget(self.material_builds_into)

        self.material_turns_into_container.addWidget(self.material_turns_right_into)
        self.material_turns_into_container.addWidget(self.material_turns_left_into)

        self.material_turns_into_container.addWidget(self.material_grows_into)

        # decay settings
        self.material_decay_settings_decay_mode = QComboBox()
        self.material_decay_settings_decay_mode.addItems([mode.name for mode in DecayMode])
        self.material_decay_settings_tick_mod_value = QIntegerInputLabel("Tick modifier value: ")
        self.material_decay_settings_material_name = MaterialSelector("Material name: ", materials)
        self.material_decay_settings_material_name2 = MaterialSelector("Material name 2: ", materials)

        self.material_decay_settings = QCollapsibleSection("Decay settings")
        self.material_decay_settings.addWidget(self.material_decay_settings_decay_mode)
        self.material_decay_settings.addWidget(self.material_decay_settings_tick_mod_value)
        self.material_decay_settings.addWidget(self.material_decay_settings_material_name)
        self.material_decay_settings.addWidget(self.material_decay_settings_material_name2)


        # player interaction
        self.material_player_interaction_health_change = QIntegerInputLabel("Player health change: ", minimum=-999)
        self.material_player_interaction_acid_damage = QIntegerInputLabel("Player acid damage: ", minimum=-999)
        self.material_player_interaction_is_interactable = QBooleanInputLabel("Is interactable: ")
        self.material_player_interaction_can_pick_up_static = QBooleanInputLabel("Can pick up static: ")
        
        self.material_player_interaction_container = QCollapsibleSection("Player interaction")
        self.material_player_interaction_container.addWidget(self.material_player_interaction_health_change)
        self.material_player_interaction_container.addWidget(self.material_player_interaction_acid_damage)
        self.material_player_interaction_container.addWidget(self.material_player_interaction_is_interactable)
        self.material_player_interaction_container.addWidget(self.material_player_interaction_can_pick_up_static)

        # physics
        self.material_physics_weight = QIntegerInputLabel("Weight: ")
        self.material_physics_density = QIntegerInputLabel("Density: ")
        self.material_physics_hardness = QIntegerInputLabel("Hardness: ")
        self.material_physics_bounciness = QIntegerInputLabel("Bounciness: ")
        self.material_physics_actor_friction = QIntegerInputLabel("Actor friction: ")
        self.material_physics_override_actor_collision = QBooleanInputLabel("Override actor collision: ")
        self.material_physics_direction = QEnumSelector("Direction: ", Direction, Direction.UP)
        self.material_physics_is_mechanical = QBooleanInputLabel("Is mechanical: ")
        self.material_physics_friction = QIntegerInputLabel("Friction: ")
        self.material_physics_viscosity = QIntegerInputLabel("Viscosity: ")
        self.material_physics_explosion_radius = QIntegerInputLabel("Explosion radius: ")

        # physics/thermodynamics
        self.material_physics_thermodynamics_is_burning = QBooleanInputLabel("Is burning: ")
        self.material_physics_thermodynamics_default_temperature = QIntegerInputLabel("Default temperature: ", minimum=-999, maximum=10000000)
        self.material_physics_thermodynamics_thermal_conductivity = QIntegerInputLabel("Thermal conductivity: ", minimum=-999)
        self.material_physics_thermodynamics_conductance_divisor = QIntegerInputLabel("Conductance divisor: ")
        
        # physics/thermodynamics/condensation


        self.material_editor_container.setWidget(self.material_editor)
        self.material_editor_layout = QVBoxLayout()
        self.material_editor_layout.setSpacing(5)
        self.material_editor_layout.setContentsMargins(QMargins(5, 5, 5, 5))
        

        self.material_editor_layout.addWidget(self.material_title_container)
        self.material_editor_layout.addWidget(self.material_atomic_info_container)

        self.material_editor_layout.addWidget(self.material_turns_into_container)

        self.material_editor_layout.addWidget(self.material_decay_settings)
        self.material_editor_layout.addWidget(self.material_player_interaction_container)

        

        self.material_editor_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.material_editor_layout.addStretch()
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