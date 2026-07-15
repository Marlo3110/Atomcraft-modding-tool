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
    QListView,
    QPushButton,
    QColorDialog,
    QListWidget,
    QListWidgetItem,
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

    def __init__(self, txt:str = "", mats:list[Material] = [], normal_value:Material|str = "", label:bool = True):
        
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
        if label:
            layout.addWidget(self.label)
        layout.addWidget(self.decider)
        self.setLayout(layout)
        self.setContentsMargins(QMargins(1, 1, 1, 1))

    def __input_changed__(self, txt:str):
        mat = find_material_in_materials(txt, mats=self.mats)
        if mat != None:
            self.inputChanged.emit(mat)

# add list where you can add materials
class MaterialList(QWidget):
    inputChanged = pyqtSignal(bool)  # emitted whenever the list of materials changes

    def __init__(self, text: str = "", mats: list[Material] = []):
        super().__init__()

        self.mats = mats
        self.material_widgets: list[MaterialSelector] = []  # instance attr, not class attr

        self.add_button = QPushButton("Add")
        self.remove_button = QPushButton("Remove")
        self.label = QLabel(text=text)

        self.title_bar_layout = QHBoxLayout()
        self.title_bar_layout.addWidget(self.label)
        self.title_bar_layout.addWidget(self.add_button)
        self.title_bar_layout.addWidget(self.remove_button)

        self.title_bar = QWidget()
        self.title_bar.setLayout(self.title_bar_layout)

        self.list = QListWidget()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.title_bar)
        self.layout.addWidget(self.list)

        self.setLayout(self.layout)

        self.add_button.clicked.connect(self.__new_material__)
        self.remove_button.clicked.connect(self.__remove_material__)

    def __new_material__(self):
        selector = MaterialSelector(mats=self.mats, label=False)
        selector.inputChanged.connect(lambda _: self.inputChanged.emit(True))

        item = QListWidgetItem(self.list)
        item.setSizeHint(selector.sizeHint())

        self.list.addItem(item)
        self.list.setItemWidget(item, selector)

        self.material_widgets.append(selector)
        self.inputChanged.emit(True)

    def __remove_material__(self):
        if len(self.material_widgets) == 0:
            return

        row = self.list.currentRow()
        if row == -1:
            row = len(self.material_widgets) - 1

        self.material_widgets.pop(row)
        self.list.takeItem(row)

        self.inputChanged.emit(True)

    def get_materials(self) -> list[Material]:
        """Return the Material objects currently selected in the list."""
        materials = []
        for selector in self.material_widgets:
            text = selector.decider.currentText()
            mat = find_material_in_materials(text, mats=self.mats)
            if mat is not None:
                materials.append(mat)
        return materials



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
        self.temperature = QIntegerInputLabel("Temperature: ")
        self.amount = QIntegerInputLabel("Amount: ")
        self.probability = QIntegerInputLabel("Probability: ")

        self.container = QCollapsibleSection(txt)
        self.container.addWidget(self.target_material_name)
        self.container.addWidget(self.temperature)
        self.container.addWidget(self.amount)
        self.container.addWidget(self.probability)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.container)
        self.setLayout(self.layout)

class ColorButton(QPushButton):
    colorChanged = pyqtSignal(QColor)

    def __init__(self, color=QColor("white")):
        super().__init__()

        self._default = QColor(color)
        self._color = QColor(color)

        self.setFixedSize(40, 24)
        self.update_style()

    def update_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background: {self._color.name()};
                border: 1px solid gray;
                border-radius: 4px;
            }}
        """)

    def setColor(self, color):
        self._color = QColor(color)
        self.update_style()
        self.colorChanged.emit(self._color)

    def color(self):
        return QColor(self._color)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            color = QColorDialog.getColor(self._color, self)
            if color.isValid():
                self.setColor(color)

        elif event.button() == Qt.MouseButton.RightButton:
            self.setColor(self._default)

        super().mousePressEvent(event)

class QColorSelector(QWidget):
    inputChanged = pyqtSignal(QColor)

    def __init__(self, txt="", color=QColor("white"), label:bool = True):
        super().__init__()

        self.label = QLabel(txt)
        self.button = ColorButton(color)

        self.button.colorChanged.connect(self.inputChanged)

        layout = QHBoxLayout(self)
        if label:
            layout.addWidget(self.label)
        layout.addWidget(self.button)
        layout.addStretch()

    def value(self):
        return self.button.color()

    def setValue(self, color):
        self.button.setColor(color)