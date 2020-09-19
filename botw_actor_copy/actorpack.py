import json
import oead
from pathlib import Path

from bcml import util as bcmlutil
from . import util


icon_name: str
bfres_name: str


def copy_actor(directory: Path, basics: dict, force: dict):
    users: dict = {
        "DamageParamUser": False,
        "DropTableUser": False,
        "GParamUser": False,
        "LifeConditionUser": False,
        "ModelUser": False,
        "PhysicsUser": False,
        "RecipeUser": False,
        "ShopDataUser": False,
        "UMiiUser": False,
    }
    is_armor: bool
    new_folder: str = basics["target_actor"]
    if "Armor" in basics["target_actor"]:
        is_armor = True
        num_skips: int = -2 if "_B" in new_folder else -1
        new_folder = "_".join(new_folder.split("_")[:num_skips])
    vanilla_params = json.loads(Path(EXEC_DIR / "data" / "vanilla_params.json").read_text())

    actorpack: oead.Sarc = oead.Sarc(
        bcmlutil.get_game_file(f"Actor/Pack/{basics['source_actor']}.sbactorpack").read_bytes()
    )
    actorpack_new: oead.SarcWriter = oead.SarcWriter.from_sarc(actorpack)

    old_name: str = f"Actor/ActorLink/{basics['source_actor']}.bxml"
    new_name: str = f"Actor/ActorLink/{basics['target_actor']}.bxml"
    data: bytes = actorpack_new.files[old_name]
    pio: oead.aamp.ParameterIO = oead.aamp.ParameterIO.from_binary(data)
    for user in users.keys():
        if pio.objects["LinkTarget"].params[user] == basics["source_actor"]:
            users[user] = True
            pio.objects["LinkTarget"].params[user] = basics["target_actor"]
    if not users["ModelUser"]:
        modeluser: str = str(pio.objects["LinkTarget"].params["ModelUser"])
    actorpack_new.files[new_name] = oead.aamp.ParameterIO.to_binary(pio)
    actorpack_new.files.pop(old_name)

    if users["DamageParamUser"] or force["DamageParamUser"]:
        if users["DamageParamUser"]:
            old_name = f"Actor/DamageParam/{basics['source_actor']}.bdmgparam"
        else:
            param = vanilla_params[basics["source_actor"]]["DamageParamUser"]
            old_name = f"Actor/DamageParam/{param}.bdmgparam"
        if old_name in actorpack_new.files:
            new_name = f"Actor/DamageParam/{basics['target_actor']}.bdmgparam"
            actorpack_new.files[new_name] = actorpack_new.files[old_name]
            actorpack_new.files.pop(old_name)

    if users["DropTableUser"] or force["DropTableUser"]:
        if users["DropTableUser"]:
            old_name = f"Actor/DamageParam/{basics['source_actor']}.bdrop"
        else:
            param = vanilla_params[basics["source_actor"]]["DropTableUser"]
            old_name = f"Actor/DamageParam/{param}.bdrop"
        if old_name in actorpack_new.files:
            new_name = f"Actor/DamageParam/{basics['target_actor']}.bdrop"
            actorpack_new.files[new_name] = actorpack_new.files[old_name]
            actorpack_new.files.pop(old_name)

    if users["GParamUser"] or force["GParamUser"]:
        if users["GParamUser"]:
            old_name = f"Actor/GeneralParamList/{basics['source_actor']}.bgparamlist"
        else:
            param = vanilla_params[basics["source_actor"]]["GParamUser"]
            old_name = f"Actor/GeneralParamList/{param}.bgparamlist"
        if old_name in actorpack_new.files:
            new_name = f"Actor/GeneralParamList/{basics['target_actor']}.bgparamlist"
            data = actorpack_new.files[old_name]
            pio = oead.aamp.ParameterIO.from_binary(data)
            if is_armor:
                pio.objects["Armor"].params["NextRankName"] = oead.FixedSafeString64("")
            try:
                icon_name = str(pio.objects["Item"].params["UseIconActorName"])
            except KeyError:
                pass
            actorpack_new.files[new_name] = oead.aamp.ParameterIO.to_binary(pio)
            actorpack_new.files.pop(old_name)

    if users["LifeConditionUser"] or force["LifeConditionUser"]:
        if users["LifeConditionUser"]:
            old_name = f"Actor/LifeCondition/{basics['source_actor']}.blifecondition"
        else:
            param = vanilla_params[basics["source_actor"]]["LifeConditionUser"]
            old_name = f"Actor/LifeCondition/{param}.blifecondition"
        if old_name in actorpack_new.files:
            new_name = f"Actor/LifeCondition/{basics['target_actor']}.blifecondition"
            actorpack_new.files[new_name] = actorpack_new.files[old_name]
            actorpack_new.files.pop(old_name)

    if users["ModelUser"] or force["ModelUser"]:
        if users["ModelUser"]:
            old_name = f"Actor/ModelList/{basics['source_actor']}.bmodellist"
        else:
            param = vanilla_params[basics["source_actor"]]["ModelUser"]
            old_name = f"Actor/ModelList/{param}.bmodellist"
        if old_name in actorpack_new.files:
            new_name = f"Actor/ModelList/{basics['target_actor']}.bmodellist"
            data = actorpack_new.files[old_name]
            pio = oead.aamp.ParameterIO.from_binary(data)
            modeldata = pio.lists["ModelData"].lists["ModelData_0"]
            bfres_name = str(modeldata.objects["Base"].params["Folder"])
            modeldata.objects["Base"].params["Folder"] = oead.FixedSafeString64(new_folder)
            modeldata.lists["Unit"].objects["Unit_0"].params["UnitName"] = oead.FixedSafeString64(
                basics["target_actor"]
            )
            actorpack_new.files[new_name] = oead.aamp.ParameterIO.to_binary(pio)
            actorpack_new.files.pop(old_name)
    if bfres_name == "" and not modeluser == "":
        old_name = f"Actor/ModelList/{modeluser}.bmodellist"
        data = actorpack_new.files[old_name]
        pio = oead.aamp.ParameterIO.from_binary(data)
        modeldata = pio.lists["ModelData"].lists["ModelData_0"]
        bfres_name = str(modeldata.objects["Base"].params["Folder"])

    if users["PhysicsUser"] or force["PhysicsUser"]:
        if users["PhysicsUser"]:
            old_name = f"Actor/Physics/{basics['source_actor']}.bphysics"
        else:
            param = vanilla_params[basics["source_actor"]]["PhysicsUser"]
            old_name = f"Actor/Physics/{param}.bphysics"
        if old_name in actorpack_new.files:
            new_name = f"Actor/Physics/{basics['target_actor']}.bphysics"
            data = actorpack_new.files[old_name]
            pio = oead.aamp.ParameterIO.from_binary(data)
            chpath_new: str
            sbpath_new: str
            try:
                clothheader = pio.lists["ParamSet"].lists["Cloth"].objects["ClothHeader"]
                chpath: str = str(clothheader.params["cloth_setup_file_path"])
                chpath_new = f"{new_folder}/{basics['target_actor']}.hkcl"
                clothheader.params["cloth_setup_file_path"] = oead.FixedSafeString256(chpath_new)

                supportbone = pio.lists["ParamSet"].objects["SupportBone"]
                sbpath: str = str(supportbone.params["support_bone_setup_file_path"])
                sbpath_new = f"{new_folder}/{basics['target_actor']}.bphyssb"
                supportbone.params["support_bone_setup_file_path"] = oead.FixedSafeString256(
                    sbpath_new
                )
            except KeyError:
                pass
            actorpack_new.files[new_name] = oead.aamp.ParameterIO.to_binary(pio)
            actorpack_new.files.pop(old_name)

            if not chpath_new == "":
                old_name = f"Physics/Cloth/{chpath}"
                new_name = f"Physics/Cloth/{chpath_new}"
                actorpack_new.files[new_name] = actorpack_new.files[old_name]
                actorpack_new.files.pop(old_name)

            if not sbpath_new == "":
                old_name = f"Physics/SupportBone/{chpath}"
                new_name = f"Physics/SupportBone/{chpath_new}"
                actorpack_new.files[new_name] = actorpack_new.files[old_name]
                actorpack_new.files.pop(old_name)

    if users["RecipeUser"] or force["RecipeUser"]:
        if users["RecipeUser"]:
            old_name = f"Actor/Recipe/{basics['source_actor']}.brecipe"
        else:
            param = vanilla_params[basics["source_actor"]]["RecipeUser"]
            old_name = f"Actor/Recipe/{param}.brecipe"
        if old_name in actorpack_new.files:
            new_name = f"Actor/Recipe/{basics['target_actor']}.brecipe"
            actorpack_new.files[new_name] = actorpack_new.files[old_name]
            actorpack_new.files.pop(old_name)

    if users["ShopDataUser"] or force["ShopDataUser"]:
        if users["ShopDataUser"]:
            old_name = f"Actor/ShopData/{basics['source_actor']}.bshop"
        else:
            param = vanilla_params[basics["source_actor"]]["ShopDataUser"]
            old_name = f"Actor/ShopData/{param}.bshop"
        if old_name in actorpack_new.files:
            new_name = f"Actor/ShopData/{basics['target_actor']}.bshop"
            actorpack_new.files[new_name] = actorpack_new.files[old_name]
            actorpack_new.files.pop(old_name)

    if users["UMiiUser"] or force["UMiiUser"]:
        if users["UMiiUser"]:
            old_name = f"Actor/UMii/{basics['source_actor']}.bumii"
        else:
            param = vanilla_params[basics["source_actor"]]["UMiiUser"]
            old_name = f"Actor/UMii/{param}.bumii"
        if old_name in actorpack_new.files:
            new_name = f"Actor/UMii/{basics['target_actor']}.bumii"
            actorpack_new.files[new_name] = actorpack_new.files[old_name]
            actorpack_new.files.pop(old_name)

    endianness = oead.Endianness.Big if basics["bigendian"] else oead.Endianness.Little
    actorpack_new.set_endianness(endianness)
    Path(
        directory / "content" / "Actor" / "Pack" / f"{basics['target_actor']}.sbactorpack"
    ).write_bytes(oead.yaz0.compress(actorpack_new.write()[1]))
