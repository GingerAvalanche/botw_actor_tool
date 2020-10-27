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
import wx.lib.inspection
from update_check import isUpToDate

from . import EXEC_DIR
from .Ui_Main import UiMainWindow


def main() -> None:
    app = wx.App()
    mainwindow = UiMainWindow(None, title="BotW Actor Tool")
    app.SetTopWindow(mainwindow)
    version = EXEC_DIR / "__version__.py"
    git_version = "https://raw.githubusercontent.com/GingerAvalanche/botw_actor_tool/master/botw_actor_tool/__version__.py"
    if isUpToDate(version, git_version) == False:
        mainwindow.SetNeedsUpdate()
    mainwindow.Show()
    # wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()


if __name__ == "__main__":
    main()
