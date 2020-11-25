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
import re

from . import overrides


class BFUFlag:
    def __init__(self, flag: Hash = None) -> None:
        self.data_name = ""
        self.delete_rev = -1
        self.is_event_associated = False
        self.is_one_trigger = False
        self.is_program_readable = True
        self.is_program_writable = True
        self.is_save = False
        self.reset_type = 0
        if flag:
            if not BFUFlag.validate_Hash(flag):
                raise AttributeError(f"{flag['DataName']} is malformed.")
            self.data_name = flag["DataName"]
            self.delete_rev = flag["DeleteRev"].v
            self.is_event_associated = flag["IsEventAssociated"]
            self.is_one_trigger = flag["IsOneTrigger"]
            self.is_program_readable = flag["IsProgramReadable"]
            self.is_program_writable = flag["IsProgramWritable"]
            self.is_save = flag["IsSave"]
            self.reset_type = flag["ResetType"].v

    def __eq__(self, other):
        if self is other:
            return True
        if (
            not self.data_name == other.data_name
            or not self.delete_rev == other.delete_rev
            or not self.hash_value == other.hash_value
            or not self.is_event_associated == other.is_event_associated
            or not self.is_one_trigger == other.is_one_trigger
            or not self.is_program_readable == other.is_program_readable
            or not self.is_program_writable == other.is_program_writable
            or not self.is_save == other.is_save
            or not self.reset_type == other.reset_type
        ):
            return False
        return True

    @staticmethod
    def validate_Hash(hash: Hash) -> bool:
        """Returns True if all Hash properties are valid"""
        try:
            assert type(hash["DeleteRev"]) == S32
            assert type(hash["IsEventAssociated"]) == bool
            assert type(hash["IsOneTrigger"]) == bool
            assert type(hash["IsProgramReadable"]) == bool
            assert type(hash["IsProgramWritable"]) == bool
            assert type(hash["IsSave"]) == bool
            assert type(hash["ResetType"]) == S32
            return True
        except AssertionError:
            return False

    def to_Hash(self) -> Hash:
        """Converts flag to an oead.Hash meant for a gamedata file"""
        r = Hash()
        r["DataName"] = self.data_name
        r["DeleteRev"] = S32(self.delete_rev)
        r["HashValue"] = S32(self.hash_value)
        r["IsEventAssociated"] = self.is_event_associated
        r["IsOneTrigger"] = self.is_one_trigger
        r["IsProgramReadable"] = self.is_program_readable
        r["IsProgramWritable"] = self.is_program_writable
        r["IsSave"] = self.is_save
        r["ResetType"] = S32(self.reset_type)
        return r

    def to_sv_Hash(self) -> Hash:
        """Converts flag to an oead.Hash meant for a saveformat_#.bgsvdata"""
        r = Hash()
        r["DataName"] = self.data_name
        r["HashValue"] = S32(self.hash_value)
        return r

    def exists(self) -> bool:
        """Returns True if the flag contains any data"""
        return not self.hash_value == 0

    def name_contains(self, name: str) -> bool:
        """Returns true if the flag's name contains the passed string"""
        return name in self.data_name

    @property
    def data_name(self) -> str:
        return self._data_name

    @data_name.setter
    def data_name(self, name: str) -> None:
        self._data_name = name
        self._hash_value = c_int32(crc32(name.encode("utf-8"))).value

    @property
    def delete_rev(self) -> int:
        return self._delete_rev

    @delete_rev.setter
    def delete_rev(self, drev: int) -> None:
        self._delete_rev = drev

    @property
    def hash_value(self) -> int:
        return self._hash_value

    @property
    def is_event_associated(self) -> bool:
        return self._is_event_associated

    @is_event_associated.setter
    def is_event_associated(self, event_assoc: bool) -> None:
        self._is_event_associated = event_assoc

    @property
    def is_one_trigger(self) -> bool:
        return self._is_one_trigger

    @is_one_trigger.setter
    def is_one_trigger(self, is_one: bool) -> None:
        self._is_one_trigger = is_one

    @property
    def is_program_readable(self) -> bool:
        return self._is_program_readable

    @is_program_readable.setter
    def is_program_readable(self, is_read: bool) -> None:
        self._is_program_readable = is_read

    @property
    def is_program_writable(self) -> bool:
        return self._is_program_writable

    @is_program_writable.setter
    def is_program_writable(self, is_write: bool) -> None:
        self._is_program_writable = is_write

    @property
    def is_save(self) -> bool:
        return self._is_save

    @is_save.setter
    def is_save(self, save: bool) -> None:
        self._is_save = save

    @property
    def reset_type(self) -> int:
        return self._reset_type

    @reset_type.setter
    def reset_type(self, reset_type: int) -> None:
        self._reset_type = reset_type

    @property
    def is_revival(self) -> bool:
        return False

    def use_name_to_override_params(self) -> None:
        """
        Sets flag parameters to those mandated by the overrides.
        In general, this function should always be called right
        before finalizing the flag creation/changes to ensure
        that certain values that should always be the same for
        certain flag types are upheld.
        """
        OVERRIDES = overrides["STANDARD_OVERRIDES"]
        for regex, value in OVERRIDES["OVERRIDE_IS_EVENT_ASSOCIATED"].items():
            if re.search(regex, self.data_name):
                self.is_event_associated = value
        for regex, value in OVERRIDES["OVERRIDE_IS_ONE_TRIGGER"].items():
            if re.search(regex, self.data_name):
                self.is_one_trigger = value
        for regex, value in OVERRIDES["OVERRIDE_IS_PROGRAM_READABLE"].items():
            if re.search(regex, self.data_name):
                self.is_program_readable = value
        for regex, value in OVERRIDES["OVERRIDE_IS_PROGRAM_WRITABLE"].items():
            if re.search(regex, self.data_name):
                self.is_program_writable = value
        for regex, value in OVERRIDES["OVERRIDE_IS_SAVE"].items():
            if re.search(regex, self.data_name):
                self.is_save = value
        for regex, value in OVERRIDES["OVERRIDE_RESET_TYPE"].items():
            if re.search(regex, self.data_name):
                self.reset_type = value


class BoolFlag(BFUFlag):
    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(BoolFlag, self).__init__(flag=flag)
        self.category = -1
        self.init_value = 0
        self.max_value = True
        self.min_value = False
        self.is_revival = kwargs["revival"] if "revival" in kwargs else False
        if flag:
            if not BoolFlag.validate_Hash(flag):
                raise AttributeError(f"{flag['DataName']} is malformed.")
            self.category = flag["Category"].v if "Category" in flag else -1
            self.init_value = flag["InitValue"].v
            self.max_value = flag["MaxValue"]
            self.min_value = flag["MinValue"]

    def __eq__(self, other):
        if not type(other) == BoolFlag:
            return NotImplemented
        if not super(BoolFlag, self).__eq__(super(BoolFlag, other)):
            return False
        if (
            not self.category == other.category
            or not self.init_value == other.init_value
            or not self.max_value == other.max_value
            or not self.min_value == other.min_value
        ):
            return False
        return True

    @staticmethod
    def validate_Hash(hash: Hash) -> bool:
        """Returns True if all Hash properties are valid"""
        try:
            if "Category" in hash:
                assert type(hash["Category"]) == S32
            assert type(hash["InitValue"]) == S32
            assert type(hash["MaxValue"]) == bool
            assert type(hash["MinValue"]) == bool
            return True
        except AssertionError:
            return False

    def to_Hash(self) -> Hash:
        r = super(BoolFlag, self).to_Hash()
        if not self.category == -1:
            r["Category"] = S32(self.category)
        r["InitValue"] = S32(self.init_value)
        r["MaxValue"] = self.max_value
        r["MinValue"] = self.min_value
        return r

    @property
    def category(self) -> int:
        return self._category

    @category.setter
    def category(self, value: int) -> None:
        self._category = value

    @property
    def init_value(self) -> int:
        return self._init_value

    @init_value.setter
    def init_value(self, value: bool) -> None:
        self._init_value = value

    @property
    def max_value(self) -> bool:
        return self._max_value

    @max_value.setter
    def max_value(self, value: bool) -> None:
        self._max_value = value

    @property
    def min_value(self) -> bool:
        return self._min_value

    @min_value.setter
    def min_value(self, value: bool) -> None:
        self._min_value = value

    @property
    def is_revival(self) -> bool:
        return self._revival

    @is_revival.setter
    def is_revival(self, revival: bool) -> None:
        self._revival = revival

    def use_name_to_override_params(self) -> None:
        """
        Sets flag parameters to those mandated by the overrides.
        In general, this function should always be called right
        before finalizing the flag creation/changes to ensure
        that certain values that should always be the same for
        certain flag types are upheld.
        """
        super(BoolFlag, self).use_name_to_override_params()
        OVERRIDES = overrides["BOOL_OVERRIDES"]
        for regex, value in OVERRIDES["OVERRIDE_BOOL_CATEGORY"].items():
            if re.search(regex, self.data_name):
                self.category = value
        for regex, value in OVERRIDES["OVERRIDE_BOOL_INIT_VALUE"].items():
            if re.search(regex, self.data_name):
                self.init_value = value


class BoolArrayFlag(BFUFlag):
    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(BoolArrayFlag, self).__init__(flag=flag)
        self.init_value = [0]
        self.max_value = True
        self.min_value = False
        if flag:
            if not BoolArrayFlag.validate_Hash(flag):
                raise AttributeError(f"{flag['DataName']} is malformed.")
            self.init_value = [value.v for value in flag["InitValue"][0]["Values"]]
            self.max_value = flag["MaxValue"]
            self.min_value = flag["MinValue"]

    def __eq__(self, other):
        if not type(other) == BoolArrayFlag:
            return NotImplemented
        if not super(BoolArrayFlag, self).__eq__(super(BoolArrayFlag, other)):
            return False
        if (
            not self.init_value == other.init_value
            or not self.max_value == other.max_value
            or not self.min_value == other.min_value
        ):
            return False
        return True

    @staticmethod
    def validate_Hash(hash: Hash) -> bool:
        """Returns True if all Hash properties are valid"""
        try:
            assert type(hash["InitValue"]) == Array
            assert type(hash["InitValue"][0]) == Hash
            assert "Values" in hash["InitValue"][0]
            for value in hash["InitValue"][0]["Values"]:
                assert type(value) == S32
            assert type(hash["MaxValue"]) == bool
            assert type(hash["MinValue"]) == bool
            return True
        except AssertionError:
            return False

    def to_Hash(self) -> Hash:
        r = super(BoolArrayFlag, self).to_Hash()
        array_one = Array()
        array_one.append(Hash())
        array_two = Array([S32(value) for value in self.init_value])
        array_one[0]["Values"] = array_two
        r["InitValue"] = array_one
        r["MaxValue"] = self.max_value
        r["MinValue"] = self.min_value
        return r

    @property
    def init_value(self) -> List[int]:
        return self._init_value

    @init_value.setter
    def init_value(self, value: List[int]) -> None:
        self._init_value = value

    @property
    def max_value(self) -> bool:
        return self._max_value

    @max_value.setter
    def max_value(self, value: bool) -> None:
        self._max_value = value

    @property
    def min_value(self) -> bool:
        return self._min_value

    @min_value.setter
    def min_value(self, value: bool) -> None:
        self._min_value = value

    def use_name_to_override_params(self) -> None:
        """
        Sets flag parameters to those mandated by the overrides.
        In general, this function should always be called right
        before finalizing the flag creation/changes to ensure
        that certain values that should always be the same for
        certain flag types are upheld.
        """
        super(BoolArrayFlag, self).use_name_to_override_params()
        OVERRIDES = overrides["BOOL_ARRAY_OVERRIDES"]
        for regex, value in OVERRIDES["OVERRIDE_BOOL_ARRAY_INIT_VALUE"].items():
            if re.search(regex, self.data_name):
                self.init_value = value
        for regex, value in OVERRIDES["OVERRIDE_BOOL_ARRAY_MAX_VALUE"].items():
            if re.search(regex, self.data_name):
                self.max_value = value
        for regex, value in OVERRIDES["OVERRIDE_BOOL_ARRAY_MIN_VALUE"].items():
            if re.search(regex, self.data_name):
                self.min_value = value


class S32Flag(BFUFlag):
    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(S32Flag, self).__init__(flag=flag)
        self.init_value = 0
        self.max_value = 2147483647
        self.min_value = 0
        self.is_revival = kwargs["revival"] if "revival" in kwargs else False
        if flag:
            if not S32Flag.validate_Hash(flag):
                raise AttributeError(f"{flag['DataName']} is malformed.")
            self._init_value = flag["InitValue"].v
            self._max_value = flag["MaxValue"].v
            self._min_value = flag["MinValue"].v

    def __eq__(self, other):
        if not type(other) == S32Flag:
            return NotImplemented
        if not super(S32Flag, self).__eq__(super(S32Flag, other)):
            return False
        if (
            not self.init_value == other.init_value
            or not self.max_value == other.max_value
            or not self.min_value == other.min_value
        ):
            return False
        return True

    @staticmethod
    def validate_Hash(hash: Hash) -> bool:
        """Returns True if all Hash properties are valid"""
        try:
            assert type(hash["InitValue"]) == S32
            assert type(hash["MaxValue"]) == S32
            assert type(hash["MinValue"]) == S32
            return True
        except AssertionError:
            return False

    def to_Hash(self) -> Hash:
        r = super(S32Flag, self).to_Hash()
        r["InitValue"] = S32(self._init_value)
        r["MaxValue"] = S32(self._max_value)
        r["MinValue"] = S32(self._min_value)
        return r

    @property
    def init_value(self) -> int:
        return self._init_value

    @init_value.setter
    def init_value(self, value: int) -> None:
        self._init_value = value

    @property
    def max_value(self) -> int:
        return self._max_value

    @max_value.setter
    def max_value(self, value: int) -> None:
        self._max_value = value

    @property
    def min_value(self) -> int:
        return self._min_value

    @min_value.setter
    def min_value(self, value: int) -> None:
        self._min_value = value

    @property
    def is_revival(self) -> bool:
        return self._revival

    @is_revival.setter
    def is_revival(self, revival: bool) -> None:
        self._revival = revival

    def use_name_to_override_params(self) -> None:
        """
        Sets flag parameters to those mandated by the overrides.
        In general, this function should always be called right
        before finalizing the flag creation/changes to ensure
        that certain values that should always be the same for
        certain flag types are upheld.
        """
        super(S32Flag, self).use_name_to_override_params()
        OVERRIDES = overrides["S32_OVERRIDES"]
        for regex, value in OVERRIDES["OVERRIDE_S32_INIT_VALUE"].items():
            if re.search(regex, self.data_name):
                self.init_value = value
        for regex, value in OVERRIDES["OVERRIDE_S32_MAX_VALUE"].items():
            if re.search(regex, self.data_name):
                self.max_value = value
        for regex, value in OVERRIDES["OVERRIDE_S32_MIN_VALUE"].items():
            if re.search(regex, self.data_name):
                self.min_value = value


class S32ArrayFlag(BFUFlag):
    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(S32ArrayFlag, self).__init__(flag=flag)
        self.init_value = [0]
        self.max_value = 6553500
        self.min_value = -1
        if flag:
            if not S32ArrayFlag.validate_Hash(flag):
                raise AttributeError(f"{flag['DataName']} is malformed.")
            self.init_value = [int(value) for value in flag["InitValue"][0]["Values"]]
            self.max_value = flag["MaxValue"].v
            self.min_value = flag["MinValue"].v

    def __eq__(self, other):
        if not type(other) == S32ArrayFlag:
            return NotImplemented
        if not super(S32ArrayFlag, self).__eq__(super(S32ArrayFlag, other)):
            return False
        if (
            not self.init_value == other.init_value
            or not self.max_value == other.max_value
            or not self.min_value == other.min_value
        ):
            return False
        return True

    @staticmethod
    def validate_Hash(hash: Hash) -> bool:
        """Returns True if all Hash properties are valid"""
        try:
            assert type(hash["InitValue"]) == Array
            assert type(hash["InitValue"][0]) == Hash
            assert "Values" in hash["InitValue"][0]
            for value in hash["InitValue"][0]["Values"]:
                assert type(value) == S32
            assert type(hash["MaxValue"]) == S32
            assert type(hash["MinValue"]) == S32
            return True
        except AssertionError:
            return False

    def to_Hash(self) -> Hash:
        r = super(S32ArrayFlag, self).to_Hash()
        array_one = Array()
        array_one.append(Hash())
        array_two = Array([S32(value) for value in self.init_value])
        array_one[0]["Values"] = array_two
        r["InitValue"] = array_one
        r["MaxValue"] = S32(self.max_value)
        r["MinValue"] = S32(self.min_value)
        return r

    @property
    def init_value(self) -> List[int]:
        return self._init_value

    @init_value.setter
    def init_value(self, value: List[int]) -> None:
        self._init_value = value

    @property
    def max_value(self) -> int:
        return self._max_value

    @max_value.setter
    def max_value(self, value: int) -> None:
        self._max_value = value

    @property
    def min_value(self) -> int:
        return self._min_value

    @min_value.setter
    def min_value(self, value: int) -> None:
        self._min_value = value

    def use_name_to_override_params(self) -> None:
        """
        Sets flag parameters to those mandated by the overrides.
        In general, this function should always be called right
        before finalizing the flag creation/changes to ensure
        that certain values that should always be the same for
        certain flag types are upheld.
        """
        super(S32ArrayFlag, self).use_name_to_override_params()
        OVERRIDES = overrides["S32_ARRAY_OVERRIDES"]
        for regex, value in OVERRIDES["OVERRIDE_S32_ARRAY_INIT_VALUE"].items():
            if re.search(regex, self.data_name):
                self.init_value = value
        for regex, value in OVERRIDES["OVERRIDE_S32_ARRAY_MAX_VALUE"].items():
            if re.search(regex, self.data_name):
                self.max_value = value
        for regex, value in OVERRIDES["OVERRIDE_S32_ARRAY_MIN_VALUE"].items():
            if re.search(regex, self.data_name):
                self.min_value = value


class F32Flag(BFUFlag):
    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(F32Flag, self).__init__(flag=flag)
        self.init_value = 0.0
        self.max_value = 1000000.0
        self.min_value = 0.0
        if flag:
            if not F32Flag.validate_Hash(flag):
                raise AttributeError(f"{flag['DataName']} is malformed.")
            self.init_value = flag["InitValue"].v
            self.max_value = flag["MaxValue"].v
            self.min_value = flag["MinValue"].v

    def __eq__(self, other):
        if not type(other) == F32Flag:
            return NotImplemented
        if not super(F32Flag, self).__eq__(super(F32Flag, other)):
            return False
        if (
            not self.init_value == other.init_value
            or not self.max_value == other.max_value
            or not self.min_value == other.min_value
        ):
            return False
        return True

    @staticmethod
    def validate_Hash(hash: Hash) -> bool:
        """Returns True if all Hash properties are valid"""
        try:
            assert type(hash["InitValue"]) == F32
            assert type(hash["MaxValue"]) == F32
            assert type(hash["MinValue"]) == F32
            return True
        except AssertionError:
            return False

    def to_Hash(self) -> Hash:
        r = super(F32Flag, self).to_Hash()
        r["InitValue"] = F32(self.init_value)
        r["MaxValue"] = F32(self.max_value)
        r["MinValue"] = F32(self.min_value)
        return r

    @property
    def init_value(self) -> float:
        return self._init_value

    @init_value.setter
    def init_value(self, value: float) -> None:
        self._init_value = value

    @property
    def max_value(self) -> float:
        return self._max_value

    @max_value.setter
    def max_value(self, value: float) -> None:
        self._max_value = value

    @property
    def min_value(self) -> float:
        return self._min_value

    @min_value.setter
    def min_value(self, value: float) -> None:
        self._min_value = value

    def use_name_to_override_params(self) -> None:
        """
        Sets flag parameters to those mandated by the overrides.
        In general, this function should always be called right
        before finalizing the flag creation/changes to ensure
        that certain values that should always be the same for
        certain flag types are upheld.
        """
        super(F32Flag, self).use_name_to_override_params()
        OVERRIDES = overrides["F32_OVERRIDES"]
        for regex, value in OVERRIDES["OVERRIDE_F32_INIT_VALUE"].items():
            if re.search(regex, self.data_name):
                self.init_value = value
        for regex, value in OVERRIDES["OVERRIDE_F32_MAX_VALUE"].items():
            if re.search(regex, self.data_name):
                self.max_value = value
        for regex, value in OVERRIDES["OVERRIDE_F32_MIN_VALUE"].items():
            if re.search(regex, self.data_name):
                self.min_value = value


class F32ArrayFlag(BFUFlag):
    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(F32ArrayFlag, self).__init__(flag=flag)
        self.init_value = [0.0]
        self.max_value = 360.0
        self.min_value = -1.0
        if flag:
            if not F32ArrayFlag.validate_Hash(flag):
                raise AttributeError(f"{flag['DataName']} is malformed.")
            self.init_value = [value.v for value in flag["InitValue"][0]["Values"]]
            self.max_value = flag["MaxValue"].v
            self.min_value = flag["MinValue"].v

    def __eq__(self, other):
        if not type(other) == F32ArrayFlag:
            return NotImplemented
        if not super(F32ArrayFlag, self).__eq__(super(F32ArrayFlag, other)):
            return False
        if (
            not self.init_value == other.init_value
            or not self.max_value == other.max_value
            or not self.min_value == other.min_value
        ):
            return False
        return True

    @staticmethod
    def validate_Hash(hash: Hash) -> bool:
        """Returns True if all Hash properties are valid"""
        try:
            assert type(hash["InitValue"]) == Array
            assert type(hash["InitValue"][0]) == Hash
            assert "Values" in hash["InitValue"][0]
            for value in hash["InitValue"][0]["Values"]:
                assert type(value) == F32
            assert type(hash["MaxValue"]) == F32
            assert type(hash["MinValue"]) == F32
            return True
        except AssertionError:
            return False

    def to_Hash(self) -> Hash:
        r = super(F32ArrayFlag, self).to_Hash()
        array_one = Array()
        array_one.append(Hash())
        array_two = Array([F32(value) for value in self.init_value])
        array_one[0]["Values"] = array_two
        r["InitValue"] = array_one
        r["MaxValue"] = F32(self.max_value)
        r["MinValue"] = F32(self.min_value)
        return r

    @property
    def init_value(self) -> List[float]:
        return self._init_value

    @init_value.setter
    def init_value(self, value: List[float]) -> None:
        self._init_value = value

    @property
    def max_value(self) -> float:
        return self._max_value

    @max_value.setter
    def max_value(self, value: float) -> None:
        self._max_value = value

    @property
    def min_value(self) -> float:
        return self._min_value

    @min_value.setter
    def min_value(self, value: float) -> None:
        self._min_value = value

    def use_name_to_override_params(self) -> None:
        """
        Sets flag parameters to those mandated by the overrides.
        In general, this function should always be called right
        before finalizing the flag creation/changes to ensure
        that certain values that should always be the same for
        certain flag types are upheld.
        """
        super(F32ArrayFlag, self).use_name_to_override_params()
        OVERRIDES = overrides["F32_ARRAY_OVERRIDES"]
        for regex, value in OVERRIDES["OVERRIDE_F32_ARRAY_INIT_VALUE"].items():
            if re.search(regex, self.data_name):
                self.init_value = value
        for regex, value in OVERRIDES["OVERRIDE_F32_ARRAY_MAX_VALUE"].items():
            if re.search(regex, self.data_name):
                self.max_value = value
        for regex, value in OVERRIDES["OVERRIDE_F32_ARRAY_MIN_VALUE"].items():
            if re.search(regex, self.data_name):
                self.min_value = value


class StringFlag(BFUFlag):
    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(StringFlag, self).__init__(flag=flag)
        self.init_value = ""
        self.max_value = ""
        self.min_value = ""
        if flag:
            if not StringFlag.validate_Hash(flag):
                raise AttributeError(f"{flag['DataName']} is malformed.")
            self.init_value = flag["InitValue"]
            self.max_value = flag["MaxValue"]
            self.min_value = flag["MinValue"]

    def __eq__(self, other):
        if not isinstance(other, StringFlag):
            return NotImplemented
        if not super(StringFlag, self).__eq__(super(StringFlag, other)):
            return False
        if (
            not self.init_value == other.init_value
            or not self.max_value == other.max_value
            or not self.min_value == other.min_value
        ):
            return False
        return True

    @staticmethod
    def validate_Hash(hash: Hash) -> bool:
        """Returns True if all Hash properties are valid"""
        try:
            assert type(hash["InitValue"]) == str
            assert type(hash["MaxValue"]) == str
            assert type(hash["MinValue"]) == str
            return True
        except AssertionError:
            return False

    def to_Hash(self) -> Hash:
        r = super(StringFlag, self).to_Hash()
        return r

    @property
    def init_value(self) -> str:
        return self._init_value

    @init_value.setter
    def init_value(self, value: str) -> None:
        self._init_value = value

    @property
    def max_value(self) -> str:
        return self._max_value

    @max_value.setter
    def max_value(self, value: str) -> None:
        self._max_value = value

    @property
    def min_value(self) -> str:
        return self._min_value

    @min_value.setter
    def min_value(self, value: str) -> None:
        self._min_value = value

    def use_name_to_override_params(self) -> None:
        """
        Sets flag parameters to those mandated by the overrides.
        In general, this function should always be called right
        before finalizing the flag creation/changes to ensure
        that certain values that should always be the same for
        certain flag types are upheld.
        """
        super(StringFlag, self).use_name_to_override_params()
        OVERRIDES = overrides["STRING_OVERRIDES"]
        for regex, value in OVERRIDES["OVERRIDE_STRING_INIT_VALUE"].items():
            if re.search(regex, self.data_name):
                self.init_value = value
        for regex, value in OVERRIDES["OVERRIDE_STRING_MAX_VALUE"].items():
            if re.search(regex, self.data_name):
                self.max_value = value
        for regex, value in OVERRIDES["OVERRIDE_STRING_MIN_VALUE"].items():
            if re.search(regex, self.data_name):
                self.min_value = value


class String32Flag(StringFlag):
    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(String32Flag, self).__init__(flag=flag)

    def to_Hash(self) -> Hash:
        r = super(String32Flag, self).to_Hash()
        # r["InitValue"] = FixedSafeString32(self.init_value)
        r["InitValue"] = self.init_value
        # r["MaxValue"] = FixedSafeString32(self.max_value)
        r["MaxValue"] = self.max_value
        # r["MinValue"] = FixedSafeString32(self.min_value)
        r["MinValue"] = self.min_value
        return r


class String64Flag(StringFlag):
    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(String64Flag, self).__init__(flag=flag)

    def to_Hash(self) -> Hash:
        r = super(String64Flag, self).to_Hash()
        # r["InitValue"] = FixedSafeString64(self.init_value)
        r["InitValue"] = self.init_value
        # r["MaxValue"] = FixedSafeString64(self.max_value)
        r["MaxValue"] = self.max_value
        # r["MinValue"] = FixedSafeString64(self.min_value)
        r["MinValue"] = self.min_value
        return r


class String256Flag(StringFlag):
    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(String256Flag, self).__init__(flag=flag)

    def to_Hash(self) -> Hash:
        r = super(String256Flag, self).to_Hash()
        # r["InitValue"] = FixedSafeString256(self.init_value)
        r["InitValue"] = self.init_value
        # r["MaxValue"] = FixedSafeString256(self.max_value)
        r["MaxValue"] = self.max_value
        # r["MinValue"] = FixedSafeString256(self.min_value)
        r["MinValue"] = self.min_value
        return r


class StringArrayFlag(BFUFlag):
    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(StringArrayFlag, self).__init__(flag=flag)
        self.init_value = [""]
        self.max_value = ""
        self.min_value = ""
        if flag:
            if not StringArrayFlag.validate_Hash(flag):
                raise AttributeError(f"{flag['DataName']} is malformed.")
            self.init_value = [value for value in flag["InitValue"][0]["Values"]]
            self.max_value = flag["MaxValue"]
            self.min_value = flag["MinValue"]

    def __eq__(self, other):
        if not isinstance(other, StringArrayFlag):
            return NotImplemented
        if not super(StringArrayFlag, self).__eq__(super(StringArrayFlag, other)):
            return False
        if (
            not self.init_value == other.init_value
            or not self.max_value == other.max_value
            or not self.min_value == other.min_value
        ):
            return False
        return True

    @staticmethod
    def validate_Hash(hash: Hash) -> bool:
        """Returns True if all Hash properties are valid"""
        try:
            assert type(hash["InitValue"]) == Array
            assert type(hash["InitValue"][0]) == Hash
            assert "Values" in hash["InitValue"][0]
            for value in hash["InitValue"][0]["Values"]:
                assert type(value) == str
            assert type(hash["MaxValue"]) == str
            assert type(hash["MinValue"]) == str
            return True
        except AssertionError:
            return False

    def to_Hash(self) -> Hash:
        r = super(StringArrayFlag, self).to_Hash()
        return r

    @property
    def init_value(self) -> List[str]:
        return self._init_value

    @init_value.setter
    def init_value(self, value: List[str]) -> None:
        self._init_value = value

    @property
    def max_value(self) -> str:
        return self._max_value

    @max_value.setter
    def max_value(self, value: str) -> None:
        self._max_value = value

    @property
    def min_value(self) -> str:
        return self._min_value

    @min_value.setter
    def min_value(self, value: str) -> None:
        self._min_value = value

    def use_name_to_override_params(self) -> None:
        """
        Sets flag parameters to those mandated by the overrides.
        In general, this function should always be called right
        before finalizing the flag creation/changes to ensure
        that certain values that should always be the same for
        certain flag types are upheld.
        """
        super(StringArrayFlag, self).use_name_to_override_params()
        OVERRIDES = overrides["STRING_ARRAY_OVERRIDES"]
        for regex, value in OVERRIDES["OVERRIDE_STRING_ARRAY_INIT_VALUE"].items():
            if re.search(regex, self.data_name):
                self.init_value = value
        for regex, value in OVERRIDES["OVERRIDE_STRING_ARRAY_MAX_VALUE"].items():
            if re.search(regex, self.data_name):
                self.max_value = value
        for regex, value in OVERRIDES["OVERRIDE_STRING_ARRAY_MIN_VALUE"].items():
            if re.search(regex, self.data_name):
                self.min_value = value


class String64ArrayFlag(StringArrayFlag):
    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(String64ArrayFlag, self).__init__(flag=flag)

    def to_Hash(self) -> Hash:
        r = super(String64ArrayFlag, self).to_Hash()
        array_one = Array()
        array_one.append(Hash())
        # array_two = [FixedSafeString64(value) for value in self.init_value]
        array_two = Array(self.init_value)
        array_one[0]["Values"] = array_two
        r["InitValue"] = array_one
        # r["MaxValue"] = FixedSafeString64(self.max_value)
        r["MaxValue"] = self.max_value
        # r["MinValue"] = FixedSafeString64(self.min_value)
        r["MinValue"] = self.min_value
        return r


class String256ArrayFlag(StringArrayFlag):
    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(String256ArrayFlag, self).__init__(flag=flag)

    def to_Hash(self) -> Hash:
        r = super(String256ArrayFlag, self).to_Hash()
        array_one = Array()
        array_one.append(Hash())
        # array_two = [FixedSafeString256(value) for value in self.init_value]
        array_two = Array(self.init_value)
        array_one[0]["Values"] = array_two
        r["InitValue"] = array_one
        # r["MaxValue"] = FixedSafeString256(self.max_value)
        r["MaxValue"] = self.max_value
        # r["MinValue"] = FixedSafeString256(self.min_value)
        r["MinValue"] = self.min_value
        return r


class Vec2Flag(BFUFlag):
    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(Vec2Flag, self).__init__(flag=flag)
        self.init_value = (0.0, 0.0)
        self.max_value = (255.0, 255.0)
        self.min_value = (0.0, 0.0)
        if flag:
            if not Vec2Flag.validate_Hash(flag):
                raise AttributeError(f"{flag['DataName']} is malformed.")
            self.init_value = (flag["InitValue"][0][0].v, flag["InitValue"][0][1].v)
            self.max_value = (flag["MaxValue"][0][0].v, flag["MaxValue"][0][1].v)
            self.min_value = (flag["MinValue"][0][0].v, flag["MinValue"][0][1].v)

    def __eq__(self, other):
        if not type(other) == Vec2Flag:
            return NotImplemented
        if not super(Vec2Flag, self).__eq__(super(Vec2Flag, other)):
            return False
        if (
            not self.init_value == other.init_value
            or not self.max_value == other.max_value
            or not self.min_value == other.min_value
        ):
            return False
        return True

    @staticmethod
    def validate_Hash(hash: Hash) -> bool:
        """Returns True if all Hash properties are valid"""
        try:
            assert type(hash["InitValue"][0][0]) == F32
            assert type(hash["InitValue"][0][1]) == F32
            assert type(hash["MaxValue"][0][0]) == F32
            assert type(hash["MaxValue"][0][1]) == F32
            assert type(hash["MinValue"][0][0]) == F32
            assert type(hash["MinValue"][0][1]) == F32
            return True
        except AssertionError:
            return False

    def to_Hash(self) -> Hash:
        r = super(Vec2Flag, self).to_Hash()
        array = Array()
        vec = Array()
        vec.append(F32(self.init_value[0]))
        vec.append(F32(self.init_value[1]))
        array.append(vec)
        r["InitValue"] = array
        array = Array()
        vec = Array()
        vec.append(F32(self.max_value[0]))
        vec.append(F32(self.max_value[1]))
        array.append(vec)
        r["MaxValue"] = array
        array = Array()
        vec = Array()
        vec.append(F32(self.min_value[0]))
        vec.append(F32(self.min_value[1]))
        array.append(vec)
        r["MinValue"] = array
        return r

    @property
    def init_value(self) -> Tuple[float, float]:
        return self._init_value

    @init_value.setter
    def init_value(self, value: Tuple[float, float]) -> None:
        self._init_value = value

    @property
    def max_value(self) -> Tuple[float, float]:
        return self._max_value

    @max_value.setter
    def max_value(self, value: Tuple[float, float]) -> None:
        self._max_value = value

    @property
    def min_value(self) -> Tuple[float, float]:
        return self._min_value

    @min_value.setter
    def min_value(self, value: Tuple[float, float]) -> None:
        self._min_value = value

    def use_name_to_override_params(self) -> None:
        """
        Sets flag parameters to those mandated by the overrides.
        In general, this function should always be called right
        before finalizing the flag creation/changes to ensure
        that certain values that should always be the same for
        certain flag types are upheld.
        """
        super(Vec2Flag, self).use_name_to_override_params()
        OVERRIDES = overrides["VEC2_OVERRIDES"]
        for regex, value in OVERRIDES["OVERRIDE_VEC2_INIT_VALUE"].items():
            if re.search(regex, self.data_name):
                self.init_value = value
        for regex, value in OVERRIDES["OVERRIDE_VEC2_MAX_VALUE"].items():
            if re.search(regex, self.data_name):
                self.max_value = value
        for regex, value in OVERRIDES["OVERRIDE_VEC2_MIN_VALUE"].items():
            if re.search(regex, self.data_name):
                self.min_value = value


class Vec2ArrayFlag(BFUFlag):
    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(Vec2ArrayFlag, self).__init__(flag=flag)
        self.init_value = [(0.0, 0.0)]
        self.max_value = (255.0, 255.0)
        self.min_value = (0.0, 0.0)
        if flag:
            if not Vec2ArrayFlag.validate_Hash(flag):
                raise AttributeError(f"{flag['DataName']} is malformed.")
            vec_array = []
            for vector in flag["InitValue"][0]["Values"]:
                vec_array.append((vector[0][0].v, vector[0][1].v))
            self.init_value = vec_array
            self.max_value = (flag["MaxValue"][0][0].v, flag["MaxValue"][0][1].v)
            self.min_value = (flag["MinValue"][0][0].v, flag["MinValue"][0][1].v)

    def __eq__(self, other):
        if not type(other) == Vec2ArrayFlag:
            return NotImplemented
        if not super(Vec2ArrayFlag, self).__eq__(super(Vec2ArrayFlag, other)):
            return False
        if (
            not self.init_value == other.init_value
            or not self.max_value == other.max_value
            or not self.min_value == other.min_value
        ):
            return False
        return True

    @staticmethod
    def validate_Hash(hash: Hash) -> bool:
        """Returns True if all Hash properties are valid"""
        try:
            assert type(hash["InitValue"]) == Array
            assert type(hash["InitValue"][0]) == Hash
            assert "Values" in hash["InitValue"][0]
            for value in hash["InitValue"][0]["Values"]:
                assert type(value[0][0]) == F32
                assert type(value[0][1]) == F32
            assert type(hash["MaxValue"][0][0]) == F32
            assert type(hash["MaxValue"][0][1]) == F32
            assert type(hash["MinValue"][0][0]) == F32
            assert type(hash["MinValue"][0][1]) == F32
            return True
        except AssertionError:
            return False

    def to_Hash(self) -> Hash:
        r = super(Vec2ArrayFlag, self).to_Hash()
        vec_array = Array()
        vec_array.append(Hash())
        vec_array[0]["Values"] = Array()
        for i in range(len(self.init_value)):
            vector = self.init_value[i]
            vec = Array()
            vec.append(F32(vector[0]))
            vec.append(F32(vector[1]))
            vec_array[0]["Values"].append(Array())
            vec_array[0]["Values"][i].append(vec)
        r["InitValue"] = vec_array
        vec_array = Array()
        vec = Array()
        vec.append(F32(self.max_value[0]))
        vec.append(F32(self.max_value[1]))
        vec_array.append(vec)
        r["MaxValue"] = vec_array
        vec_array = Array()
        vec = Array()
        vec.append(F32(self.min_value[0]))
        vec.append(F32(self.min_value[1]))
        vec_array.append(vec)
        r["MinValue"] = vec_array
        return r

    @property
    def init_value(self) -> List[Tuple[float, float]]:
        return self._init_value

    @init_value.setter
    def init_value(self, value: List[Tuple[float, float]]) -> None:
        self._init_value = value

    @property
    def max_value(self) -> Tuple[float, float]:
        return self._max_value

    @max_value.setter
    def max_value(self, value: Tuple[float, float]) -> None:
        self._max_value = value

    @property
    def min_value(self) -> Tuple[float, float]:
        return self._min_value

    @min_value.setter
    def min_value(self, value: Tuple[float, float]) -> None:
        self._min_value = value

    def use_name_to_override_params(self) -> None:
        """
        Sets flag parameters to those mandated by the overrides.
        In general, this function should always be called right
        before finalizing the flag creation/changes to ensure
        that certain values that should always be the same for
        certain flag types are upheld.
        """
        super(Vec2ArrayFlag, self).use_name_to_override_params()
        OVERRIDES = overrides["VEC2_ARRAY_OVERRIDES"]
        for regex, value in OVERRIDES["OVERRIDE_VEC2_ARRAY_INIT_VALUE"].items():
            if re.search(regex, self.data_name):
                self.init_value = value
        for regex, value in OVERRIDES["OVERRIDE_VEC2_ARRAY_MAX_VALUE"].items():
            if re.search(regex, self.data_name):
                self.max_value = value
        for regex, value in OVERRIDES["OVERRIDE_VEC2_ARRAY_MIN_VALUE"].items():
            if re.search(regex, self.data_name):
                self.min_value = value


class Vec3Flag(BFUFlag):
    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(Vec3Flag, self).__init__(flag=flag)
        self.init_value = (0.0, 0.0, 0.0)
        self.max_value = (100000.0, 100000.0, 100000.0)
        self.min_value = (-100000.0, -100000.0, -100000.0)
        if flag:
            if not Vec3Flag.validate_Hash(flag):
                raise AttributeError(f"{flag['DataName']} is malformed.")
            self.init_value = (
                flag["InitValue"][0][0].v,
                flag["InitValue"][0][1].v,
                flag["InitValue"][0][2].v,
            )
            self.max_value = (
                flag["MaxValue"][0][0].v,
                flag["MaxValue"][0][1].v,
                flag["MaxValue"][0][2].v,
            )
            self.min_value = (
                flag["MinValue"][0][0].v,
                flag["MinValue"][0][1].v,
                flag["MinValue"][0][2].v,
            )

    def __eq__(self, other):
        if not type(other) == Vec3Flag:
            return NotImplemented
        if not super(Vec3Flag, self).__eq__(super(Vec3Flag, other)):
            return False
        if (
            not self.init_value == other.init_value
            or not self.max_value == other.max_value
            or not self.min_value == other.min_value
        ):
            return False
        return True

    @staticmethod
    def validate_Hash(hash: Hash) -> bool:
        """Returns True if all Hash properties are valid"""
        try:
            assert type(hash["InitValue"][0][0]) == F32
            assert type(hash["InitValue"][0][1]) == F32
            assert type(hash["InitValue"][0][2]) == F32
            assert type(hash["MaxValue"][0][0]) == F32
            assert type(hash["MaxValue"][0][1]) == F32
            assert type(hash["MaxValue"][0][2]) == F32
            assert type(hash["MinValue"][0][0]) == F32
            assert type(hash["MinValue"][0][1]) == F32
            assert type(hash["MinValue"][0][2]) == F32
            return True
        except AssertionError:
            return False

    def to_Hash(self) -> Hash:
        r = super(Vec3Flag, self).to_Hash()
        vec_array = Array()
        vec = Array()
        vec.append(F32(self.init_value[0]))
        vec.append(F32(self.init_value[1]))
        vec.append(F32(self.init_value[2]))
        vec_array.append(vec)
        r["InitValue"] = vec_array
        vec_array = Array()
        vec = Array()
        vec.append(F32(self.max_value[0]))
        vec.append(F32(self.max_value[1]))
        vec.append(F32(self.max_value[2]))
        vec_array.append(vec)
        r["MaxValue"] = vec_array
        vec_array = Array()
        vec = Array()
        vec.append(F32(self.min_value[0]))
        vec.append(F32(self.min_value[1]))
        vec.append(F32(self.min_value[2]))
        vec_array.append(vec)
        r["MinValue"] = vec_array
        return r

    @property
    def init_value(self) -> Tuple[float, float, float]:
        return self._init_value

    @init_value.setter
    def init_value(self, value: Tuple[float, float, float]) -> None:
        self._init_value = value

    @property
    def max_value(self) -> Tuple[float, float, float]:
        return self._max_value

    @max_value.setter
    def max_value(self, value: Tuple[float, float, float]) -> None:
        self._max_value = value

    @property
    def min_value(self) -> Tuple[float, float, float]:
        return self._min_value

    @min_value.setter
    def min_value(self, value: Tuple[float, float, float]) -> None:
        self._min_value = value

    def use_name_to_override_params(self) -> None:
        """
        Sets flag parameters to those mandated by the overrides.
        In general, this function should always be called right
        before finalizing the flag creation/changes to ensure
        that certain values that should always be the same for
        certain flag types are upheld.
        """
        super(Vec3Flag, self).use_name_to_override_params()
        OVERRIDES = overrides["VEC3_OVERRIDES"]
        for regex, value in OVERRIDES["OVERRIDE_VEC3_INIT_VALUE"].items():
            if re.search(regex, self.data_name):
                self.init_value = value
        for regex, value in OVERRIDES["OVERRIDE_VEC3_MAX_VALUE"].items():
            if re.search(regex, self.data_name):
                self.max_value = value
        for regex, value in OVERRIDES["OVERRIDE_VEC3_MIN_VALUE"].items():
            if re.search(regex, self.data_name):
                self.min_value = value


class Vec3ArrayFlag(BFUFlag):
    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(Vec3ArrayFlag, self).__init__(flag=flag)
        self.init_value = [(0.0, 0.0, 0.0)]
        self.max_value = (255.0, 255.0, 255.0)
        self.min_value = (0.0, 0.0, 0.0)
        if flag:
            if not Vec3ArrayFlag.validate_Hash(flag):
                raise AttributeError(f"{flag['DataName']} is malformed.")
            vec_array = []
            for vector in flag["InitValue"][0]["Values"]:
                vec_array.append((vector[0][0].v, vector[0][1].v, vector[0][2].v))
            self.init_value = vec_array
            self.max_value = (
                flag["MaxValue"][0][0].v,
                flag["MaxValue"][0][1].v,
                flag["MaxValue"][0][2].v,
            )
            self.min_value = (
                flag["MinValue"][0][0].v,
                flag["MinValue"][0][1].v,
                flag["MinValue"][0][2].v,
            )

    def __eq__(self, other):
        if not type(other) == Vec3ArrayFlag:
            return NotImplemented
        if not super(Vec3ArrayFlag, self).__eq__(super(Vec3ArrayFlag, other)):
            return False
        if (
            not self.init_value == other.init_value
            or not self.max_value == other.max_value
            or not self.min_value == other.min_value
        ):
            return False
        return True

    @staticmethod
    def validate_Hash(hash: Hash) -> bool:
        """Returns True if all Hash properties are valid"""
        try:
            assert type(hash["InitValue"]) == Array
            assert type(hash["InitValue"][0]) == Hash
            assert "Values" in hash["InitValue"][0]
            for value in hash["InitValue"][0]["Values"]:
                assert type(value[0][0]) == F32
                assert type(value[0][1]) == F32
                assert type(value[0][2]) == F32
            assert type(hash["MaxValue"][0][0]) == F32
            assert type(hash["MaxValue"][0][1]) == F32
            assert type(hash["MaxValue"][0][2]) == F32
            assert type(hash["MinValue"][0][0]) == F32
            assert type(hash["MinValue"][0][1]) == F32
            assert type(hash["MinValue"][0][2]) == F32
            return True
        except AssertionError:
            return False

    def to_Hash(self) -> Hash:
        r = super(Vec3ArrayFlag, self).to_Hash()
        vec_array = Array()
        vec_array.append(Hash())
        vec_array[0]["Values"] = Array()
        for i in range(len(self.init_value)):
            vector = self.init_value[i]
            vec = Array()
            vec.append(F32(vector[0]))
            vec.append(F32(vector[1]))
            vec.append(F32(vector[2]))
            vec_array[0]["Values"].append(Array())
            vec_array[0]["Values"][i].append(vec)
        r["InitValue"] = vec_array
        vec_array = Array()
        vec = Array()
        vec.append(F32(self.max_value[0]))
        vec.append(F32(self.max_value[1]))
        vec.append(F32(self.max_value[2]))
        vec_array.append(vec)
        r["MaxValue"] = vec_array
        vec_array = Array()
        vec = Array()
        vec.append(F32(self.min_value[0]))
        vec.append(F32(self.min_value[1]))
        vec.append(F32(self.min_value[2]))
        vec_array.append(vec)
        r["MinValue"] = vec_array
        return r

    @property
    def init_value(self) -> List[Tuple[float, float, float]]:
        return self._init_value

    @init_value.setter
    def init_value(self, value: List[Tuple[float, float, float]]) -> None:
        self._init_value = value

    @property
    def max_value(self) -> Tuple[float, float, float]:
        return self._max_value

    @max_value.setter
    def max_value(self, value: Tuple[float, float, float]) -> None:
        self._max_value = value

    @property
    def min_value(self) -> Tuple[float, float, float]:
        return self._min_value

    @min_value.setter
    def min_value(self, value: Tuple[float, float, float]) -> None:
        self._min_value = value

    def use_name_to_override_params(self) -> None:
        """
        Sets flag parameters to those mandated by the overrides.
        In general, this function should always be called right
        before finalizing the flag creation/changes to ensure
        that certain values that should always be the same for
        certain flag types are upheld.
        """
        super(Vec3ArrayFlag, self).use_name_to_override_params()
        OVERRIDES = overrides["VEC3_ARRAY_OVERRIDES"]
        for regex, value in OVERRIDES["OVERRIDE_VEC3_ARRAY_INIT_VALUE"].items():
            if re.search(regex, self.data_name):
                self.init_value = value
        for regex, value in OVERRIDES["OVERRIDE_VEC3_ARRAY_MAX_VALUE"].items():
            if re.search(regex, self.data_name):
                self.max_value = value
        for regex, value in OVERRIDES["OVERRIDE_VEC3_ARRAY_MIN_VALUE"].items():
            if re.search(regex, self.data_name):
                self.min_value = value


class Vec4Flag(BFUFlag):
    def __init__(self, flag: Hash = None, **kwargs) -> None:
        super(Vec4Flag, self).__init__(flag=flag)
        self.init_value = (0.0, 0.0, 0.0, 0.0)
        self.max_value = (255.0, 255.0, 255.0, 255.0)
        self.min_value = (0.0, 0.0, 0.0, 0.0)
        if flag:
            if not Vec4Flag.validate_Hash(flag):
                raise AttributeError(f"{flag['DataName']} is malformed.")
            self.init_value = (
                flag["InitValue"][0][0].v,
                flag["InitValue"][0][1].v,
                flag["InitValue"][0][2].v,
                flag["InitValue"][0][3].v,
            )
            self.max_value = (
                flag["MaxValue"][0][0].v,
                flag["MaxValue"][0][1].v,
                flag["MaxValue"][0][2].v,
                flag["MaxValue"][0][3].v,
            )
            self.min_value = (
                flag["MinValue"][0][0].v,
                flag["MinValue"][0][1].v,
                flag["MinValue"][0][2].v,
                flag["MinValue"][0][3].v,
            )

    def __eq__(self, other):
        if not type(other) == Vec4Flag:
            return NotImplemented
        if not super(Vec4Flag, self).__eq__(super(Vec4Flag, other)):
            return False
        if (
            not self.init_value == other._init_value
            or not self.max_value == other.max_value
            or not self.min_value == other.min_value
        ):
            return False
        return True

    @staticmethod
    def validate_Hash(hash: Hash) -> bool:
        """Returns True if all Hash properties are valid"""
        try:
            assert type(hash["InitValue"][0][0]) == F32
            assert type(hash["InitValue"][0][1]) == F32
            assert type(hash["InitValue"][0][2]) == F32
            assert type(hash["InitValue"][0][3]) == F32
            assert type(hash["MaxValue"][0][0]) == F32
            assert type(hash["MaxValue"][0][1]) == F32
            assert type(hash["MaxValue"][0][2]) == F32
            assert type(hash["MaxValue"][0][3]) == F32
            assert type(hash["MinValue"][0][0]) == F32
            assert type(hash["MinValue"][0][1]) == F32
            assert type(hash["MinValue"][0][2]) == F32
            assert type(hash["MinValue"][0][3]) == F32
            return True
        except AssertionError:
            return False

    def to_Hash(self) -> Hash:
        r = super(Vec4Flag, self).to_Hash()
        array = Array()
        vec = Array()
        vec.append(F32(self.init_value[0]))
        vec.append(F32(self.init_value[1]))
        vec.append(F32(self.init_value[2]))
        vec.append(F32(self.init_value[3]))
        array.append(vec)
        r["InitValue"] = array
        array = Array()
        vec = Array()
        vec.append(F32(self.max_value[0]))
        vec.append(F32(self.max_value[1]))
        vec.append(F32(self.max_value[2]))
        vec.append(F32(self.max_value[3]))
        array.append(vec)
        r["MaxValue"] = array
        array = Array()
        vec = Array()
        vec.append(F32(self.min_value[0]))
        vec.append(F32(self.min_value[1]))
        vec.append(F32(self.min_value[2]))
        vec.append(F32(self.min_value[3]))
        array.append(vec)
        r["MinValue"] = array
        return r

    @property
    def init_value(self) -> Tuple[float, float, float, float]:
        return self._init_value

    @init_value.setter
    def init_value(self, value: Tuple[float, float, float, float]) -> None:
        self._init_value = value

    @property
    def max_value(self) -> Tuple[float, float, float, float]:
        return self._max_value

    @max_value.setter
    def max_value(self, value: Tuple[float, float, float, float]) -> None:
        self._max_value = value

    @property
    def min_value(self) -> Tuple[float, float, float, float]:
        return self._min_value

    @min_value.setter
    def min_value(self, value: Tuple[float, float, float, float]) -> None:
        self._min_value = value

    def use_name_to_override_params(self) -> None:
        """
        Sets flag parameters to those mandated by the overrides.
        In general, this function should always be called right
        before finalizing the flag creation/changes to ensure
        that certain values that should always be the same for
        certain flag types are upheld.
        """
        super(Vec4Flag, self).use_name_to_override_params()
        OVERRIDES = overrides["VEC4_OVERRIDES"]
        for regex, value in OVERRIDES["OVERRIDE_VEC4_INIT_VALUE"].items():
            if re.search(regex, self.data_name):
                self.init_value = value
        for regex, value in OVERRIDES["OVERRIDE_VEC4_MAX_VALUE"].items():
            if re.search(regex, self.data_name):
                self.max_value = value
        for regex, value in OVERRIDES["OVERRIDE_VEC4_MIN_VALUE"].items():
            if re.search(regex, self.data_name):
                self.min_value = value
