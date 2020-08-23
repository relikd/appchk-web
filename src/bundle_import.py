#!/usr/bin/env python3

import os
import common_lib as mylib


def next_path(path_pattern):
    i = 1
    while os.path.exists(path_pattern % i):
        i = i * 2
    a, b = (i // 2, i)
    while a + 1 < b:
        c = (a + b) // 2  # interval midpoint
        a, b = (c, b) if os.path.exists(path_pattern % c) else (a, c)
    return path_pattern % b


def process():
    print('checking incoming files ...')
    prefix = mylib.path_len(mylib.path_data())
    needs_update = set()
    for fname, jdata in mylib.enum_newly_added():
        try:
            bundle_id = jdata['app-bundle'].strip()
            if mylib.valid_bundle_id(bundle_id):
                dest = mylib.path_data_app(bundle_id)
                needs_update.add(bundle_id)
            else:
                dest = mylib.path_data('_manually')
                # needs_update.add('_manually')

            mylib.mkdir(dest)
            dest_file = next_path(mylib.path_add(dest, 'id_%s.json'))
            mylib.mv(fname, dest_file, printOmitPrefix=prefix)
        except KeyError:
            mylib.err('json-import', 'malformed json: ' + bundle_id)
    print('done.')
    print('')
    return needs_update
