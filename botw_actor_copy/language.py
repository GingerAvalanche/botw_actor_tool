import shutil
from pathlib import Path

from bcml import util as bcmlutil
from . import util


def copy_actor(actorinfo_path: Path, source_actor: str, target_actor: str, big_endian: bool):
    return
    if not actorinfo_path.exists():
        shutil.copy(bcmlutil.get_game_file("Actor/ActorInfo.product.sbyml"), actorinfo_path)
    actorinfo_dir = str(actorinfo_path).replace("\\", "/")
