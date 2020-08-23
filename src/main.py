#!/usr/bin/env python3

import common_lib as mylib
import bundle_import
import bundle_combine
import bundle_download
import html_root
import html_index
import html_bundle


def reset_new():
    print("RESET json files ...")
    prefix = mylib.path_len(mylib.path_data())
    for bid in mylib.enum_appids():
        for src, _ in mylib.enum_jsons(bid):
            frmt = mylib.path_add(mylib.path_data('_in', '%s.json'))
            dest = bundle_import.next_path(frmt)
            mylib.mv(src, dest, printOmitPrefix=prefix)
    print('')


def del_id(bundle_ids):
    if bundle_ids == ['*']:
        bundle_ids = list(mylib.enum_appids())

    for bid in bundle_ids:
        dest = mylib.path_out_app(bid)
        if mylib.dir_exists(dest):
            mylib.rm(dest)
            html_index.process()


def full_chain(force=False):
    bundle_ids = bundle_import.process()
    if force:
        bundle_ids = list(mylib.enum_data_appids())
    if len(bundle_ids) > 0:
        bundle_combine.process(bundle_ids)
        new_ids = html_bundle.process(bundle_ids)
        if len(new_ids) > 0:
            bundle_download.process(new_ids)
            html_index.process()
            html_root.process()
        else:
            print('none to import, not rebuilding index')


def process():
    # reset_new()
    # del_id(['*'])
    full_chain(force=False)


process()
