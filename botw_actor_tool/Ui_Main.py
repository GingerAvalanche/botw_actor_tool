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

import wx
from pathlib import Path
from typing import Union

from .actor import BATActor, try_retrieve_custom_file
from .Ui_Settings import UiSettingsPanel
from .Ui_ActorLink import UiActorLinkPanel
from .Ui_ActorSelect import UiActorSelect
from .Ui_TextEditor import UiTextEditor
from .Ui_Texts import UiTexts
from .util import (
    BatSettings,
    LINKS,
    _set_dark_mode,
    find_file,
)


def link_to_tab_index(link: str) -> int:
    # I am not proud...
    not_implemented = ["ElinkUser", "ProfileUser", "SlinkUser", "XlinkUser"]
    if link in not_implemented:
        return -1
    index = LINKS.index(link)
    if index == 0 or index == 7:
        return -1
    elif index > 7:
        return index - 1
    else:
        return index


class UiMainWindow(wx.Frame):
    _actor: BATActor
    _prevcontents: int
    _bound_events: list

    def __init__(self, *args, **kwargs) -> None:
        super(UiMainWindow, self).__init__(*args, **kwargs)
        settings = BatSettings()
        try:
            pos = settings.get_win_pos()
            self.SetPosition(wx.Point(pos[0], pos[1]))
            size = settings.get_win_size()
            self.SetSize(size[0], size[1])
        except KeyError:
            pass
        self._prevcontents = 0
        self._save_dir = ""
        self.InitUI()
        self.DarkMode()

    def InitUI(self) -> None:
        tabs = [
            "Actor Link",
            "AI Program",
            "AI Schedule",
            "AS",
            "Attention",
            "Awareness",
            "Bone Control",
            "Chemical",
            "Damage Param",
            "Drop Table",
            "Elink",
            "General Param",
            "Life Condition",
            "LOD",
            "Model",
            "Physics",
            "Profile",
            "Ragdoll Blend",
            "Ragdoll Config",
            "Recipe",
            "Shop Data",
            "Slink",
            "UMii",
            "Xlink",
            "Animation Info",
            "Texts",
            "Flags",
        ]
        self._menubar = wx.MenuBar()
        filemenu = wx.Menu()

        actorselectoption = filemenu.Append(
            wx.ID_ANY, "Open Vanilla Actor\tCtrl+N", "Open an actor from your game directory"
        )
        openoption = filemenu.Append(
            wx.ID_OPEN, "Open Mod Actor\tCtrl+O", "Open an actor from a mod directory"
        )
        filemenu.AppendSeparator()
        saveoption = filemenu.Append(
            wx.ID_ANY, "Save Actor\tCtrl+S", "Save the current actor files to a mod directory"
        )
        filemenu.AppendSeparator()
        quitmenuoption = filemenu.Append(wx.ID_EXIT, "&Quit\tCtrl+Q", "Quit application")
        self._menubar.Append(filemenu, "&File")

        settingsmenu = wx.Menu()
        settingsoption = settingsmenu.Append(wx.ID_ANY, "Settings", "Open the settings")
        self._menubar.Append(settingsmenu, "&Settings")

        # debugmenu = wx.Menu()
        # textsoption = debugmenu.Append(wx.ID_ANY, "Print texts to console", "Test texts generator")
        # self._menubar.Append(debugmenu, "&Debug")

        self.SetMenuBar(self._menubar)

        self.Bind(wx.EVT_MENU, self.OnNew, actorselectoption)
        self.Bind(wx.EVT_MENU, self.OnOpen, openoption)
        self.Bind(wx.EVT_MENU, self.OnSave, saveoption)
        self.Bind(wx.EVT_MENU, self.OnQuit, quitmenuoption)
        self.Bind(wx.EVT_MENU, self.OnSettings, settingsoption)
        # self.Bind(wx.EVT_MENU, self.OnTexts, textsoption)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        panelbox = wx.BoxSizer(wx.VERTICAL)

        self._linkselectorbox = wx.RadioBox(
            self, label="Actor Property", choices=tabs, majorDimension=7,
        )
        for i in range(len(tabs)):
            self._linkselectorbox.EnableItem(i, False)
        panelbox.Add(self._linkselectorbox, flag=wx.EXPAND | wx.ALL, border=10)
        self.Bind(wx.EVT_RADIOBOX, self.OnPropRadio, self._linkselectorbox)

        self._linkcontents = wx.Panel(self)
        lcbox = wx.BoxSizer(wx.HORIZONTAL)
        actorpanel = UiActorLinkPanel(self._linkcontents)
        lcbox.Add(actorpanel, proportion=1, flag=wx.EXPAND)
        self._linkcontents.SetSizerAndFit(lcbox)
        self._linkcontents.Disable()

        panelbox.Add(
            self._linkcontents,
            proportion=1,
            flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
            border=10,
        )

        self.CreateStatusBar()

        self.SetSizerAndFit(panelbox)

    def SetNeedsUpdate(self) -> None:
        update = wx.Menu()
        updateoption = update.Append(wx.ID_ANY, "How to Update", "How to update")
        self._menubar.Append(update, "Update Available")
        self.Bind(wx.EVT_MENU, self.OnUpdate, updateoption)

    def SetActor(self, actorname: str) -> None:
        actorpath = find_file(Path(f"Actor/Pack/{actorname}.sbactorpack"))
        self.LoadActor(actorpath)

    def LoadActor(self, actorpath: Union[Path, str]) -> None:
        self._actor = BATActor(actorpath)
        self.Freeze()
        for i in range(self._linkselectorbox.GetCount()):
            self._linkselectorbox.EnableItem(i, False)
        self._linkselectorbox.EnableItem(0, True)
        self._linkselectorbox.SetSelection(0)
        for i in range(len(LINKS)):
            if not self._actor.get_link(LINKS[i]) == "Dummy":
                enable = True
            else:
                enable = False
            index = link_to_tab_index(LINKS[i])
            if not index == -1:
                self._linkselectorbox.EnableItem(index, enable)
        self._linkselectorbox.EnableItem(25, True)
        self.ClearLinkContents()
        self.SetForActorLink()
        self._linkcontents.Enable()
        self._prevcontents = 0
        self.SetLabel(f"{self._actor.get_name()} - BotW Actor Tool")
        self.Thaw()

    def EnableRadioForLink(self, link: str, enable: bool) -> None:
        index = link_to_tab_index(link)
        if not index == -1:
            self._linkselectorbox.EnableItem(index, enable)

    def OnNew(self, e) -> None:
        root_dir = BatSettings().get_setting("update_dir")
        with UiActorSelect(root_dir, self) as dlg:
            code, actor = dlg.ShowModal()
            if code == 0:
                self.SetActor(actor)
        self.DarkMode()

    def OnOpen(self, e) -> None:
        with wx.DirDialog(self, "Select your mod's content or romfs directory") as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                root_dir = dlg.GetPath()
                with UiActorSelect(root_dir, self) as dlg:
                    code, actor = dlg.ShowModal()
                    if code == 0:
                        actorpath = Path(f"{root_dir}/Actor/Pack/{actor}.sbactorpack")
                        self.LoadActor(actorpath)
        self.DarkMode()

    def OnSave(self, e) -> None:
        with wx.DirDialog(self, "Select your mod's content or romfs directory") as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                root_dir = dlg.GetPath()
                if Path(root_dir).name == "romfs":
                    be = False
                elif Path(root_dir).name == "content":
                    be = True
                else:
                    with wx.MessageDialog(self, "Must choose either content or romfs!") as dlg:
                        dlg.ShowModal()
                    return
                self.Freeze()
                self._actor.save(root_dir, be)
                self.Thaw()

    def OnQuit(self, e) -> None:
        self.Close()

    def OnSettings(self, e) -> None:
        with UiSettingsPanel(self) as dlg:
            dlg.ShowModal()
        self.DarkMode()

    def OnTexts(self, e) -> None:
        print(self._actor._texts.get_texts())

    def OnUpdate(self, e) -> None:
        with wx.MessageDialog(
            self,
            "Update available on PyPI.\n\nInstall it with the console command:\n\npip install -U botw_actor_tool",
        ) as dlg:
            dlg.ShowModal()

    def OnClose(self, e) -> None:
        settings = BatSettings()
        settings.set_win_pos(tuple(self.GetPosition()))
        settings.set_win_size(tuple(self.GetSize()))
        settings.save_settings()
        e.Skip()

    def OnPropRadio(self, e) -> None:
        selection = e.GetInt()
        if self._prevcontents == selection:
            return
        self.Freeze()
        self.ClearLinkContents()
        funcs = [
            self.SetForActorLink,
            self.SetForAIProg,
            self.SetForAISched,
            self.SetForAS,
            self.SetForAttention,
            self.SetForAwareness,
            self.SetForBoneCtrl,
            self.SetForChemical,
            self.SetForDamageParam,
            self.SetForDropTable,
            self.SetForElink,
            self.SetForGParam,
            self.SetForLifeCondition,
            self.SetForLOD,
            self.SetForModel,
            self.SetForPhysics,
            self.SetForProfile,
            self.SetForRgBlendWeight,
            self.SetForRgConfigList,
            self.SetForRecipe,
            self.SetForShopData,
            self.SetForSlink,
            self.SetForUMii,
            self.SetForXlink,
            self.SetForAnimationInfo,
            self.SetForTexts,
            self.SetForFlags,
        ]
        funcs[selection]()
        self._linkcontents.Layout()
        self.Thaw()
        self._prevcontents = selection
        self.DarkMode()

    def ClearLinkContents(self) -> None:
        if len(self._linkcontents.GetChildren()) == 1:
            window = self._linkcontents.GetChildren()[0]
            window.UnbindAll()
            window.Destroy()

    def SetForActorLink(self) -> None:
        sizer = self._linkcontents.GetSizer()
        panel = UiActorLinkPanel(self._linkcontents)
        sizer.Add(panel, proportion=1, flag=wx.EXPAND)
        self._linkcontents.Layout()
        panel.InitPack(self._actor)

    def SetForAIProg(self) -> None:
        link = "AIProgramUser"
        actorname = self._actor.get_name()
        linkref = self._actor.get_link(link)
        rename = False if actorname == linkref else True
        self.SetTextEditor(link, rename)

    def SetForAISched(self) -> None:
        link = "AIScheduleUser"
        actorname = self._actor.get_name()
        linkref = self._actor.get_link(link)
        rename = False if actorname == linkref else True
        self.SetTextEditor(link, rename)

    def SetForAS(self) -> None:
        link = "ASUser"
        actorname = self._actor.get_name()
        linkref = self._actor.get_link(link)
        rename = False if actorname == linkref else True
        self.SetTextEditor(link, rename)
        # TODO: Switch this to a special AS window

    def SetForAttention(self) -> None:
        link = "AttentionUser"
        actorname = self._actor.get_name()
        linkref = self._actor.get_link(link)
        rename = False if actorname == linkref else True
        self.SetTextEditor(link, rename)

    def SetForAwareness(self) -> None:
        link = "AwarenessUser"
        actorname = self._actor.get_name()
        linkref = self._actor.get_link(link)
        rename = False if actorname == linkref else True
        self.SetTextEditor(link, rename)

    def SetForBoneCtrl(self) -> None:
        link = "BoneControlUser"
        actorname = self._actor.get_name()
        linkref = self._actor.get_link(link)
        rename = False if actorname == linkref else True
        self.SetTextEditor(link, rename)

    def SetForChemical(self) -> None:
        link = "ChemicalUser"
        actorname = self._actor.get_name()
        linkref = self._actor.get_link(link)
        rename = False if actorname == linkref else True
        self.SetTextEditor(link, rename)

    def SetForDamageParam(self) -> None:
        link = "DamageParamUser"
        actorname = self._actor.get_name()
        linkref = self._actor.get_link(link)
        rename = False if actorname == linkref else True
        self.SetTextEditor(link, rename)

    def SetForDropTable(self) -> None:
        link = "DropTableUser"
        actorname = self._actor.get_name()
        linkref = self._actor.get_link(link)
        rename = False if actorname == linkref else True
        self.SetTextEditor(link, rename)

    def SetForElink(self) -> None:
        self.Dummy()

    def SetForGParam(self) -> None:
        link = "GParamUser"
        actorname = self._actor.get_name()
        linkref = self._actor.get_link(link)
        rename = False if actorname == linkref else True
        self.SetTextEditor(link, rename)

    def SetForLifeCondition(self) -> None:
        link = "LifeConditionUser"
        actorname = self._actor.get_name()
        linkref = self._actor.get_link(link)
        rename = False if actorname == linkref else True
        self.SetTextEditor(link, rename)

    def SetForLOD(self) -> None:
        link = "LODUser"
        actorname = self._actor.get_name()
        linkref = self._actor.get_link(link)
        rename = False if actorname == linkref else True
        self.SetTextEditor(link, rename)

    def SetForModel(self) -> None:
        link = "ModelUser"
        actorname = self._actor.get_name()
        linkref = self._actor.get_link(link)
        rename = False if actorname == linkref else True
        self.SetTextEditor(link, rename)

    def SetForPhysics(self) -> None:
        link = "PhysicsUser"
        actorname = self._actor.get_name()
        linkref = self._actor.get_link(link)
        rename = False if actorname == linkref else True
        self.SetTextEditor(link, rename)

    def SetForProfile(self) -> None:
        self.Dummy()

    def SetForRgBlendWeight(self) -> None:
        link = "RgBlendWeightUser"
        actorname = self._actor.get_name()
        linkref = self._actor.get_link(link)
        rename = False if actorname == linkref else True
        self.SetTextEditor(link, rename)

    def SetForRgConfigList(self) -> None:
        link = "RgConfigListUser"
        actorname = self._actor.get_name()
        linkref = self._actor.get_link(link)
        rename = False if actorname == linkref else True
        self.SetTextEditor(link, rename)

    def SetForRecipe(self) -> None:
        link = "RecipeUser"
        actorname = self._actor.get_name()
        linkref = self._actor.get_link(link)
        rename = False if actorname == linkref else True
        self.SetTextEditor(link, rename)

    def SetForShopData(self) -> None:
        link = "ShopDataUser"
        actorname = self._actor.get_name()
        linkref = self._actor.get_link(link)
        rename = False if actorname == linkref else True
        self.SetTextEditor(link, rename)

    def SetForSlink(self) -> None:
        self.Dummy()

    def SetForUMii(self) -> None:
        link = "UMiiUser"
        actorname = self._actor.get_name()
        linkref = self._actor.get_link(link)
        rename = False if actorname == linkref else True
        self.SetTextEditor(link, rename)

    def SetForXlink(self) -> None:
        self.Dummy()

    def SetForAnimationInfo(self) -> None:
        link = "AnimationInfo"
        actorname = self._actor.get_name()
        linkref = self._actor.get_link(link)
        rename = False if actorname == linkref else True
        self.SetTextEditor(link, rename)

    def SetForTexts(self) -> None:
        sizer = self._linkcontents.GetSizer()
        panel = UiTexts(self._linkcontents)
        panel.InitUI(self._actor.get_name(), self._actor.get_texts())
        sizer.Add(panel, proportion=1, flag=wx.EXPAND)
        self._linkcontents.Layout()

    def SetForFlags(self) -> None:
        self.Dummy()

    def SetTextEditor(self, link: str, rename: bool) -> None:
        sizer = self._linkcontents.GetSizer()
        panel = UiTextEditor(self._linkcontents)
        sizer.Add(panel, proportion=1, flag=wx.EXPAND)
        self._linkcontents.Layout()
        panel.SetRenameOnEdit(rename)
        panel.InitData(link, self._actor.get_link_data(link))

    def Dummy(self) -> None:
        return

    def SetActorName(self, name: str) -> None:
        self._actor.set_name(name)
        self.SetLabel(f"{name} - BotW Actor Tool")

    def GetActorName(self) -> str:
        return self._actor.get_name()

    def UpdateActorLink(self, link: str, linkref: str, try_retrieve_data: bool = False) -> bool:
        if not self._actor.set_link(link, linkref):
            return False
        if try_retrieve_data:
            data = try_retrieve_custom_file(link, linkref)
            if data:
                dlg = wx.MessageDialog(
                    self, f"Found a vanilla {link} file named {linkref}. Import?", style=wx.YES_NO,
                )
                if dlg.ShowModal() == wx.ID_YES:
                    self.UpdateActorLinkData(link, data)
        return True

    def UpdateActorLinkData(self, link: str, data: str) -> None:
        self._actor.set_link_data(link, data)

    def SetTexts(self, texts: dict) -> None:
        self._actor.set_texts(texts)

    def DarkMode(self) -> None:
        set_dark = BatSettings().get_dark_mode()
        _set_dark_mode(self, set_dark)
        self.Refresh()
