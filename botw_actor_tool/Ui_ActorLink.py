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

from .actor import BATActor
from .util import LINKS


class UiActorLinkPanel(wx.Panel):
    _actor: BATActor
    _bound_events: list = []
    _ctrls: dict = {}

    def __init__(self, *args, **kwargs) -> None:
        super(UiActorLinkPanel, self).__init__(*args, **kwargs)
        self.InitUI()

    def InitUI(self) -> None:
        boxsizer = wx.BoxSizer(wx.VERTICAL)

        # Actor Name
        linksizer = wx.BoxSizer(wx.HORIZONTAL)
        st = wx.StaticText(self, size=(125, -1), label="Actor Name:")
        tc = wx.TextCtrl(self, size=(-1, 25), style=wx.TE_MULTILINE | wx.TE_NO_VSCROLL)
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
        tc = wx.TextCtrl(self, size=(-1, 25), style=wx.TE_MULTILINE | wx.TE_NO_VSCROLL)
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
            tc = wx.TextCtrl(self, size=(-1, 25), style=wx.TE_MULTILINE | wx.TE_NO_VSCROLL)
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
        tc = wx.TextCtrl(self, size=(-1, 25), style=wx.TE_MULTILINE | wx.TE_NO_VSCROLL)
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
