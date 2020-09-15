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
        json = dict({'bundle': [], 'pardom': dict(), 'subdom': dict()})
    return json


def delete_from_index(index, bundle_ids, deleteOnly=False):
    ids_to_delete = set()
    for bid in bundle_ids:
        try:
            i = index['bundle'].index(bid)
        except ValueError:  # index not found
            continue
        ids_to_delete.add(i)
        if deleteOnly:
            index['bundle'][i] = '_'

    if len(ids_to_delete) == 0:
        return False

    for key in ['pardom', 'subdom']:
        for domain in list(index[key].keys()):
            for i in ids_to_delete:
                try:
                    index[key][domain].remove(i)
                except ValueError:  # ignore if not present
                    continue
            if not index[key][domain]:
                del(index[key][domain])
    return True


def insert_in_index(index, bundle_ids):
    has_changes = False
    for bid in bundle_ids:
        try:
            i = index['bundle'].index(bid)
        except ValueError:  # index not found
            i = len(index['bundle'])
            index['bundle'].append(bid)
        json, _ = mylib.json_read_evaluated(bid)
        for key in ['pardom', 'subdom']:  # assuming keys are identical
            for domain, _, _ in json[key]:
                try:
                    index[key][domain].append(i)
                except KeyError:
                    index[key][domain] = [i]
                has_changes = True
    return has_changes


def process(bundle_ids, deleteOnly=False):
    print('writing reverse index ...')
    index_file = get_index_path()
    if bundle_ids == ['*']:
        bundle_ids = list(mylib.enum_data_appids())
        mylib.rm_file(index_file)  # rebuild from ground up
    # load previous index
    json = load_index_json(index_file)
    # delete previous index entries
    did_change = delete_from_index(json, bundle_ids, deleteOnly=deleteOnly)
    # write new index to disk
    if not deleteOnly:
        did_change |= insert_in_index(json, bundle_ids)
    if did_change:
        mylib.json_write(index_file, json, pretty=False)
    else:
        print('  no change')
    print('')


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) > 0:
        process(args)
    else:
        # process(['*'], deleteOnly=False)
        mylib.usage(__file__, '[bundle_id] [...]')
