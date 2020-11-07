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
        root_dir = pack.parent
        while True:
            if (root_dir / "Actor").exists() or (
                not root_dir.stem == "Actor" and (root_dir / "Pack").exists()
            ):
                break
            root_dir = root_dir.parent
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
            self._misc_texts[entry] = msyt["entries"][entry]

    def set_texts(self, texts: Dict[str, str]) -> None:
        self._texts = texts

    def get_texts(self) -> Dict[str, str]:
        return self._texts

    def set_actor_name(self, name: str) -> None:
        self._actor_name = name

    def write(self, root_str: str, be: bool) -> None:
        if self._texts:
            for entry, text in self._texts.items():
                entry_name = f"{self._actor_name}_{entry}"
                self._misc_texts[entry_name] = {"contents": [{"text": text}]}  # type:ignore[index]

            settings = util.BatSettings()
            msyt = {
                "group_count": self._group_count,
                "atr1_unknown": self._atr_unknown,
                "entries": {},
            }
            for entry, data in self._misc_texts.items():
                msyt["entries"][entry] = data  # type:ignore[index]
            platform = "wiiu" if be else "switch"
            temp = settings.get_data_dir() / "temp.msbt"
            pymsyt.write_msbt(msyt, temp, platform=platform)
            msbt = temp.read_bytes()
            temp.unlink()
            lang = settings.get_setting("lang")
            text_pack = Path(f"{root_str}/Pack/Bootup_{lang}.pack")
            text_pack_load = text_pack
            if not text_pack.exists():
                text_pack.parent.mkdir(parents=True, exist_ok=True)
                text_pack.touch()
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
            text_pack.write_bytes(text_sarc_writer.write()[1])
