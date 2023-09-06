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

import asyncio

import re as regx

# noinspection PyPep8Naming
from sre_constants import error as RegexError

from typing import Final, Optional, Union
from aiohttp import ClientSession, ClientTimeout, ClientError
from base import to_base, from_base, is_base

endpoint_groups: Final[str] = 'groups'
endpoint_id: Final[str] = 'id'
endpoints: Final[tuple[str, ...]] = (endpoint_groups, endpoint_id)

min_length: Final[int] = 1
max_length: Final[int] = 4

length_range: Final[range] = range(min_length, max_length + 1)

_url_base: Final[str] = 'abcdefghijklmnopqrstuvwxyz0123456789-_'
_url_fmt: Final[str] = 'https://steamcommunity.com/%s/%s'

_sort_depth_layers: Final[tuple[str, ...]] = ('0123456789', 'abcdefghijklmnopqrstuvwxyz', '-_')
_sort_depth_max: Final[int] = len(_sort_depth_layers)

_default_timeout: Final[ClientTimeout] = ClientTimeout()


def gen_urls(min_len: Optional[int], max_len: Optional[int], pattern: Optional[Union[str, regx.Pattern]] = None) -> Optional[list[str]]:
    if not min_len \
            or not max_len:
        return None

    if min_len < min_length \
            or max_len > max_length \
            or max_len < min_len:
        raise ValueError()

    if isinstance(pattern, str) and pattern:
        try:
            pattern = regx.compile(pattern)
        except RegexError:
            return None

    gen_list: Final[list[str]] = []

    left: Final[int] = from_base(_url_base[0] * min_len, _url_base)
    right: Final[int] = from_base(_url_base[-1] * max_len, _url_base)

    for i in range(left, right):
        url: str = to_base(i, _url_base)
        if pattern is None \
                or pattern.search(url):
            gen_list.append(url)

    return gen_list


def check_urls(endpoint: Optional[str], gen_list: Optional[list[str]]) -> Optional[list[str]]:
    if not endpoint:
        return None

    if not gen_list:
        return None

    endpoint = endpoint.lower()
    if endpoint not in endpoints:
        return None

    check_list: Final[list[str]] = []

    asyncio.get_event_loop() \
        .run_until_complete(_check_urls0(endpoint, gen_list, check_list))

    return check_list


async def _check_urls0(endpoint: str, gen_list: list[str], check_list: list[str]) -> None:
    async with ClientSession(timeout=_default_timeout) as session:
        await asyncio.gather(*[_check_url0(session, endpoint, url, check_list) for url in gen_list])


async def _check_url0(session: ClientSession, endpoint: str, url: str, check_list: list[str]) -> None:
    async with session.get(_url_fmt % (endpoint, url)) as response:
        try:
            content: Final[str] = await response.text()

            if content \
                    and '<p class="returnLink">' in content \
                    and 'This group has been removed' not in content:
                check_list.append(url)
        except (ValueError, ClientError):
            pass


def compare_urls(url0: Optional[str], url1: Optional[str]) -> int:
    if url0 == url1 \
            or url0 is None \
            or url1 is None:
        return 0

    # Length comparison
    len0: Final[int] = len(url0)
    len1: Final[int] = len(url1)

    if len0 != len1:
        return -1 if len0 < len1 else 1

    # Depth comparison
    depth0: Final[int] = _sort_depth(url0)
    depth1: Final[int] = _sort_depth(url1)

    if depth0 != depth1:
        return -1 if depth0 < depth1 else 1

    # Identifier comparison
    id0: Final[int] = from_base(url0, _url_base)
    id1: Final[int] = from_base(url1, _url_base)

    return -1 if id0 < id1 else 1


def _sort_depth(url: str) -> int:
    depth_level: int = _sort_depth_max

    for i in range(_sort_depth_max):
        if not is_base(url, _sort_depth_layers[i]):
            continue

        depth_level = i
        break

    return depth_level
