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

    def InitUI(self) -> None:
        boxsizer = wx.BoxSizer(wx.VERTICAL)

        self._editor = wx.stc.StyledTextCtrl(self, style=wx.TE_MULTILINE | wx.TE_WORDWRAP)
        self._editor.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        self._editor.SetMarginWidth(1, 24)

        self._editor.Bind(wx.EVT_MOUSEWHEEL, self.OnScroll)
        self._editor.Bind(wx.EVT_SCROLLWIN_THUMBRELEASE, self.OnScroll)
        self._editor.Bind(wx.EVT_CHAR, self.OnFindDialog)
        self._editor.Bind(wx.EVT_FIND, self.OnFind)
        self._editor.Bind(wx.EVT_FIND_NEXT, self.OnFind)
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
            savedesc,
            proportion=1,
            flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
            border=10,
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
            if not self._editor.GetMarginWidth(1) == 24:
                self._editor.SetMarginWidth(1, 24)
            else:
                return
        elif count < 1000:
            if not self._editor.GetMarginWidth(1) == 32:
                self._editor.SetMarginWidth(1, 32)
            else:
                return
        elif count < 10000:
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

    def OnFindDialog(self, e) -> None:
        if e.GetKeyCode() == wx.WXK_CONTROL_F:
            finddata = wx.FindReplaceData(flags=wx.FR_DOWN)
            finddata.SetFindString(self._editor.GetSelectedText())
            dlg = wx.FindReplaceDialog(self._editor, finddata, "Find")
            dlg.Show()
        else:
            e.Skip()

    def OnFind(self, e) -> None:
        from_, to_ = self._editor.GetSelection()
        self._editor.ClearSelections()
        fs = e.GetFindString()
        fl = e.GetFlags()
        if fl & wx.FR_DOWN:
            self._editor.SetAnchor(to_)
            self._editor.SetCurrentPos(to_)
            self._editor.SearchAnchor()
            loc = self._editor.SearchNext(fl, fs)
            if loc == -1:
                self._editor.SetAnchor(0)
                self._editor.SetCurrentPos(0)
                self._editor.SearchAnchor()
                self._editor.SearchNext(fl, fs)
        else:
            self._editor.SetAnchor(from_)
            self._editor.SetCurrentPos(from_)
            self._editor.SearchAnchor()
            loc = self._editor.SearchPrev(fl, fs)
            if loc == -1:
                self._editor.SetAnchor(self._editor.GetTextLength())
                self._editor.SetCurrentPos(self._editor.GetTextLength())
                self._editor.SearchAnchor()
                self._editor.SearchPrev(fl, fs)
        from_, to_ = self._editor.GetSelection()
        self._editor.ScrollRange(to_, from_)

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
