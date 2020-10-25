import oead
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from . import actorinfo, util


physics_ext = {
    "Cloth": ".hkcl",
    "Ragdoll": ".hkrg",
    "RigidBody": ".hkrb",
    "StaticCompound": ".hksc",
    "SupportBone": ".bphyssb",
}


class ActorPack:
    _actorname: str
    _aampfiles: Dict[str, oead.aamp.ParameterIO]
    _bymlfiles: Dict[str, oead.byml.Hash]
    _miscfiles: dict
    _info: oead.byml.Hash
    _links: dict
    _tags: list
    _misc_tags: list
    _has_far: bool
    _needs_info_update: bool
    _titlebg: bool

    def __init__(self) -> None:
        self._actorname = ""
        self._aampfiles = {}
        self._bymlfiles = {}
        self._miscfiles = {}
        self._info = oead.byml.Hash()
        self._links = {}
        self._tags = []
        self._misc_tags = []
        self._has_far = False
        self._needs_info_update = False
        self._titlebg = False

    def from_actor(self, pack: Union[Path, str]) -> None:
        handled_filenames = set()
        if isinstance(pack, str):
            self._titlebg = True
            pack_nests = pack.split("//")
            pack = Path(pack_nests[-1])
            titlebg = oead.Sarc(Path(pack_nests[0]).read_bytes())
            data = util.unyaz_if_needed(titlebg.get_file(pack_nests[-1]).data)
            actorinfo_path = (
                Path(pack_nests[0]).parent / "../Actor/ActorInfo.product.sbyml"
            ).resolve()
        else:
            data = util.unyaz_if_needed(pack.read_bytes())
            actorinfo_path = (pack.parent / "../ActorInfo.product.sbyml").resolve()
        self._actorname = pack.stem
        sarcdata = oead.Sarc(data)

        actorlink_name = f"Actor/ActorLink/{self._actorname}.bxml"
        actorlink = oead.aamp.ParameterIO.from_binary(sarcdata.get_file(actorlink_name).data)
        name_table = oead.aamp.get_default_name_table()
        for key in actorlink.objects:
            if name_table.get_name(key.hash, 0, 0) == "LinkTarget":
                for link in actorlink.objects[key].params:
                    linkstr = name_table.get_name(link.hash, 0, 0)
                    self._links[linkstr] = actorlink.objects["LinkTarget"].params[link].v
            elif name_table.get_name(key.hash, 0, 0) == "Tags":
                for tag in actorlink.objects[key].params:
                    self._tags.append(actorlink.objects["Tags"].params[tag].v)
            else:
                self._misc_tags.append({key: actorlink.objects[key]})
        handled_filenames.add(actorlink_name)

        for link in util.AAMP_LINK_REFS:
            folder, ext = util.AAMP_LINK_REFS[link]
            linkref = self._links[link]
            if linkref == "Dummy":
                continue
            filename = f"Actor/{folder}/{linkref}{ext}"
            filedata = sarcdata.get_file(filename).data
            self._aampfiles[link] = oead.aamp.ParameterIO.from_binary(filedata)
            handled_filenames.add(filename)

        for link in util.BYML_LINK_REFS:
            folder, ext = util.BYML_LINK_REFS[link]
            linkref = self._links[link]
            if linkref == "Dummy":
                continue
            filename = f"Actor/{folder}/{linkref}{ext}"
            filedata = sarcdata.get_file(filename).data
            self._aampfiles[link] = oead.byml.from_binary(filedata)
            handled_filenames.add(filename)

        for f in sarcdata.get_files():
            if not f.name in handled_filenames:
                self._miscfiles[f"{f.name}"] = bytes(f.data)

        if not actorinfo_path.exists():
            actorinfo_path = Path(util.find_file(Path("Actor/ActorInfo.product.sbyml")))
        actorinfo = oead.byml.from_binary(oead.yaz0.decompress(actorinfo_path.read_bytes()))
        for actor in actorinfo["Actors"]:
            if actor["name"] == self._actorname:
                self._info = actor
                break
        del actorinfo
        del actorinfo_path

    def get_name(self) -> str:
        return self._actorname

    def set_name(self, name: str) -> None:
        self._titlebg = False
        for link, linkref in self._links.items():
            if linkref == self._actorname:
                self._links[link] = name

        conversion_list = [
            (self._aampfiles, oead.aamp.ParameterIO),
            (self._bymlfiles, oead.byml),
        ]
        for i in range(len(conversion_list)):
            files, convert_type = conversion_list[i]
            for link, value in files.items():
                yaml = convert_type.to_text(value)
                if self._actorname in yaml:
                    new_yaml = yaml.replace(self._actorname, name)
                    files[link] = convert_type.from_text(new_yaml)
        for filename in self._miscfiles.keys():
            if self._actorname in filename:
                filedata = self._miscfiles[filename]
                self._miscfiles.pop(filename)
                new_filename = filename.replace(self._actorname, name)
                self._miscfiles[new_filename] = filedata
        self._actorname = name
        if "Armor_" in name and self._links["ModelUser"] == self._actorname:
            mlist = self._aampfiles["ModelUser"]
        self._needs_info_update = True

    def get_link(self, link: str) -> str:
        return self._links[link]

    def set_link(self, link: str, linkref: str) -> None:
        old_linkref = self._links[link]
        self._links[link] = linkref

        if util._link_to_tab_index(link) == -1:
            return

        if link in util.AAMP_LINK_REFS:
            folder, ext = util.AAMP_LINK_REFS[link]
            if old_linkref == "Dummy":
                self._aampfiles[link] = oead.aamp.ParameterIO()
            elif linkref == "Dummy":
                self._aampfiles.pop(link)
        elif link in util.BYML_LINK_REFS:
            folder, ext = util.BYML_LINK_REFS[link]
            if old_linkref == "Dummy":
                self._bymlfiles[link] = oead.byml.Hash()
            elif linkref == "Dummy":
                self._bymlfiles.pop(link)
        self._needs_info_update = True

    def get_link_data(self, link: str) -> str:
        linkref = self._links[link]
        if not linkref == "Dummy":
            if link in util.AAMP_LINK_REFS:
                return oead.aamp.ParameterIO.to_text(self._aampfiles[link])
            elif link in util.BYML_LINK_REFS:
                return oead.byml.to_text(self._bymlfiles[link])
        return ""

    def set_link_data(self, link: str, data: str) -> None:
        if link in util.AAMP_LINK_REFS:
            self._aampfiles[link] = oead.aamp.ParameterIO.from_text(data)
        elif link in util.BYML_LINK_REFS:
            self._bymlfiles[link] = oead.byml.from_text(data)
        self._needs_info_update = True

    def get_info(self) -> oead.byml.Hash:
        if self._needs_info_update:
            # TODO: This is messy, we shouldn't let someone else directly modify our property
            actorinfo.generate_actor_info(self, self._info)
            self._needs_info_update = False
        return self._info

    def get_tags(self) -> str:
        return ", ".join(self._tags)

    def set_tags(self, tags: str) -> None:
        self._needs_info_update = True
        self._tags = [tag for tag in tags.split(", ")]

    def get_actorlink(self) -> oead.aamp.ParameterIO:
        actorlink = oead.aamp.ParameterIO()
        actorlink.objects["LinkTarget"] = oead.aamp.ParameterObject()
        for link, linkref in self._links.items():
            actorlink.objects["LinkTarget"].params[link] = linkref
        if self._tags:
            actorlink.objects["Tags"] = oead.aamp.ParameterObject()
            for i in range(len(self._tags)):
                actorlink.objects["Tags"].params[f"Tag{i}"] = self._tags[i]
        if self._misc_tags:
            for tagset in self._misc_tags:
                for key in tagset:
                    actorlink.objects[key] = tagset[key]
        return actorlink

    def set_has_far(self, has_far: bool) -> None:
        self._has_far = has_far

    def get_has_far(self) -> bool:
        return self._has_far

    def get_bytes(self, be: bool) -> bytes:
        writer = oead.SarcWriter()
        endianness = oead.Endianness.Big if be else oead.Endianness.Little
        writer.set_endianness(endianness)

        filename = f"Actor/ActorLink/{self._actorname}.bxml"
        writer.files[filename] = oead.aamp.ParameterIO.to_binary(self.get_actorlink())

        for link, data in self._aampfiles.items():
            folder, ext = util.AAMP_LINK_REFS[link]
            filename = f"Actor/{folder}/{self.get_link(link)}{ext}"
            writer.files[filename] = oead.aamp.ParameterIO.to_binary(data)

        for link, data in self._bymlfiles.items():
            folder, ext = util.BYML_LINK_REFS[link]
            filename = f"Actor/{folder}/{self.get_link(link)}{ext}"
            writer.files[filename] = oead.byml.to_binary(data, be)

        for filename, data in self._miscfiles.items():
            writer.files[filename] = data

        return writer.write()[1]
