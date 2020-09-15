#!/usr/bin/env python3

import sys
import common_lib as mylib


def get_index_path():
    pth = mylib.path_root('data', '_eval')
    mylib.mkdir(pth)
    return mylib.path_add(pth, 'reverse_index.json')


def load_index_json(file_path):
    if mylib.file_exists(file_path):
        json = mylib.json_read(file_path)
    else:
        json = dict({'pardom': dict(), 'subdom': dict()})
    return json


def delete_from_index(index, bundle_ids):
    for key in ['pardom', 'subdom']:
        for domain in list(index[key].keys()):
            for bid in bundle_ids:
                try:
                    index[key][domain].remove(bid)
                except ValueError:
                    pass  # ignore if not present
            if not index[key][domain]:
                del(index[key][domain])


def insert_in_index(index, bundle_ids):
    for bid in bundle_ids:
        json, _ = mylib.json_read_evaluated(bid)
        for key in ['pardom', 'subdom']:  # assuming keys are identical
            for domain, _, _ in json[key]:
                try:
                    index[key][domain].append(bid)
                except KeyError:
                    index[key][domain] = [bid]


def process(bundle_ids, deleteOnly=False):
    print('writing reverse index ...')
    index_file = get_index_path()
    if bundle_ids == ['*']:
        bundle_ids = list(mylib.enum_data_appids())
        mylib.rm_file(index_file)  # rebuild from ground up
    # load previous index
    json = load_index_json(index_file)
    # delete previous index entries
    delete_from_index(json, bundle_ids)
    # write new index to disk
    if not deleteOnly:
        insert_in_index(json, bundle_ids)
    mylib.json_write(index_file, json, pretty=False)
    print('')


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) > 0:
        process(args)
    else:
        # process(['*'])
        mylib.usage(__file__, '[bundle_id] [...]')
