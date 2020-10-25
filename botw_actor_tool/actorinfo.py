# There is a loooot of bullshit in this file. It's an attempt to automate a system
# that was probably done manually. Most of the params are able to be handled
# automatically with a few tricks, but almost all files that get pulled from also
# have extra params that needed special handling. Luckily, they were few enough in
# number not to justify spending the extra time to handle them gracefully, but it
# also means that this might be incredibly difficult to read.

import oead
import zlib
from ctypes import c_int32
from json import loads
from math import isclose
from pathlib import Path
from typing import Union

from . import EXEC_DIR, util
from .pack import ActorPack

KEYS_BY_PROFILE = loads((EXEC_DIR / "data/keys_by_profile.json").read_bytes())["keys_per_profile"]

ACTORLINK_KEYS = [
    ("actorScale", "ActorScale"),
    ("elink", "ElinkUser"),
    ("profile", "ProfileUser"),
    ("slink", "SlinkUser"),
    ("xlink", "XlinkUser"),
]
DROPTABLE_ARRAY_KEYS = {
    "Normal": [
        "ItemName01",
        "ItemName02",
        "ItemName03",
        "ItemName04",
        "ItemName05",
        "ItemName06",
        "ItemName07",
        "ItemName08",
        "ItemName09",
        "ItemName10",
    ],
    "Normal2": [
        "ItemName01",
        "ItemName02",
        "ItemName03",
        "ItemName04",
        "ItemName05",
        "ItemName06",
        "ItemName07",
        "ItemName08",
        "ItemName09",
        "ItemName10",
    ],
    "Normal3": [
        "ItemName01",
        "ItemName02",
        "ItemName03",
        "ItemName04",
        "ItemName05",
        "ItemName06",
        "ItemName07",
        "ItemName08",
        "ItemName09",
        "ItemName10",
    ],
    "Normal4": [
        "ItemName01",
        "ItemName02",
        "ItemName03",
        "ItemName04",
        "ItemName05",
        "ItemName06",
        "ItemName07",
        "ItemName08",
        "ItemName09",
        "ItemName10",
    ],
    "Normal5": [
        "ItemName01",
        "ItemName02",
        "ItemName03",
        "ItemName04",
        "ItemName05",
        "ItemName06",
        "ItemName07",
        "ItemName08",
        "ItemName09",
        "ItemName10",
    ],
}
GPARAMLIST_KEYS = {
    "AnimalUnit": [("animalUnitBasePlayRate", "BasePlayRate", oead.F32, False)],
    "Armor": [
        ("armorDefenceAddLevel", "DefenceAddLevel", oead.S32, False),
        ("armorNextRankName", "NextRankName", str, False),
        ("armorStarNum", "StarNum", oead.S32, False),
    ],
    "ArmorEffect": [
        ("armorEffectAncientPowUp", "AncientPowUp", bool, False),
        ("armorEffectEffectLevel", "EffectLevel", oead.S32, False),
        ("armorEffectEffectType", "EffectType", str, False),
        ("armorEffectEnableClimbWaterfall", "EnableClimbWaterfall", bool, False),
        ("armorEffectEnableSpinAttack", "EnableSpinAttack", bool, False),
    ],
    "ArmorHead": [("armorHeadMantleType", "HeadMantleType", oead.S32, False)],
    "ArmorUpper": [
        ("armorUpperDisableSelfMantle", "DisableSelfMantle", bool, False),
        ("armorUpperUseMantleType", "UseMantleType", oead.S32, False),
    ],
    "Arrow": [
        ("arrowArrowDeletePer", "ArrowDeletePer", oead.S32, False),
        ("arrowArrowNum", "ArrowNum", oead.S32, False),
        ("arrowDeleteTime", "DeleteTime", oead.S32, False),
        ("arrowDeleteTimeWithChemical", "DeleteTimeWithChemical", oead.S32, False),
        ("arrowEnemyShootNumForDelete", "EnemyShootNumForDelete", oead.S32, False),
    ],
    "Attack": [("attackPower", "Power", oead.S32, False)],
    "Bow": [
        ("bowArrowName", "ArrowName", str, False),
        ("bowIsLeadShot", "IsLeadShot", bool, False),
        ("bowIsRapidFire", "IsRapidFire", bool, False),
        ("bowLeadShotNum", "LeadShotNum", oead.S32, False),
        ("bowRapidFireNum", "RapidFireNum", oead.S32, False),
    ],
    "CookSpice": [
        ("cookSpiceBoostEffectiveTime", "BoostEffectiveTime", oead.S32, False),
        ("cookSpiceBoostHitPointRecover", "BoostHitPointRecover", oead.S32, False),
        ("cookSpiceBoostMaxHeartLevel", "BoostMaxHeartLevel", oead.S32, False),
        ("cookSpiceBoostStaminaLevel", "BoostStaminaLevel", oead.S32, False),
        ("cookSpiceBoostSuccessRate", "BoostSuccessRate", oead.S32, False),
    ],
    "CureItem": [
        ("cureItemEffectLevel", "EffectLevel", oead.S32, False),
        ("cureItemEffectType", "EffectType", str, False),
        ("cureItemEffectiveTime", "EffectiveTime", oead.S32, True),
        ("cureItemHitPointRecover", "HitPointRecover", oead.S32, False),
    ],
    "Enemy": [("enemyRank", "Rank", oead.S32, False)],
    "General": [("generalLife", "Life", oead.S32, False)],
    "Horse": [
        ("horseASVariation", "ASVariation", str, False),
        ("horseGearTopChargeNum", "GearTopChargeNum", oead.S32, False),
        ("horseNature", "Nature", oead.S32, False),
    ],
    "HorseUnit": [("horseUnitRiddenAnimalType", "RiddenAnimalType", oead.S32, False)],
    "Item": [
        ("itemBuyingPrice", "BuyingPrice", oead.S32, False),
        ("itemCreatingPrice", "CreatingPrice", oead.S32, False),
        ("itemSaleRevivalCount", "SaleRevivalCount", oead.S32, False),
        ("itemSellingPrice", "SellingPrice", oead.S32, False),
        ("itemStainColor", "StainColor", oead.S32, False),
        ("itemUseIconActorName", "UseIconActorName", str, False),
    ],
    "MasterSword": [
        ("masterSwordSearchEvilDist", "SearchEvilDist", oead.F32, False),
        ("masterSwordSleepActorName", "SleepActorName", str, False),
        ("masterSwordTrueFormActorName", "TrueFormActorName", str, False),
        ("masterSwordTrueFormAttackPower", "TrueFormAttackPower", oead.S32, False),
    ],
    "MonsterShop": [
        ("monsterShopBuyMamo", "BuyMamo", oead.S32, False),
        ("monsterShopSellMamo", "SellMamo", oead.S32, False),
    ],
    "PictureBook": [
        ("pictureBookLiveSpot1", "LiveSpot1", oead.S32, False),
        ("pictureBookLiveSpot2", "LiveSpot2", oead.S32, False),
        ("pictureBookSpecialDrop", "SpecialDrop", oead.S32, False),
    ],
    "Rupee": [("rupeeRupeeValue", "RupeeValue", oead.S32, False)],
    "SeriesArmor": [
        ("seriesArmorEnableCompBonus", "EnableCompBonus", bool, False),
        ("seriesArmorSeriesType", "SeriesType", str, False),
    ],
    "System": [
        ("systemIsGetItemSelf", "IsGetItemSelf", bool, False),
        ("systemSameGroupActorName", "SameGroupActorName", str, False),
    ],
    "Traveler": [
        ("travelerAppearGameDataName", "AppearGameDataName", str, True),
        ("travelerDeleteGameDataName", "DeleteGameDataName", str, True),
        ("travelerRideHorseName", "RideHorseName", str, True),
        ("travelerRoutePoint0Name", "RoutePoint0Name", str, True),
        ("travelerRoutePoint1Name", "RoutePoint1Name", str, True),
        ("travelerRoutePoint2Name", "RoutePoint2Name", str, True),
        ("travelerRoutePoint3Name", "RoutePoint3Name", str, True),
        ("travelerRoutePoint4Name", "RoutePoint4Name", str, True),
        ("travelerRoutePoint5Name", "RoutePoint5Name", str, True),
        ("travelerRoutePoint6Name", "RoutePoint6Name", str, True),
        ("travelerRoutePoint7Name", "RoutePoint7Name", str, True),
        ("travelerRoutePoint8Name", "RoutePoint8Name", str, True),
        ("travelerRoutePoint9Name", "RoutePoint9Name", str, True),
        ("travelerRoutePoint10Name", "RoutePoint10Name", str, True),
        ("travelerRoutePoint11Name", "RoutePoint11Name", str, True),
        ("travelerRoutePoint12Name", "RoutePoint12Name", str, True),
        ("travelerRoutePoint13Name", "RoutePoint13Name", str, True),
        ("travelerRoutePoint14Name", "RoutePoint14Name", str, True),
        ("travelerRoutePoint15Name", "RoutePoint15Name", str, True),
        ("travelerRoutePoint16Name", "RoutePoint16Name", str, True),
        ("travelerRoutePoint17Name", "RoutePoint17Name", str, True),
        ("travelerRoutePoint18Name", "RoutePoint18Name", str, True),
        ("travelerRoutePoint19Name", "RoutePoint19Name", str, True),
        ("travelerRoutePoint20Name", "RoutePoint20Name", str, True),
        ("travelerRoutePoint21Name", "RoutePoint21Name", str, True),
        ("travelerRoutePoint22Name", "RoutePoint22Name", str, True),
        ("travelerRoutePoint23Name", "RoutePoint23Name", str, True),
        ("travelerRoutePoint24Name", "RoutePoint24Name", str, True),
        ("travelerRoutePoint25Name", "RoutePoint25Name", str, True),
        ("travelerRoutePoint26Name", "RoutePoint26Name", str, True),
        ("travelerRoutePoint27Name", "RoutePoint27Name", str, True),
        ("travelerRouteType", "RouteType", str, True),
    ],
    "WeaponCommon": [
        ("weaponCommonGuardPower", "GuardPower", oead.S32, False),
        ("weaponCommonPoweredSharpAddAtkMax", "PoweredSharpAddAtkMax", oead.S32, False),
        ("weaponCommonPoweredSharpAddAtkMin", "PoweredSharpAddAtkMin", oead.S32, False),
        ("weaponCommonPoweredSharpAddLifeMax", "PoweredSharpAddLifeMax", oead.S32, False),
        ("weaponCommonPoweredSharpAddLifeMin", "PoweredSharpAddLifeMin", oead.S32, False),
        (
            "weaponCommonPoweredSharpAddRapidFireMax",
            "PoweredSharpAddRapidFireMax",
            oead.F32,
            False,
        ),
        (
            "weaponCommonPoweredSharpAddRapidFireMin",
            "PoweredSharpAddRapidFireMin",
            oead.F32,
            False,
        ),
        ("weaponCommonPoweredSharpAddSpreadFire", "PoweredSharpAddSpreadFire", bool, False),
        ("weaponCommonPoweredSharpAddSurfMaster", "PoweredSharpAddSurfMaster", bool, False),
        ("weaponCommonPoweredSharpAddThrowMax", "PoweredSharpAddThrowMax", oead.F32, False),
        ("weaponCommonPoweredSharpAddThrowMin", "PoweredSharpAddThrowMin", oead.F32, False),
        ("weaponCommonPoweredSharpAddZoomRapid", "PoweredSharpAddZoomRapid", bool, False),
        (
            "weaponCommonPoweredSharpWeaponAddGuardMax",
            "PoweredSharpWeaponAddGuardMax",
            oead.S32,
            False,
        ),
        (
            "weaponCommonPoweredSharpWeaponAddGuardMin",
            "PoweredSharpWeaponAddGuardMin",
            oead.S32,
            False,
        ),
        ("weaponCommonRank", "Rank", oead.S32, False),
        ("weaponCommonSharpWeaponAddAtkMax", "SharpWeaponAddAtkMax", oead.S32, False),
        ("weaponCommonSharpWeaponAddAtkMin", "SharpWeaponAddAtkMin", oead.S32, False),
        ("weaponCommonSharpWeaponAddCrit", "SharpWeaponAddCrit", bool, False),
        ("weaponCommonSharpWeaponAddGuardMax", "SharpWeaponAddGuardMax", oead.S32, False),
        ("weaponCommonSharpWeaponAddGuardMin", "SharpWeaponAddGuardMin", oead.S32, False),
        ("weaponCommonSharpWeaponAddLifeMax", "SharpWeaponAddLifeMax", oead.S32, False),
        ("weaponCommonSharpWeaponAddLifeMin", "SharpWeaponAddLifeMin", oead.S32, False),
        ("weaponCommonSharpWeaponPer", "SharpWeaponPer", oead.F32, False),
        ("weaponCommonStickDamage", "StickDamage", oead.S32, False),
    ],
}
LIFECONDITION_ARRAY_KEYS = [
    ("invalidTimes", "InvalidTimes", str, False),
    ("invalidWeathers", "InvalidWeathers", str, False),
]
LIFECONDITION_KEYS = {
    "DisplayDistance": [("traverseDist", "Item", oead.F32, True)],
    "YLimitAlgorithm": [("yLimitAlgorithm", "Item", str, False)],
}
MODELLIST_KEYS = {
    "Attention": [("cursorOffsetY", "CursorOffsetY", oead.F32, True)],
    "ControllerInfo": [
        ("variationMatAnim", "VariationMatAnim", str, True),
        ("variationMatAnimFrame", "VariationMatAnimFrame", oead.S32, True),
    ],
}
RECIPE_KEYS = {
    "Normal0": [
        ("normal0ItemName01", "ItemName01", str, False),
        ("normal0ItemName02", "ItemName02", str, False),
        ("normal0ItemName03", "ItemName03", str, False),
        ("normal0ItemNum01", "ItemNum01", oead.S32, False),
        ("normal0ItemNum02", "ItemNum02", oead.S32, False),
        ("normal0ItemNum03", "ItemNum03", oead.S32, False),
        ("normal0StuffNum", "ColumnNum", oead.S32, False),
    ]
}
NULL_VALUES = [  # never ignore bool
    (oead.S32, util.S32_equality, 0),
    (oead.F32, util.F32_equality, 0),
    (str, util.FSS_equality, ""),
]


def _deepretrieve_info(
    data: dict,
    keys: Union[dict, list],
    el: Union[oead.aamp.ParameterIO, oead.aamp.ParameterList, oead.aamp.ParameterObject],
) -> None:
    if isinstance(keys, dict):
        for key, value in keys.items():
            if key in el.lists:
                _deepretrieve_info(data, value, el.lists[key])
            elif key in el.objects:
                _deepretrieve_info(data, value, el.objects[key])
    else:
        for info, param, otype, check in keys:
            if check:
                # convoluted - if we want to ignore a null value, check through null types
                # and if we find it's null, stop checking null types and then ignore value
                set_continue = False
                for otype2, eqfunc, nullval in NULL_VALUES:
                    if otype == otype2 and eqfunc(el.params[param].v, nullval):  # type: ignore[operator]
                        set_continue = True
                        break
                if set_continue:
                    continue
            try:
                data[info] = otype(el.params[param].v)
            except KeyError:
                pass


def get_all_actors(path: str) -> list:
    actorlist = []
    if path:
        for actor in [actor.stem for actor in Path(path).glob("Actor/Pack/*.sbactorpack")]:
            actorlist.append(actor)
    else:
        actorinfo_path = Path(util.find_file(Path("Actor/ActorInfo.product.sbyml")))
        actorinfo = oead.byml.from_binary(oead.yaz0.decompress(actorinfo_path.read_bytes()))
        for aiactor in actorinfo["Actors"]:
            actorlist.append(str(aiactor["name"]))
    return sorted(actorlist)


def get_actorlink_entries(data: oead.aamp.ParameterIO) -> dict:
    d: dict = {}
    for i, l in ACTORLINK_KEYS:
        v = data.objects["LinkTarget"].params[l].v
        if isinstance(v, str):
            if not v == "Dummy":
                d[i] = v
        else:
            if not v == 1.0:
                d[i] = oead.F32(v)
    return d


def get_actorlink_tags(data: oead.aamp.ParameterIO) -> Union[oead.byml.Hash, None]:
    d: Union[oead.byml.Hash, None] = None
    if "Tags" in data.objects:
        d = oead.byml.Hash()
        for _, val in data.objects["Tags"].params.items():
            taghash = zlib.crc32(val.v.encode("utf-8"))
            tagval = oead.U32(taghash) if taghash > 2147483647 else oead.S32(taghash)
            taghex = f"tag{str(hex(taghash))[2:]}"
            d[taghex] = tagval
    return d


def get_chemical_entries(data: oead.aamp.ParameterIO) -> dict:
    d: dict = {}
    if "chemical_root" in data.lists:
        cr = data.lists["chemical_root"]
        if "chemical_body" in cr.lists:
            cb = cr.lists["chemical_body"]
            if "rigid_c_00" in cb.objects:
                rc = cb.objects["rigid_c_00"]
                if "attribute" in rc.params:
                    if rc.params["attribute"].v == 650:
                        if not "Chemical" in d:
                            d["Chemical"] = oead.byml.Hash()
                        d["Chemical"]["Capaciter"] = oead.S32(1)
            if "shape_00" in cb.objects:
                s0 = cb.objects["shape_00"]
                if "name" in s0.params:
                    if s0.params["name"].v == "WeaponFire":
                        if not "Chemical" in d:
                            d["Chemical"] = oead.byml.Hash()
                        d["Chemical"]["Burnable"] = oead.S32(1)
    return d


def get_droptable_entries(data: oead.aamp.ParameterIO) -> dict:
    d: dict = {"drops": {}}
    for table, keys in DROPTABLE_ARRAY_KEYS.items():
        if table in data.objects:
            d["drops"][table] = oead.byml.Array()
            for key in keys:
                if key in data.objects[table].params:
                    d["drops"][table].append(str(data.objects[table].params[key].v))
    # TODO: Figure out what the Amiibo key is all about
    return d


def get_gparamlist_entries(data: oead.aamp.ParameterIO) -> dict:
    d: dict = {}
    _deepretrieve_info(d, GPARAMLIST_KEYS, data)
    return d


def get_lifecondition_entries(data: oead.aamp.ParameterIO) -> dict:
    d: dict = {}
    _deepretrieve_info(d, LIFECONDITION_KEYS, data)
    for i, p, t, c in LIFECONDITION_ARRAY_KEYS:
        if p in data.objects:
            d[i] = oead.byml.Array()
            idx = 0
            while True:
                idx += 1
                keyname = "Item%03d" % idx
                try:
                    if c:
                        set_continue = False
                        for t2, e, n in NULL_VALUES:
                            if t == t2 and e(data.objects[p].params[keyname].v, n):  # type: ignore
                                set_continue = True
                                break
                        if not set_continue:
                            d[i].append(t(data.objects[p].params[keyname].v))
                except KeyError:
                    break
    return d


def get_modellist_entries(data: oead.aamp.ParameterIO) -> dict:
    d: dict = {}
    _deepretrieve_info(d, MODELLIST_KEYS, data)
    if "Attention" in data.objects:
        att = data.objects["Attention"]
        if "LookAtOffset" in att.params:
            value = att.params["LookAtOffset"].v.y
            if not isclose(value, 0, rel_tol=1e-5):
                d["lookAtOffsetY"] = oead.F32(value)
    if "ControllerInfo" in data.objects:
        ci = data.objects["ControllerInfo"]
        if "AddColor" in ci.params:
            clr = ci.params["AddColor"].v
            if not isclose(clr.r + clr.g + clr.b + clr.a, 0, rel_tol=1e-5):
                t = oead.F32
                d["addColorR"] = t(clr.r)
                d["addColorG"] = t(clr.g)
                d["addColorB"] = t(clr.b)
                d["addColorA"] = t(clr.a)
        if "BaseScale" in ci.params:
            t = oead.F32
            bs = ci.params["BaseScale"].v
            if not bs.x == 1 and bs.y == 1 and bs.z == 1:
                d["baseScaleX"] = t(bs.x)
                d["baseScaleY"] = t(bs.y)
                d["baseScaleZ"] = t(bs.z)
        if "FarModelCullingCenter" in ci.params:
            fmccx = ci.params["FarModelCullingCenter"].v.x
            fmccy = ci.params["FarModelCullingCenter"].v.y
            fmccz = ci.params["FarModelCullingCenter"].v.z
        if "FarModelCullingHeight" in ci.params:
            fmch = ci.params["FarModelCullingHeight"].v
        if "FarModelCullingRadius" in ci.params:
            fmcr = ci.params["FarModelCullingRadius"].v
        if not fmccx + fmccy + fmccz + fmch + fmcr == 0:
            t = oead.F32
            center = oead.byml.Hash({"X": t(fmccx), "Y": t(fmccy), "Z": t(fmccz)})
            d["farModelCulling"] = oead.byml.Hash()
            d["farModelCulling"]["center"] = center
            d["farModelCulling"]["height"] = t(fmch)
            d["farModelCulling"]["radius"] = t(fmcr)
    if "ModelData" in data.lists:
        md = data.lists["ModelData"]
        if "ModelData_0" in md.lists:
            md0 = md.lists["ModelData_0"]
            if "Base" in md0.objects:
                d["bfres"] = str(md0.objects["Base"].params["Folder"].v)
            if "Unit" in md0.lists:
                u = md0.lists["Unit"]
                if "Unit_0" in u.objects:
                    d["mainModel"] = str(u.objects["Unit_0"].params["UnitName"].v)
    return d


def get_physics_entries(data: oead.aamp.ParameterIO) -> dict:
    d: dict = {}
    if "ParamSet" in data.lists:
        ps = data.lists["ParamSet"]
        if "RigidBodySet" in ps.lists:
            rbs = ps.lists["RigidBodySet"]
            if "RigidBodySet_0" in rbs.lists:
                rbs0 = rbs.lists["RigidBodySet_0"]
                if "RigidBody_0" in rbs0.lists:
                    rb0 = rbs0.lists["RigidBody_0"]
                    if 948250248 in rb0.objects:
                        numbers = rb0.objects[948250248]
                        if "center_of_mass" in numbers.params:
                            d["rigidBodyCenterY"] = oead.F32(numbers.params["center_of_mass"].v.y)
    return d


def get_recipe_entries(data: oead.aamp.ParameterIO) -> dict:
    d: dict = {}
    _deepretrieve_info(d, RECIPE_KEYS, data)
    return d


def generate_actor_info(pack: ActorPack, old_info: oead.byml.Hash) -> oead.byml.Hash:
    entry = old_info
    entry["name"] = pack.get_name()
    entry["isHasFar"] = pack.get_has_far()

    profile = pack.get_link("ProfileUser")
    if not pack.get_link("SlinkUser") == "Dummy":
        entry["bugMask"] = oead.S32(2)  # TODO: Find what sets the first bit of bugMask

    if entry["sortKey"].v > 0:
        entry["sortKey"] = oead.S32(entry["sortKey"].v + 1)

    actorlink = pack.get_actorlink()
    for key, value in get_actorlink_entries(actorlink).items():
        if key in KEYS_BY_PROFILE[profile]:
            entry[key] = value
    tags = get_actorlink_tags(actorlink)
    if tags:
        entry["tags"] = tags

    funcs = {
        "ChemicalUser": get_chemical_entries,
        "DropTableUser": get_droptable_entries,
        "GParamUser": get_gparamlist_entries,
        "LifeConditionUser": get_lifecondition_entries,
        "ModelUser": get_modellist_entries,
        "PhysicsUser": get_physics_entries,
        "RecipeUser": get_recipe_entries,
    }

    for link, func in funcs.items():
        yaml = pack.get_link_data(link)
        if not yaml == "":
            for key, value in func(oead.aamp.ParameterIO.from_text(yaml)).items():
                entry[key] = value

    keys_to_pop: list = []
    for key in entry.keys():
        if not key in KEYS_BY_PROFILE[profile]:
            keys_to_pop.append(key)
    for key in keys_to_pop:
        del entry[key]
    del keys_to_pop

    return entry
