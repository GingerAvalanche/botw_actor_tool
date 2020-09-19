import json
import oead
from pathlib import Path

from bcml import util as bcmlutil
from . import util


icon_name: str


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

    old_bxml_name = f"Actor/ActorLink/{basics['source_actor']}.bxml"
    bxml_name = f"Actor/ActorLink/{basics['target_actor']}.bxml"
    bxml_data = actorpack_new.files[old_bxml_name]
    bxml_io: oead.aamp.ParameterIO = oead.aamp.ParameterIO.from_binary(bxml_data)
    for user in users.keys():
        if bxml_io.objects["LinkTarget"].params[user] == basics["source_actor"]:
            users[user] = True
            bxml_io.objects["LinkTarget"].params[user] = basics["target_actor"]
    actorpack_new.files[bxml_name] = oead.aamp.ParameterIO.to_binary(bxml_io)
    actorpack_new.files.pop(old_bxml_name)

    if users["DamageParamUser"] or force["DamageParamUser"]:
        if users["DamageParamUser"]:
            old_bdp_name = f"Actor/DamageParam/{basics['source_actor']}.bdmgparam"
        else:
            param = vanilla_params[basics["source_actor"]]["DamageParamUser"]
            old_bdp_name = f"Actor/DamageParam/{param}.bdmgparam"
        bdp_name = f"Actor/DamageParam/{basics['target_actor']}.bdmgparam"
        actorpack_new.files[bdp_name] = actorpack_new.files[old_bdp_name]
        actorpack_new.files.pop(old_bdp_name)

    if users["DropTableUser"] or force["DropTableUser"]:
        if users["DropTableUser"]:
            old_bd_name = f"Actor/DamageParam/{basics['source_actor']}.bdrop"
        else:
            param = vanilla_params[basics["source_actor"]]["DropTableUser"]
            old_bd_name = f"Actor/DamageParam/{param}.bdrop"
        bd_name = f"Actor/DamageParam/{basics['target_actor']}.bdrop"
        actorpack_new.files[bd_name] = actorpack_new.files[old_bd_name]
        actorpack_new.files.pop(old_bd_name)

    if users["GParamUser"] or force["GParamUser"]:
        if users["GParamUser"]:
            old_bgpl_name = f"Actor/GeneralParamList/{basics['source_actor']}.bgparamlist"
        else:
            param = vanilla_params[basics["source_actor"]]["GParamUser"]
            old_bgpl_name = f"Actor/GeneralParamList/{param}.bgparamlist"
        bgpl_name = f"Actor/GeneralParamList/{basics['target_actor']}.bgparamlist"
        bgpl_data = actorpack_new.files[old_bgpl_name]
        bgpl_io: oead.aamp.ParameterIO = oead.aamp.ParameterIO.from_binary(bgpl_data)
        if is_armor:
            bgpl_io.objects["Armor"].params["NextRankName"] = oead.FixedSafeString64("")
        try:
            icon_name = str(bgpl_io.objects["Item"].params["UseIconActorName"])
        except KeyError:
            pass
        actorpack_new.files[bgpl_name] = oead.aamp.ParameterIO.to_binary(bgpl_io)
        actorpack_new.files.pop(old_bgpl_name)

    if users["LifeConditionUser"] or force["LifeConditionUser"]:
        if users["LifeConditionUser"]:
            old_blc_name = f"Actor/LifeCondition/{basics['source_actor']}.blifecondition"
        else:
            param = vanilla_params[basics["source_actor"]]["LifeConditionUser"]
            old_blc_name = f"Actor/LifeCondition/{param}.blifecondition"
        blc_name = f"Actor/LifeCondition/{basics['target_actor']}.blifecondition"
        actorpack_new.files[blc_name] = actorpack_new.files[old_blc_name]
        actorpack_new.files.pop(old_blc_name)

    if users["ModelUser"] or force["ModelUser"]:
        if users["ModelUser"]:
            old_bml_name = f"Actor/ModelList/{basics['source_actor']}.bmodellist"
        else:
            param = vanilla_params[basics["source_actor"]]["ModelUser"]
            old_bml_name = f"Actor/ModelList/{param}.bmodellist"
        bml_name = f"Actor/ModelList/{basics['target_actor']}.bmodellist"
        bml_data = actorpack_new.files[old_bml_name]
        bml_io: oead.aamp.ParameterIO = oead.aamp.ParameterIO.from_binary(bml_data)
        modeldata = bml_io.lists["ModelData"].lists["ModelData_0"]
        modeldata.objects["Base"].params["Folder"] = oead.FixedSafeString64(new_folder)
        modeldata.lists["Unit"].objects["Unit_0"].params["UnitName"] = oead.FixedSafeString64(
            basics["target_actor"]
        )
        actorpack_new.files[bml_name] = oead.aamp.ParameterIO.to_binary(bml_io)
        actorpack_new.files.pop(old_bml_name)

    if users["PhysicsUser"] or force["PhysicsUser"]:
        if users["PhysicsUser"]:
            old_bp_name = f"Actor/Physics/{basics['source_actor']}.bphysics"
        else:
            param = vanilla_params[basics["source_actor"]]["PhysicsUser"]
            old_bp_name = f"Actor/Physics/{param}.bphysics"
        bp_name = f"Actor/Physics/{basics['target_actor']}.bphysics"
        bp_data = actorpack_new.files[old_bp_name]
        bp_io: oead.aamp.ParameterIO = oead.aamp.ParameterIO.from_binary(bp_data)
        chpath_new: str
        sbpath_new: str
        try:
            clothheader = bp_io.lists["ParamSet"].lists["Cloth"].objects["ClothHeader"]
            chpath: str = str(clothheader.params["cloth_setup_file_path"])
            chpath_new = f"{new_folder}/{basics['target_actor']}.hkcl"
            clothheader.params["cloth_setup_file_path"] = oead.FixedSafeString256(chpath_new)

            supportbone = bp_io.lists["ParamSet"].objects["SupportBone"]
            sbpath: str = str(supportbone.params["support_bone_setup_file_path"])
            sbpath_new = f"{new_folder}/{basics['target_actor']}.bphyssb"
            supportbone.params["support_bone_setup_file_path"] = oead.FixedSafeString256(
                sbpath_new
            )
        except KeyError:
            pass
        if not chpath_new == "":
            old_hkcl_name = f"Physics/Cloth/{chpath}"
            hkcl_name = f"Physics/Cloth/{chpath_new}"
            actorpack_new.files[hkcl_name] = actorpack_new.files[old_hkcl_name]
            actorpack_new.files.pop(old_hkcl_name)
        if not sbpath_new == "":
            old_bpsb_name = f"Physics/SupportBone/{chpath}"
            bpsb_name = f"Physics/SupportBone/{chpath_new}"
            actorpack_new.files[bpsb_name] = actorpack_new.files[old_bpsb_name]
            actorpack_new.files.pop(old_bpsb_name)
        actorpack_new.files[bp_name] = oead.aamp.ParameterIO.to_binary(bp_io)
        actorpack_new.files.pop(old_bp_name)

    if users["RecipeUser"] or force["RecipeUser"]:
        if users["RecipeUser"]:
            old_br_name = f"Actor/Recipe/{basics['source_actor']}.brecipe"
        else:
            param = vanilla_params[basics["source_actor"]]["RecipeUser"]
            old_br_name = f"Actor/Recipe/{param}.brecipe"
        br_name = f"Actor/Recipe/{basics['target_actor']}.brecipe"
        actorpack_new.files[br_name] = actorpack_new.files[old_br_name]
        actorpack_new.files.pop(old_br_name)

    if users["ShopDataUser"] or force["ShopDataUser"]:
        if users["ShopDataUser"]:
            old_blc_name = f"Actor/ShopData/{basics['source_actor']}.bshop"
        else:
            param = vanilla_params[basics["source_actor"]]["ShopDataUser"]
            old_blc_name = f"Actor/ShopData/{param}.bshop"
        blc_name = f"Actor/ShopData/{basics['target_actor']}.bshop"
        actorpack_new.files[blc_name] = actorpack_new.files[old_blc_name]
        actorpack_new.files.pop(old_blc_name)

    if users["UMiiUser"] or force["UMiiUser"]:
        if users["UMiiUser"]:
            old_blc_name = f"Actor/UMii/{basics['source_actor']}.bumii"
        else:
            param = vanilla_params[basics["source_actor"]]["UMiiUser"]
            old_blc_name = f"Actor/UMii/{param}.bumii"
        blc_name = f"Actor/UMii/{basics['target_actor']}.bumii"
        actorpack_new.files[blc_name] = actorpack_new.files[old_blc_name]
        actorpack_new.files.pop(old_blc_name)

    Path(
        directory / "content" / "Actor" / "Pack" / f"{basics['target_actor']}.sbactorpack"
    ).write_bytes(oead.yaz0.compress(actorpack_new.write()[1]))
