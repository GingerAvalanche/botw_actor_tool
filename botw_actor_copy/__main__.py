import argparse
import shutil
from pathlib import Path

from bcml import util as bcmlutil
from . import actorinfo, actorpack, bootup, language


def generate_path(to_generate: Path) -> str:
    if not to_generate.exists():
        to_generate.mkdir(parents=True, exist_ok=True)
    return str(to_generate).replace("\\", "/")


def main() -> None:
    parser = argparse.ArgumentParser(description="Tool for copying actors in LoZ:BotW")
    parser.add_argument("directory", help="The root folder of your mod")
    parser.add_argument("source_actor", help="Name of the actor to copy")
    parser.add_argument("target_actor", help="Name of the actor to create")
    parser.add_argument(
        "-b", "--bigendian", help="Use big endian mode (for Wii U)", action="store_true",
    )

    args = parser.parse_args()
    directory: Path = Path(args.directory)
    if not (directory / "content").exists():
        dir = str(directory).replace("\\", "/")
        raise FileNotFoundError(f"Could not find folder named 'content' inside {dir}")
    try:
        source_pack = bcmlutil.get_game_file(f"Actor/Pack/{args.source_actor}.sbactorpack")
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Could not find source actor {args.source_actor} in your game/update files."
        )
    actorpack_dir: str = generate_path(directory / "content" / "Actor" / "Pack")
    model_dir: str = generate_path(directory / "content" / "Model")
    pack_dir: str = generate_path(directory / "content" / "Pack")
    icon_dir: str = generate_path(directory / "content" / "UI" / "StockItem")

    actorpack.copy_actor(directory, args.source_actor, args.target_actor, args.bigendian)

    actorinfo_path: Path = directory / "content" / "Actor" / "ActorInfo.product.sbyml"
    actorinfo.copy_actor(actorinfo_path, args.source_actor, args.target_actor, args.bigendian)

    bootup_path: Path = directory / "content" / "Pack" / "Bootup.pack"
    bootup.copy_actor(bootup_path, args.source_actor, args.target_actor, args.bigendian)

    lang_path: Path = directory / "content" / "Pack" / f"Bootup_{bcmlutil.get_settings('lang')}.pack"
    language.copy_actor(lang_path, args.source_actor, args.target_actor, args.bigendian)

    try:
        if not Path(directory / "content" / "Model" / f"{args.target_actor}.sbfres").exists():
            shutil.copy(
                bcmlutil.get_game_file(f"Model/{args.source_actor}.sbfres"),
                directory / "content" / "Model" / f"{args.target_actor}.sbfres",
            )
        if args.bigendian:
            if not Path(
                directory / "content" / "Model" / f"{args.target_actor}.Tex1.sbfres"
            ).exists():
                shutil.copy(
                    bcmlutil.get_game_file(f"Model/{args.source_actor}.Tex1.sbfres"),
                    directory / "content" / "Model" / f"{args.target_actor}.Tex1.sbfres",
                )
                shutil.copy(
                    bcmlutil.get_game_file(f"Model/{args.source_actor}.Tex2.sbfres"),
                    directory / "content" / "Model" / f"{args.target_actor}.Tex2.sbfres",
                )
        else:
            if not Path(
                directory / "content" / "Model" / f"{args.target_actor}.Tex.sbfres"
            ).exists():
                shutil.copy(
                    bcmlutil.get_game_file(f"Model/{args.source_actor}.Tex.sbfres"),
                    directory / "content" / "Model" / f"{args.target_actor}.Tex.sbfres",
                )
    except FileNotFoundError:
        print(
            f"{args.source_actor} seems to use a different actor's model, skipping model copy..."
        )
        pass

    try:
        shutil.copy(
            bcmlutil.get_game_file(f"UI/StockItem/{args.source_actor}.sbitemico"),
            directory / "content" / "UI" / "StockItem" / f"{args.target_actor}.sbitemico",
        )
    except FileNotFoundError:
        print(f"{args.source_actor} seems to use a different actor's icon, skipping icon copy...")
        pass
