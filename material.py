from __future__ import annotations

from dataclasses import dataclass, field, asdict
from misc import *


@dataclass
class Material:
    Name: str = "test"
    Color: Color = field(default_factory=lambda: Color(0.5, 0.5, 0.5, 1.0))
    LocIdName: str = ""
    Description: str = "test material"
    State: State = State.SOLID

    ProtonNumber: int = 0
    NeutronNumber: int = 0

    TurnsIntoFromAlphaParticleImpact: Material | None = None
    TurnsIntoFromProtonImpact: Material | None = None
    TurnsIntoFromNeutronImpact: Material | None = None

    DecaySettings: DecaySettings | None = None

    PickUpInto: Material | None = None
    MinesInto: Material | None = None
    BuildsInto: Material | None = None

    TurnsOnInto: Material | None = None
    TurnsOffInto: Material | None = None

    RotatesRightInto: Material | None = None
    RotatesLeftInto: Material | None = None
    GrowsInto: Material | None = None

    WireIndex: int | None = None

    HealthChange: float = 0
    AcidDamage: float = 0

    Weight: float = 0
    Density: float = 0
    Hardness: float = 0

    Composition: Composition | None = None
    DissolvesInto: Material | None = None

    Bounciness: float = 0
    ActorFriction: float | None = None
    OverrideActorCollision: bool | None = None

    IsInteractable: bool = False
    IsBurning: bool = False
    IgnoreFogOfWar: bool = False
    CanBeCutByPlasma: bool = False

    Direction: Direction = Direction.UP
    IsForeground: bool = True

    IsCarryingSignal: bool = False
    IsUnstable: bool = False

    RequiredSupportDirection: Direction | None = None

    DoNotBlockLaser: bool = False
    IsBuilt: bool = False
    IsMechanical: bool = False

    CanPickUpStatic: bool = False
    IsOn: bool = False

    WireSignalState: WireSignalState | None = None

    DoNotShowInGuide: bool = False
    IsFoodIngredient: bool = False

    MaterialAudioTypeId: int = 0

    GrowthRules: GrowthRules | None = None
    GrowthMedium: Material | None = None

    Friction: float = 0
    Viscosity: float = 0

    DefaultTemperature: float | None = None
    ThermalConductivity: float | None = None
    ConductanceDivisor: float | None = None

    ColorDelegate: Material | None = None

    Alpha: float = 0.0

    LightColor: Color | None = None
    LightRange: int | None = None

    Condensation: StateChange | None = None
    Evaporation: StateChange | None = None

    Fire: Fire | None = None

    ExplosionRadius: int = 0

    DropRates: DropRates | None = None

    Ignition: Ignition | None = None

    def toJSON(self) -> dict:
        def mat_name(m):
            return m.Name if isinstance(m, Material) else m

        dict_ = self.__dict__

        dict_["State"] = self.State.value
        dict_["Direction"] = self.Direction.value
        dict_["RequiredSupportDirection"] = self.RequiredSupportDirection.value if self.RequiredSupportDirection is not None else None
        dict_["WireSignalState"] = self.WireSignalState.value if self.WireSignalState is not None else None

        dict_["ColorDelegate"] = mat_name(self.ColorDelegate)
        dict_["TurnsIntoFromAlphaParticleImpact"] = mat_name(self.TurnsIntoFromAlphaParticleImpact)
        dict_["TurnsIntoFromProtonImpact"] = mat_name(self.TurnsIntoFromProtonImpact)
        dict_["TurnsIntoFromNeutronImpact"] = mat_name(self.TurnsIntoFromNeutronImpact)
        dict_["PickUpInto"] = mat_name(self.PickUpInto)
        dict_["MinesInto"] = mat_name(self.MinesInto)
        dict_["BuildsInto"] = mat_name(self.BuildsInto)
        dict_["TurnsOnInto"] = mat_name(self.TurnsOnInto)
        dict_["TurnsOffInto"] = mat_name(self.TurnsOffInto)
        dict_["RotatesRightInto"] = mat_name(self.RotatesRightInto)
        dict_["RotatesLeftInto"] = mat_name(self.RotatesLeftInto)
        dict_["GrowsInto"] = mat_name(self.GrowsInto)
        dict_["DissolvesInto"] = mat_name(self.DissolvesInto)
        dict_["GrowthMedium"] = mat_name(self.GrowthMedium)

        dict_["LightColor"] = self.LightColor.toJSON() if self.LightColor is not None else None
        dict_["Color"] = self.Color.toJSON() if self.Color is not None else None
        dict_["Fire"] = self.Fire.toJSON() if self.Fire is not None else None
        dict_["Composition"] = self.Composition.toJSON() if self.Composition is not None else None
        dict_["DropRates"] = self.DropRates.toJSON() if self.DropRates is not None else None
        dict_["DecaySettings"] = self.DecaySettings.toJSON() if self.DecaySettings is not None else None
        dict_["GrowthRules"] = self.GrowthRules.toJSON() if self.GrowthRules is not None else None
        dict_["Condensation"] = self.Condensation.toJSON() if self.Condensation is not None else None
        dict_["Evaporation"] = self.Evaporation.toJSON() if self.Evaporation is not None else None
        dict_["Ignition"] = self.Ignition.toJSON() if self.Ignition is not None else None

        return dict_
    

    @classmethod
    def fromJSON(cls, data: dict) -> Material:
        def resolveMaterial(string:str) -> Material | None:
            if string == None:
                return None
            else:
                return Material(Name=string)
        return cls(
            Name=data["Name"],
            Color=Color.fromJSON(data["Color"]),
            LocIdName=data["LocIdName"],
            Description=data["Description"],
            State=State(data["State"]) if data["State"] is not None else None,

            ProtonNumber=data["ProtonNumber"],
            NeutronNumber=data["NeutronNumber"],

            # Material-reference fields: kept as raw name strings here.
            # Resolve to real Material objects in a second pass after
            # every material in the set has been loaded.
            TurnsIntoFromAlphaParticleImpact=data["TurnsIntoFromAlphaParticleImpact"],
            TurnsIntoFromProtonImpact=data["TurnsIntoFromProtonImpact"],
            TurnsIntoFromNeutronImpact=data["TurnsIntoFromNeutronImpact"],

            DecaySettings=DecaySettings.fromJSON(data["DecaySettings"]),

            PickUpInto=data["PickUpInto"], # turns into ... from ...
            MinesInto=data["MinesInto"],# turns into ... from ...
            BuildsInto=data["BuildsInto"],# turns into ... from ...

            TurnsOnInto=data["TurnsOnInto"],# turns into ... from ...
            TurnsOffInto=data["TurnsOffInto"],# turns into ... from ...

            RotatesRightInto=data["RotatesRightInto"],# turns into ... from ...
            RotatesLeftInto=data["RotatesLeftInto"],# turns into ... from ...
            GrowsInto=data["GrowsInto"], # plant

            WireIndex=data["WireIndex"], # electronics

            HealthChange=data["HealthChange"], # player interaction
            AcidDamage=data["AcidDamage"], # player interaction

            Weight=data["Weight"], # physics
            Density=data["Density"],# physics
            Hardness=data["Hardness"],# physics

            Composition=Composition.fromJSON(data["Composition"]), # chemistry
            DissolvesInto=data["DissolvesInto"], # chemistry

            Bounciness=data["Bounciness"], # physics
            ActorFriction=data["ActorFriction"], # physics
            OverrideActorCollision=data["OverrideActorCollision"], # physics

            IsInteractable=data["IsInteractable"], # player interaction
            IsBurning=data["IsBurning"], # physics/thermodynamics
            IgnoreFogOfWar=data["IgnoreFogOfWar"], # visual
            CanBeCutByPlasma=data["CanBeCutByPlasma"], # misc

            Direction=Direction(data["Direction"]) if data["Direction"] is not None else None, # physics
            IsForeground=data["IsForeground"], # visual

            IsCarryingSignal=data["IsCarryingSignal"], # electronic
            IsUnstable=data["IsUnstable"], # radioactivity

            RequiredSupportDirection=Direction(data["RequiredSupportDirection"]) if data["RequiredSupportDirection"] is not None else None, # physics

            DoNotBlockLaser=data["DoNotBlockLaser"], # misc
            IsBuilt=data["IsBuilt"], # misc
            IsMechanical=data["IsMechanical"], # physics

            CanPickUpStatic=data["CanPickUpStatic"], # player interaction
            IsOn=data["IsOn"], # electronics

            WireSignalState=WireSignalState(data["WireSignalState"]) if data["WireSignalState"] is not None else None, # electronics

            DoNotShowInGuide=data["DoNotShowInGuide"], # misc
            IsFoodIngredient=data["IsFoodIngredient"], # plant

            MaterialAudioTypeId=data["MaterialAudioTypeId"], # misc

            GrowthRules=GrowthRules.fromJSON(data["GrowthRules"]), # plant
            GrowthMedium=data["GrowthMedium"], # plant

            Friction=data["Friction"], # physics
            Viscosity=data["Viscosity"], # physics

            DefaultTemperature=data["DefaultTemperature"], #  physics/thermodynamics
            ThermalConductivity=data["ThermalConductivity"], #  physics/thermodynamics
            ConductanceDivisor=data["ConductanceDivisor"], #  physics/thermodynamics

            ColorDelegate=data["ColorDelegate"], # visual

            Alpha=data["Alpha"], # visual

            LightColor=Color.fromJSON(data["LightColor"]), # visual
            LightRange=data["LightRange"], # visual

            Condensation=StateChange.fromJSON(data["Condensation"]), #  physics/thermodynamics
            Evaporation=StateChange.fromJSON(data["Evaporation"]), #  physics/thermodynamics

            Fire=Fire.fromJSON(data["Fire"]), # visual

            ExplosionRadius=data["ExplosionRadius"], # physics
            
            DropRates=DropRates.fromJSON(data["DropRates"]), # misc

            Ignition=Ignition.fromJSON(data.get("Ignition")), # combustion/ignition
        )