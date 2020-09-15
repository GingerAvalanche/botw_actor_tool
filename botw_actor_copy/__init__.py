import os
from pathlib import Path

gdata_file_prefixes = {
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

EXEC_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
