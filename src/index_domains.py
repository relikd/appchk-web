#!/usr/bin/env python3

import sys
import common_lib as mylib
import bundle_combine
import tracker_download


def fname_all():
    return mylib.path_data_index('all_domains.json')


def fname_tracker():
    return mylib.path_data_index('tracker_domains.json')


def index_fname(tracker_only=False):
    return mylib.path_data_index(
        'tracker_domains.json' if tracker_only else 'all_domains.json')


def load_json_from_disk(index_file):
    if mylib.file_exists(index_file):
        return mylib.json_read(index_file)
    else:
        return {'bundle': [], 'pardom': {}, 'subdom': {}}


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


def filter_tracker_only(index):
    sub_trkr = {}
    par_trkr = {}
    for domain, ids in filter(lambda x: tracker_download.is_tracker(x[0]),
                              index['subdom'].items()):
        sub_trkr[domain] = ids
        pardom = bundle_combine.get_parent_domain(domain)
        try:
            par_trkr[pardom].update(ids)
        except KeyError:
            par_trkr[pardom] = set(ids)
    for dom, ids in par_trkr.items():
        par_trkr[dom] = list(ids)
    index['subdom'] = sub_trkr
    index['pardom'] = par_trkr


def load(tracker=False):
    return load_json_from_disk(fname_tracker() if tracker else fname_all())


def number_of_apps(index):
    return sum(1 for x in index['bundle'] if x != '_')


def enrich_with_bundle_ids(index):
    for key in ['pardom', 'subdom']:
        for dom, ids in index[key].items():
            index[key][dom] = [index['bundle'][i] for i in ids]


def process(bundle_ids, deleteOnly=False):
    print('writing index: domains ...')
    fname = fname_all()
    if bundle_ids == ['*']:
        bundle_ids = list(mylib.enum_data_appids())
        print('  full reset')
        mylib.rm_file(fname)  # rebuild from ground up

    index = load_json_from_disk(fname)
    did_change = delete_from_index(index, bundle_ids, deleteOnly=deleteOnly)
    if not deleteOnly:
        did_change |= insert_in_index(index, bundle_ids)
    if did_change:
        mylib.json_write(fname, index, pretty=False)
        filter_tracker_only(index)
        mylib.json_write(fname_tracker(), index, pretty=False)
    else:
        print('  no change')
    print('')


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) > 0:
        process(args)
    else:
        process(['*'], deleteOnly=False)
        mylib.usage(__file__, '[bundle_id] [...]')
