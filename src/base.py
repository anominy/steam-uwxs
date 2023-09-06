#  steam-uwxs
#
#  Copyright (C) 2023  anominy
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from typing import Final


def to_base(num: int, base: str) -> str:
    if num < 1:
        raise ValueError()

    base_len: Final[int] = len(base)

    r: str = ''
    while num:
        mod: int = (num - 1) % base_len
        r = base[mod] + r
        num = (num - mod) // base_len

    return r


def from_base(num: str, base: str) -> int:
    base_len: Final[int] = len(base)

    r: int = 0
    for i in num:
        r = r * base_len + base.index(i) + 1

    return r


def is_base(num: str, base: str) -> bool:
    for c in num:
        if c not in base:
            return False

    return True
