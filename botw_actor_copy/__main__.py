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
    parser.add_argument(
        "-0", "--DamageParamUser", help="Force renaming of bdmgparam", action="store_true",
    )
    parser.add_argument(
        "-1", "--DropTableUser", help="Force renaming of bdrop", action="store_true",
    )
    parser.add_argument(
        "-2", "--GParamUser", help="Force renaming of bgparamlist", action="store_true",
    )
    parser.add_argument(
        "-3", "--LifeConditionUser", help="Force renaming of blifecondition", action="store_true",
    )
    parser.add_argument(
        "-4", "--ModelUser", help="Force renaming of bmodellist", action="store_true",
    )
    parser.add_argument(
        "-5", "--PhysicsUser", help="Force renaming of bphysics", action="store_true",
    )
    parser.add_argument(
        "-6", "--RecipeUser", help="Force renaming of brecipe", action="store_true",
    )
    parser.add_argument(
        "-7", "--ShopDataUser", help="Force renaming of bshop", action="store_true",
    )
    parser.add_argument(
        "-8", "--UMiiUser", help="Force renaming of bumii", action="store_true",
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
    basics: dict = {
        "source_actor": args.source_actor,
        "target_actor": args.target_actor,
        "bigendian": args.bigendian,
    }
    force: dict = {
        "DamageParamUser": args.DamageParamUser,
        "DropTableUser": args.DropTableUser,
        "GParamUser": args.GParamUser,
        "LifeConditionUser": args.LifeConditionUser,
        "ModelUser": args.ModelUser,
        "PhysicsUser": args.PhysicsUser,
        "RecipeUser": args.RecipeUser,
        "ShopDataUser": args.ShopDataUser,
        "UMiiUser": args.UMiiUser,
    }

    actorpack.copy_actor(directory, basics, force)

    actorinfo_path: Path = directory / "content" / "Actor" / "ActorInfo.product.sbyml"
    actorinfo.copy_actor(actorinfo_path, basics, actorpack.bfres_name)

    bootup_path: Path = directory / "content" / "Pack" / "Bootup.pack"
    bootup.copy_actor(bootup_path, basics)

    lang_path: Path = directory / "content" / "Pack" / f"Bootup_{bcmlutil.get_settings('lang')}.pack"
    language.copy_actor(lang_path, basics)

    path: str
    if actorpack.bfres_name == "":
        path = f"Model/{args.source_actor}.sbfres"
    elif force["ModelUser"] and not actorpack.bfres_name == "":
        path = f"Model/{actorpack.bfres_name}.sbfres"
    try:
        if not Path(directory / "content" / "Model" / f"{args.target_actor}.sbfres").exists():
            shutil.copy(
                bcmlutil.get_game_file(path),
                directory / "content" / "Model" / f"{args.target_actor}.sbfres",
            )
    except FileNotFoundError:
        print(f"Could not find {args.source_actor}'s model. Skipping model copy...")
        pass

    if actorpack.bfres_name == "":
        path = args.source_actor
    elif force["ModelUser"] and not actorpack.bfres_name == "":
        path = actorpack.bfres_name
    try:
        if args.bigendian:
            if not Path(
                directory / "content" / "Model" / f"{args.target_actor}.Tex1.sbfres"
            ).exists():
                shutil.copy(
                    bcmlutil.get_game_file(f"Model/{path}.Tex1.sbfres"),
                    directory / "content" / "Model" / f"{args.target_actor}.Tex1.sbfres",
                )
                shutil.copy(
                    bcmlutil.get_game_file(f"Model/{path}.Tex2.sbfres"),
                    directory / "content" / "Model" / f"{args.target_actor}.Tex2.sbfres",
                )
        else:
            if not Path(
                directory / "content" / "Model" / f"{args.target_actor}.Tex.sbfres"
            ).exists():
                shutil.copy(
                    bcmlutil.get_game_file(f"Model/{path}.Tex.sbfres"),
                    directory / "content" / "Model" / f"{args.target_actor}.Tex.sbfres",
                )
    except FileNotFoundError:
        print(
            f"Could not find {args.source_actor}'s textures. Was the bigendian flag set wrong? Skipping texture copy..."
        )
        pass

    if actorpack.icon_name == "":
        path = f"UI/StockItem/{args.source_actor}.sbitemico"
    elif force["ModelUser"] and not actorpack.icon_name == "":
        path = f"UI/StockItem/{actorpack.icon_name}.sbitemico"
    try:
        shutil.copy(
            bcmlutil.get_game_file(path),
            directory / "content" / "UI" / "StockItem" / f"{args.target_actor}.sbitemico",
        )
    except FileNotFoundError:
        print(f"{args.source_actor} doesn't use an icon, skipping icon copy...")
        pass
