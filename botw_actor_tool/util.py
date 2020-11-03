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

from math import ceil, isclose
from pathlib import Path
from platform import system
from typing import Union
import configparser
import os
import wx

import oead

from . import BGDATA_MAPPING
from .store import FlagStore


RESIDENT_ACTORS = [
    "GameROMPlayer",
    "Dm_Npc_Gerudo_HeroSoul_Kago",
    "Dm_Npc_Goron_HeroSoul_Kago",
    "Dm_Npc_Rito_HeroSoul_Kago",
    "Dm_Npc_Zora_HeroSoul_Kago",
    "Dm_Npc_RevivalFairy",
    "PlayerStole2",
    "WakeBoardRope",
    "Armor_Default_Extra_00",
    "Armor_Default_Extra_01",
    "Item_Conductor",
    "Animal_Insect_X",
    "Animal_Insect_A",
    "Animal_Insect_B",
    "Animal_Insect_M",
    "Animal_Insect_S",
    "Explode",
    "NormalArrow",
    "FireArrow",
    "IceArrow",
    "ElectricArrow",
    "BombArrow_A",
    "AncientArrow",
    "BrightArrow",
    "BrightArrowTP",
    "RemoteBomb",
    "RemoteBomb2",
    "RemoteBombCube",
    "RemoteBombCube2",
    "Item_Magnetglove",
    "Obj_IceMakerBlock",
    "CarryBox",
    "PlayerShockWave",
    "FireRodLv1Fire",
    "FireRodLv2Fire",
    "FireRodLv2FireChild",
    "ThunderRodLv1Thunder",
    "ThunderRodLv2Thunder",
    "ThunderRodLv2ThunderChild",
    "IceRodLv1Ice",
    "IceRodLv2Ice",
    "Animal_Insect_H",
    "Animal_Insect_F",
    "Item_Material_07",
    "Item_Material_03",
    "Item_Material_01",
    "Item_Ore_F",
]
LINKS = [
    "ActorNameJpn",
    "AIProgramUser",
    "AIScheduleUser",
    "ASUser",
    "AttentionUser",
    "AwarenessUser",
    "BoneControlUser",
    "ActorCaptureUser",
    "ChemicalUser",
    "DamageParamUser",
    "DropTableUser",
    "ElinkUser",
    "GParamUser",
    "LifeConditionUser",
    "LODUser",
    "ModelUser",
    "PhysicsUser",
    "ProfileUser",
    "RgBlendWeightUser",
    "RgConfigListUser",
    "RecipeUser",
    "ShopDataUser",
    "SlinkUser",
    "UMiiUser",
    "XlinkUser",
    "AnimationInfo",
]
AAMP_LINK_REFS: dict = {
    # "ActorNameJpn",
    "AIProgramUser": ("AIProgram", ".baiprog"),
    "ASUser": ("ASList", ".baslist"),
    "AttentionUser": ("AttClientList", ".batcllist"),
    "AwarenessUser": ("Awareness", ".bawareness"),
    "BoneControlUser": ("BoneControl", ".bbonectrl"),
    # "ActorCaptureUser",
    "ChemicalUser": ("Chemical", ".bchemical"),
    "DamageParamUser": ("DamageParam", ".bdmgparam"),
    "DropTableUser": ("DropTable", ".bdrop"),
    # "ElinkUser",
    "GParamUser": ("GeneralParamList", ".bgparamlist"),
    "LifeConditionUser": ("LifeCondition", ".blifecondition"),
    "LODUser": ("LOD", ".blod"),
    "ModelUser": ("ModelList", ".bmodellist"),
    "PhysicsUser": ("Physics", ".bphysics"),
    # "ProfileUser",
    "RgBlendWeightUser": ("RagdollBlendWeight", ".brgbw"),
    "RgConfigListUser": ("RagdollConfigList", ".brgconfiglist"),
    "RecipeUser": ("Recipe", ".brecipe"),
    "ShopDataUser": ("ShopData", ".bshop"),
    # "SlinkUser",
    "UMiiUser": ("UMii", ".bumii"),
    # "XlinkUser",
}
BYML_LINK_REFS: dict = {
    "AIScheduleUser": ("AISchedule", ".baischedule"),
    "AnimationInfo": ("AnimationInfo", ".baniminfo"),
}
LANGUAGES = [
    "USen",
    "EUen",
    "USfr",
    "USes",
    "EUde",
    "EUes",
    "EUfr",
    "EUit",
    "EUnl",
    "EUru",
    "CNzh",
    "JPja",
    "KRko",
    "TWzh",
]


def _set_dark_mode(window: wx.Window, enabled: bool) -> None:
    if enabled:
        bg = wx.Colour(40, 40, 40)
        fg = wx.Colour(255, 255, 255)
    else:
        bg = wx.NullColour
        fg = wx.NullColour
    window.SetBackgroundColour(bg)
    window.SetForegroundColour(fg)
    for child in window.Children:
        if isinstance(child, wx.stc.StyledTextCtrl):
            set_stc_dark_mode(child, enabled)
        else:
            _set_dark_mode(child, enabled)
    window.Refresh()


def set_stc_dark_mode(stc: wx.stc.StyledTextCtrl, enabled: bool) -> None:
    if enabled:
        default = "fore:#FFFFFF"
        line = "fore:#FFFFFF"
        comment = "fore:#00FF00"
        identifier = "fore:#FF0000"
        keyword = "fore:#FFFFFF"
        number = "fore:#FFBBBB"
        bg = "back:#202020"
        caret = wx.Colour(255, 255, 255)
    else:
        default = "fore:#000000"
        line = "fore:#000000"
        comment = "fore:#FF00FF"
        identifier = "fore:#2020FF"
        keyword = "fore:#000000"
        number = "fore:005555"
        bg = "back:#FFFFFF"
        caret = wx.Colour(0, 0, 0)
    face = "face:Consolas"
    stc.SetLexer(wx.stc.STC_LEX_YAML)
    stc.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, f"{default},{bg},{face}")
    stc.StyleSetSpec(wx.stc.STC_STYLE_LINENUMBER, f"{line},{bg},{face}")
    stc.StyleSetSpec(wx.stc.STC_YAML_DEFAULT, f"{default},{bg},{face}")
    stc.StyleSetSpec(wx.stc.STC_YAML_COMMENT, f"{comment},{bg},{face}")
    stc.StyleSetSpec(wx.stc.STC_YAML_IDENTIFIER, f"bold,{identifier},{bg},{face}")
    stc.StyleSetSpec(wx.stc.STC_YAML_KEYWORD, f"{keyword},{bg},{face}")
    stc.StyleSetSpec(wx.stc.STC_YAML_NUMBER, f"bold,{number},{bg},{face}")
    stc.StyleSetSpec(wx.stc.STC_YAML_REFERENCE, f"{default},{bg},{face}")
    stc.StyleSetSpec(wx.stc.STC_YAML_DOCUMENT, f"{default},{bg},{face}")
    stc.StyleSetSpec(wx.stc.STC_YAML_TEXT, f"{default},{bg},{face}")
    stc.StyleSetSpec(wx.stc.STC_YAML_ERROR, f"{default},{bg},{face}")
    stc.StyleSetSpec(wx.stc.STC_YAML_OPERATOR, f"{default},{bg},{face}")
    stc.SetCaretForeground(caret)


def get_gamedata_sarc(bootup_path: Path) -> oead.Sarc:
    bootup_sarc = oead.Sarc(bootup_path.read_bytes())
    gamedata_sarc = oead.Sarc(
        oead.yaz0.decompress(bootup_sarc.get_file("GameData/gamedata.ssarc").data)
    )
    return gamedata_sarc


def get_last_two_savedata_files(bootup_path) -> list:
    bootup_sarc = oead.Sarc(bootup_path.read_bytes())
    savedata_sarc = oead.Sarc(
        oead.yaz0.decompress(bootup_sarc.get_file("GameData/savedataformat.ssarc").data)
    )
    savedata_writer = oead.SarcWriter.from_sarc(savedata_sarc)
    idx = 0
    files = []
    while True:
        try:
            savedata_writer.files[f"/saveformat_{idx+2}.bgsvdata"]
            idx += 1
        except KeyError:
            files.append(savedata_writer.files[f"/saveformat_{idx}.bgsvdata"])
            files.append(savedata_writer.files[f"/saveformat_{idx+1}.bgsvdata"])
            return files


def make_new_gamedata(store: FlagStore, big_endian: bool) -> bytes:
    bgwriter = oead.SarcWriter(
        endian=oead.Endianness.Big if big_endian else oead.Endianness.Little
    )
    for prefix, data_type in BGDATA_MAPPING.items():
        bgdata_array = store.flags_to_bgdata_Array(prefix)
        num_files = ceil(len(bgdata_array) / 4096)
        for idx in range(num_files):
            start = idx * 4096
            end = (idx + 1) * 4096
            if end > len(bgdata_array):
                end = len(bgdata_array)
            bgwriter.files[f"/{prefix}_{idx}.bgdata"] = oead.byml.to_binary(
                oead.byml.Hash({data_type: bgdata_array[start:end]}), big_endian
            )
    return bgwriter.write()[1]


def make_new_savedata(store: FlagStore, big_endian: bool, orig_files: list) -> bytes:
    svwriter = oead.SarcWriter(
        endian=oead.Endianness.Big if big_endian else oead.Endianness.Little
    )
    svdata_array = store.flags_to_svdata_Array()
    num_files = ceil(len(svdata_array) / 8192)
    for idx in range(num_files):
        start = idx * 8192
        end = (idx + 1) * 8192
        if end > len(svdata_array):
            end = len(svdata_array)
        svwriter.files[f"/saveformat_{idx}.bgsvdata"] = oead.byml.to_binary(
            oead.byml.Hash(
                {
                    "file_list": oead.byml.Array(
                        [
                            {
                                "IsCommon": False,
                                "IsCommonAtSameAccount": False,
                                "IsSaveSecureCode": True,
                                "file_name": "game_data.sav",
                            },
                            oead.byml.Array(svdata_array[start:end]),
                        ]
                    ),
                    "save_info": oead.byml.Array(
                        [
                            {
                                "directory_num": oead.S32(num_files + 2),
                                "is_build_machine": True,
                                "revision": oead.S32(18203),
                            }
                        ]
                    ),
                }
            ),
            big_endian,
        )
    svwriter.files[f"/saveformat_{num_files}.bgsvdata"] = orig_files[0]
    svwriter.files[f"/saveformat_{num_files+1}.bgsvdata"] = orig_files[1]
    return svwriter.write()[1]


def inject_files_into_bootup(bootup_path: Path, files: list, datas: list):
    sarc_data = bootup_path.read_bytes()
    yaz = sarc_data[0:4] == b"Yaz0"
    if yaz:
        sarc_data = oead.yaz0.decompress(sarc_data)
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
    bootup_path.write_bytes(new_bytes if not yaz else oead.yaz0.compress(new_bytes))
    del new_bytes


def inject_bytes_into_sarc(sarc: Path, name: str, data: bytes) -> None:
    sarc_data = sarc.read_bytes()
    yaz = sarc_data[0:4] == b"Yaz0"
    if yaz:
        sarc_data = oead.yaz0.decompress(sarc_data)
    sarc_writer = oead.SarcWriter.from_sarc(oead.Sarc(sarc_data))
    del sarc_data
    sarc_writer.files[name] = data
    new_bytes = sarc_writer.write()[1]
    del sarc_writer
    sarc.write_bytes(new_bytes if not yaz else oead.yaz0.compress(new_bytes))
    del new_bytes


def unpack_oead_file(f: oead.File) -> tuple:
    return (f.name, oead.byml.from_binary(f.data))


def find_file(rel_path: Path) -> Union[Path, str]:
    settings = BatSettings()
    if rel_path.stem in RESIDENT_ACTORS:
        filepath = settings.get_setting("update_dir").replace("\\", "/")
        internal_path = str(rel_path).replace("\\", "/")
        return f"{filepath}/Pack/TitleBG.pack//{internal_path}"
    else:
        if (Path(settings.get_setting("update_dir")) / rel_path).exists():
            return Path(settings.get_setting("update_dir")) / rel_path
        elif (Path(settings.get_setting("dlc_dir")) / rel_path).exists():
            return Path(settings.get_setting("dlc_dir")) / rel_path
        elif (Path(settings.get_setting("game_dir")) / rel_path).exists():
            return Path(settings.get_setting("game_dir")) / rel_path
        else:
            raise FileNotFoundError(f"{rel_path} doesn't seem to exist.")


def unyaz_if_needed(data: bytes) -> bytes:
    if data[0:4] == b"Yaz0":
        return oead.yaz0.decompress(data)
    else:
        return data


def S32_equality(s: oead.S32, i: int) -> bool:
    return int(s) == i


def F32_equality(f: oead.F32, i: int) -> bool:
    return isclose(f, i, rel_tol=1e-5)


def FSS_equality(
    s0: Union[
        str,
        oead.FixedSafeString16,
        oead.FixedSafeString32,
        oead.FixedSafeString48,
        oead.FixedSafeString64,
        oead.FixedSafeString128,
        oead.FixedSafeString256,
    ],
    s1: str,
) -> bool:
    return str(s0) == s1


class BatSettings:
    _settings: configparser.ConfigParser

    def __init__(self) -> None:
        self._settings = configparser.ConfigParser()
        if (self.get_data_dir() / "settings.ini").exists():
            with (self.get_data_dir() / "settings.ini").open("r", encoding="utf-8") as s_file:
                self._settings.read_file(s_file)
        else:
            self._settings.read_dict(
                {
                    "General": {
                        "game_dir": "",
                        "update_dir": "",
                        "dlc_dir": "",
                        "dark_theme": False,
                        "lang": "USen",
                    },
                    "Window": {"WinPosX": "0", "WinPosY": "0", "WinHeight": "0", "WinWidth": "0"},
                }
            )

    def get_data_dir(self) -> Path:
        if system() == "Windows":
            data_dir = Path(os.path.expandvars("%LOCALAPPDATA%")) / "botw_actor_tool"
        else:
            data_dir = Path.home() / ".config" / "botw_actor_tool"
        if not data_dir.exists():
            data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir

    def set_setting(self, name: str, value: str) -> None:
        self._settings["General"][name] = value

    def get_setting(self, name: str) -> str:
        return self._settings["General"][name]

    def save_settings(self) -> None:
        settings_path = self.get_data_dir() / "settings.ini"
        with settings_path.open("w", encoding="utf-8") as s_file:
            self._settings.write(s_file)

    def set_dark_mode(self, enabled: bool) -> None:
        setting = "True" if enabled else "False"
        self.set_setting("dark_theme", setting)

    def get_dark_mode(self) -> bool:
        return True if self.get_setting("dark_theme") == "True" else False

    def get_win_pos(self) -> tuple:
        return (int(self._settings["Window"]["WinPosX"]), int(self._settings["Window"]["WinPosY"]))

    def set_win_pos(self, pos: tuple) -> None:
        if not "Window" in self._settings:
            self._settings["Window"] = {}
        self._settings["Window"]["WinPosX"] = str(pos[0])
        self._settings["Window"]["WinPosY"] = str(pos[1])

    def get_win_size(self) -> tuple:
        return (
            int(self._settings["Window"]["WinHeight"]),
            int(self._settings["Window"]["WinWidth"]),
        )

    def set_win_size(self, size: tuple) -> None:
        self._settings["Window"]["WinHeight"] = str(size[0])
        self._settings["Window"]["WinWidth"] = str(size[1])

    def validate_game_dir(self, game_path: Path) -> bool:
        if not game_path or not game_path.is_dir():
            return False
        if not (game_path / "Pack" / "Dungeon000.pack").exists():
            return False
        return True

    def validate_update_dir(self, update_path: Path) -> bool:
        if not update_path or not update_path.is_dir():
            return False
        if not (
            update_path / "Actor" / "Pack" / "ActorObserverByActorTagTag.sbactorpack"
        ).exists():
            return False
        return True

    def validate_dlc_dir(self, dlc_path: Path) -> bool:
        if not dlc_path or not dlc_path.is_dir():
            return False
        if not (dlc_path / "Pack" / "AocMainField.pack").exists():
            return False
        return True
