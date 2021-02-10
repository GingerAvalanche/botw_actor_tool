# Breath of the Wild Actor Tool, edits actor files fin LoZ:BotW
# Copyright (C) 2020 GingerAvalanche (chodness@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import oead
import shutil
from pathlib import Path
from typing import Dict, List, Union
from zlib import crc32

from . import actorinfo, generic_link_files, util
from .flag import BoolFlag, S32Flag
from .pack import ActorPack
from .texts import ActorTexts
from .store import FlagStore


FAR_LINKS: List[str] = [
    "LifeConditionUser",
    "ModelUser",
    "PhysicsUser",
]
FLAG_CLASSES: Dict[str, type] = {
    "_DispNameFlag": BoolFlag,
    "EquipTime_": S32Flag,
    "IsGet_": BoolFlag,
    "IsNewPictureBook_": BoolFlag,
    "IsRegisteredPictureBook_": BoolFlag,
    "PictureBookSize_": S32Flag,
    "PorchTime_": S32Flag,
}
FLAG_TYPES: Dict[str, List[str]] = {
    "Animal": ["IsNewPictureBook_", "IsRegisteredPictureBook_", "PictureBookSize_"],
    "Armor": ["EquipTime_", "IsGet_", "PorchTime_"],
    "Enemy": ["IsNewPictureBook_", "IsRegisteredPictureBook_", "PictureBookSize_"],
    "Item": ["IsGet_", "IsNewPictureBook_", "IsRegisteredPictureBook_", "PictureBookSize_"],
    "Npc": ["_DispNameFlag"],
    "Weapon": [
        "EquipTime_",
        "IsGet_",
        "IsNewPictureBook_",
        "IsRegisteredPictureBook_",
        "PictureBookSize_",
        "PorchTime_",
    ],
}


def try_retrieve_custom_file(link: str, fn: str) -> str:
    s = ""
    if link in generic_link_files:
        if fn in generic_link_files[link]:
            an = generic_link_files[link][fn]
            a = ActorPack()
            a.from_actor(util.find_file(Path(f"Actor/Pack/{an}.sbactorpack")))
            s = a.get_link_data(link)
            del a
    return s


class BATActor:
    _pack: ActorPack
    _info: oead.byml.Hash
    _needs_info_update: bool
    _has_far: bool
    _far_pack: ActorPack
    _far_info: oead.byml.Hash
    _far_needs_info_update: bool
    _texts: ActorTexts
    _flags: FlagStore
    _flag_hashes: Dict[str, set]
    _resident: bool
    _origname: str
    _far_origname: str

    def __init__(self, pack: Union[Path, str]) -> None:
        if isinstance(pack, str):
            self._resident = True
            actorinfo_path = (
                Path(pack.split("//")[0]).parent / "../Actor/ActorInfo.product.sbyml"
            ).resolve()
        self._pack = ActorPack()
        self._pack.from_actor(pack)
        self._origname = self._pack.get_name()
        self._has_far = False
        self._needs_info_update = False
        if isinstance(pack, Path):
            self._resident = False
            actorinfo_path = (pack.parent / "../ActorInfo.product.sbyml").resolve()
            if pack.with_name(f"{pack.name}_Far").exists():
                self._far_pack = ActorPack()
                self._far_pack.from_actor(Path(f"{pack.name}_Far"))
                self._far_origname = self._far_pack.get_name()
                self._has_far = True
                self._far_needs_info_update = False
        self._texts = ActorTexts(Path(pack), self._pack.get_link("ProfileUser"))
        self._flags = FlagStore()
        self._flag_hashes = {"bool_data": set(), "s32_data": set()}
        self.set_flags(self._origname)

        if not actorinfo_path.exists():
            actorinfo_path = Path(util.find_file(Path("Actor/ActorInfo.product.sbyml")))
        actorinfo = oead.byml.from_binary(oead.yaz0.decompress(actorinfo_path.read_bytes()))
        info_set = far_info_set = False
        for actor in actorinfo["Actors"]:
            if actor["name"] == self._origname:
                self._info = actor
                info_set = True
            if self._has_far:
                if actor["name"] == self._far_pack.get_name():
                    self._far_info = actor
                    far_info_set = True
            if info_set and (far_info_set or not self._has_far):
                break
        del actorinfo
        del actorinfo_path

        if not self._info or (self._has_far and not self._far_info):
            raise RuntimeError(
                f"ActorInfo.product.sbyml did not contain an info entry for {self._origname}"
            )

    def get_name(self) -> str:
        return self._pack.get_name()

    def set_name(self, name: str) -> None:
        self._pack.set_name(name)
        self._texts.set_actor_name(name)
        self.set_flags(name)
        self._needs_info_update = True
        self._resident = False

    def get_link(self, link: str) -> str:
        return self._pack.get_link(link)

    def set_link(self, link: str, linkref: str) -> bool:
        if self._has_far:
            if link == "LifeConditionUser" and linkref == "Dummy":
                return False
            self._pack.set_link(link, linkref)
            self._needs_info_update = True
            if link in FAR_LINKS:
                self._far_pack.set_link(link, linkref)
                self._far_needs_info_update = True
            return True
        else:
            self._pack.set_link(link, linkref)
            self._needs_info_update = True
            return True

    def get_has_far(self) -> bool:
        return self._has_far

    def set_has_far(self, enabled: bool, pack: Path = Path()) -> bool:
        if enabled and not self._has_far:
            self._far_pack = ActorPack()
            for link in [link for link in FAR_LINKS if not link == "LifeConditionUser"]:
                linkref = self._pack.get_link(link)
                if not linkref == "Dummy":
                    self._far_pack.set_link_data(link, self._pack.get_link_data(link))
            self._far_pack.set_name(f"{self._pack.get_name()}_Far")
            self._has_far = True
            self._needs_info_update = True
            self._resident = False
            return True
        if not enabled:
            del self._far_pack
            self._has_far = False
            self._needs_info_update = True
            return True
        return False

    def get_link_data(self, link: str) -> str:
        return self._pack.get_link_data(link)

    def set_link_data(self, link: str, data: str) -> None:
        self._pack.set_link_data(link, data)
        self._needs_info_update = True

    def get_tags(self) -> str:
        return self._pack.get_tags()

    def set_tags(self, tags: str) -> None:
        self._needs_info_update = True
        self._pack.set_tags(tags)

    def get_info(self) -> oead.byml.Hash:
        if self._needs_info_update:
            # TODO: This is messy, we shouldn't let someone else directly modify our property
            actorinfo.generate_actor_info(
                self._pack, self._has_far, self._info, self._origname == self._pack.get_name()
            )
            self._needs_info_update = False
        return self._info

    def get_far_info(self) -> oead.byml.Hash:
        if self._far_needs_info_update:
            # TODO: This is messy, we shouldn't let someone else directly modify our property
            actorinfo.generate_actor_info(
                self._far_pack,
                False,
                self._far_info,
                self._far_origname == self._far_pack.get_name(),
            )
            self._far_needs_info_update = False
        return self._far_info

    def get_actorlink(self) -> oead.aamp.ParameterIO:
        return self._pack.get_actorlink()

    def get_texts(self) -> Dict[str, str]:
        return self._texts.get_texts()

    def set_texts(self, texts: Dict[str, str]) -> None:
        self._texts.set_texts(texts)

    def set_flags(self, name: str) -> None:
        for ftype, hashes in self._flag_hashes.items():
            for hash in hashes:
                self._flags.remove(ftype, hash)
            self._flag_hashes[ftype].clear()
        actor_type = name.split("_")[0]
        if actor_type in FLAG_TYPES:
            for prefix in FLAG_TYPES[actor_type]:
                flag = FLAG_CLASSES[prefix]()
                if isinstance(flag, BoolFlag):
                    ftype = "bool_data"
                else:
                    ftype = "s32_data"
                if prefix[0] == "_":
                    flag.data_name = f"{name}{prefix}"
                else:
                    flag.data_name = f"{prefix}{name}"
                self._flag_hashes[ftype].add(flag.hash_value)
                flag.use_name_to_override_params()
                self._flags.add(ftype, flag)

    def save(self, root_dir: str, be: bool) -> None:
        if self._resident:
            titlebg_path = Path(f"{root_dir}/Pack/TitleBG.pack")
            actor_dir = f"Actor/Pack/{self._pack.get_name()}.sbactorpack"
            if not titlebg_path.exists():
                titlebg_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(util.find_file(Path("Pack/TitleBG.pack")), titlebg_path)
            yaz0_bytes = oead.yaz0.compress(self._pack.get_bytes(be))
            util.inject_bytes_into_sarc(titlebg_path, actor_dir, yaz0_bytes)
        else:
            actor_path = Path(f"{root_dir}/Actor/Pack/{self._pack.get_name()}.sbactorpack")
            yaz0_bytes = oead.yaz0.compress(self._pack.get_bytes(be))
            if not actor_path.exists():
                actor_path.parent.mkdir(parents=True, exist_ok=True)
                actor_path.touch()
            actor_path.write_bytes(yaz0_bytes)

        hash = crc32(self._pack.get_name().encode("utf-8"))
        info = self.get_info()

        if self._has_far:
            actor_path = Path(f"{root_dir}/Actor/Pack/{self._far_pack.get_name()}.sbactorpack")
            yaz0_bytes = oead.yaz0.compress(self._far_pack.get_bytes(be))
            if not actor_path.exists():
                actor_path.touch()
            actor_path.write_bytes(yaz0_bytes)

            far_hash = crc32(self._far_pack.get_name().encode("utf-8"))
            far_info = self.get_far_info()

        actorinfo_path = Path(f"{root_dir}/Actor/ActorInfo.product.sbyml")
        actorinfo_load_path = actorinfo_path
        if not actorinfo_load_path.exists():
            actorinfo_load_path.touch()
            actorinfo_load_path = Path(util.find_file(Path("Actor/ActorInfo.product.sbyml")))
        actorinfo = oead.byml.from_binary(oead.yaz0.decompress(actorinfo_load_path.read_bytes()))

        hashes = [int(h) for h in actorinfo["Hashes"]]
        try:
            hash_index = hashes.index(hash)
        except ValueError:
            hashes.append(hash)
            hashes.sort()
            hash_index = hashes.index(hash)
            actorinfo["Actors"].insert(hash_index, oead.byml.Hash())
        if self._has_far:
            try:
                far_hash_index = hashes.index(far_hash)
            except ValueError:
                hashes.append(far_hash)
                hashes.sort()
                far_hash_index = hashes.index(far_hash)
                actorinfo["Actors"].insert(far_hash_index, oead.byml.Hash())
        actorinfo["Hashes"] = oead.byml.Array(
            [oead.U32(h) if h > 2147483647 else oead.S32(h) for h in hashes]
        )

        actorinfo["Actors"][hash_index] = info
        if self._has_far:
            actorinfo["Actors"][far_hash_index] = far_info

        actorinfo_path.write_bytes(oead.yaz0.compress(oead.byml.to_binary(actorinfo, be)))

        self._texts.write(root_dir, be)

        bootup_path = Path(f"{root_dir}/Pack/Bootup.pack")
        if not bootup_path.exists():
            bootup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(util.find_file(Path("Pack/Bootup.pack")), bootup_path)

        gamedata_sarc = util.get_gamedata_sarc(bootup_path)
        for bgdata_name, bgdata_hash in map(util.unpack_oead_file, gamedata_sarc.get_files()):
            self._flags.add_flags_from_Hash_no_overwrite(bgdata_name, bgdata_hash)

        files_to_write: list = []
        files_to_write.append("GameData/gamedata.ssarc")
        files_to_write.append("GameData/savedataformat.ssarc")
        orig_files = util.get_last_two_savedata_files(bootup_path)
        datas_to_write: list = []
        datas_to_write.append(oead.yaz0.compress(util.make_new_gamedata(self._flags, be)))
        datas_to_write.append(
            oead.yaz0.compress(util.make_new_savedata(self._flags, be, orig_files))
        )
        util.inject_files_into_bootup(bootup_path, files_to_write, datas_to_write)
