from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QToolButton,
    QStyle,
    QLabel,
    QComboBox,
    QSpinBox,
    QCompleter,
    QSizePolicy,
    QCheckBox,
)
from PyQt6.QtGui import (
    QIcon,
    QColor,
    QPixmap,
    QPainter,
)
from PyQt6.QtCore import Qt, pyqtSignal, QMargins
from material import (Material)
from misc import (
                    StateChange,
                 )
from enum import Enum

def find_material_in_materials(name:str, mats:list[Material]) -> Material:
    for i in mats:
        if i.Name == name:
            return i
    return None

def colored_icon(icon: QIcon, color: QColor, size=32) -> QIcon:
    pixmap = icon.pixmap(size, size)

    colored_pixmap = QPixmap(pixmap.size())
    colored_pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(colored_pixmap)
    painter.drawPixmap(0, 0, pixmap)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(colored_pixmap.rect(), color)
    painter.end()

    return QIcon(colored_pixmap)


class QCollapsibleSection(QWidget):
    def __init__(self, txt: str = "", enabled:bool = False):
        super().__init__()
        brightness = 200

        self.icon_collapsed = colored_icon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarShadeButton),
            QColor(brightness, brightness, brightness),
        )
        self.icon_expanded = colored_icon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarUnshadeButton),
            QColor(brightness, brightness, brightness),
        )

        self.pushbutton = QToolButton()
        self.pushbutton.setIcon(self.icon_collapsed)
        self.pushbutton.setCheckable(True)
        self.pushbutton.setAutoRaise(True)
        self.pushbutton.toggled.connect(self.toggle)

        self.checkbox = QCheckBox()
        self.checkbox.toggled.connect(self.toggle_enable)

        self.title = QLabel(txt)

        title_container = QWidget()
        title_container_layout = QHBoxLayout()
        title_container_layout.setContentsMargins(0, 0, 0, 0)
        title_container_layout.addWidget(self.checkbox)
        title_container_layout.addWidget(self.pushbutton)
        title_container_layout.addWidget(self.title)
        title_container_layout.addStretch()
        title_container.setLayout(title_container_layout)

        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(20, 0, 0, 0)
        self.content_area.setLayout(self.content_layout)
        self.content_area.setVisible(False)

        layout = QVBoxLayout()
        layout.addWidget(title_container)
        layout.addWidget(self.content_area)

        self.setLayout(layout)

        self.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Maximum
        )

        self.toggle_enable(enabled)
    def toggle_enable(self, checked: bool):
        if checked:
            self.pushbutton.setCheckable(True)

        else:
            self.pushbutton.setChecked(False)
            self.pushbutton.setCheckable(False)
            
        

    def toggle(self, checked: bool):
        self.content_area.setVisible(checked)
        self.pushbutton.setIcon(self.icon_expanded if checked else self.icon_collapsed)

    def addWidget(self, widget: QWidget):
        """Add a widget to the collapsible content area."""
        self.content_layout.addWidget(widget)

class QIntegerInputLabel(QWidget):
    inputChanged = pyqtSignal(int)

    def __init__(self, txt:str = "", prefix:str = "", minimum:int = 0, maximum:int = 999):
        super().__init__()
        self.label = QLabel(txt)
        self.input_field = QSpinBox()
        self.input_field.setMinimum(minimum)
        self.input_field.setMaximum(maximum)
        self.input_field.setPrefix(prefix)


        self.input_field.textChanged.connect(self.inputChanged.emit)

        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.input_field)
        self.setLayout(layout)

from PyQt6.QtWidgets import QWidget, QLabel, QCheckBox, QHBoxLayout
from PyQt6.QtCore import pyqtSignal


class QBooleanInputLabel(QWidget):
    inputChanged = pyqtSignal(bool)

    def __init__(self, txt: str = "", checked: bool = False):
        super().__init__()

        self.label = QLabel(txt)
        self.input_field = QCheckBox()
        self.input_field.setChecked(checked)

        self.input_field.toggled.connect(self.inputChanged.emit)

        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.input_field)

        self.setLayout(layout)

    def value(self) -> bool:
        return self.input_field.isChecked()

    def setValue(self, value: bool):
        self.input_field.setChecked(value)

class MaterialSelector(QWidget):
    inputChanged = pyqtSignal(Material)

    def __init__(self, txt:str = "", mats:list[Material] = [], normal_value:Material|str = ""):
        
        super().__init__()
        self.mats = mats

        self.label = QLabel(txt)
        self.decider = QComboBox()

        if normal_value.lower() != "none":
            self.decider.addItem("None")
        if normal_value != "":
            self.decider.addItem(normal_value.Name if normal_value.__class__ == "Material" else normal_value)

        self.decider.addItems([mat.Name for mat in mats])
        self.decider.setEditable(True)
        self.decider.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.decider.completer().setCompletionMode(QCompleter.CompletionMode.InlineCompletion)
        self.decider.completer().setModelSorting(QCompleter.ModelSorting.CaseInsensitivelySortedModel)

        self.decider.editTextChanged.connect(self.__input_changed__)

        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.decider)
        self.setLayout(layout)
        self.setContentsMargins(QMargins(1, 1, 1, 1))

    def __input_changed__(self, txt:str):
        mat = find_material_in_materials(txt, mats=self.mats)
        if mat != None:
            self.inputChanged.emit(mat)

class QEnumSelector(QWidget):
    inputChanged = pyqtSignal(object)  # emits the selected enum member

    def __init__(self, txt: str = "", enum: type[Enum] = None, normal_value: Enum | None = None):
        super().__init__()

        self.label = QLabel(txt)
        self.decider = QComboBox()

        self.enum = enum

        if enum is not None:
            for member in enum:
                self.decider.addItem(member.name, member)

        if normal_value is not None:
            index = self.decider.findData(normal_value)
            if index != -1:
                self.decider.setCurrentIndex(index)

        self.decider.currentIndexChanged.connect(self.__input_changed__)

        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.decider)
        self.setLayout(layout)
        self.setContentsMargins(QMargins(1, 1, 1, 1))

    def __input_changed__(self):
        self.inputChanged.emit(self.value())

    def value(self) -> Enum:
        return self.decider.currentData()

    def setValue(self, value: Enum):
        index = self.decider.findData(value)
        if index != -1:
            self.decider.setCurrentIndex(index)

class QStateChange(QWidget):
    inputChanged = pyqtSignal(StateChange)

    def __init__(self, txt:str = "State change", mats:list[Material] = []):
        super().__init__()

        self.target_material_name = MaterialSelector("Target material name: ", mats=mats)