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
import zlib
from pathlib import Path
from typing import Union

from . import generic_link_files, actorinfo
from .actor import BATActor
from .Ui_Settings import UiSettingsPanel
from .Ui_ActorSelect import UiActorSelect
from .Ui_Texts import UiTexts
from .util import (
    BatSettings,
    LINKS,
    _link_to_tab_index,
    _set_dark_mode,
    _try_retrieve_custom_file,
    find_file,
)


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
        menu = wx.MenuBar()
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
        menu.Append(filemenu, "&File")

        settingsmenu = wx.Menu()
        settingsoption = settingsmenu.Append(wx.ID_ANY, "Settings", "Open the settings")
        menu.Append(settingsmenu, "&Settings")

        # debugmenu = wx.Menu()
        # textsoption = debugmenu.Append(wx.ID_ANY, "Print texts to console", "Test texts generator")
        # menu.Append(debugmenu, "&Debug")

        self.SetMenuBar(menu)

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
            index = _link_to_tab_index(LINKS[i])
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
        index = _link_to_tab_index(link)
        if not index == -1:
            self._linkselectorbox.EnableItem(index, enable)

    def OnNew(self, e) -> None:
        root_dir = BatSettings().get_setting("update_dir")
        with UiActorSelect(root_dir, self) as dlg:
            code, actor = dlg.ShowModal()
            if code == 0:
                self.SetActor(actor)

    def OnOpen(self, e) -> None:
        with wx.DirDialog(self, "Select your mod's content or romfs directory") as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                root_dir = dlg.GetPath()
                with UiActorSelect(root_dir, self) as dlg:
                    code, actor = dlg.ShowModal()
                    if code == 0:
                        actorpath = Path(f"{root_dir}/Actor/Pack/{actor}.sbactorpack")
                        self.LoadActor(actorpath)

    def OnSave(self, e) -> None:
        with wx.DirDialog(self, "Select your mod's content or romfs directory") as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                root_dir = dlg.GetPath()
                if Path(root_dir).name == "romfs":
                    be = False
                elif Path(root_dir).name == "content":
                    be = True
                else:
                    dlg = wx.MessageDialog(self, "Must choose either content or romfs!")
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

    def OnTexts(self, e) -> None:
        print(self._actor._texts.get_texts())

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
            data = _try_retrieve_custom_file(link, linkref)
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


class UiActorLinkPanel(wx.Panel):
    _actor: BATActor
    _bound_events: list = []
    _ctrls: dict = {}

    def __init__(self, *args, **kwargs) -> None:
        super(UiActorLinkPanel, self).__init__(*args, **kwargs)
        self.InitUI()
        self.TopLevelParent.DarkMode()

    def InitUI(self) -> None:
        boxsizer = wx.BoxSizer(wx.VERTICAL)

        # Actor Name
        linksizer = wx.BoxSizer(wx.HORIZONTAL)
        st = wx.StaticText(self, size=(125, -1), label="Actor Name:")
        tc = wx.TextCtrl(self)
        bt = wx.Button(self, size=(70, 25), label="Apply")
        linksizer.Add(st, flag=wx.ALIGN_CENTER_VERTICAL)
        linksizer.Add(tc, proportion=1)
        linksizer.Add(bt)
        self.Bind(wx.EVT_BUTTON, self.OnActorNameChange, bt)
        boxsizer.Add(linksizer, flag=wx.EXPAND)
        self._ctrls["ActorName"] = tc

        # Priority
        linksizer = wx.BoxSizer(wx.HORIZONTAL)
        st = wx.StaticText(self, size=(125, -1), label="Priority:")
        tc = wx.TextCtrl(self)
        bt = wx.Button(self, size=(70, 25), label="Apply")
        linksizer.Add(st, flag=wx.ALIGN_CENTER_VERTICAL)
        linksizer.Add(tc, proportion=1)
        linksizer.Add(bt)
        self.Bind(wx.EVT_BUTTON, self.OnPriorityChange, bt)
        boxsizer.Add(linksizer, flag=wx.EXPAND)
        self._ctrls["Priority"] = tc

        # Rest of the links
        for link in LINKS:
            linksizer = wx.BoxSizer(wx.HORIZONTAL)
            st = wx.StaticText(self, size=(125, -1), label=f"{link}:")
            linksizer.Add(st, flag=wx.ALIGN_CENTER_VERTICAL)
            rb1 = wx.RadioButton(self, label="Dummy", style=wx.RB_GROUP, name=f"{link}")
            rb2 = wx.RadioButton(self, label="ActorName", name=f"{link}")
            rb3 = wx.RadioButton(self, label="Custom:", name=f"{link}")
            linksizer.Add(rb1, flag=wx.ALIGN_CENTER_VERTICAL)
            linksizer.Add(rb2, flag=wx.ALIGN_CENTER_VERTICAL)
            linksizer.Add(rb3, flag=wx.ALIGN_CENTER_VERTICAL)
            tc_width = rb2.GetSize().GetWidth()
            tc = wx.TextCtrl(self)
            tc.Disable()
            linksizer.Add(tc, proportion=1)
            bt = wx.Button(self, size=(120, 25), label="Update Custom Link", name=f"{link}")
            bt.Disable()
            linksizer.Add(bt)
            boxsizer.Add(linksizer, flag=wx.EXPAND)
            self.Bind(wx.EVT_RADIOBUTTON, self.OnLinkChangeDummy, rb1)
            self.Bind(wx.EVT_RADIOBUTTON, self.OnLinkChangeActorName, rb2)
            self.Bind(wx.EVT_RADIOBUTTON, self.OnLinkChangeCustom, rb3)
            self.Bind(wx.EVT_BUTTON, self.OnLinkUpdate, bt)
            self._ctrls[f"{link}_Dummy"] = rb1
            self._ctrls[f"{link}_ActorName"] = rb2
            self._ctrls[f"{link}_Custom"] = rb3
            self._ctrls[f"{link}_Custom_Text"] = tc
            self._ctrls[f"{link}_Custom_Update"] = bt

        # Tags
        linksizer = wx.BoxSizer(wx.HORIZONTAL)
        st = wx.StaticText(self, size=(125, -1), label="Tags:")
        tc = wx.TextCtrl(self)
        bt = wx.Button(self, size=(70, 25), label="Apply")
        linksizer.Add(st, flag=wx.ALIGN_CENTER_VERTICAL)
        linksizer.Add(tc, proportion=1)
        linksizer.Add(bt)
        self.Bind(wx.EVT_BUTTON, self.OnTagsChange, bt)
        boxsizer.Add(linksizer, flag=wx.EXPAND)
        self._ctrls["Tags"] = tc

        self.SetSizerAndFit(boxsizer)

    def InitPack(self, actor: BATActor) -> None:
        self._ctrls["ActorName"].SetValue(actor.get_name())
        self._ctrls["Priority"].SetValue(actor.get_link("Priority"))
        for link in LINKS:
            linkval = actor.get_link(link)
            self._ctrls[f"{link}_ActorName"].SetLabel(actor.get_name())
            if linkval == "Dummy":
                self._ctrls[f"{link}_Dummy"].SetValue(True)
            elif linkval == actor.get_name():
                self._ctrls[f"{link}_ActorName"].SetValue(True)
            else:
                self._ctrls[f"{link}_Custom"].SetValue(True)
                self._ctrls[f"{link}_Custom_Text"].SetValue(linkval)
                self._ctrls[f"{link}_Custom_Text"].Enable()
                self._ctrls[f"{link}_Custom_Update"].Enable()
        self._ctrls["Tags"].SetValue(actor.get_tags())
        self.ResizeLayout()

    def Bind(self, event, handler, source=None, id=wx.ID_ANY, id2=wx.ID_ANY):
        self._bound_events.append((event, handler, source))
        super().Bind(event, handler, source, id, id2)

    def Unbind(self, event, source=None, id=wx.ID_ANY, id2=wx.ID_ANY, handler=None) -> bool:
        key = (event, handler, source)
        if key in self._bound_events:
            self._bound_events.remove(key)
        return super().Unbind(event, source=source, id=id, id2=id2, handler=handler)

    def UnbindAll(self) -> None:
        while not len(self._bound_events) == 0:
            event, handler, source = self._bound_events[0]
            self.Unbind(event, source=source, handler=handler)

    def OnActorNameChange(self, e) -> None:
        new_name = self._ctrls["ActorName"].GetValue()
        self.TopLevelParent.SetActorName(new_name)
        for link in LINKS:
            self._ctrls[f"{link}_ActorName"].SetLabel(new_name)
        self.ResizeLayout()

    def OnPriorityChange(self, e) -> None:
        self.TopLevelParent._actor.set_link("Priority", self._ctrls["Priority"].GetValue())

    def OnLinkChangeDummy(self, e) -> None:
        button = e.GetEventObject()
        link = button.GetName()
        link_set = self.TopLevelParent.UpdateActorLink(link, "Dummy")
        if not link_set:
            dlg = wx.MessageDialog(self, "Actor with a Far variant must have LifeConditionUser")
            dlg.ShowModal()
            return
        self._ctrls[f"{link}_Custom_Text"].Disable()
        self._ctrls[f"{link}_Custom_Text"].SetValue("")
        self._ctrls[f"{link}_Custom_Update"].Disable()
        self.TopLevelParent.EnableRadioForLink(link, False)

    def OnLinkChangeActorName(self, e) -> None:
        button = e.GetEventObject()
        link = button.GetName()
        linkref = self.TopLevelParent._actor.get_name()
        self.TopLevelParent.UpdateActorLink(link, linkref, True)
        self._ctrls[f"{link}_Custom_Text"].Disable()
        self._ctrls[f"{link}_Custom_Text"].SetValue("")
        self._ctrls[f"{link}_Custom_Update"].Disable()
        self.TopLevelParent.EnableRadioForLink(link, True)

    def OnLinkChangeCustom(self, e) -> None:
        button = e.GetEventObject()
        link = button.GetName()
        self._ctrls[f"{link}_Custom_Text"].Enable()
        self._ctrls[f"{link}_Custom_Update"].Enable()
        self.TopLevelParent.EnableRadioForLink(link, False)

    def OnLinkUpdate(self, e) -> None:
        link = e.GetEventObject().GetName()
        old_linkref = self.TopLevelParent._actor.get_link(link)
        linkref = self._ctrls[f"{link}_Custom_Text"].GetValue()
        if linkref == "":
            return
        self.TopLevelParent.UpdateActorLink(link, linkref, True)
        self.TopLevelParent.EnableRadioForLink(link, True)

    def OnTagsChange(self, e) -> None:
        self.TopLevelParent._actor.set_tags(self._ctrls["Tags"].GetValue())

    def ResizeLayout(self) -> None:
        for link in LINKS:
            actorname_ctrl = self._ctrls[f"{link}_ActorName"]
            actorname_ctrl.Fit()
        self.Layout()


class UiTextEditor(wx.Panel):
    _bound_events: list
    _editor: wx.stc.StyledTextCtrl
    _hash: int
    _link: str
    _rename_on_edit: bool
    _suppress_rename: bool

    def __init__(self, *args, **kwargs) -> None:
        super(UiTextEditor, self).__init__(*args, **kwargs)
        self._bound_events = []
        self._suppress_rename = False
        self.InitUI()
        self.TopLevelParent.DarkMode()

    def InitUI(self) -> None:
        boxsizer = wx.BoxSizer(wx.VERTICAL)

        self._editor = wx.stc.StyledTextCtrl(self, style=wx.TE_MULTILINE | wx.TE_WORDWRAP)
        self._editor.StyleSetFont(
            0, wx.Font(10, wx.MODERN, wx.FONTSTYLE_NORMAL, wx.NORMAL, False, "Consolas")
        )
        self._editor.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        self._editor.Bind(wx.EVT_MOUSEWHEEL, self.OnScroll)
        self._editor.Bind(wx.EVT_SCROLLWIN_THUMBRELEASE, self.OnScroll)
        boxsizer.Add(self._editor, proportion=1, flag=wx.EXPAND, border=10)

        savesizer = wx.BoxSizer(wx.HORIZONTAL)
        savedesc = wx.StaticText(
            self,
            label="Changes will be lost when switching tabs unless you save with this button:",
            style=wx.ALIGN_RIGHT,
        )
        savebtn = wx.Button(self, label="Save", size=(70, 25))
        self.Bind(wx.EVT_BUTTON, self.OnSave, savebtn)
        savesizer.Add(
            savedesc, proportion=1, flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=10,
        )
        savesizer.Add(savebtn)
        boxsizer.Add(savesizer, flag=wx.EXPAND | wx.TOP, border=10)

        self.SetSizerAndFit(boxsizer)

    def InitData(self, link: str, data: str) -> None:
        self._link = link
        self._hash = zlib.crc32(data.encode("utf-8"))
        self._editor.SetText(data)

    def SetRenameOnEdit(self, rename: bool) -> None:
        self._rename_on_edit = rename

    def OnScroll(self, e) -> None:
        e.Skip()
        scroll_amount = 0
        try:
            scroll_amount = e.GetLinesPerAction()
            if e.GetWheelRotation() > 0:
                scroll_amount = 0 - scroll_amount
        except AttributeError:
            pass
        index = self._editor.GetFirstVisibleLine() + 1
        lines = self._editor.LinesOnScreen() + index
        max_lines = self._editor.GetLineCount()
        count = index + scroll_amount
        while index < lines:
            if index == max_lines:
                break
            index += self._editor.WrapCount(index)
            count += 1
        if count < 100:
            if not self._editor.GetMarginWidth(1) == 16:
                self._editor.SetMarginWidth(1, 16)
            else:
                return
        elif count < 1000:
            if not self._editor.GetMarginWidth(1) == 24:
                self._editor.SetMarginWidth(1, 24)
            else:
                return
        elif count < 10000:
            if not self._editor.GetMarginWidth(1) == 32:
                self._editor.SetMarginWidth(1, 32)
            else:
                return
        elif count < 100000:
            if not self._editor.GetMarginWidth(1) == 40:
                self._editor.SetMarginWidth(1, 40)
            else:
                return
        else:
            if not self._editor.GetMarginWidth(1) == 48:
                self._editor.SetMarginWidth(1, 48)

    def OnSave(self, e) -> None:
        data = self._editor.GetText()
        hash = zlib.crc32(data.encode("utf-8"))
        if hash == self._hash:
            return
        if self._rename_on_edit and not self._suppress_rename:
            new_name = self.TopLevelParent.GetActorName()
            message = (
                f"Current filename is custom, which means it could be shared with other actors.\n"
                f"If this filename is shared with other actors, changing the file could cause bugs.\n"
                f"It is highly recommended to change the file's name to avoid these collisions.\n"
                f"Do you want to change the file's name to {new_name}?"
            )
            dlg = wx.MessageDialog(self, message, style=wx.YES_NO)
            if dlg.ShowModal() == wx.ID_YES:
                self.TopLevelParent.UpdateActorLink(self._link, new_name)
            else:
                message = "Suppress further messages of this kind for this file?"
                dlg = wx.MessageDialog(self, message, style=wx.YES_NO)
                if dlg.ShowModal() == wx.ID_YES:
                    self._suppress_rename = True
        self.TopLevelParent.UpdateActorLinkData(self._link, data)
        self._hash = hash

    def Bind(self, event, handler, source=None, id=wx.ID_ANY, id2=wx.ID_ANY):
        self._bound_events.append((event, handler, source))
        super().Bind(event, handler, source, id, id2)

    def Unbind(self, event, source=None, id=wx.ID_ANY, id2=wx.ID_ANY, handler=None) -> bool:
        key = (event, handler, source)
        if key in self._bound_events:
            self._bound_events.remove(key)
        return super().Unbind(event, source=source, id=id, id2=id2, handler=handler)

    def UnbindAll(self) -> None:
        self._editor.Unbind(wx.EVT_MOUSEWHEEL, handler=self.OnScroll)
        self._editor.Unbind(wx.EVT_SCROLLWIN_THUMBRELEASE, handler=self.OnScroll)
        while not len(self._bound_events) == 0:
            event, handler, source = self._bound_events[0]
            self.Unbind(event, source=source, handler=handler)
