#!/usr/bin/env python3

import sys
import lib_common as mylib
import download_itunes  # app_names

_app_names_dict = None


def fname_apps_all():
    return mylib.path_data_index('app_names_all.json')


def fname_apps_compact():
    return mylib.path_data_index('app_names_compact.json')


def load_json_if_not_already():
    global _app_names_dict
    if not _app_names_dict:
        _app_names_dict = mylib.json_safe_read(fname_apps_compact(), {})


def get_name(bundle_id, fallback='&lt; App-Name &gt;'):
    load_json_if_not_already()
    try:
        return _app_names_dict[bundle_id]
    except KeyError:
        return fallback


def get_sorted_app_names():
    load_json_if_not_already()
    return sorted(_app_names_dict.items(), key=lambda x: x[1].lower())


def process(bundle_ids, deleteOnly=False):
    global _app_names_dict
    print('writing index: app names ...')
    if bundle_ids == ['*']:
        print('  full reset')
        mylib.rm_file(fname_apps_all())  # rebuild from ground up
        mylib.rm_file(fname_apps_compact())

    index = mylib.json_safe_read(fname_apps_all(), {})
    did_change = False
    for bid in mylib.appids_in_data(bundle_ids):
        if deleteOnly:
            did_change |= mylib.try_del(index, [bid])
            continue
        names = download_itunes.get_app_names(bid)
        if not names:
            mylib.err('index-app-names', 'could not load: {}'.format(bid))
            continue
        try:
            if index[bid] == names:
                continue
        except KeyError:
            pass
        index[bid] = names
        did_change = True
    if did_change:
        print('  writing')
        mylib.json_write(fname_apps_all(), index, pretty=False)
        _app_names_dict = {bid: download_itunes.choose_lang(names)
                           for bid, names in index.items()}
        mylib.json_write(fname_apps_compact(), _app_names_dict, pretty=False)
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
