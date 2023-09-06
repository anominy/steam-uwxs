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

import os
import asyncio
import steam

from typing import Final
from argparse import ArgumentParser, Namespace
from functools import cmp_to_key

_license_path: Final[str] = f'{os.path.dirname(__file__)}/../COPYING'


def _main() -> None:
    arg_parser: Final[ArgumentParser] = ArgumentParser()

    arg_parser.add_argument(
        '--license',
        help='show the project license and exit',
        dest='is_license',
        action='store_true',
    )

    arg_parser.add_argument(
        '--min-length',
        type=int,
        help='minimum url length',
        dest='min_len',
        action='store',
        choices=steam.length_range,
        default=None
    )

    arg_parser.add_argument(
        '--max-length',
        type=int,
        help='maximum url length',
        dest='max_len',
        action='store',
        choices=steam.length_range,
        default=None
    )

    arg_parser.add_argument(
        '--endpoint',
        type=str,
        help='steam url endpoint',
        dest='endpoint',
        action='store',
        choices=steam.endpoints,
        default=steam.endpoint_id
    )

    arg_parser.add_argument(
        '--pattern',
        type=str,
        help='steam url pattern',
        dest='pattern',
        metavar='REGEX',
        action='store'
    )

    arg_parser.add_argument(
        '--sort',
        help='sort output urls',
        dest='is_sort',
        action='store_true'
    )

    arg_parser.add_argument(
        '--in',
        type=str,
        help='input from file',
        metavar='FILENAME',
        dest='in_file',
        action='store',
        default=None
    )

    arg_parser.add_argument(
        '--out',
        type=str,
        help='output to file',
        metavar='FILENAME',
        dest='out_file',
        action='store',
        default=None
    )

    args: Final[Namespace] = arg_parser.parse_args()

    if args.is_license:
        with open(_license_path, 'r') as license_file:
            print(license_file.read())

        return

    asyncio.set_event_loop(asyncio.new_event_loop())

    if args.in_file is not None:
        with open(args.in_file, 'r') as file:
            gen_list: Final[list[str]] = [word for line in file for word in line.split()]
    else:
        gen_list: Final[list[str]] = steam.gen_urls(args.min_len, args.max_len, args.pattern)

    check_list: Final[list[str]] = steam.check_urls(args.endpoint, gen_list)
    if not check_list:
        return

    if args.is_sort:
        check_list.sort(key=cmp_to_key(steam.compare_urls))

    if args.out_file is not None:
        with open(args.out_file, 'w') as file:
            print(*check_list, sep='\n', file=file)
    else:
        print(*check_list, sep='\n')


if __name__ == '__main__':
    try:
        _main()
    except KeyboardInterrupt:
        pass
