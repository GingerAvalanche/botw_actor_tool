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

import os
from json import loads
from pathlib import Path

EXEC_DIR = Path(os.path.dirname(os.path.realpath(__file__)))

BGDATA_MAPPING = {
    "bool_array_data": "bool_array_data",
    "bool_data": "bool_data",
    "f32_array_data": "f32_array_data",
    "f32_data": "f32_data",
    "revival_bool_data": "bool_data",
    "revival_s32_data": "s32_data",
    "s32_array_data": "s32_array_data",
    "s32_data": "s32_data",
    "string256_array_data": "string256_array_data",
    "string256_data": "string256_data",
    "string32_data": "string_data",
    "string64_array_data": "string64_array_data",
    "string64_data": "string64_data",
    "vector2f_array_data": "vector2f_array_data",
    "vector2f_data": "vector2f_data",
    "vector3f_array_data": "vector3f_array_data",
    "vector3f_data": "vector3f_data",
    "vector4f_data": "vector4f_data",
}

generic_link_files = loads((EXEC_DIR / "data/generic_link_files.json").read_bytes())
overrides = loads((EXEC_DIR / "data/overrides.json").read_text())
