import oead
import pymsyt
from pathlib import Path
from typing import Dict

from . import util


class ActorTexts:
    _texts: Dict[str, str]
    _misc_texts: dict
    _actor_name: str
    _profile: str
    _group_count: int
    _atr_unknown: int

    def __init__(self, pack: Path, profile: str):
        self._texts = {}
        self._misc_texts = {}
        self._actor_name = pack.stem
        self._profile = profile
        root_dir = Path(str(pack).split("Actor")[0])
        settings = util.BatSettings()
        lang = settings.get_setting("lang")
        text_pack = root_dir / f"Pack/Bootup_{lang}.pack"
        if not text_pack.exists():
            root_dir = Path(settings.get_setting("update_dir"))
            text_pack = root_dir / f"Pack/Bootup_{lang}.pack"
        text_sarc = oead.Sarc(text_pack.read_bytes())
        message = f"Message/Msg_{lang}.product.ssarc"
        message_sarc = oead.Sarc(oead.yaz0.decompress(text_sarc.get_file(message).data))
        msbt = message_sarc.get_file(f"ActorType/{self._profile}.msbt")
        if not msbt:
            return
        temp = settings.get_data_dir() / "temp.msbt"
        with temp.open("wb") as t_file:
            t_file.write(msbt.data)
        msyt = pymsyt.parse_msbt(temp)
        del text_sarc
        del message_sarc
        del msbt
        temp.unlink()
        self._group_count = msyt["group_count"]
        self._atr_unknown = msyt["atr1_unknown"]
        for entry in msyt["entries"]:
            if self._actor_name in entry:
                entry_name = entry.replace(f"{self._actor_name}_", "")
                for control_type in msyt["entries"][entry]["contents"]:
                    if "text" in control_type:
                        self._texts[entry_name] = control_type["text"]
            else:
                self._misc_texts[entry] = msyt["entries"][entry]

    def set_texts(self, texts: Dict[str, str]) -> None:
        self._texts = texts

    def get_texts(self) -> Dict[str, str]:
        return self._texts

    def write(self, root_str: str, be: bool) -> None:
        if self._texts:
            settings = util.BatSettings()
            msyt = {
                "group_count": self._group_count,
                "atr1_unknown": self._atr_unknown,
                "entries": {},
            }
            for entry, data in self._misc_texts.items():
                msyt["entries"][entry] = data  # type:ignore[index]
            for entry, text in self._texts.items():
                entry_name = f"{self._actor_name}_{entry}"
                msyt["entries"][entry_name] = {"contents": [{"text": text}]}  # type:ignore[index]
            platform = "wiiu" if be else "switch"
            temp = settings.get_data_dir() / "temp.msbt"
            pymsyt.write_msbt(msyt, temp, platform=platform)
            msbt = temp.read_bytes()
            temp.unlink()
            lang = settings.get_setting("lang")
            text_pack = Path(f"{root_str}/Pack/Bootup_{lang}.pack")
            text_pack_load = text_pack
            if not text_pack_load.exists():
                text_pack_load = Path(util.find_file(Path(f"Pack/Bootup_{lang}.pack")))
            text_sarc = oead.Sarc(text_pack_load.read_bytes())
            text_sarc_writer = oead.SarcWriter.from_sarc(text_sarc)
            message = f"Message/Msg_{lang}.product.ssarc"
            message_sarc = oead.Sarc(oead.yaz0.decompress(text_sarc.get_file(message).data))
            message_sarc_writer = oead.SarcWriter.from_sarc(message_sarc)
            msbt_name = f"ActorType/{self._profile}.msbt"
            message_sarc_writer.files[msbt_name] = msbt
            message_bytes = message_sarc_writer.write()[1]
            text_sarc_writer.files[message] = oead.yaz0.compress(message_bytes)
            with text_pack.open("wb") as t_file:
                t_file.write(text_sarc_writer.write()[1])
