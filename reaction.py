from dataclasses import dataclass
from material import Material

@dataclass
class Reaction:
    Name:str = "test"
    PrimaryInput:Material = None
    Inputs:list[list[Material, int]] = None
    Outputs:list[list[Material, int]] = None
    Catalysts:list[Material] = None
    Electrolysis:bool = False
    Temperature:int = 0
    MaxTemperature:int = 50000
    ChangeInTemperature:int = 0
    Probability:float = 0

    def toJSON(self):
        def mat_name(m):
            return m.Name if isinstance(m, Material) else m
        inputs = {}
        for k,v in self.Inputs.items():
            inputs[k] = v.Amount

        outputs = {}
        for k,v in self.Outputs.items():
            outputs[k] = v.Amount

        catalysts = {}
        for k,v in self.Catalysts.items():
            catalysts[k] = v.Amount

        return {
            "Name": self.Name,
            "PrimaryInput": self.PrimaryInput.Name,
            "Inputs": inputs,
            "Outputs": outputs,
            "catalysts": catalysts,
            "Electrolysis": self.Electrolysis,
            "Temperature": self.Temperature,
            "MaxTemperature": self.MaxTemperature,
            "ChangeInTemperature": self.ChangeInTemperature,
            "Probability": self.Probability
        }

    @classmethod
    def fromJSON(cls, data:dict) -> Reaction:
        return cls(
            Name=data["Name"],
            PrimaryInput=data["PrimaryInput"],
            Inputs=data["Inputs"],
            Outputs=data["Outputs"],
            Catalysts=data["Catalysts"],
            Electrolysis=data["Electrolysis"],
            Temperature=data["Temperature"],
            MaxTemperature=data["MaxTemperature"],
            ChangeInTemperature=data["ChangeInTemperature"],
            Probability=data["Probability"]
        )


