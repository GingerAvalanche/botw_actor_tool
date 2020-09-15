import oead
from pathlib import Path

from bcml import util as bcmlutil
from . import util


def copy_actor(directory: Path, source_actor: str, target_actor: str, big_endian: bool):
    if "Armor" in source_actor:

    actorpack: oead.Sarc = oead.Sarc(
        bcmlutil.get_game_file(f"Actor/Pack/{source_actor}.sbactorpack").read_bytes()
    )
    actorpack_new: oead.SarcWriter = oead.SarcWriter.from_sarc(actorpack)

    users: dict = {
        "GParamUser": "",
        "LifeConditionUser": "",
        "ModelUser": "",
        "PhysicsUser": "",
        "RecipeUser": "",
        "ShopDataUser": "",
    }

    bxml: oead.File = actorpack.get_file(f"Actor/ActorLink/{source_actor}.bxml")
    bxml.name = f"Actor/ActorLink/{target_actor}.bxml"
    bxml_io: oead.aamp.ParameterIO = oead.aamp.ParameterIO.from_binary(bxml.data)
    for user in users.keys():
        if bxml_io.objects["LinkTarget"].params[user] == source_actor:
            users[user] = target_actor
            bxml_io.objects["LinkTarget"].params[user] = target_actor

    if not users["GParamUser"] == "":
        bgparamlist: oead.File = actorpack.get_file(
            f"Actor/GeneralParamList/{source_actor}.bgparamlist"
        )
        bgparamlist.name = f"Actor/GeneralParamList/{target_actor}.bgparamlist"

    if not users["LifeConditionUser"] == "":
        blifecondition: oead.File = actorpack.get_file(
            f"Actor/LifeCondition/{source_actor}.blifecondition"
        )
        blifecondition.name = f"Actor/LifeCondition/{target_actor}.blifecondition"

    if not users["ModelUser"] == "":
        bmodellist: oead.File = actorpack.get_file(f"Actor/ModelList/{source_actor}.bmodellist")
        bmodellist.name = f"Actor/ModelList/{target_actor}.bmodellist"

    if not users["PhysicsUser"] == "":
        bphysics: oead.File = actorpack.get_file(f"Actor/Physics/{source_actor}.bphysics")
        bphysics.name = f"Actor/Physics/{target_actor}.bphysics"
        bphysics_io: oead.aamp.ParameterIO = oead.aamp.ParameterIO.from_binary(bphysics.data)
        chpath_new: str
        sbpath_new: str
        try:
            clothheader = bphysics_io.lists["ParamSet"].lists["Cloth"].objects["ClothHeader"]
            chpath: str = str(clothheader.params["cloth_setup_file_path"])
            chpath_new = chpath # convert chpath to chpath_new
            clothheader.params["cloth_setup_file_path"] = oead.FixedSafeString256(chpath_new)

            supportbone = bphysics_io.lists["ParamSet"].objects["SupportBone"]
            sbpath: str = str(supportbone.params["support_bone_setup_file_path"])
            sbpath_new = sbpath
            supportbone.params["support_bone_setup_file_path"] = oead.FixedSafeString256(
                sbpath_new
            )
        except KeyError:
            pass
        if not chpath_new == "":
            hkcl: oead.File = actorpack.get_file(f"Physics/Cloth/{chpath}")
            hkcl.name = f"Physics/Cloth/{chpath_new}"
        if not sbpath_new == "":
            bphyssb: oead.File = actorpack.get_file(f"Physics/SupportBone/{chpath}")
            bphyssb.name = f"Physics/SupportBone/{chpath_new}"

    Path(directory / "content" / "Actor" / "Pack" / f"{target_actor}.sbactorpack").write_bytes(
        bcmlutil.compress(actorpack_new.write()[1])
    )
