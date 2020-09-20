#!/usr/bin/env python3

import sys
import common_lib as mylib


def index_file():
    return mylib.path_data_index('meta.json')


def load_json_from_disk(fname):
    return mylib.json_read(fname) if mylib.file_exists(fname) else {}


def load():
    return load_json_from_disk(index_file())


def get_total_counts():
    try:
        return load_json_from_disk(index_file())['_']
    except KeyError:
        return [0, 0]


def process(bundle_ids, deleteOnly=False):
    print('writing index: meta ...')
    fname = index_file()
    if bundle_ids == ['*']:
        bundle_ids = list(mylib.enum_data_appids())
        print('  full reset')
        mylib.rm_file(fname)  # rebuild from ground up

    # json format: `bundle-id : [#recordings, #logs, #domains, #subdomains]`
    index = load_json_from_disk(fname)
    for bid in bundle_ids:
        # delete old value
        try:
            del(index[bid])
        except KeyError:
            pass
        if deleteOnly:
            continue
        # set new value
        json, _ = mylib.json_read_evaluated(bid)
        index[bid] = [json['sum_rec'], json['sum_logs'],
                      len(json['pardom']), len(json['subdom'])]
    # sum of counts
    try:
        del(index['_'])
    except KeyError:
        pass
    total = [0, 0]
    for val in index.values():
        total[0] += val[0]
        total[1] += val[1]
    index['_'] = total

    # write json
    mylib.json_write(fname, index, pretty=False)
    print('')


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) > 0:
        process(args)
    else:
        # process(['*'], deleteOnly=False)
        mylib.usage(__file__, '[bundle_id] [...]')
