#!/usr/bin/env python3

import os
import sys
import common_lib as mylib
import bundle_combine
import bundle_download
import html_root
import html_index
import html_bundle
import tracker_download


def print_usage_and_exit():
    mylib.usage(__file__, 'command [params]')
    print('''
  import                 | check '_in' folder for new apps
  tracker                | update tracking domains
  icons                  | check & download missing icons
  run [bundle_id] [...]  | recombine and rebuild apps
  del [bundle_id] [...]  | remove app and rebuild index
''')
    exit(0)


def del_id(bundle_ids):
    if bundle_ids == ['*']:
        bundle_ids = list(mylib.enum_appids())

    for bid in bundle_ids:
        dest = mylib.path_out_app(bid)
        if mylib.dir_exists(dest):
            mylib.rm(dest)
            html_index.process()


def combine_and_update(bundle_ids, where=None, forceGraphs=False):
    affected = bundle_combine.process(bundle_ids, where=where)
    if len(affected) == 0:
        print('no bundle affected by tracker, not generating bundle html')
        return
    new_ids = html_bundle.process(affected, forceGraphs=forceGraphs)
    if len(new_ids) == 0:
        print('no new bundle, not rebuilding index')
        return
    bundle_download.process(new_ids)
    html_index.process()
    html_root.process()


def import_update():
    print('checking incoming data ...')
    needs_update = set()
    for fname, bid in mylib.enum_newly_added():
        if bid == '_manually':
            # TODO: notify admin that manual action is required
            mylib.err('import', 'manual action required!')
        else:
            print('  ' + bid)
            needs_update.add(bid)
        os.remove(fname)
    print('')
    if len(needs_update) > 0:
        combine_and_update(needs_update, forceGraphs=True)


def tracker_update():
    new_trackers = tracker_download.process()
    if new_trackers:
        combine_and_update(['*'], where=new_trackers)


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) == 0:
        print_usage_and_exit()
    cmd = args[0]
    params = args[1:]
    if cmd == 'import':
        import_update()
    elif cmd == 'del':
        if len(params) == 0:
            print_usage_and_exit()
        del_id(params)  # ['_manually']
    elif cmd == 'run':
        if len(params) == 0:
            print_usage_and_exit()
        combine_and_update(params)  # ['*'], where=['test.com']
    elif cmd == 'icons':
        if bundle_download.download_missing_icons(force=False):
            html_index.process()
    elif cmd == 'tracker':
        tracker_update()
        # tracker_download.combine_all('x')
