from math import ceil
from pathlib import Path
from typing import Union

import oead
from bcml import util as bcmlutil
from . import gdata_file_prefixes


bgdict: dict = {}
# bgdata is a dict that contains bool_data (a list of dict (that are individual flags))
svdict: dict = {}
# bgsvdata is a dict of file_list (which is a list that contains a dict (IsCommon, IsCommonAtSameAccount, IsSaveSecureCode, file_name) and a list of dict (that are individual flags)) and save_info (unimportant)
new_gamedata_entries: dict = {}
new_savedata_entries: dict = {}
mod_gamedata_entries: dict = {}
mod_savedata_entries: dict = {}
del_gamedata_entries: dict = {}
del_savedata_entries: dict = {}


def make_bgdict(bootup_dir: str) -> None:
    for prefix, dictname in gdata_file_prefixes.items():
        gdata_idx: int = 0
        while True:
            try:
                bgdatafile = oead.byml.from_binary(
                    bcmlutil.get_nested_file_bytes(
                        f"{bootup_dir}//GameData/gamedata.ssarc///{prefix}_{gdata_idx}.bgdata"
                    )
                )
                if prefix not in bgdict:
                    bgdict[prefix] = {}
                for flag in bgdatafile[dictname]:
                    bgdict[prefix][flag["HashValue"].v] = flag
                gdata_idx += 1
            except AttributeError:
                break


def make_svdict(bootup_dir: str) -> None:
    svdata_idx: int = 0
    while True:
        try:
            svdatafile = oead.byml.from_binary(
                bcmlutil.get_nested_file_bytes(
                    f"{bootup_dir}//GameData/savedataformat.ssarc///saveformat_{svdata_idx}.bgsvdata"
                )
            )
            file_name = svdatafile["file_list"][0]["file_name"]
            if file_name not in svdict:
                svdict[file_name] = {}
            for flag in svdatafile["file_list"][1]:
                svdict[file_name][flag["HashValue"].v] = flag
            svdata_idx += 1
        except AttributeError:
            break


def make_new_gamedata(big_endian: bool) -> bytes:
    bgwriter = oead.SarcWriter(
        endian=oead.Endianness.Big if big_endian else oead.Endianness.Little
    )
    for prefix, flagdata in bgdict.items():
        dictname = gdata_file_prefixes[prefix]
        flagarray = oead.byml.Array([flag for _, flag in sorted(flagdata.items())])
        num_files = ceil(len(flagdata) / 4096)
        for idx in range(num_files):
            start = idx * 4096
            end = (idx + 1) * 4096
            if end > len(flagdata):
                end = len(flagdata)
            bgwriter.files[f"/{prefix}_{idx}.bgdata"] = oead.byml.to_binary(
                oead.byml.Hash({dictname: flagarray[start:end]}), big_endian,
            )
    return bgwriter.write()[1]


def make_new_savedata(big_endian: bool) -> bytes:
    svwriter = oead.SarcWriter(
        endian=oead.Endianness.Big if big_endian else oead.Endianness.Little
    )
    svdatafilenum: int = 0
    numsvdatafiles: int = ceil(len(svdict["game_data.sav"]) / 8192) + 2
    for file_name, flagdata in svdict.items():
        flagarray = oead.byml.Array([flag for _, flag in sorted(flagdata.items())])
        num_files = ceil(len(flagdata) / 8192)
        for idx in range(num_files):
            start = idx * 8192
            end = (idx + 1) * 8192
            if end > len(flagdata):
                end = len(flagdata)
            svwriter.files[f"/saveformat_{svdatafilenum}.bgsvdata"] = oead.byml.to_binary(
                oead.byml.Hash(
                    {
                        "file_list": oead.byml.Array(
                            [
                                {
                                    "IsCommon": False,
                                    "IsCommonAtSameAccount": False,
                                    "IsSaveSecureCode": True,
                                    "file_name": file_name,
                                },
                                oead.byml.Array(flagarray[start:end]),
                            ]
                        ),
                        "save_info": oead.byml.Array(
                            [
                                {
                                    "directory_num": oead.S32(numsvdatafiles),
                                    "is_build_machine": True,
                                    "revision": oead.S32(18203),
                                }
                            ]
                        ),
                    }
                ),
                big_endian,
            )
            svdatafilenum += 1
    return svwriter.write()[1]


def inject_files_into_bootup(bootup_path: Path, files: list, datas: list):
    sarc_data = bootup_path.read_bytes()
    yaz = sarc_data[0:4] == b"Yaz0"
    if yaz:
        sarc_data = bcmlutil.decompress(sarc_data)
    old_sarc = oead.Sarc(sarc_data)
    del sarc_data
    new_sarc = oead.SarcWriter.from_sarc(old_sarc)
    del old_sarc
    for idx in range(len(files)):
        new_sarc.files[files[idx]] = (
            datas[idx] if isinstance(datas[idx], bytes) else bytes(datas[idx])
        )
    new_bytes = new_sarc.write()[1]
    del new_sarc
    bootup_path.write_bytes(new_bytes if not yaz else bcmlutil.compress(new_bytes))
    del new_bytes


def search_bgdict(search: Union[str, int]) -> dict:
    found: dict = {}
    if isinstance(search, str):
        for prefix, flagdata in bgdict.items():
            for hash, flag in flagdata.items():
                if search in flag["DataName"]:
                    if prefix not in found:
                        found[prefix] = set()
                    found[prefix].add(hash)
    else:
        for prefix, flagdata in bgdict.items():
            if search in flagdata:
                found[prefix].add(search)
    return found


def search_svdict(search: Union[str, int]) -> dict:
    found: dict = {}
    if isinstance(search, str):
        for prefix, flagdata in svdict.items():
            for hash, flag in flagdata.items():
                if search in flag["DataName"]:
                    if prefix not in found:
                        found[prefix] = set()
                    found[prefix].add(hash)
    else:
        for prefix, flagdata in svdict.items():
            if search in flagdata:
                found[prefix].add(search)
    return found


def search_bgdict_part(search: Union[str, int], datatype: str) -> set:
    found: set = set()
    if isinstance(search, str):
        for hash, flag in bgdict[datatype].items():
            if search in flag["DataName"]:
                found.add(hash)
    else:
        if search in bgdict[datatype]:
            found.add(search)
    return found


def search_svdict_part(search: Union[str, int], datatype: str) -> set:
    found: set = set()
    if isinstance(search, str):
        for hash, flag in svdict[datatype].items():
            if search in flag["DataName"]:
                found.add(hash)
    else:
        if search in svdict[datatype]:
            found.add(search)
    return found


def new_flag_bgdict(entry, datatype: str) -> None:
    bgdict[datatype][entry["HashValue"].v] = entry
    new_gamedata_entries[datatype].add(entry["HashValue"].v)


def new_flag_svdict(entry, datatype: str) -> None:
    svdict[datatype][entry["HashValue"].v] = entry
    new_savedata_entries[datatype].add(entry["HashValue"].v)


def mod_flag_bgdict(entry, old: int, datatype: str) -> None:
    old_entry = bgdict[datatype][old]
    for parameter in old_entry.keys():
        try:
            old_param = old_entry[parameter].v
            new_param = entry[parameter].v
        except AttributeError:
            old_param = old_entry[parameter]
            new_param = entry[parameter]
        if not old_param == new_param:
            bgdict[datatype].pop(old)
            bgdict[datatype][entry["HashValue"].v] = entry
            mod_gamedata_entries[datatype].add(entry["HashValue"].v)
            return


def mod_flag_svdict(entry, old: int, datatype: str) -> None:
    old_entry = svdict[datatype][old]
    for parameter in old_entry.keys():
        try:
            old_param = old_entry[parameter].v
            new_param = entry[parameter].v
        except AttributeError:
            old_param = old_entry[parameter]
            new_param = entry[parameter]
        if not old_param == new_param:
            svdict[datatype].pop(old)
            svdict[datatype][entry["HashValue"].v] = entry
            mod_savedata_entries[datatype].add(entry["HashValue"].v)
            return


def rem_flag_bgdict(hash: int, prefix: str = "") -> None:
    if not prefix == "":
        if hash in bgdict[prefix]:
            bgdict[prefix].pop(hash)
            del_gamedata_entries[prefix].add(hash)
    else:
        for prefix in bgdict.keys():
            if hash in bgdict[prefix]:
                bgdict[prefix].pop(hash)
                del_gamedata_entries[prefix].add(hash)
                return


def rem_flag_svdict(hash: int, file_name: str = "") -> None:
    if not file_name == "":
        if hash in svdict[file_name]:
            svdict[file_name].pop(hash)
            del_savedata_entries[file_name].add(hash)
    else:
        for file_name in svdict.keys():
            if hash in svdict[file_name]:
                svdict[file_name].pop(hash)
                del_savedata_entries[file_name].add(hash)
                break


def get_new_bgdict_changes() -> int:
    changes: int = 0
    for _, hashes in new_gamedata_entries.items():
        changes += len(hashes)
    return changes


def get_mod_bgdict_changes() -> int:
    changes: int = 0
    for _, hashes in mod_gamedata_entries.items():
        changes += len(hashes)
    return changes


def get_del_bgdict_changes() -> int:
    changes: int = 0
    for _, hashes in del_gamedata_entries.items():
        changes += len(hashes)
    return changes


def get_num_bgdict_changes() -> int:
    return get_new_bgdict_changes() + get_mod_bgdict_changes() + get_del_bgdict_changes()


def get_new_svdict_changes() -> int:
    changes: int = 0
    for _, hashes in new_savedata_entries.items():
        changes += len(hashes)
    return changes


def get_mod_svdict_changes() -> int:
    changes: int = 0
    for _, hashes in mod_savedata_entries.items():
        changes += len(hashes)
    return changes


def get_del_svdict_changes() -> int:
    changes: int = 0
    for _, hashes in del_savedata_entries.items():
        changes += len(hashes)
    return changes


def get_num_svdict_changes() -> int:
    return get_new_svdict_changes() + get_mod_svdict_changes() + get_del_svdict_changes()


def get_total_changes() -> int:
    return get_num_bgdict_changes() + get_num_svdict_changes()


def prep_entry_dicts_for_run(run_type: str) -> None:
    sv_run_type: str = "game_data.sav"  # hack until someone ever edits something in caption or options
    if run_type not in new_gamedata_entries:
        new_gamedata_entries[run_type] = set()
    if sv_run_type not in new_savedata_entries:
        new_savedata_entries[sv_run_type] = set()
    if run_type not in mod_gamedata_entries:
        mod_gamedata_entries[run_type] = set()
    if sv_run_type not in mod_savedata_entries:
        mod_savedata_entries[sv_run_type] = set()
    if run_type not in del_gamedata_entries:
        del_gamedata_entries[run_type] = set()
    if sv_run_type not in del_savedata_entries:
        del_savedata_entries[sv_run_type] = set()


def get_verbose_output() -> str:
    r: list = ["\nGame data entries:\n  New flags:\n"]
    for datatype, hashes in new_gamedata_entries.items():
        r.append(f"    {len(hashes)} flags were added to {datatype}\n")
    r.append("  Modified flags:\n")
    for datatype, hashes in mod_gamedata_entries.items():
        r.append(f"    {len(hashes)} flags were modified in {datatype}\n")
    r.append("  Deleted flags:\n")
    for datatype, hashes in del_gamedata_entries.items():
        r.append(f"    {len(hashes)} flags were deleted from {datatype}\n")
    r.append("Save data entries:\n")
    r.append("  New flags:\n")
    for datatype, hashes in new_savedata_entries.items():
        r.append(f"    {len(hashes)} flags were added to {datatype}\n")
    r.append("  Modified flags:\n")
    for datatype, hashes in mod_savedata_entries.items():
        r.append(f"    {len(hashes)} flags were modified in {datatype}\n")
    r.append("  Deleted flags:\n")
    for datatype, hashes in del_savedata_entries.items():
        r.append(f"    {len(hashes)} flags were deleted from {datatype}\n")
    return "".join(r)
