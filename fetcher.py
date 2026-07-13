import json as js
import os
from material import Material
from reaction import Reaction
from misc import *

class MaterialFetcher:
    def __init__(self, userdata_folder:str = "/home/marlo3110/.local/share/Steam/steamapps/compatdata/3649520/pfx/drive_c/users/steamuser/AppData/Roaming/godot/app_userdata/Atomcraft/"):
        self.userdata_folder = userdata_folder
        self.materials_folder = "%s/Materials" % self.userdata_folder

    def fetch(self) -> list[material]:
        def get_material_reference(name:str, mats:list[Material]):
            for i in mats:
                if i.Name == name:
                    return i
            return None
        # iterate through all the files in the materials_folder folder
        materials = []

        alldicts = []
        for file in os.listdir(self.materials_folder):
            if file.endswith(".json"):
                full_filename = "%s/%s" % (self.materials_folder, file)
                with open(full_filename,'r') as fi:
                    dict = js.loads(fi.read())

                alldicts.append(list(dict)[0])

        allmats = []
        for i in alldicts:
            if i["Name"].startswith("Music"):
                pass
            else:
                mat = Material.fromJSON(i)
                allmats.append(mat)
        
        # second parsing pass
        for i in allmats:
            if i.TurnsIntoFromAlphaParticleImpact != None:
                i.TurnsIntoFromAlphaParticleImpact = get_material_reference(i.TurnsIntoFromAlphaParticleImpact, allmats)
            if i.TurnsIntoFromProtonImpact != None:
                i.TurnsIntoFromProtonImpact = get_material_reference(i.TurnsIntoFromProtonImpact, allmats)
            if i.TurnsIntoFromNeutronImpact != None:
                i.TurnsIntoFromNeutronImpact = get_material_reference(i.TurnsIntoFromNeutronImpact, allmats)
            if i.DecaySettings != None:
                if i.DecaySettings.MaterialName != None:
                    i.DecaySettings.MaterialName = get_material_reference(i.DecaySettings.MaterialName, allmats)
                if i.DecaySettings.MaterialName2 != None:
                    i.DecaySettings.MaterialName2 = get_material_reference(i.DecaySettings.MaterialName2, allmats)
            if i.PickUpInto != None:
                i.PickUpInto = get_material_reference(i.PickUpInto, allmats)
            if i.MinesInto != None:
                i.MinesInto = get_material_reference(i.MinesInto, allmats)
            if i.BuildsInto != None:
                pass
                i.BuildsInto = get_material_reference(i.BuildsInto, allmats)
            if i.TurnsOnInto != None:
                i.TurnsOnInto = get_material_reference(i.TurnsOnInto, allmats)
            if i.TurnsOffInto != None:
                i.TurnsOffInto = get_material_reference(i.TurnsOffInto, allmats)
            if i.RotatesRightInto != None:
                i.RotatesRightInto = get_material_reference(i.RotatesRightInto, allmats)
            if i.RotatesLeftInto != None:
                i.RotatesLeftInto = get_material_reference(i.RotatesLeftInto, allmats)
            if i.GrowsInto != None:
                i.GrowsInto = get_material_reference(i.GrowsInto, allmats)
            if i.Composition != None:
                for j in i.Composition.Elements:
                    if j["Item1"] != None:
                        j["Item1"] = get_material_reference(j["Item1"], allmats)
            if i.DissolvesInto != None:
                i.DissolvesInto = get_material_reference(i.DissolvesInto, allmats)
            if i.GrowthRules != None:
                if i.GrowthRules.GrowthMaterialName != None:
                    i.GrowthRules.GrowthMaterialName = get_material_reference(i.GrowthRules.GrowthMaterialName, allmats)
            if i.ColorDelegate != None:
                i.ColorDelegate = get_material_reference(i.ColorDelegate, allmats)
            if i.Condensation != None:
                if i.Condensation.TargetMaterialName != None:
                    i.Condensation.TargetMaterialName = get_material_reference(i.Condensation.TargetMaterialName, allmats)
            if i.Evaporation != None:
                if i.Evaporation.TargetMaterialName != None:
                    i.Evaporation.TargetMaterialName = get_material_reference(i.Evaporation.TargetMaterialName, allmats)
            if i.Fire != None:
                if i.Fire.ExtinguishTargetMaterialName != None:
                    i.Fire.ExtinguishTargetMaterialName = get_material_reference(i.Fire.ExtinguishTargetMaterialName, allmats)
                if i.Fire.CombustionTargetMaterialNames != None:
                    for j in i.Fire.CombustionTargetMaterialNames:
                        j = get_material_reference(j, allmats)
            if i.DropRates != None:
                for j in i.DropRates.DropRates:
                    if j[0] != None:
                        j[0] = get_material_reference(j[0], allmats)


        return allmats

class ReactionFetcher:
    def __init__(self, userdata_folder:str = "/home/marlo3110/.local/share/Steam/steamapps/compatdata/3649520/pfx/drive_c/users/steamuser/AppData/Roaming/godot/app_userdata/Atomcraft/"):
        self.userdata_folder = userdata_folder
        self.reactions_folder = "%s/Reactions" % self.userdata_folder

    def fetch(self, mats:list[Material]) -> list[Reaction]:
        def get_material_reference(name:str):
            for i in mats:
                if i.Name == name:
                    return i
            return None

        # iterate through all the files in the reactions_folder folder
        reactions = []

        alldicts = []
        for file in os.listdir(self.reactions_folder):
            if file.endswith(".json"):
                full_filename = "%s/%s" % (self.reactions_folder, file)
                with open(full_filename,'r') as fi:
                    dict = js.loads(fi.read())

                alldicts.append(list(dict)[0])
        allreacts = []
        for i in alldicts:
            reaction = Reaction.fromJSON(i)
            allreacts.append(reaction)
        
        # second parsing pass
        for i in allreacts:
            i.PrimaryInput = get_material_reference(i.PrimaryInput)

            inputs = []
            for k, v in i.Inputs.items():
                inputs.append(MaterialAmount(get_material_reference(k), v))

            outputs = []
            for k, v in i.Outputs.items():
                outputs.append(MaterialAmount(get_material_reference(k), v))

            catalysts = []
            for k, v in i.Catalysts.items():
                catalysts.append(MaterialAmount(get_material_reference(k), v))
            
            i.Inputs = inputs
            i.Outputs = outputs
            i.Catalysts = catalysts
        return allreacts