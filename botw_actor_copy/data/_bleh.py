import json
import oead
from pathlib import Path

d: dict = {}
k: list = [
    # "ActorNameJpn",
    # "AIProgramUser",
    # "AIScheduleUser",
    # "ASUser",
    # "AttentionUser",
    # "AwarenessUser",
    # "BoneControlUser",
    # "ActorCaptureUser",
    # "ChemicalUser",
    "DamageParamUser",
    "DropTableUser",
    "ElinkUser",
    "GParamUser",
    "LifeConditionUser",
    # "LODUser",
    "ModelUser",
    "PhysicsUser",
    # "ProfileUser",
    # "RgBlendWeightUser",
    # "RgConfigListUser",
    "RecipeUser",
    "ShopDataUser",
    "SlinkUser",
    "UMiiUser",
    "XlinkUser",
    # "AnimationInfo",
]

for sarc in Path.cwd().glob("*.sbactorpack"):
    n = sarc.stem
    a = oead.Sarc(oead.yaz0.decompress(sarc.read_bytes()))
    for f in a.get_files():
        if "bxml" in f.name:
            data = f.data
            break
    io = oead.aamp.ParameterIO.from_binary(data)
    for key in k:
        v = str(io.objects["LinkTarget"].params[key])
        if n == v:
            continue
        elif n in v or v in n:
            if len(v.split("_")) > 1:
                if not n in d:
                    d[n] = {}
                d[n][key] = v

Path("_output.txt").touch(exist_ok=True)
Path("_output.txt").write_text(json.dumps(d, indent=4, sort_keys=True))
