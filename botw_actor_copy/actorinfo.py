import oead
import shutil
import zlib
from copy import deepcopy
from ctypes import c_int32
from pathlib import Path

from bcml import util as bcmlutil
from . import util


def copy_actor(actorinfo_path: Path, basics: dict, bfres_name: str):
    if not actorinfo_path.exists():
        shutil.copy(bcmlutil.get_game_file("Actor/ActorInfo.product.sbyml"), actorinfo_path)
    actorinfo = oead.byml.from_binary(oead.yaz0.decompress(actorinfo_path.read_bytes()))

    old_hash_value = zlib.crc32(bytes(f"{basics['source_actor']}"))
    if c_int32(old_hash_value) < 0:
        old_hash = oead.U32(old_hash_value)
    else:
        old_hash = oead.S32(old_hash_value)
    new_hash_value = zlib.crc32(bytes(f"{basics['target_actor']}"))
    if c_int32(new_hash_value) < 0:
        new_hash = oead.U32(new_hash_value)
    else:
        new_hash = oead.S32(new_hash_value)

    old_loc = actorinfo["Hashes"].index(old_hash)
    actorinfo["Hashes"].append(new_hash)
    sort(actorinfo["Hashes"])
    new_loc = actorinfo["Hashes"].index(new_hash)

    new_entry = deepcopy(actorinfo["Actors"][old_loc])
    new_entry["name"] = basics["target_actor"]
    if not bfres_name == "" and "bfres" in new_entry:
        new_entry["bfres"] = bfres_name
        new_entry["mainModel"] = basics["target_actor"]
        new_entry["sortKey"] = oead.S32(int(new_entry["sortKey"]) + 1)
        # ^ basic fix for inventory/album sorting. May need to do something about it later

    actorinfo["Actors"].insert(new_entry, new_loc)
    actorinfo_path.write_bytes(oead.yaz0.compress(oead.byml.to_binary(actorinfo)))
