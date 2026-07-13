import fetcher
from misc import *
from material import Material
from dataclasses import asdict
from json import dumps
from enum import Enum

material_fetcher = fetcher.MaterialFetcher()
reaction_fetcher = fetcher.ReactionFetcher()

materials = []
reactions = []



def fetch_data():
    materials = material_fetcher.fetch()
    print(materials[255])
    reactions = reaction_fetcher.fetch(materials)


fetch_data()

def json_default(o):
    if isinstance(o, Material):
        return o.toJSON()
    if isinstance(o, Enum):
        return o.toJSON() if hasattr(o, "toJSON") else o.name
    return o.__dict__

granite = Material(Name = "Granite", Color = Color(0.5, 0.5, 0.5, 1.0), Description = "A common type of felsic intrusive igneous rock that is granular and phaneritic in texture.", State = State.SOLID, ProtonNumber = 14, NeutronNumber = 14, HealthChange = 100, AcidDamage = 0, Weight = 2.75, Density = 2.75, Hardness = 6.5, Bounciness = 0.1, ActorFriction = 0.8, OverrideActorCollision = True, IsInteractable = True, IsBurning = False, IgnoreFogOfWar = False, CanBeCutByPlasma = False, Direction = Direction.UP, IsForeground = True, IsCarryingSignal = False, IsUnstable = False)
composition = Composition(Elements=[{"Item1": granite, "Item2": 1}])
mat = Material(Fire = Fire(granite, [granite], 1.0, 15.0, Color(0.9999992, 0.6666673, 0.0, 1.0)), Composition=composition)

#print(dumps(mat.toJSON(), default=json_default, indent=4))

#print(dumps(materials[0].toJSON(), default=json_default, indent=4))