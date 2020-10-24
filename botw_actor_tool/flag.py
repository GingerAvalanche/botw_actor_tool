from ctypes import c_int32
from enum import Enum
from oead import (
    S32,
    F32,
    FixedSafeString32,
    FixedSafeString64,
    FixedSafeString256,
    Vector2f,
    Vector3f,
    Vector4f,
)
from oead.byml import Hash, Array
from typing import List, Tuple
from zlib import crc32

from . import overrides


class BFUFlag:
    _data_name: str
    _delete_rev: int
    _hash_value: int
    _is_event_associated: bool
    _is_one_trigger: bool
    _is_program_readable: bool
    _is_program_writable: bool
    _is_save: bool
    _reset_type: int

    def __init__(self, flag: Hash = None) -> None:
        if flag:
            self._data_name = str(flag["DataName"])
            self._delete_rev = flag["DeleteRev"].v
            self._hash_value = flag["HashValue"].v
            self._is_event_associated = flag["IsEventAssociated"]
            self._is_one_trigger = flag["IsOneTrigger"]
            self._is_program_readable = flag["IsProgramReadable"]
            self._is_program_writable = flag["IsProgramWritable"]
            self._is_save = flag["IsSave"]
            self._reset_type = flag["ResetType"].v
        else:
            self._data_name = ""
            self._delete_rev = -1
            self._hash_value = 0
            self._is_event_associated = False
            self._is_one_trigger = False
            self._is_program_readable = True
            self._is_program_writable = True
            self._is_save = False
            self._reset_type = 0

    def __eq__(self, other):
        if not type(other) == BFUFlag:
            return NotImplemented
        if self is other:
            return True
        if (
            not self._data_name == other._data_name
            or not self._delete_rev == other._delete_rev
            or not self._hash_value == other._hash_value
            or not self._is_event_associated == other._is_event_associated
            or not self._is_one_trigger == other._is_one_trigger
            or not self._is_program_readable == other._is_program_readable
            or not self._is_program_writable == other._is_program_writable
            or not self._is_save == other._is_save
            or not self._reset_type == other._reset_type
        ):
            return False
        return True

    def to_Hash(self) -> Hash:
        r = Hash()
        r["DataName"] = self._data_name
        r["DeleteRev"] = S32(self._delete_rev)
        r["HashValue"] = S32(self._hash_value)
        r["IsEventAssociated"] = self._is_event_associated
        r["IsOneTrigger"] = self._is_one_trigger
        r["IsProgramReadable"] = self._is_program_readable
        r["IsProgramWritable"] = self._is_program_writable
        r["IsSave"] = self._is_save
        r["ResetType"] = S32(self._reset_type)
        return r

    def to_sv_Hash(self) -> Hash:
        r = Hash()
        r["DataName"] = self._data_name
        r["HashValue"] = S32(self._hash_value)
        return r

    def exists(self) -> bool:
        return not self._hash_value == 0

    def get_name(self) -> str:
        return self._data_name

    def name_contains(self, name: str) -> bool:
        return name in self._data_name

    def set_data_name(self, name: str) -> None:
        self._data_name = name
        self._hash_value = c_int32(crc32(name.encode("utf-8"))).value

    def set_event_assoc(self, event_assoc: bool) -> None:
        self._is_event_associated = event_assoc

    def set_reset_type(self, reset_type: int) -> None:
        self._reset_type = reset_type

    def get_hash(self) -> int:
        return self._hash_value

    def set_is_one_trigger(self, is_one: bool) -> None:
        self._is_one_trigger = is_one

    def is_save(self) -> bool:
        return self._is_save

    def set_is_save(self, is_save: bool) -> None:
        self._is_save = is_save

    def set_category(self, value) -> None:
        """Used by BoolFlag to set the _category"""

    def set_init_value(self, value) -> None:
        """Sets initial values, subclasses set the type"""

    def set_max_value(self, value) -> None:
        """Sets max values, subclasses set the type"""

    def set_min_value(self, value) -> None:
        """Sets min values, subclasses set the type"""

    def is_revival(self) -> bool:
        """Gets whether or not the flag belongs in the revival files.
        Only valid for S32Flag and BoolFlag."""

    def use_name_to_override_params(self) -> None:
        OVERRIDES = overrides["STANDARD_OVERRIDES"]
        for substr, value in OVERRIDES["OVERRIDE_IS_EVENT_ASSOCIATED"].items():
            if substr in self._data_name:
                self._is_event_associated = value
        for substr, value in OVERRIDES["OVERRIDE_IS_ONE_TRIGGER"].items():
            if substr in self._data_name:
                self._is_one_trigger = value
        for substr, value in OVERRIDES["OVERRIDE_IS_PROGRAM_READABLE"].items():
            if substr in self._data_name:
                self._is_program_readable = value
        for substr, value in OVERRIDES["OVERRIDE_IS_PROGRAM_WRITABLE"].items():
            if substr in self._data_name:
                self._is_program_writable = value
        for substr, value in OVERRIDES["OVERRIDE_IS_SAVE"].items():
            if substr in self._data_name:
                self._is_save = value
        for substr, value in OVERRIDES["OVERRIDE_RESET_TYPE"].items():
            if substr in self._data_name:
                self._reset_type = value


class BoolFlag(BFUFlag):
    _category: int
    _init_value: int
    _max_value: bool
    _min_value: bool
    _revival: bool

    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(BoolFlag, self).__init__(flag=flag)
        self._revival = kwargs["revival"] if "revival" in kwargs else False
        if flag:
            self._category = flag["Category"].v if "Category" in flag else -1
            self._init_value = flag["InitValue"].v
            self._max_value = flag["MaxValue"]
            self._min_value = flag["MinValue"]
        else:
            self._category = -1
            self._init_value = 0
            self._max_value = True
            self._min_value = False

    def __eq__(self, other):
        if not type(other) == BoolFlag:
            return NotImplemented
        if not super(BoolFlag, self).__eq__(super(BoolFlag, other)):
            return False
        if (
            not self._category == other._category
            or not self._init_value == other._init_value
            or not self._max_value == other._max_value
            or not self._min_value == other._min_value
        ):
            return False
        return True

    def to_Hash(self) -> Hash:
        r = super(BoolFlag, self).to_Hash()
        if not self._category == -1:
            r["Category"] = S32(self._category)
        r["InitValue"] = S32(self._init_value)
        r["MaxValue"] = self._max_value
        r["MinValue"] = self._min_value
        return r

    def set_category(self, value: int) -> None:
        self._category = value

    def set_init_value(self, value: bool) -> None:
        self._init_value = value

    def set_max_value(self, value: bool) -> None:
        self._max_value = value

    def set_min_value(self, value: bool) -> None:
        self._min_value = value

    def is_revival(self) -> bool:
        return self._revival

    def use_name_to_override_params(self) -> None:
        super(BoolFlag, self).use_name_to_override_params()
        OVERRIDES = overrides["BOOL_OVERRIDES"]
        for substr, value in OVERRIDES["OVERRIDE_BOOL_CATEGORY"].items():
            if substr in self._data_name:
                self._category = value
        for substr, value in OVERRIDES["OVERRIDE_BOOL_INIT_VALUE"].items():
            if substr in self._data_name:
                self._init_value = value


class BoolArrayFlag(BFUFlag):
    _init_value: List[int]
    _max_value: bool
    _min_value: bool

    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(BoolArrayFlag, self).__init__(flag=flag)
        if flag:
            self._init_value = [value.v for value in flag["InitValue"][0]["Values"]]
            self._max_value = flag["MaxValue"]
            self._min_value = flag["MinValue"]
        else:
            self._init_value = [0]
            self._max_value = True
            self._min_value = False

    def __eq__(self, other):
        if not type(other) == BoolArrayFlag:
            return NotImplemented
        if not super(BoolArrayFlag, self).__eq__(super(BoolArrayFlag, other)):
            return False
        if (
            not self._init_value == other._init_value
            or not self._max_value == other._max_value
            or not self._min_value == other._min_value
        ):
            return False
        return True

    def to_Hash(self) -> Hash:
        r = super(BoolArrayFlag, self).to_Hash()
        array_one = Array()
        array_one.append(Hash())
        array_two = Array([S32(value) for value in self._init_value])
        array_one[0]["Values"] = array_two
        r["InitValue"] = array_one
        r["MaxValue"] = self._max_value
        r["MinValue"] = self._min_value
        return r

    def set_category(self, value) -> None:
        return

    def set_init_value(self, value: List[int]) -> None:
        self._init_value = value

    def set_max_value(self, value: bool) -> None:
        self._max_value = value

    def set_min_value(self, value: bool) -> None:
        self._min_value = value

    def is_revival(self) -> bool:
        return False

    def use_name_to_override_params(self) -> None:
        super(BoolArrayFlag, self).use_name_to_override_params()
        OVERRIDES = overrides["BOOL_ARRAY_OVERRIDES"]
        for substr, value in OVERRIDES["OVERRIDE_BOOL_ARRAY_INIT_VALUE"].items():
            if substr in self._data_name:
                self._init_value = value
        for substr, value in OVERRIDES["OVERRIDE_BOOL_ARRAY_MAX_VALUE"].items():
            if substr in self._data_name:
                self._max_value = value
        for substr, value in OVERRIDES["OVERRIDE_BOOL_ARRAY_MIN_VALUE"].items():
            if substr in self._data_name:
                self._min_value = value


class S32Flag(BFUFlag):
    _init_value: int
    _max_value: int
    _min_value: int
    _revival: bool

    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(S32Flag, self).__init__(flag=flag)
        self._revival = kwargs["revival"] if "revival" in kwargs else False
        if flag:
            self._init_value = flag["InitValue"].v
            self._max_value = flag["MaxValue"].v
            self._min_value = flag["MinValue"].v
        else:
            self._init_value = 0
            self._max_value = 2147483647
            self._min_value = 0

    def __eq__(self, other):
        if not type(other) == S32Flag:
            return NotImplemented
        if not super(S32Flag, self).__eq__(super(S32Flag, other)):
            return False
        if (
            not self._init_value == other._init_value
            or not self._max_value == other._max_value
            or not self._min_value == other._min_value
        ):
            return False
        return True

    def to_Hash(self) -> Hash:
        r = super(S32Flag, self).to_Hash()
        r["InitValue"] = S32(self._init_value)
        r["MaxValue"] = S32(self._max_value)
        r["MinValue"] = S32(self._min_value)
        return r

    def set_category(self, value) -> None:
        return

    def set_init_value(self, value: int) -> None:
        self._init_value = value

    def set_max_value(self, value: int) -> None:
        self._max_value = value

    def set_min_value(self, value: int) -> None:
        self._min_value = value

    def is_revival(self) -> bool:
        return self._revival

    def use_name_to_override_params(self) -> None:
        super(S32Flag, self).use_name_to_override_params()
        OVERRIDES = overrides["S32_OVERRRIDES"]
        for substr, value in OVERRIDES["OVERRIDE_S32_INIT_VALUE"].items():
            if substr in self._data_name:
                self._init_value = value
        for substr, value in OVERRIDES["OVERRIDE_S32_MAX_VALUE"].items():
            if substr in self._data_name:
                self._max_value = value
        for substr, value in OVERRIDES["OVERRIDE_S32_MIN_VALUE"].items():
            if substr in self._data_name:
                self._min_value = value


class S32ArrayFlag(BFUFlag):
    _init_value: List[int]
    _max_value: int
    _min_value: int

    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(S32ArrayFlag, self).__init__(flag=flag)
        if flag:
            self._init_value = [int(value) for value in flag["InitValue"][0]["Values"]]
            self._max_value = flag["MaxValue"].v
            self._min_value = flag["MinValue"].v
        else:
            self._init_value = [0]
            self._max_value = 6553500
            self._min_value = -1

    def __eq__(self, other):
        if not type(other) == S32ArrayFlag:
            return NotImplemented
        if not super(S32ArrayFlag, self).__eq__(super(S32ArrayFlag, other)):
            return False
        if (
            not self._init_value == other._init_value
            or not self._max_value == other._max_value
            or not self._min_value == other._min_value
        ):
            return False
        return True

    def to_Hash(self) -> Hash:
        r = super(S32ArrayFlag, self).to_Hash()
        array_one = Array()
        array_one.append(Hash())
        array_two = Array([S32(value) for value in self._init_value])
        array_one[0]["Values"] = array_two
        r["InitValue"] = array_one
        r["MaxValue"] = S32(self._max_value)
        r["MinValue"] = S32(self._min_value)
        return r

    def set_category(self, value) -> None:
        return

    def set_init_value(self, value: List[int]) -> None:
        self._init_value = value

    def set_max_value(self, value: int) -> None:
        self._max_value = value

    def set_min_value(self, value: int) -> None:
        self._min_value = value

    def is_revival(self) -> bool:
        return False

    def use_name_to_override_params(self) -> None:
        super(S32ArrayFlag, self).use_name_to_override_params()
        OVERRIDES = overrides["S32_ARRAY_OVERRIDES"]
        for substr, value in OVERRIDES["OVERRIDE_S32_ARRAY_INIT_VALUE"].items():
            if substr in self._data_name:
                self._init_value = value
        for substr, value in OVERRIDES["OVERRIDE_S32_ARRAY_MAX_VALUE"].items():
            if substr in self._data_name:
                self._max_value = value
        for substr, value in OVERRIDES["OVERRIDE_S32_ARRAY_MIN_VALUE"].items():
            if substr in self._data_name:
                self._min_value = value


class F32Flag(BFUFlag):
    _init_value: float
    _max_value: float
    _min_value: float

    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(F32Flag, self).__init__(flag=flag)
        if flag:
            self._init_value = flag["InitValue"].v
            self._max_value = flag["MaxValue"].v
            self._min_value = flag["MinValue"].v
        else:
            self._init_value = 0.0
            self._max_value = 1000000.0
            self._min_value = 0.0

    def __eq__(self, other):
        if not type(other) == F32Flag:
            return NotImplemented
        if not super(F32Flag, self).__eq__(super(F32Flag, other)):
            return False
        if (
            not self._init_value == other._init_value
            or not self._max_value == other._max_value
            or not self._min_value == other._min_value
        ):
            return False
        return True

    def to_Hash(self) -> Hash:
        r = super(F32Flag, self).to_Hash()
        r["InitValue"] = F32(self._init_value)
        r["MaxValue"] = F32(self._max_value)
        r["MinValue"] = F32(self._min_value)
        return r

    def set_category(self, value) -> None:
        return

    def set_init_value(self, value: float) -> None:
        self._init_value = value

    def set_max_value(self, value: float) -> None:
        self._max_value = value

    def set_min_value(self, value: float) -> None:
        self._min_value = value

    def is_revival(self) -> bool:
        return False

    def use_name_to_override_params(self) -> None:
        super(F32Flag, self).use_name_to_override_params()
        OVERRIDES = overrides["F32_OVERRIDES"]
        for substr, value in OVERRIDES["OVERRIDE_F32_INIT_VALUE"].items():
            if substr in self._data_name:
                self._init_value = value
        for substr, value in OVERRIDES["OVERRIDE_F32_MAX_VALUE"].items():
            if substr in self._data_name:
                self._max_value = value
        for substr, value in OVERRIDES["OVERRIDE_F32_MIN_VALUE"].items():
            if substr in self._data_name:
                self._min_value = value


class F32ArrayFlag(BFUFlag):
    _init_value: List[float]
    _max_value: float
    _min_value: float

    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(F32ArrayFlag, self).__init__(flag=flag)
        if flag:
            self._init_value = [value.v for value in flag["InitValue"][0]["Values"]]
            self._max_value = flag["MaxValue"].v
            self._min_value = flag["MinValue"].v
        else:
            self._init_value = [0.0]
            self._max_value = 360.0
            self._min_value = -1.0

    def __eq__(self, other):
        if not type(other) == F32ArrayFlag:
            return NotImplemented
        if not super(F32ArrayFlag, self).__eq__(super(F32ArrayFlag, other)):
            return False
        if (
            not self._init_value == other._init_value
            or not self._max_value == other._max_value
            or not self._min_value == other._min_value
        ):
            return False
        return True

    def to_Hash(self) -> Hash:
        r = super(F32ArrayFlag, self).to_Hash()
        array_one = Array()
        array_one.append(Hash())
        array_two = Array([F32(value) for value in self._init_value])
        array_one[0]["Values"] = array_two
        r["InitValue"] = array_one
        r["MaxValue"] = F32(self._max_value)
        r["MinValue"] = F32(self._min_value)
        return r

    def set_category(self, value) -> None:
        return

    def set_init_value(self, value: List[float]) -> None:
        self._init_value = value

    def set_max_value(self, value: float) -> None:
        self._max_value = value

    def set_min_value(self, value: float) -> None:
        self._min_value = value

    def is_revival(self) -> bool:
        return False

    def use_name_to_override_params(self) -> None:
        super(F32ArrayFlag, self).use_name_to_override_params()
        OVERRIDES = overrides["F32_ARRAY_OVERRIDES"]
        for substr, value in OVERRIDES["OVERRIDE_F32_ARRAY_INIT_VALUE"].items():
            if substr in self._data_name:
                self._init_value = value
        for substr, value in OVERRIDES["OVERRIDE_F32_ARRAY_MAX_VALUE"].items():
            if substr in self._data_name:
                self._max_value = value
        for substr, value in OVERRIDES["OVERRIDE_F32_ARRAY_MIN_VALUE"].items():
            if substr in self._data_name:
                self._min_value = value


class StringFlag(BFUFlag):
    _init_value: str
    _max_value: str
    _min_value: str

    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(StringFlag, self).__init__(flag=flag)
        if flag:
            self._init_value = str(flag["InitValue"])
            self._max_value = str(flag["MaxValue"])
            self._min_value = str(flag["MinValue"])
        else:
            self._init_value = ""
            self._max_value = ""
            self._min_value = ""

    def __eq__(self, other):
        if not type(other) == StringFlag:
            return NotImplemented
        if not super(StringFlag, self).__eq__(super(StringFlag, other)):
            return False
        if (
            not self._init_value == other._init_value
            or not self._max_value == other._max_value
            or not self._min_value == other._min_value
        ):
            return False
        return True

    def to_Hash(self) -> Hash:
        r = super(StringFlag, self).to_Hash()
        return r

    def set_category(self, value) -> None:
        return

    def set_init_value(self, value: str) -> None:
        self._init_value = value

    def set_max_value(self, value: str) -> None:
        self._max_value = value

    def set_min_value(self, value: str) -> None:
        self._min_value = value

    def is_revival(self) -> bool:
        return False

    def use_name_to_override_params(self) -> None:
        super(StringFlag, self).use_name_to_override_params()
        OVERRIDES = overrides["STRING_OVERRIDES"]
        for substr, value in OVERRIDES["OVERRIDE_STRING_INIT_VALUE"].items():
            if substr in self._data_name:
                self._init_value = value
        for substr, value in OVERRIDES["OVERRIDE_STRING_MAX_VALUE"].items():
            if substr in self._data_name:
                self._max_value = value
        for substr, value in OVERRIDES["OVERRIDE_STRING_MIN_VALUE"].items():
            if substr in self._data_name:
                self._min_value = value


class String32Flag(StringFlag):
    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(String32Flag, self).__init__(flag=flag)

    def to_Hash(self) -> Hash:
        r = super(String32Flag, self).to_Hash()
        # r["InitValue"] = FixedSafeString32(self._init_value)
        r["InitValue"] = self._init_value
        # r["MaxValue"] = FixedSafeString32(self._max_value)
        r["MaxValue"] = self._max_value
        # r["MinValue"] = FixedSafeString32(self._min_value)
        r["MinValue"] = self._min_value
        return r


class String64Flag(StringFlag):
    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(String64Flag, self).__init__(flag=flag)

    def to_Hash(self) -> Hash:
        r = super(String64Flag, self).to_Hash()
        # r["InitValue"] = FixedSafeString64(self._init_value)
        r["InitValue"] = self._init_value
        # r["MaxValue"] = FixedSafeString64(self._max_value)
        r["MaxValue"] = self._max_value
        # r["MinValue"] = FixedSafeString64(self._min_value)
        r["MinValue"] = self._min_value
        return r


class String256Flag(StringFlag):
    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(String256Flag, self).__init__(flag=flag)

    def to_Hash(self) -> Hash:
        r = super(String256Flag, self).to_Hash()
        # r["InitValue"] = FixedSafeString256(self._init_value)
        r["InitValue"] = self._init_value
        # r["MaxValue"] = FixedSafeString256(self._max_value)
        r["MaxValue"] = self._max_value
        # r["MinValue"] = FixedSafeString256(self._min_value)
        r["MinValue"] = self._min_value
        return r


class StringArrayFlag(BFUFlag):
    _init_value: List[str]
    _max_value: str
    _min_value: str

    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(StringArrayFlag, self).__init__(flag=flag)
        if flag:
            self._init_value = [str(value) for value in flag["InitValue"][0]["Values"]]
            self._max_value = str(flag["MaxValue"])
            self._min_value = str(flag["MinValue"])
        else:
            self._init_value = [""]
            self._max_value = ""
            self._min_value = ""

    def __eq__(self, other):
        if not type(other) == StringArrayFlag:
            return NotImplemented
        if not super(StringArrayFlag, self).__eq__(super(StringArrayFlag, other)):
            return False
        if (
            not self._init_value == other._init_value
            or not self._max_value == other._max_value
            or not self._min_value == other._min_value
        ):
            return False
        return True

    def to_Hash(self) -> Hash:
        r = super(StringArrayFlag, self).to_Hash()
        return r

    def set_category(self, value) -> None:
        return

    def set_init_value(self, value: List[str]) -> None:
        self._init_value = value

    def set_max_value(self, value: str) -> None:
        self._max_value = value

    def set_min_value(self, value: str) -> None:
        self._min_value = value

    def is_revival(self) -> bool:
        return False

    def use_name_to_override_params(self) -> None:
        super(StringArrayFlag, self).use_name_to_override_params()
        OVERRIDES = overrides["STRING_ARRAY_OVERRIDES"]
        for substr, value in OVERRIDES["OVERRIDE_STRING_ARRAY_INIT_VALUE"].items():
            if substr in self._data_name:
                self._init_value = value
        for substr, value in OVERRIDES["OVERRIDE_STRING_ARRAY_MAX_VALUE"].items():
            if substr in self._data_name:
                self._max_value = value
        for substr, value in OVERRIDES["OVERRIDE_STRING_ARRAY_MIN_VALUE"].items():
            if substr in self._data_name:
                self._min_value = value


class String64ArrayFlag(StringArrayFlag):
    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(String64ArrayFlag, self).__init__(flag=flag)

    def to_Hash(self) -> Hash:
        r = super(String64ArrayFlag, self).to_Hash()
        array_one = Array()
        array_one.append(Hash())
        # array_two = [FixedSafeString64(value) for value in self._init_value]
        array_two = Array(self._init_value)
        array_one[0]["Values"] = array_two
        r["InitValue"] = array_one
        # r["MaxValue"] = FixedSafeString64(self._max_value)
        r["MaxValue"] = self._max_value
        # r["MinValue"] = FixedSafeString64(self._min_value)
        r["MinValue"] = self._min_value
        return r


class String256ArrayFlag(StringArrayFlag):
    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(String256ArrayFlag, self).__init__(flag=flag)

    def to_Hash(self) -> Hash:
        r = super(String256ArrayFlag, self).to_Hash()
        array_one = Array()
        array_one.append(Hash())
        # array_two = [FixedSafeString256(value) for value in self._init_value]
        array_two = Array(self._init_value)
        array_one[0]["Values"] = array_two
        r["InitValue"] = array_one
        # r["MaxValue"] = FixedSafeString256(self._max_value)
        r["MaxValue"] = self._max_value
        # r["MinValue"] = FixedSafeString256(self._min_value)
        r["MinValue"] = self._min_value
        return r


class Vec2Flag(BFUFlag):
    _init_value: Tuple[float, float]
    _max_value: Tuple[float, float]
    _min_value: Tuple[float, float]

    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(Vec2Flag, self).__init__(flag=flag)
        if flag:
            self._init_value = (flag["InitValue"][0][0].v, flag["InitValue"][0][1].v)
            self._max_value = (flag["MaxValue"][0][0].v, flag["MaxValue"][0][1].v)
            self._min_value = (flag["MinValue"][0][0].v, flag["MinValue"][0][1].v)
        else:
            self._init_value = (0.0, 0.0)
            self._max_value = (255.0, 255.0)
            self._min_value = (0.0, 0.0)

    def __eq__(self, other):
        if not type(other) == Vec2Flag:
            return NotImplemented
        if not super(Vec2Flag, self).__eq__(super(Vec2Flag, other)):
            return False
        if (
            not self._init_value == other._init_value
            or not self._max_value == other._max_value
            or not self._min_value == other._min_value
        ):
            return False
        return True

    def to_Hash(self) -> Hash:
        r = super(Vec2Flag, self).to_Hash()
        array = Array()
        vec = Array()
        vec.append(F32(self._init_value[0]))
        vec.append(F32(self._init_value[1]))
        array.append(vec)
        r["InitValue"] = array
        array = Array()
        vec = Array()
        vec.append(F32(self._max_value[0]))
        vec.append(F32(self._max_value[1]))
        array.append(vec)
        r["MaxValue"] = array
        array = Array()
        vec = Array()
        vec.append(F32(self._min_value[0]))
        vec.append(F32(self._min_value[1]))
        array.append(vec)
        r["MinValue"] = array
        return r

    def set_category(self, value) -> None:
        return

    def set_init_value(self, value: Tuple[float, float]) -> None:
        self._init_value = value

    def set_max_value(self, value: Tuple[float, float]) -> None:
        self._max_value = value

    def set_min_value(self, value: Tuple[float, float]) -> None:
        self._min_value = value

    def is_revival(self) -> bool:
        return False

    def use_name_to_override_params(self) -> None:
        super(Vec2Flag, self).use_name_to_override_params()
        OVERRIDES = overrides["VEC2_OVERRIDES"]
        for substr, value in OVERRIDES["OVERRIDE_VEC2_INIT_VALUE"].items():
            if substr in self._data_name:
                self._init_value = value
        for substr, value in OVERRIDES["OVERRIDE_VEC2_MAX_VALUE"].items():
            if substr in self._data_name:
                self._max_value = value
        for substr, value in OVERRIDES["OVERRIDE_VEC2_MIN_VALUE"].items():
            if substr in self._data_name:
                self._min_value = value


class Vec2ArrayFlag(BFUFlag):
    _init_value: List[Tuple[float, float]]
    _max_value: Tuple[float, float]
    _min_value: Tuple[float, float]

    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(Vec2ArrayFlag, self).__init__(flag=flag)
        if flag:
            vec_array = []
            for vector in flag["InitValue"][0]["Values"]:
                vec_array.append((vector[0][0].v, vector[0][1].v))
            self._init_value = vec_array
            self._max_value = (flag["MaxValue"][0][0].v, flag["MaxValue"][0][1].v)
            self._min_value = (flag["MinValue"][0][0].v, flag["MinValue"][0][1].v)
        else:
            self._init_value = [(0.0, 0.0)]
            self._max_value = (255.0, 255.0)
            self._min_value = (0.0, 0.0)

    def __eq__(self, other):
        if not type(other) == Vec2ArrayFlag:
            return NotImplemented
        if not super(Vec2ArrayFlag, self).__eq__(super(Vec2ArrayFlag, other)):
            return False
        if (
            not self._init_value == other._init_value
            or not self._max_value == other._max_value
            or not self._min_value == other._min_value
        ):
            return False
        return True

    def to_Hash(self) -> Hash:
        r = super(Vec2ArrayFlag, self).to_Hash()
        vec_array = Array()
        vec_array.append(Hash())
        vec_array[0]["Values"] = Array()
        for i in range(len(self._init_value)):
            vector = self._init_value[i]
            vec = Array()
            vec.append(F32(vector[0]))
            vec.append(F32(vector[1]))
            vec_array[0]["Values"].append(Array())
            vec_array[0]["Values"][i].append(vec)
        r["InitValue"] = vec_array
        vec_array = Array()
        vec = Array()
        vec.append(F32(self._max_value[0]))
        vec.append(F32(self._max_value[1]))
        vec_array.append(vec)
        r["MaxValue"] = vec_array
        vec_array = Array()
        vec = Array()
        vec.append(F32(self._min_value[0]))
        vec.append(F32(self._min_value[1]))
        vec_array.append(vec)
        r["MinValue"] = vec_array
        return r

    def set_category(self, value) -> None:
        return

    def set_init_value(self, value: List[Tuple[float, float]]) -> None:
        self._init_value = value

    def set_max_value(self, value: Tuple[float, float]) -> None:
        self._max_value = value

    def set_min_value(self, value: Tuple[float, float]) -> None:
        self._min_value = value

    def is_revival(self) -> bool:
        return False

    def use_name_to_override_params(self) -> None:
        super(Vec2ArrayFlag, self).use_name_to_override_params()
        OVERRIDES = overrides["VEC2_ARRAY_OVERRIDES"]
        for substr, value in OVERRIDES["OVERRIDE_VEC2_ARRAY_INIT_VALUE"].items():
            if substr in self._data_name:
                self._init_value = value
        for substr, value in OVERRIDES["OVERRIDE_VEC2_ARRAY_MAX_VALUE"].items():
            if substr in self._data_name:
                self._max_value = value
        for substr, value in OVERRIDES["OVERRIDE_VEC2_ARRAY_MIN_VALUE"].items():
            if substr in self._data_name:
                self._min_value = value


class Vec3Flag(BFUFlag):
    _init_value: Tuple[float, float, float]
    _max_value: Tuple[float, float, float]
    _min_value: Tuple[float, float, float]

    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(Vec3Flag, self).__init__(flag=flag)
        if flag:
            self._init_value = (
                flag["InitValue"][0][0].v,
                flag["InitValue"][0][1].v,
                flag["InitValue"][0][2].v,
            )
            self._max_value = (
                flag["MaxValue"][0][0].v,
                flag["MaxValue"][0][1].v,
                flag["MaxValue"][0][2].v,
            )
            self._min_value = (
                flag["MinValue"][0][0].v,
                flag["MinValue"][0][1].v,
                flag["MinValue"][0][2].v,
            )
        else:
            self._init_value = (0.0, 0.0, 0.0)
            self._max_value = (100000.0, 100000.0, 100000.0)
            self._min_value = (-100000.0, -100000.0, -100000.0)

    def __eq__(self, other):
        if not type(other) == Vec3Flag:
            return NotImplemented
        if not super(Vec3Flag, self).__eq__(super(Vec3Flag, other)):
            return False
        if (
            not self._init_value == other._init_value
            or not self._max_value == other._max_value
            or not self._min_value == other._min_value
        ):
            return False
        return True

    def to_Hash(self) -> Hash:
        r = super(Vec3Flag, self).to_Hash()
        vec_array = Array()
        vec = Array()
        vec.append(F32(self._init_value[0]))
        vec.append(F32(self._init_value[1]))
        vec.append(F32(self._init_value[2]))
        vec_array.append(vec)
        r["InitValue"] = vec_array
        vec_array = Array()
        vec = Array()
        vec.append(F32(self._max_value[0]))
        vec.append(F32(self._max_value[1]))
        vec.append(F32(self._max_value[2]))
        vec_array.append(vec)
        r["MaxValue"] = vec_array
        vec_array = Array()
        vec = Array()
        vec.append(F32(self._min_value[0]))
        vec.append(F32(self._min_value[1]))
        vec.append(F32(self._min_value[2]))
        vec_array.append(vec)
        r["MinValue"] = vec_array
        return r

    def set_category(self, value) -> None:
        return

    def set_init_value(self, value: Tuple[float, float, float]) -> None:
        self._init_value = value

    def set_max_value(self, value: Tuple[float, float, float]) -> None:
        self._max_value = value

    def set_min_value(self, value: Tuple[float, float, float]) -> None:
        self._min_value = value

    def is_revival(self) -> bool:
        return False

    def use_name_to_override_params(self) -> None:
        super(Vec3Flag, self).use_name_to_override_params()
        OVERRIDES = overrides["VEC3_OVERRIDES"]
        for substr, value in OVERRIDES["OVERRIDE_VEC3_INIT_VALUE"].items():
            if substr in self._data_name:
                self._init_value = value
        for substr, value in OVERRIDES["OVERRIDE_VEC3_MAX_VALUE"].items():
            if substr in self._data_name:
                self._max_value = value
        for substr, value in OVERRIDES["OVERRIDE_VEC3_MIN_VALUE"].items():
            if substr in self._data_name:
                self._min_value = value


class Vec3ArrayFlag(BFUFlag):
    _init_value: List[Tuple[float, float, float]]
    _max_value: Tuple[float, float, float]
    _min_value: Tuple[float, float, float]

    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(Vec3ArrayFlag, self).__init__(flag=flag)
        if flag:
            vec_array = []
            for vector in flag["InitValue"][0]["Values"]:
                vec_array.append((vector[0][0].v, vector[0][1].v, vector[0][2].v))
            self._init_value = vec_array
            self._max_value = (
                flag["MaxValue"][0][0].v,
                flag["MaxValue"][0][1].v,
                flag["MaxValue"][0][2].v,
            )
            self._min_value = (
                flag["MinValue"][0][0].v,
                flag["MinValue"][0][1].v,
                flag["MinValue"][0][2].v,
            )
        else:
            self._init_value = [(0.0, 0.0, 0.0)]
            self._max_value = (255.0, 255.0, 255.0)
            self._min_value = (0.0, 0.0, 0.0)

    def __eq__(self, other):
        if not type(other) == Vec3ArrayFlag:
            return NotImplemented
        if not super(Vec3ArrayFlag, self).__eq__(super(Vec3ArrayFlag, other)):
            return False
        if (
            not self._init_value == other._init_value
            or not self._max_value == other._max_value
            or not self._min_value == other._min_value
        ):
            return False
        return True

    def to_Hash(self) -> Hash:
        r = super(Vec3ArrayFlag, self).to_Hash()
        vec_array = Array()
        vec_array.append(Hash())
        vec_array[0]["Values"] = Array()
        for i in range(len(self._init_value)):
            vector = self._init_value[i]
            vec = Array()
            vec.append(F32(vector[0]))
            vec.append(F32(vector[1]))
            vec.append(F32(vector[2]))
            vec_array[0]["Values"].append(Array())
            vec_array[0]["Values"][i].append(vec)
        r["InitValue"] = vec_array
        vec_array = Array()
        vec = Array()
        vec.append(F32(self._max_value[0]))
        vec.append(F32(self._max_value[1]))
        vec.append(F32(self._max_value[2]))
        vec_array.append(vec)
        r["MaxValue"] = vec_array
        vec_array = Array()
        vec = Array()
        vec.append(F32(self._min_value[0]))
        vec.append(F32(self._min_value[1]))
        vec.append(F32(self._min_value[2]))
        vec_array.append(vec)
        r["MinValue"] = vec_array
        return r

    def set_category(self, value) -> None:
        return

    def set_init_value(self, value: List[Tuple[float, float, float]]) -> None:
        self._init_value = value

    def set_max_value(self, value: Tuple[float, float, float]) -> None:
        self._max_value = value

    def set_min_value(self, value: Tuple[float, float, float]) -> None:
        self._min_value = value

    def is_revival(self) -> bool:
        return False

    def use_name_to_override_params(self) -> None:
        super(Vec3ArrayFlag, self).use_name_to_override_params()
        OVERRIDES = overrides["VEC3_ARRAY_OVERRIDES"]
        for substr, value in OVERRIDES["OVERRIDE_VEC3_ARRAY_INIT_VALUE"].items():
            if substr in self._data_name:
                self._init_value = value
        for substr, value in OVERRIDES["OVERRIDE_VEC3_ARRAY_MAX_VALUE"].items():
            if substr in self._data_name:
                self._max_value = value
        for substr, value in OVERRIDES["OVERRIDE_VEC3_ARRAY_MIN_VALUE"].items():
            if substr in self._data_name:
                self._min_value = value


class Vec4Flag(BFUFlag):
    _init_value: Tuple[float, float, float, float]
    _max_value: Tuple[float, float, float, float]
    _min_value: Tuple[float, float, float, float]

    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(Vec4Flag, self).__init__(flag=flag)
        if flag:
            self._init_value = (
                flag["InitValue"][0][0].v,
                flag["InitValue"][0][1].v,
                flag["InitValue"][0][2].v,
                flag["InitValue"][0][3].v,
            )
            self._max_value = (
                flag["MaxValue"][0][0].v,
                flag["MaxValue"][0][1].v,
                flag["MaxValue"][0][2].v,
                flag["MaxValue"][0][3].v,
            )
            self._min_value = (
                flag["MinValue"][0][0].v,
                flag["MinValue"][0][1].v,
                flag["MinValue"][0][2].v,
                flag["MinValue"][0][3].v,
            )
        else:
            self._init_value = (0.0, 0.0, 0.0, 0.0)
            self._max_value = (255.0, 255.0, 255.0, 255.0)
            self._min_value = (0.0, 0.0, 0.0, 0.0)

    def __eq__(self, other):
        if not type(other) == Vec4Flag:
            return NotImplemented
        if not super(Vec4Flag, self).__eq__(super(Vec4Flag, other)):
            return False
        if (
            not self._init_value == other._init_value
            or not self._max_value == other._max_value
            or not self._min_value == other._min_value
        ):
            return False
        return True

    def to_Hash(self) -> Hash:
        r = super(Vec4Flag, self).to_Hash()
        array = Array()
        vec = Array()
        vec.append(F32(self._init_value[0]))
        vec.append(F32(self._init_value[1]))
        vec.append(F32(self._init_value[2]))
        vec.append(F32(self._init_value[3]))
        array.append(vec)
        r["InitValue"] = array
        array = Array()
        vec = Array()
        vec.append(F32(self._max_value[0]))
        vec.append(F32(self._max_value[1]))
        vec.append(F32(self._max_value[2]))
        vec.append(F32(self._max_value[3]))
        array.append(vec)
        r["MaxValue"] = array
        array = Array()
        vec = Array()
        vec.append(F32(self._min_value[0]))
        vec.append(F32(self._min_value[1]))
        vec.append(F32(self._min_value[2]))
        vec.append(F32(self._min_value[3]))
        array.append(vec)
        r["MinValue"] = array
        return r

    def set_category(self, value) -> None:
        return

    def set_init_value(self, value: Tuple[float, float, float, float]) -> None:
        self._init_value = value

    def set_max_value(self, value: Tuple[float, float, float, float]) -> None:
        self._max_value = value

    def set_min_value(self, value: Tuple[float, float, float, float]) -> None:
        self._min_value = value

    def is_revival(self) -> bool:
        return False

    def use_name_to_override_params(self) -> None:
        super(Vec4Flag, self).use_name_to_override_params()
        OVERRIDES = overrides["VEC4_OVERRIDES"]
        for substr, value in OVERRIDES["OVERRIDE_VEC4_INIT_VALUE"].items():
            if substr in self._data_name:
                self._init_value = value
        for substr, value in OVERRIDES["OVERRIDE_VEC4_MAX_VALUE"].items():
            if substr in self._data_name:
                self._max_value = value
        for substr, value in OVERRIDES["OVERRIDE_VEC4_MIN_VALUE"].items():
            if substr in self._data_name:
                self._min_value = value

