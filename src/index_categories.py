#!/usr/bin/env python3

import sys
import lib_common as mylib
import download_itunes  # get_genres

_dict_apps = None
_dict_names = None


def fname_app_categories():
    return mylib.path_data_index('app_categories.json')


def fname_cat_name_all():
    return mylib.path_data_index('category_names_all.json')


def fname_cat_name_compact():
    return mylib.path_data_index('category_names_compact.json')


def load_json_if_not_already(noNames=False):
    global _dict_apps, _dict_names
    if not _dict_apps:
        _dict_apps = mylib.json_safe_read(fname_app_categories(), {})
    if not _dict_names and not noNames:
        _dict_names = mylib.json_safe_read(fname_cat_name_compact(), {})


def try_update_app(index, bid, genre_ids):
    try:
        if index[bid] == genre_ids:
            return False
    except KeyError:
        pass
    index[bid] = genre_ids
    return True


def try_update_name_all(index, cid, lang, name):
    try:
        index[cid]
    except KeyError:
        index[cid] = {}
    try:
        if index[cid][lang]:
            return False  # key already exists
    except KeyError:
        pass
    index[cid][lang] = name
    return True  # updated, need to persist changes


def reset_index():
    global _dict_apps, _dict_names
    mylib.rm_file(fname_app_categories())  # rebuild from ground up
    mylib.rm_file(fname_cat_name_all())
    mylib.rm_file(fname_cat_name_compact())
    _dict_apps = None
    _dict_names = None


def get_categories(bundle_id):
    load_json_if_not_already()
    try:
        genres = _dict_apps[bundle_id]
    except KeyError:
        return []
    res = []
    for gid in genres:
        res.append((gid, _dict_names[gid]))
    return res


def enum_all_categories():
    load_json_if_not_already()
    reverse_index = {}
    for bid, genre_ids in _dict_apps.items():
        for gid in genre_ids:
            try:
                reverse_index[gid].append(bid)
            except KeyError:
                reverse_index[gid] = [bid]
    for gid, name in _dict_names.items():
        yield gid, name, reverse_index[gid]


def process(bundle_ids, force=False):
    global _dict_apps, _dict_names
    print('writing index: categories ...')
    if force and bundle_ids == ['*']:
        print('  full reset')
        reset_index()

    load_json_if_not_already(noNames=False)
    name_index = mylib.json_safe_read(fname_cat_name_all(), {})
    write_name_index = False
    write_app_index = False
    for bid in mylib.appids_in_data(bundle_ids):
        cateogory_ids = []
        for lang, cid, gname in download_itunes.enum_genres(bid):
            if cid not in cateogory_ids:
                cateogory_ids.append(cid)
            if try_update_name_all(name_index, cid, lang, gname):
                write_name_index = True
        if try_update_app(_dict_apps, bid, cateogory_ids):
            write_app_index = True

    if write_app_index:
        print('  write app-index')
        mylib.json_write(fname_app_categories(), _dict_apps, pretty=False)
    if write_name_index:
        print('  write name-index')
        mylib.json_write(fname_cat_name_all(), name_index, pretty=False)
        _dict_names = {cid: download_itunes.choose_lang(names)
                       for cid, names in name_index.items()}
        mylib.json_write(fname_cat_name_compact(), _dict_names, pretty=False)
    print('')


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) > 0:
        process(args)
    else:
        # process(['*'], force=True)
        mylib.usage(__file__, '[bundle_id] [...]')
