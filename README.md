# Breath of the Wild Actor Editor
Utility for editing actors in Legend of Zelda: Breath of the Wild. With it, you can edit actors simply. No longer will you need to edit 4 different files just to add one new item! Now you can just select the item you want to base yours off of, change the name, change the texts, hit save, and boom! New item.

Note that the tool does not handle resource files (.sbfres). Those need to be handled with Switch Toolbox.

## Dependencies
* A dumped copy of Legend of Zelda: Breath of the Wild (for Wii U or Switch)
* Python 3.8-3.9 (64-bit, added to system PATH)

The following `pip` packages, which will be automatically installed:
* `wxPython`
* `PyMsyt`
* `oead`

## Setup
1. Download and install a version of Python between 3.8 and 3.9, 64-bit. You must choose the "Add to System PATH" option during installation.
2. Open a command line and run `pip install botw_actor_tool`

### How to Use
`botw_actor_tool`
* Open the tool with this command
* Set your paths in the Settings before trying to load any actors. It won't be able to find actor lists if it has no paths.
  * Paths are the same as they are in BCML
  * Settings has a dark mode option. The option is currently terrible. Use it at your own risk.
* Load a vanilla actor by using Ctrl+N or File -> Load Vanilla Actor. This will open a window that will allow you to choose the vanilla actor to load.
* Load a mod actor by using Ctrl+O or File -> Load Mod Actor. This will open a window that will allow you to choose your mod's `content` or `romfs` folder, and will then find any actors in that mod's `Actor/Pack` folder and display them for you to choose which one to load.
* Save by using Ctrl+S or File -> Save. Note that any changes to individual files/links that you haven't applied/saved will be lost.

#### Layout
##### Actor Link
This contains an entry for every "link" in the ActorLink file, plus a section for Tags.
* Links can be "Dummy" (no file), the actor's name, or a custom name. Selecting "Custom" won't actually do anything until you enter a custom name and click Update Custom Link.
* Tags are comma-separated, and will support as many or as few tags as you need.

##### Text Editors
Most tabs will open up text editors that allow you to edit the yaml of the files in question, and will then convert it back to aamp or byml when you click the Save button at the bottom.
* If you don't click the Save button at the bottom, your changes will be lost on switching tabs.

##### Texts Tab
Not to be confused with the text editor tabs, the texts tab is where you edit the texts of your item in-game. Things like its description, name, and compendium summary.
* BaseName - The name to display in the inventory. Only valid for cookable recipes that have more than one outcome.
* Name - The name to display in the inventory for most items.
* Desc - The inventory description of an actor that can go in Link's inventory.
* PictureBook - The description of an actor, as it appears in the compendium after you've taken a picture of it.

#### Obscure Features
* Putting the name of a file that exists in vanilla into a Custom link text field and then clicking Update Custom Link will retrieve that vanilla file's data and ask if you want to import it to your actor.
* Editing a file with a custom name will prompt you to change the name. This is due to BotW assuming that all files with the same name contain the same data, and only loading one of them.

## Contributing
* Issues: https://github.com/GingerAvalanche/botw_actor_tool/issues
* Source: https://github.com/GingerAvalanche/botw_actor_tool

This software is in early, but usable, beta. Only extensively tested with armor and weapon actors, but should work fine with other actor types. Feel free to report issues or otherwise contribute in any way.

## License
This software is licensed under the terms of the GNU Affero General Public License, version 3+. The source is publicly available on Github.
