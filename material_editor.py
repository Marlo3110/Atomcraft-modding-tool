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
                        QStateChange,
                        QColorSelector,
                        MaterialList,
                        MaterialAmountList,
                        QTextInputLabel,
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

        self.material_turns_into_container = QCollapsibleSection("Turns into ... from ...")
        self.material_turns_into_container.addWidget(self.material_turns_into_from_alpha_particle)
        self.material_turns_into_container.addWidget(self.material_turns_into_from_proton_impact)
        self.material_turns_into_container.addWidget(self.material_turns_into_from_neutron_impact)

        self.material_turns_into_container.addWidget(self.material_picks_up_into)
        self.material_turns_into_container.addWidget(self.material_mines_into)
        self.material_turns_into_container.addWidget(self.material_builds_into)

        self.material_turns_into_container.addWidget(self.material_turns_right_into)
        self.material_turns_into_container.addWidget(self.material_turns_left_into)

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
        self.material_physics_thermodynamics_condensation = QStateChange("Condensation", mats=materials)
        # physics/thermodynamics/evaporation
        self.material_physics_thermodynamics_evaporation = QStateChange("Evaporation", mats=materials)

        self.material_physics_thermodynamics_container = QCollapsibleSection("Thermodynamics")
        self.material_physics_thermodynamics_container.addWidget(self.material_physics_thermodynamics_is_burning)
        self.material_physics_thermodynamics_container.addWidget(self.material_physics_thermodynamics_default_temperature)
        self.material_physics_thermodynamics_container.addWidget(self.material_physics_thermodynamics_thermal_conductivity)
        self.material_physics_thermodynamics_container.addWidget(self.material_physics_thermodynamics_conductance_divisor)
        self.material_physics_thermodynamics_container.addWidget(self.material_physics_thermodynamics_condensation)
        self.material_physics_thermodynamics_container.addWidget(self.material_physics_thermodynamics_evaporation)
        
        

        self.material_physics_container = QCollapsibleSection("Physics")
        self.material_physics_container.addWidget(self.material_physics_weight)
        self.material_physics_container.addWidget(self.material_physics_density)
        self.material_physics_container.addWidget(self.material_physics_bounciness)
        self.material_physics_container.addWidget(self.material_physics_actor_friction)
        self.material_physics_container.addWidget(self.material_physics_override_actor_collision)
        self.material_physics_container.addWidget(self.material_physics_direction)
        self.material_physics_container.addWidget(self.material_physics_is_mechanical)
        self.material_physics_container.addWidget(self.material_physics_friction)
        self.material_physics_container.addWidget(self.material_physics_viscosity)
        self.material_physics_container.addWidget(self.material_physics_explosion_radius)
        self.material_physics_container.addWidget(self.material_physics_thermodynamics_container)

        # plant
        self.material_plant_grows_into = MaterialSelector("Grows into", mats=materials)
        self.material_plant_is_food_ingredient = QBooleanInputLabel("Is food ingredient: ")

        # plant/growth rules
        self.material_plant_growth_rules_direction = QEnumSelector("Direction: ", Direction, Direction.UP)
        self.material_plant_growth_rules_medium_type = QEnumSelector("Growth medium: ", MediumType, MediumType.DIRT)
        self.material_plant_growth_rules_growth_rate = QIntegerInputLabel("Growth rate: ")
        self.material_plant_growth_rules_growth_material_name = MaterialSelector("Growth material name: ", mats=materials)

        self.material_plant_growth_rules_container = QCollapsibleSection("Growth rules")
        self.material_plant_growth_rules_container.addWidget(self.material_plant_growth_rules_direction)
        self.material_plant_growth_rules_container.addWidget(self.material_plant_growth_rules_medium_type)
        self.material_plant_growth_rules_container.addWidget(self.material_plant_growth_rules_growth_rate)
        self.material_plant_growth_rules_container.addWidget(self.material_plant_growth_rules_growth_material_name)

        self.material_plant_container = QCollapsibleSection("Plant")
        self.material_plant_container.addWidget(self.material_plant_grows_into)
        self.material_plant_container.addWidget(self.material_plant_is_food_ingredient)
        self.material_plant_container.addWidget(self.material_plant_growth_rules_container)

        # electronics
        
        self.material_electronics_wire_index = QIntegerInputLabel("Wire index: ")
        self.material_electronics_is_on = QBooleanInputLabel("Is on: ")

        self.material_electronics_container = QCollapsibleSection("Electronics")
        self.material_electronics_container.addWidget(self.material_electronics_wire_index)
        self.material_electronics_container.addWidget(self.material_electronics_is_on)

        # visual

        self.material_visual_ignrore_fog_of_war = QBooleanInputLabel("Ignore fog of war: ")
        self.material_visual_is_foreground = QBooleanInputLabel("Is foreground: ")
        self.material_visual_color_delegate = MaterialSelector("Color delegate: ", mats=materials)
        self.material_visual_alpha = QIntegerInputLabel("Transparency: ")

        # light
        self.material_visual_light_color = QColorSelector("Light color: ")
        self.material_visual_light_range = QIntegerInputLabel("Light range: ")

        self.material_visual_light_container = QCollapsibleSection("Light")
        self.material_visual_light_container.addWidget(self.material_visual_light_color)
        self.material_visual_light_container.addWidget(self.material_visual_light_range)
        
        # 🔥 (No, I actually did not use ChatGPT for this. I copied the emoji from emojipedia.org)
        self.material_visual_fire_heat_output = QIntegerInputLabel("Heat output: ")
        self.material_visual_fire_percent_chance_to_spread = QIntegerInputLabel(r"% chance to spread: ")
        self.material_visual_fire_flame_color = QColorSelector("Flame color: ")
        self.material_visual_fire_extinguish_target_material_name = MaterialSelector("Extinguish target material name: ", mats=materials)
        self.material_visual_fire_combustion_target_material_names = MaterialList("Combustion target material name: ", mats=materials)

        self.material_visual_fire_combustion_target_material_names.setMinimumHeight(200)
        

        self.material_visual_fire_container = QCollapsibleSection("🔥")
        self.material_visual_fire_container.addWidget(self.material_visual_fire_heat_output)
        self.material_visual_fire_container.addWidget(self.material_visual_fire_percent_chance_to_spread)
        self.material_visual_fire_container.addWidget(self.material_visual_fire_flame_color)
        self.material_visual_fire_container.addWidget(self.material_visual_fire_extinguish_target_material_name)
        self.material_visual_fire_container.addWidget(self.material_visual_fire_combustion_target_material_names)

        self.material_visual_container = QCollapsibleSection("Visual")
        self.material_visual_container.addWidget(self.material_visual_ignrore_fog_of_war)
        self.material_visual_container.addWidget(self.material_visual_is_foreground)
        self.material_visual_container.addWidget(self.material_visual_color_delegate)
        self.material_visual_container.addWidget(self.material_visual_alpha)
        self.material_visual_container.addWidget(self.material_visual_light_container)
        self.material_visual_container.addWidget(self.material_visual_fire_container)

        # misc

        self.material_misc_can_be_cut_by_plasma = QBooleanInputLabel("Can be cut by plasma: ")
        self.material_misc_do_not_block_laser = QBooleanInputLabel("Do not block laser: ")
        self.material_misc_is_built = QBooleanInputLabel("Is built: ")
        self.material_misc_do_not_show_in_guide = QBooleanInputLabel("Do not show guide: ")
        self.material_misc_material_audio_type_id = QIntegerInputLabel("Material audio type id: ")
        self.material_misc_drop_rates = MaterialAmountList("Drop rates", mats=materials)

        self.material_misc_container = QCollapsibleSection("Miscellaneous")
        self.material_misc_container.addWidget(self.material_misc_can_be_cut_by_plasma)
        self.material_misc_container.addWidget(self.material_misc_do_not_block_laser)
        self.material_misc_container.addWidget(self.material_misc_is_built)
        self.material_misc_container.addWidget(self.material_misc_do_not_show_in_guide)
        self.material_misc_container.addWidget(self.material_misc_material_audio_type_id)
        self.material_misc_container.addWidget(self.material_misc_drop_rates)


        # chemistry
        self.material_chemistry_formula = QTextInputLabel("Formula: ")
        self.material_chemistry_dissolves_into = MaterialSelector("Dissolves into: ", mats=materials)
        self.material_chemistry_composition = MaterialAmountList("Composition", mats=materials)

        self.material_chemistry_container = QCollapsibleSection("Chemistry")
        self.material_chemistry_container.addWidget(self.material_chemistry_formula)
        self.material_chemistry_container.addWidget(self.material_chemistry_dissolves_into)
        self.material_chemistry_container.addWidget(self.material_chemistry_composition)


        # adding widgets
        self.material_editor_container.setWidget(self.material_editor)
        self.material_editor_layout = QVBoxLayout()
        self.material_editor_layout.setSpacing(5)
        self.material_editor_layout.setContentsMargins(QMargins(5, 5, 5, 5))
        

        self.material_editor_layout.addWidget(self.material_title_container)
        self.material_editor_layout.addWidget(self.material_atomic_info_container)

        self.material_editor_layout.addWidget(self.material_turns_into_container)

        self.material_editor_layout.addWidget(self.material_decay_settings)
        self.material_editor_layout.addWidget(self.material_player_interaction_container)
        self.material_editor_layout.addWidget(self.material_physics_container)
        self.material_editor_layout.addWidget(self.material_plant_container)
        self.material_editor_layout.addWidget(self.material_electronics_container)
        self.material_editor_layout.addWidget(self.material_visual_container)
        self.material_editor_layout.addWidget(self.material_misc_container)
        self.material_editor_layout.addWidget(self.material_chemistry_container)
        

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

    def get_material(self) -> Material:
        """Build a Material from the current state of every widget in the editor."""

        existing = editing_material  # may be None (creating a new material)

        def preserve(attr_name, default=None):
            """For fields with no editable widget: keep the loaded material's
            value, or fall back to a default if we're creating a fresh one."""
            return getattr(existing, attr_name) if existing is not None else default

        # --- decay settings ---
        decay_settings = DecaySettings(
            DecayMode=DecayMode[self.material_decay_settings_decay_mode.currentText()],
            TickModifierValue=self.material_decay_settings_tick_mod_value.input_field.value(),
            MaterialName=self.material_decay_settings_material_name.value(),
            MaterialName2=self.material_decay_settings_material_name2.value(),
        )

        # --- growth rules ---
        growth_rules = GrowthRules(
            Direction=self.material_plant_growth_rules_direction.value(),
            MediumType=self.material_plant_growth_rules_medium_type.value(),
            GrowthRate=self.material_plant_growth_rules_growth_rate.input_field.value(),
            GrowthMaterialName=self.material_plant_growth_rules_growth_material_name.value(),
        )

        # --- state changes (condensation / evaporation) ---
        def build_state_change(widget: QStateChange) -> StateChange:
            return StateChange(
                TargetMaterialName=widget.target_material_name.value(),
                Temperature=widget.temperature.input_field.value(),
                Amount=widget.amount.input_field.value(),
                Probability=widget.probability.input_field.value(),
            )

        condensation = build_state_change(self.material_physics_thermodynamics_condensation)
        evaporation = build_state_change(self.material_physics_thermodynamics_evaporation)

        # --- fire ---
        fire = Fire(
            HeatOutput=self.material_visual_fire_heat_output.input_field.value(),
            PercentChanceToSpread=self.material_visual_fire_percent_chance_to_spread.input_field.value(),
            FlameColor=Color.fromQColor(self.material_visual_fire_flame_color.value()),
            ExtinguishTargetMaterialName=self.material_visual_fire_extinguish_target_material_name.value(),
            CombustionTargetMaterialNames=self.material_visual_fire_combustion_target_material_names.get_materials(),
        )

        # --- drop rates / composition (both lists of MaterialAmount) ---
        drop_rates = DropRates(
            Amounts=self.material_misc_drop_rates.get_material_amounts(),
        )
        composition = Composition(
            Amounts=self.material_chemistry_composition.get_material_amounts(),
        )

        # --- light color ---
        light_color = Color.fromQColor(self.material_visual_light_color.value())

        return Material(
            Name=self.material_name.text(),
            Color=preserve("Color", Color(0.5, 0.5, 0.5, 1.0)),  # no editable widget for base color
            LocIdName=preserve("LocIdName", ""),                  # no widget
            Description=self.material_description.text(),
            State=State[self.material_state.currentText()],

            Formula=self.material_chemistry_formula.value(),

            ProtonNumber=self.material_proton_number.input_field.value(),
            NeutronNumber=self.material_neutron_number.input_field.value(),

            TurnsIntoFromAlphaParticleImpact=self.material_turns_into_from_alpha_particle.value(),
            TurnsIntoFromProtonImpact=self.material_turns_into_from_proton_impact.value(),
            TurnsIntoFromNeutronImpact=self.material_turns_into_from_neutron_impact.value(),

            DecaySettings=decay_settings,

            PickUpInto=self.material_picks_up_into.value(),
            MinesInto=self.material_mines_into.value(),
            BuildsInto=self.material_builds_into.value(),

            TurnsOnInto=preserve("TurnsOnInto"),   # no widget
            TurnsOffInto=preserve("TurnsOffInto"), # no widget

            RotatesRightInto=self.material_turns_right_into.value(),
            RotatesLeftInto=self.material_turns_left_into.value(),
            GrowsInto=self.material_plant_grows_into.value(),

            WireIndex=self.material_electronics_wire_index.input_field.value(),

            HealthChange=self.material_player_interaction_health_change.input_field.value(),
            AcidDamage=self.material_player_interaction_acid_damage.input_field.value(),

            Weight=self.material_physics_weight.input_field.value(),
            Density=self.material_physics_density.input_field.value(),
            Hardness=self.material_physics_hardness.input_field.value(),

            Composition=composition,
            DissolvesInto=self.material_chemistry_dissolves_into.value(),

            Bounciness=self.material_physics_bounciness.input_field.value(),
            ActorFriction=self.material_physics_actor_friction.input_field.value(),
            OverrideActorCollision=self.material_physics_override_actor_collision.value(),

            IsInteractable=self.material_player_interaction_is_interactable.value(),
            IsBurning=self.material_physics_thermodynamics_is_burning.value(),
            IgnoreFogOfWar=self.material_visual_ignrore_fog_of_war.value(),
            CanBeCutByPlasma=self.material_misc_can_be_cut_by_plasma.value(),

            Direction=self.material_physics_direction.value(),
            IsForeground=self.material_visual_is_foreground.value(),

            IsCarryingSignal=preserve("IsCarryingSignal", False),  # no widget
            IsUnstable=preserve("IsUnstable", False),              # no widget

            RequiredSupportDirection=preserve("RequiredSupportDirection"),  # no widget

            DoNotBlockLaser=self.material_misc_do_not_block_laser.value(),
            IsBuilt=self.material_misc_is_built.value(),
            IsMechanical=self.material_physics_is_mechanical.value(),

            CanPickUpStatic=self.material_player_interaction_can_pick_up_static.value(),
            IsOn=self.material_electronics_is_on.value(),

            WireSignalState=preserve("WireSignalState"),  # no widget

            DoNotShowInGuide=self.material_misc_do_not_show_in_guide.value(),
            IsFoodIngredient=self.material_plant_is_food_ingredient.value(),

            MaterialAudioTypeId=self.material_misc_material_audio_type_id.input_field.value(),

            GrowthRules=growth_rules,
            GrowthMedium=preserve("GrowthMedium"),  # widget picks MediumType, field wants Material — mismatch

            Friction=self.material_physics_friction.input_field.value(),
            Viscosity=self.material_physics_viscosity.input_field.value(),

            DefaultTemperature=self.material_physics_thermodynamics_default_temperature.input_field.value(),
            ThermalConductivity=self.material_physics_thermodynamics_thermal_conductivity.input_field.value(),
            ConductanceDivisor=self.material_physics_thermodynamics_conductance_divisor.input_field.value(),

            ColorDelegate=self.material_visual_color_delegate.value(),

            Alpha=self.material_visual_alpha.input_field.value(),
            LightColor=light_color,
            LightRange=self.material_visual_light_range.input_field.value(),
            Condensation=condensation,
            Evaporation=evaporation,
            Fire=fire,
            ExplosionRadius=self.material_physics_explosion_radius.input_field.value(),
            DropRates=drop_rates,
            Ignition=preserve("Ignition")
        )

app = QApplication([])
window = MainWindow()
window.show()

app.exec()