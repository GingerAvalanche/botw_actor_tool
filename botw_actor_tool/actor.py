import oead
import shutil
import yaml
from pathlib import Path
from typing import Dict, Union
from zlib import crc32

from . import util
from .flag import BoolFlag, S32Flag
from .pack import ActorPack
from .texts import ActorTexts
from .store import FlagStore


FAR_LINKS: list = [
    "LifeConditionUser",
    "ModelUser",
    "PhysicsUser",
]
FLAG_CLASSES: dict = {
    "EquipTime_": S32Flag,
    "IsGet_": BoolFlag,
    "IsNewPictureBook_": BoolFlag,
    "IsRegisteredPictureBook_": BoolFlag,
    "PictureBookSize_": S32Flag,
    "PorchTime_": S32Flag,
}
FLAG_TYPES: dict = {
    "Armor": ["EquipTime_", "IsGet_", "PorchTime_"],
    "Item": ["IsGet_", "IsNewPictureBook_", "IsRegisteredPictureBook_", "PictureBookSize_"],
    "Weapon": [
        "EquipTime_",
        "IsGet_",
        "IsNewPictureBook_",
        "IsRegisteredPictureBook_",
        "PictureBookSize_",
        "PorchTime_",
    ],
}


class BATActor:
    _pack: ActorPack
    _far_pack: ActorPack
    _texts: ActorTexts
    _flags: FlagStore

    def __init__(self, pack: Union[Path, str]) -> None:
        self._pack = ActorPack()
        self._pack.from_actor(pack)
        if isinstance(pack, Path):
            if pack.with_name(f"{pack.name}_Far").exists():
                self._far_pack = ActorPack()
                self._far_pack.from_actor(Path(f"{pack.name}_Far"))
        self._texts = ActorTexts(Path(pack), self._pack.get_link("ProfileUser"))

    def get_name(self) -> str:
        return self._pack.get_name()

    def set_name(self, name: str) -> None:
        self._pack.set_name(name)
        self._flags.remove_all()
        actor_type = name.split("_")[0]
        if actor_type in FLAG_TYPES:
            for prefix in FLAG_TYPES[actor_type]:
                if "Is" in prefix:
                    ftype = "bool_data"
                else:
                    ftype = "s32_data"
                flag = FLAG_CLASSES[prefix]()
                flag.set_data_name(f"{prefix}{name}")
                flag.use_name_to_override_params()
                self._flags.add(ftype, flag)

    def get_link(self, link: str) -> str:
        return self._pack.get_link(link)

    def set_link(self, link: str, linkref: str) -> bool:
        if self._far_pack:
            if link == "LifeConditionUser" and linkref == "Dummy":
                return False
            self._pack.set_link(link, linkref)
            if link in FAR_LINKS:
                self._far_pack.set_link(link, linkref)
            return True
        else:
            self._pack.set_link(link, linkref)
            return True

    def get_has_far(self) -> bool:
        return self._pack.get_has_far()

    def set_has_far(self, enabled: bool, pack: Path = Path()) -> bool:
        if enabled and not self._pack.get_has_far():
            self._far_pack = ActorPack()
            for link in [link for link in FAR_LINKS if not link == "LifeConditionUser"]:
                linkref = self._pack.get_link(link)
                if not linkref == "Dummy":
                    self._far_pack.set_link_data(link, self._pack.get_link_data(link))
            self._far_pack.set_name(f"{self._pack.get_name()}_Far")
            self._pack.set_has_far(True)
            return True
        if not enabled:
            del self._far_pack
            self._pack.set_has_far(False)
            return True
        return False

    def get_link_data(self, link: str) -> str:
        return self._pack.get_link_data(link)

    def set_link_data(self, link: str, data: str) -> None:
        self._pack.set_link_data(link, data)

    def get_tags(self) -> str:
        return self._pack.get_tags()

    def set_tags(self, tags: str) -> None:
        self._pack.set_tags(tags)

    def get_actorlink(self) -> oead.aamp.ParameterIO:
        return self._pack.get_actorlink()

    def get_texts(self) -> Dict[str, str]:
        return self._texts.get_texts()

    def set_texts(self, texts: Dict[str, str]) -> None:
        self._texts.set_texts(texts)

    def save(self, root_dir: str, be: bool) -> None:
        actor_path = Path(f"{root_dir}/Actor/Pack/{self._pack.get_name()}.sbactorpack")
        yaz0_bytes = oead.yaz0.compress(self._pack.get_bytes(be))
        with actor_path.open("wb") as a_file:
            a_file.write(yaz0_bytes)

        hash = crc32(self._pack.get_name().encode("utf-8"))
        info = self._pack.get_info()

        if self._pack.get_has_far():
            actor_path = Path(f"{root_dir}/Actor/Pack/{self._far_pack.get_name()}.sbactorpack")
            yaz0_bytes = oead.yaz0.compress(self._far_pack.get_bytes(be))
            with actor_path.open("wb") as a_file:
                a_file.write(yaz0_bytes)

            far_hash = crc32(self._far_pack.get_name().encode("utf-8"))
            far_info = self._far_pack.get_info()

        actorinfo_path = Path(f"{root_dir}/Actor/ActorInfo.product.sbyml")
        actorinfo_load_path = actorinfo_path
        if not actorinfo_load_path.exists():
            actorinfo_load_path = Path(util.find_file(Path("Actor/ActorInfo.product.sbyml")))
        actorinfo = oead.byml.from_binary(oead.yaz0.decompress(actorinfo_load_path.read_bytes()))

        hashes = [int(h) for h in actorinfo["Hashes"]]
        hashes.append(hash)
        if self._pack.get_has_far():
            hashes.append(far_hash)
        actorinfo["Hashes"] = oead.byml.Array(
            [oead.U32(h) if h > 2147483647 else oead.S32(h) for h in sorted(hashes)]
        )

        actorinfo["Actors"].append(info)
        if self._pack.get_has_far():
            actorinfo["Actors"].append(far_info)
        actorinfo["Actors"] = sorted(
            actorinfo["Actors"], key=lambda a: crc32(a["name"].encode("utf-8"))
        )

        with actorinfo_path.open("wb") as ai_file:
            ai_file.write(oead.yaz0.compress(oead.byml.to_binary(actorinfo)))

        self._texts.write(root_dir, be)

        bootup_path = Path(f"{root_dir}/Pack/Bootup.pack")
        if not bootup_path.exists():
            bootup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(util.find_file(Path("Pack/Bootup.pack")), bootup_path)

        gamedata_sarc = util.get_gamedata_sarc(bootup_path)
        for bgdata_name, bgdata_hash in map(util.unpack_oead_file, gamedata_sarc.get_files()):
            self._flags.add_flags_from_Hash(bgdata_name, bgdata_hash, False)

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
