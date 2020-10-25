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

from . import util


class UiSettingsPanel(wx.Dialog):
    _settings: util.BatSettings
    _ctrls: dict

    def __init__(self, *args, **kwargs) -> None:
        super(UiSettingsPanel, self).__init__(*args, **kwargs)
        self.SetTitle("Settings")
        self._settings = util.BatSettings()
        self._ctrls = {}
        self.InitUI()
        util._set_dark_mode(self, self._settings.get_dark_mode())

    def InitUI(self):
        panelbox = wx.BoxSizer(wx.VERTICAL)

        gamedirbox = wx.BoxSizer(wx.HORIZONTAL)
        gamedirtext = wx.StaticText(self, label="Game Directory", size=(100, -1))
        gamedirctrl = wx.TextCtrl(
            self, value=str(self._settings.get_setting("game_dir")), size=(300, -1)
        )
        gamedirbtn = wx.Button(self, label="Browse...", size=(70, 25))
        self._ctrls["game_dir"] = gamedirctrl
        gamedirbox.Add(gamedirtext, flag=wx.ALIGN_CENTER_VERTICAL)
        gamedirbox.Add(gamedirctrl, proportion=1)
        gamedirbox.Add(gamedirbtn)
        panelbox.Add(gamedirbox, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        panelbox.AddSpacer(10)

        updatedirbox = wx.BoxSizer(wx.HORIZONTAL)
        updatedirtext = wx.StaticText(self, label="Update Directory", size=(100, -1))
        updatedirctrl = wx.TextCtrl(
            self, value=str(self._settings.get_setting("update_dir")), size=(300, -1)
        )
        updatedirbtn = wx.Button(self, label="Browse...", size=(70, 25))
        self._ctrls["update_dir"] = updatedirctrl
        updatedirbox.Add(updatedirtext, flag=wx.ALIGN_CENTER_VERTICAL)
        updatedirbox.Add(updatedirctrl, proportion=1)
        updatedirbox.Add(updatedirbtn)
        panelbox.Add(updatedirbox, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)

        panelbox.AddSpacer(10)

        dlcdirbox = wx.BoxSizer(wx.HORIZONTAL)
        dlcdirtext = wx.StaticText(self, label="DLC Directory", size=(100, -1))
        dlcdirctrl = wx.TextCtrl(
            self, value=str(self._settings.get_setting("dlc_dir")), size=(300, -1)
        )
        dlcdirbtn = wx.Button(self, label="Browse...", size=(70, 25))
        self._ctrls["dlc_dir"] = dlcdirctrl
        dlcdirbox.Add(dlcdirtext, flag=wx.ALIGN_CENTER_VERTICAL)
        dlcdirbox.Add(dlcdirctrl, proportion=1)
        dlcdirbox.Add(dlcdirbtn)
        panelbox.Add(dlcdirbox, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)

        panelbox.AddSpacer(10)

        langbox = wx.BoxSizer(wx.HORIZONTAL)
        langtext = wx.StaticText(self, label="Language", size=(100, -1))
        langctrl = wx.Choice(self, choices=util.LANGUAGES)
        langctrl.SetSelection(util.LANGUAGES.index(self._settings.get_setting("lang")))
        self._ctrls["lang"] = langctrl
        langbox.Add(langtext, flag=wx.ALIGN_CENTER_VERTICAL)
        langbox.Add(langctrl)
        panelbox.Add(langbox, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)

        panelbox.AddSpacer(10)

        checkboxbox = wx.BoxSizer(wx.HORIZONTAL)
        darkmodebox = wx.CheckBox(self, label="Dark Mode")
        darkmodebox.SetValue(self._settings.get_dark_mode())
        self._ctrls["dark"] = darkmodebox
        checkboxbox.Add(darkmodebox)
        panelbox.Add(checkboxbox, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)

        buttonbox = wx.BoxSizer(wx.HORIZONTAL)
        acceptbutton = wx.Button(self, label="Accept", size=(70, 25))
        buttonbox.Add(acceptbutton)
        cancelbutton = wx.Button(self, label="Cancel", size=(70, 25))
        buttonbox.Add(cancelbutton)
        panelbox.Add(buttonbox, flag=wx.ALIGN_RIGHT | wx.ALL, border=10)

        self.Bind(wx.EVT_BUTTON, self.OnGameDirBrowse, gamedirbtn)
        self.Bind(wx.EVT_BUTTON, self.OnUpdateDirBrowse, updatedirbtn)
        self.Bind(wx.EVT_BUTTON, self.OnDlcDirBrowse, dlcdirbtn)
        self.Bind(wx.EVT_CHECKBOX, self.OnDarkMode, darkmodebox)
        self.Bind(wx.EVT_BUTTON, self.OnAccept, acceptbutton)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, cancelbutton)

        self.SetSizerAndFit(panelbox)

    def OnGameDirBrowse(self, e) -> None:
        with wx.DirDialog(
            self,
            "Select game directory",
            self._ctrls["game_dir"].GetValue(),
            pos=self.GetPosition(),
        ) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self._ctrls["game_dir"].SetValue(dlg.GetPath())

    def OnUpdateDirBrowse(self, e) -> None:
        with wx.DirDialog(
            self,
            "Select update directory",
            self._ctrls["update_dir"].GetValue(),
            pos=self.GetPosition(),
        ) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self._ctrls["update_dir"].SetValue(dlg.GetPath())

    def OnDlcDirBrowse(self, e) -> None:
        with wx.DirDialog(
            self,
            "Select DLC directory",
            self._ctrls["dlc_dir"].GetValue(),
            pos=self.GetPosition(),
        ) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self._ctrls["dlc_dir"].SetValue(dlg.GetPath())

    def OnDarkMode(self, e) -> None:
        checked = e.GetEventObject().GetValue()
        util._set_dark_mode(self, checked)

    def OnAccept(self, e) -> None:
        game_dir = self._ctrls["game_dir"].GetValue()
        update_dir = self._ctrls["update_dir"].GetValue()
        dlc_dir = self._ctrls["dlc_dir"].GetValue()
        fails = []

        if not self._settings.validate_game_dir(Path(game_dir)):
            fails.append("Game directory")

        if not self._settings.validate_update_dir(Path(update_dir)):
            fails.append("Update directory")

        if not self._settings.validate_dlc_dir(Path(dlc_dir)):
            fails.append("DLC directory")

        if not len(fails) == 0:
            dlg = wx.MessageDialog(
                self,
                f"The following directories failed to validate because they were entered wrong: {', '.join(fails)}",
                "Directory Validation Error",
                wx.OK,
            )
            with dlg as d:
                d.ShowModal()
            return

        self._settings.set_setting("game_dir", game_dir)
        self._settings.set_setting("update_dir", update_dir)
        self._settings.set_setting("dlc_dir", dlc_dir)
        self._settings.set_setting(
            "lang", util.LANGUAGES[self._ctrls["lang"].GetCurrentSelection()]
        )
        self._settings.set_dark_mode(self._ctrls["dark"].GetValue())
        self._settings.save_settings()
        self.Close()

    def OnCancel(self, e) -> None:
        self.Close()
