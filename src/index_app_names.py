#!/usr/bin/env python3

import sys
import common_lib as mylib
import download_itunes  # app_names

_bundle_name_dict = None


def index_fname():
    return mylib.path_data_index('app_names.json')


def missing():
    return not mylib.file_exists(index_fname())


def load_json_if_not_already():
    global _bundle_name_dict
    if not _bundle_name_dict:
        index_file = index_fname()
        if mylib.file_exists(index_file):
            _bundle_name_dict = mylib.json_read(index_file)
        else:
            _bundle_name_dict = {}


def write_json_to_disk():
    mylib.json_write(index_fname(), _bundle_name_dict, pretty=False)


def get_name(bundle_id, langs=['us', 'de'], fallback='&lt; App-Name &gt;'):
    load_json_if_not_already()
    for lang in langs:
        try:
            return _bundle_name_dict[bundle_id][lang]
        except KeyError:
            continue
    return fallback  # None


def process(bundle_ids):
    print('writing index: app names ...')
    if bundle_ids == ['*']:
        print('  full reset')
        mylib.rm_file(index_fname())  # rebuild from ground up

    load_json_if_not_already()
    did_change = False
    for bid in mylib.appids_in_data(bundle_ids):
        names = download_itunes.get_app_names(bid)
        if not names:
            mylib.err('index-app-names', 'could not load: {}'.format(bid))
            continue
        _bundle_name_dict[bid] = names
        did_change = True
    if did_change:
        write_json_to_disk()
    else:
        print('  no change')
    print('')


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) > 0:
        process(args)
    else:
        # process(['*'])
        mylib.usage(__file__, '[bundle_id] [...]')
