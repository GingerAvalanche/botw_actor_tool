# Breath of the Wild Flag Utilities
NOTE: This project is currently in unusable alpha state. This message will be removed and the package uplaoded to PyPI once it is in a usable state.
Utility for copying actors in LoZ:BotW

## Dependencies
* A dumped copy of Legend of Zelda: Breath of the Wild (for Wii U or Switch)
* Python 3.7+ (64-bit, added to system PATH)

The following `pip` packages, which will be automatically installed:
* bcml
* oead

## Setup
1. Download and install Python 3.7+, 64-bit. You must choose the "Add to System PATH" option during installation.
2. Open a command line and run `pip install botw_actor_copy`
3. Open `bcml` once and set up your paths, if you haven't already.

### How to Use

`botw_actor_copy [-b] [mod_root] [source_actor_name] [target_actor_name]`
* `mod_root` - The root folder of your mod. If your mod doesn't contain the necessary files and folders, they will be created. (Note that this means you can start a mod by creating an empty `[mod_root]/contents` folder and running the tool)
* `source_actor_name` - The name of the actor to copy
* `target_actor_name` - The name of the actor to create
* `-b` - Optional. Big endian mode, for Wii U.

#### Quirks
* Doesn't modify anything inside the sbfres files (`content/Model/*.sbfres`) that it generates. This is because there's no Python library for doing so. You'll need to use Switch Toolbox to edit those.
* Only creates certain gamedata and savedata flags, based on actor type. Will log which flags it creates to the console. Any additional flags should be created.

## Contributing
* Issues: https://github.com/GingerAvalanche/botw_actor_copy/issues
* Source: https://github.com/GingerAvalanche/botw_actor_copy

This software is in early, but usable, beta. Only extensively tested with armor and weapon actors, but should work fine with other actor types. Feel free to report issues or otherwise contribute in any way.

## License
This software is licensed under the terms of the GNU Affero General Public License, version 3+. The source is publicly available on Github.
