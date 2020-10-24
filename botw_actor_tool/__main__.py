import wx
import wx.lib.inspection

from .Ui_Main import UiMainWindow

# from . import actorinfo, actorpack, bootup, language


def main() -> None:
    app = wx.App()
    mainwindow = UiMainWindow(None, title="BotW Actor Tool")
    app.SetTopWindow(mainwindow)
    mainwindow.Show()
    wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()


if __name__ == "__main__":
    main()
