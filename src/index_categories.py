#!/usr/bin/env python3

import sys
import common_lib as mylib
import download_itunes  # get_genres

_dict_apps = None
_dict_names = None


def fname_app_categories():
    return mylib.path_data_index('app_categories.json')


def fname_category_names():
    return mylib.path_data_index('category_names.json')


def load_json_if_not_already():
    def load_json_from_disk(fname):
        return mylib.json_read(fname) if mylib.file_exists(fname) else {}

    global _dict_apps, _dict_names
    if not _dict_apps:
        _dict_apps = load_json_from_disk(fname_app_categories())
    if not _dict_names:
        _dict_names = load_json_from_disk(fname_category_names())


def try_update_app(bid, genre_ids):
    try:
        if _dict_apps[bid] == genre_ids:
            return False
    except KeyError:
        pass
    _dict_apps[bid] = genre_ids
    return True


def try_update_name(gid, lang, name):
    try:
        _dict_names[gid]
    except KeyError:
        _dict_names[gid] = {}
    try:
        if _dict_names[gid][lang]:
            return False  # key already exists
    except KeyError:
        pass
    _dict_names[gid][lang] = name
    return True  # updated, need to persist changes


def reset_index():
    global _dict_apps
    print('  full reset')
    mylib.rm_file(fname_app_categories())  # rebuild from ground up
    _dict_apps = None


def try_persist_changes(flag_apps, flag_names):
    if flag_apps:
        print('  write app-index')
        mylib.json_write(fname_app_categories(), _dict_apps, pretty=False)
    if flag_names:
        print('  write name-index')
        mylib.json_write(fname_category_names(), _dict_names, pretty=False)


def get_categories(bundle_id):
    load_json_if_not_already()
    try:
        genres = _dict_apps[bundle_id]
    except KeyError:
        return []
    res = []
    for gid in genres:
        for lang in ['us', 'de']:
            try:
                name = _dict_names[gid][lang]
            except KeyError:
                continue
            res.append((gid, name))
            break
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
    for gid, lang_dict in _dict_names.items():
        for lang in ['us', 'de']:
            try:
                name = lang_dict[lang]
            except KeyError:
                continue
            yield gid, name, reverse_index[gid]
            break


def process(bundle_ids, force=False):
    print('writing index: categories ...')
    if force and bundle_ids == ['*']:
        reset_index()

    load_json_if_not_already()
    write_app_index = False
    write_name_index = False
    for bid in mylib.appids_in_data(bundle_ids):
        genre_ids = []
        for lang, gid, gname in download_itunes.enum_genres(bid):
            if gid not in genre_ids:
                genre_ids.append(gid)
            if try_update_name(gid, lang, gname):
                write_name_index = True
        if try_update_app(bid, genre_ids):
            write_app_index = True

    try_persist_changes(write_app_index, write_name_index)
    print('')


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) > 0:
        process(args)
    else:
        # process(['*'])
        mylib.usage(__file__, '[bundle_id] [...]')
