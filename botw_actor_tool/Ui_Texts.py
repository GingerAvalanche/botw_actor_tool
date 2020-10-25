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

from . import util


class UiTexts(wx.Panel):
    _ctrls: dict
    _bound_events: list = []

    def __init__(self, *args, **kwargs) -> None:
        super(UiTexts, self).__init__(*args, **kwargs)
        self._ctrls = {}
        util._set_dark_mode(self, util.BatSettings().get_dark_mode())

    def InitUI(self, actor_name: str, texts: dict) -> None:
        selfsizer = wx.BoxSizer(wx.VERTICAL)

        gridsizer = wx.FlexGridSizer(cols=2, vgap=10, hgap=0)
        gridsizer.SetFlexibleDirection(wx.HORIZONTAL)
        gridsizer.AddGrowableCol(1, proportion=1)

        self._ctrls["BaseNameCheck"] = wx.CheckBox(
            self, label=f"{actor_name}_BaseName", name="BaseName"
        )
        self._ctrls["BaseNameText"] = wx.TextCtrl(self)
        if "BaseName" in texts:
            self._ctrls["BaseNameCheck"].SetValue(True)
            self._ctrls["BaseNameText"].Enable()
            self._ctrls["BaseNameText"].SetValue(texts["BaseName"])
        else:
            self._ctrls["BaseNameCheck"].SetValue(False)
            self._ctrls["BaseNameText"].Disable()
        gridsizer.Add(self._ctrls["BaseNameCheck"], flag=wx.ALIGN_CENTER_VERTICAL)
        gridsizer.Add(self._ctrls["BaseNameText"], flag=wx.ALIGN_CENTER_VERTICAL | wx.EXPAND)

        self._ctrls["NameCheck"] = wx.CheckBox(self, label=f"{actor_name}_Name", name="Name")
        self._ctrls["NameText"] = wx.TextCtrl(self)
        if "Name" in texts:
            self._ctrls["NameCheck"].SetValue(True)
            self._ctrls["NameText"].Enable()
            self._ctrls["NameText"].SetValue(texts["Name"])
        else:
            self._ctrls["NameCheck"].SetValue(False)
            self._ctrls["NameText"].Disable()
        gridsizer.Add(self._ctrls["NameCheck"], flag=wx.ALIGN_CENTER_VERTICAL)
        gridsizer.Add(self._ctrls["NameText"], flag=wx.ALIGN_CENTER_VERTICAL | wx.EXPAND)

        self._ctrls["DescCheck"] = wx.CheckBox(self, label=f"{actor_name}_Desc", name="Desc")
        self._ctrls["DescText"] = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(-1, 76))
        if "Desc" in texts:
            self._ctrls["DescCheck"].SetValue(True)
            self._ctrls["DescText"].Enable()
            self._ctrls["DescText"].SetValue(texts["Desc"])
        else:
            self._ctrls["DescCheck"].SetValue(False)
            self._ctrls["DescText"].Disable()
        gridsizer.Add(self._ctrls["DescCheck"], flag=wx.ALIGN_CENTER_VERTICAL)
        gridsizer.Add(self._ctrls["DescText"], flag=wx.ALIGN_CENTER_VERTICAL | wx.EXPAND)

        self._ctrls["PBookCheck"] = wx.CheckBox(
            self, label=f"{actor_name}_PictureBook", name="PBook"
        )
        self._ctrls["PBookText"] = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(-1, 76))
        if "PictureBook" in texts:
            self._ctrls["PBookCheck"].SetValue(True)
            self._ctrls["PBookText"].Enable()
            self._ctrls["PBookText"].SetValue(texts["PictureBook"])
        else:
            self._ctrls["PBookCheck"].SetValue(False)
            self._ctrls["PBookText"].Disable()
        gridsizer.Add(self._ctrls["PBookCheck"], flag=wx.ALIGN_CENTER_VERTICAL)
        gridsizer.Add(self._ctrls["PBookText"], flag=wx.ALIGN_CENTER_VERTICAL | wx.EXPAND)

        buttonsizer = wx.BoxSizer(wx.VERTICAL)
        savebutton = wx.Button(self, label="Save", size=(70, 25))
        buttonsizer.Add(savebutton, flag=wx.ALIGN_RIGHT)

        selfsizer.Add(gridsizer, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
        selfsizer.Add(buttonsizer, flag=wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT, border=10)

        self.Bind(wx.EVT_CHECKBOX, self.OnToggleBox, self._ctrls["BaseNameCheck"])
        self.Bind(wx.EVT_CHECKBOX, self.OnToggleBox, self._ctrls["NameCheck"])
        self.Bind(wx.EVT_CHECKBOX, self.OnToggleBox, self._ctrls["DescCheck"])
        self.Bind(wx.EVT_CHECKBOX, self.OnToggleBox, self._ctrls["PBookCheck"])
        self.Bind(wx.EVT_BUTTON, self.OnSave, savebutton)

        self.SetSizerAndFit(selfsizer)

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

    def OnToggleBox(self, e) -> None:
        checkbox = e.GetEventObject()
        checked = checkbox.GetValue()
        name = checkbox.GetName()
        if checked:
            self._ctrls[f"{name}Text"].Enable()
        else:
            self._ctrls[f"{name}Text"].Disable()
        self._ctrls[f"{name}Text"].SetValue("")

    def OnSave(self, e) -> None:
        texts = {}
        if self._ctrls["BaseNameCheck"].GetValue():
            texts["BaseName"] = self._ctrls["BaseNameText"].GetValue()
        if self._ctrls["NameCheck"].GetValue():
            texts["Name"] = self._ctrls["NameText"].GetValue()
        if self._ctrls["DescCheck"].GetValue():
            texts["Desc"] = self._ctrls["DescText"].GetValue()
        if self._ctrls["PBookCheck"].GetValue():
            texts["PictureBook"] = self._ctrls["PBookText"].GetValue()
        self.TopLevelParent.SetTexts(texts)
