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

from . import actorinfo
from .util import BatSettings, _set_dark_mode


class UiActorSelect(wx.Dialog):
    def __init__(self, root_dir, *args, **kwargs) -> None:
        super(UiActorSelect, self).__init__(*args, **kwargs)
        self.SetTitle("Select actor...")
        self.actornames = [
            name for name in actorinfo.get_all_actors(root_dir) if not "_Far" in name
        ]
        size = (300, 300)
        self.SetMinSize(size)
        self.SetMaxSize(size)
        self.InitUI()
        _set_dark_mode(self, BatSettings().get_dark_mode())

    def InitUI(self) -> None:
        panel = wx.Panel(self)

        panelbox = wx.BoxSizer(wx.VERTICAL)

        findbox = wx.BoxSizer(wx.HORIZONTAL)
        self.findtextenter = wx.TextCtrl(panel)
        findbox.Add(self.findtextenter, proportion=1, flag=wx.RIGHT, border=10)
        findtextbutton = wx.Button(panel, label="Filter", size=(70, 25))
        findbox.Add(findtextbutton)
        panelbox.Add(findbox, flag=wx.EXPAND | wx.ALL, border=10)

        selectbox = wx.BoxSizer(wx.VERTICAL)
        selecttext = wx.StaticText(panel, label="Select an actor:")
        selectbox.Add(selecttext, flag=wx.BOTTOM, border=10)
        self.selectoptions = wx.ListBox(
            panel, wx.ID_ANY, (0, 0), (0, 0), self.actornames, wx.LB_SINGLE | wx.LB_SORT
        )
        selectbox.Add(self.selectoptions, proportion=1, flag=wx.EXPAND)
        panelbox.Add(selectbox, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)

        buttonbox = wx.BoxSizer(wx.HORIZONTAL)
        acceptbutton = wx.Button(panel, label="Accept", size=(70, 25))
        buttonbox.Add(acceptbutton)
        cancelbutton = wx.Button(panel, label="Cancel", size=(70, 25))
        buttonbox.Add(cancelbutton)
        panelbox.Add(buttonbox, flag=wx.ALIGN_RIGHT | wx.ALL, border=10)

        self.Bind(wx.EVT_CHAR_HOOK, self.OnFilterChar, self.findtextenter)
        self.Bind(wx.EVT_BUTTON, self.OnFilter, findtextbutton)
        self.Bind(wx.EVT_CHAR_HOOK, self.OnSelectChar, self.selectoptions)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnAccept, self.selectoptions)
        self.Bind(wx.EVT_BUTTON, self.OnAccept, acceptbutton)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, cancelbutton)
        self.Bind(wx.EVT_CLOSE, self.OnCancel)

        panel.SetSizer(panelbox)

    def ShowModal(self) -> tuple:
        retCode = super(UiActorSelect, self).ShowModal()
        index = self.selectoptions.GetSelection()
        if index == -1:
            return (1, "")
        actorname = self.selectoptions.GetString(index)
        return (retCode, actorname)

    def OnFilterChar(self, e) -> None:
        if e.GetKeyCode() == wx.WXK_RETURN:
            self.OnFilter(e)
        else:
            e.Skip()

    def OnFilter(self, e) -> None:
        self.selectoptions.Clear()
        filterednames = []
        str_filter = self.findtextenter.GetValue()
        for name in self.actornames:
            if str_filter in name:
                filterednames.append(name)
        self.selectoptions.Set(filterednames)
        self.selectoptions.Update()

    def OnSelectChar(self, e) -> None:
        if e.GetKeyCode() == wx.WXK_RETURN:
            self.OnAccept(e)
        else:
            e.Skip()

    def OnAccept(self, e) -> None:
        self.EndModal(0)

    def OnCancel(self, e) -> None:
        self.EndModal(1)
