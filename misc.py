from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from material import Material

from enum import Enum
from dataclasses import dataclass
from PyQt6.QtGui import QColor

# Enums

class State(Enum):
    POWDER = 0
    LIQUID = 1
    GAS = 2
    SOLID = 3
    UNDEFINED = 4

class Direction(Enum):
    UP = 0
    RIGHT = 1
    LEFT = 2
    DOWN = 3
    UPRIGHT = 4
    RIGHTDOWN = 5
    LEFTTOP = 6
    DOWNLEFT = 7
    PLANT = 8

class DecayMode(Enum):
    NORMAL = 0  # this is probably wrong, no idea
    NORMALSECOND = 1
    IDK = 2
    DOWN = 3
    UPRIGHT = 4
    RIGHTDOWN = 5
    LEFTTOP = 6
    DOWNLEFT = 7
    

class MediumType(Enum):
    DIRT = 2
    IDK = 4

class WireSignalState(Enum):
    NORMAL = 0  # probably wrong, no idea
    IDK = 1
    WTF = 2
    DUDE = 3


@dataclass
class Color:
    R: float = 0.0
    G: float = 0.0
    B: float = 0.0
    A: float = 1.0

    def toJSON(self):
        return {"R": self.R, "G": self.G, "B": self.B, "A": self.A}

    @classmethod
    def fromJSON(cls, data):
        if data is None:
            return None
        return cls(R=data["R"], G=data["G"], B=data["B"], A=data["A"])

    def toQColor(self) -> QColor:
        return QColor.fromRgbF(self.R, self.G, self.B, self.A)


@dataclass
class Fire:
    ExtinguishTargetMaterialName: Material = None
    CombustionTargetMaterialNames: list[Material] = None
    HeatOutput: float = 0
    PercentChanceToSpread: float = 0
    FlameColor: Color = None

    def toJSON(self):
        return {
            "ExtinguishTargetMaterialName": self.ExtinguishTargetMaterialName.Name if self.ExtinguishTargetMaterialName else None,
            "CombustionTargetMaterialNames": [mat.Name for mat in self.CombustionTargetMaterialNames] if self.CombustionTargetMaterialNames else None,
            "HeatOutput": self.HeatOutput,
            "PercentChanceToSpread": self.PercentChanceToSpread,
            "FlameColor": self.FlameColor.toJSON() if self.FlameColor else None,
        }

    @classmethod
    def fromJSON(cls, data):
        if data is None:
            return None
        return cls(
            ExtinguishTargetMaterialName=data["ExtinguishTargetMaterialName"],  # raw name string, resolved later
            CombustionTargetMaterialNames=data["CombustionTargetMaterialNames"],  # list of name strings, resolved later
            HeatOutput=data["HeatOutput"],
            PercentChanceToSpread=data["PercentChanceToSpread"],
            FlameColor=Color.fromJSON(data["FlameColor"]),
        )


@dataclass
class Composition:
    Elements: list[dict[str, Material, int]] = None

    def toJSON(self):
        return {
            "Elements": [
                {
                    "Item1": element["Item1"].Name if element["Item1"] else None,
                    "Item2": element["Item2"],
                } for element in self.Elements
            ] if self.Elements else None
        }

    @classmethod
    def fromJSON(cls, data):
        if data is None:
            return None
        elements = data.get("Elements")
        return cls(
            Elements=[
                {"Item1": e["Item1"], "Item2": e["Item2"]}  # Item1 stays a raw name string, resolved later
                for e in elements
            ] if elements else None
        )


@dataclass
class DropRates:
    DropRates: list[list[Material, int]] = None

    def toJSON(self):
        return {
            material.Name if hasattr(material, "Name") else material: rate
            for material, rate in self.DropRates
        } if self.DropRates else None

    @classmethod
    def fromJSON(cls, data):
        if data is None:
            return None

        return cls(
            DropRates=[
                [material, rate]
                for material, rate in data.items()
            ]
        )

@dataclass
class DecaySettings:
    Mode: DecayMode = DecayMode.NORMAL
    TickModValue: int = 0
    MaterialName: Material | None = None
    MaterialName2: Material | None = None

    def toJSON(self):
        return {
            "Mode": self.Mode.value if self.Mode is not None else None,
            "TickModValue": self.TickModValue,
            "MaterialName": self.MaterialName.Name if self.MaterialName else None,
            "MaterialName2": self.MaterialName2.Name if self.MaterialName2 else None,
        }

    @classmethod
    def fromJSON(cls, data):
        if data is None:
            return None
        return cls(
            Mode=DecayMode(data["Mode"]) if data["Mode"] is not None else None,
            TickModValue=data["TickModValue"],
            MaterialName=data["MaterialName"],    # raw name string, resolved later
            MaterialName2=data["MaterialName2"],  # raw name string, resolved later
        )


@dataclass
class GrowthRules:
    Direction: Direction = Direction.UP
    MediumType: MediumType = MediumType.DIRT
    GrowthRate: int = 0
    GrowthMaterialName: Material | None = None

    def toJSON(self):
        return {
            "Direction": self.Direction.value if self.Direction is not None else None,
            "MediumType": self.MediumType.value if self.MediumType is not None else None,
            "GrowthRate": self.GrowthRate,
            "GrowthMaterialName": self.GrowthMaterialName.Name if self.GrowthMaterialName else None,
        }

    @classmethod
    def fromJSON(cls, data):
        if data is None:
            return None
        data = data[0]
        return cls(
            Direction=Direction(data["Direction"]) if data["Direction"] is not None else None,
            MediumType=MediumType(data["MediumType"]) if data["MediumType"] is not None else None,
            GrowthRate=data["GrowthRate"],
            GrowthMaterialName=data["GrowthMaterialName"],  # raw name string, resolved later
        )


@dataclass
class StateChange:
    TargetMaterialName: Material | None = None
    Temperature: int = 0
    Amount: int = 0
    Probability: int = 0

    def toJSON(self):
        return {
            "TargetMaterialName": self.TargetMaterialName.Name if self.TargetMaterialName else None,
            "Temperature": self.Temperature,
            "Amount": self.Amount,
            "Probability": self.Probability,
        }

    @classmethod
    def fromJSON(cls, data):
        if data is None:
            return None
        return cls(
            TargetMaterialName=data["TargetMaterialName"],  # raw name string, resolved later
            Temperature=data["Temperature"],
            Amount=data["Amount"],
            Probability=data["Probability"],
        )

@dataclass
class MaterialAmount:
    MaterialName: Material = None
    Amount:int = 0

    def toJSON(self):
        return {
            self.MaterialName.Name: self.Amount
        }

@dataclass
class Ignition:
    TargetMaterialName: Material = None
    Temperature: int = None
    RequiresSpark: bool = False
    Explodes: bool = False

    def toJSON(self):
        return {
            "TargetMaterialName": self.TargetMaterialName.Name if self.TargetMaterialName else None,
            "Temperature": self.Temperature,
            "RequiresSpark": self.RequiresSpark,
            "Explodes": self.Explodes,
        }

    @classmethod
    def fromJSON(cls, data):
        if data is None:
            return None
        return cls(
            TargetMaterialName=data["TargetMaterialName"],  # raw name string, resolved later
            Temperature=data["Temperature"],
            RequiresSpark=data["RequiresSpark"],
            Explodes=data["Explodes"],
        )