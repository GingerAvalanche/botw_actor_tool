import shutil
from pathlib import Path

from bcml import util as bcmlutil
from . import util


def copy_actor(bootup_path: Path, source_actor: str, target_actor: str, big_endian: bool):
    return
    if not bootup_path.exists():
        bootup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(bcmlutil.get_game_file("Pack/Bootup.pack"), bootup_path)
    bootup_dir = str(bootup_path).replace("\\", "/")

    util.make_bgdict(bootup_dir)
    util.make_svdict(bootup_dir)

    files_to_write: list = []
    files_to_write.append("GameData/gamedata.ssarc")
    files_to_write.append("GameData/savedataformat.ssarc")
    datas_to_write: list = []
    datas_to_write.append(bcmlutil.compress(util.make_new_gamedata(big_endian)))
    datas_to_write.append(bcmlutil.compress(util.make_new_savedata(big_endian)))
    util.inject_files_into_bootup(bootup_path, files_to_write, datas_to_write)
