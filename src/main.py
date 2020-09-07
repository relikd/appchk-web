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
  index                  | rebuild index & root html
  run [bundle_id] [...]  | recombine and rebuild apps
  del [bundle_id] [...]  | remove app and rebuild index
''')
    exit(0)


def rebuild_index(inclRoot=False):
    html_index.process()
    if inclRoot:  # TODO: remove check if root contains dynamic content
        html_root.process()


def del_id(bundle_ids):
    print('removing apps from website:')
    if bundle_ids == ['*']:
        bundle_ids = list(mylib.enum_appids())

    update_index = False
    for bid in bundle_ids:
        dest = mylib.path_out_app(bid)
        if mylib.dir_exists(dest):
            print('  ' + bid)
            mylib.rm(dest)
            update_index = True
    print('')
    if update_index:
        rebuild_index()


def combine_and_update(bundle_ids, where=None):
    new_ids = bundle_download.process(bundle_ids)
    affected = bundle_combine.process(bundle_ids, where=where)
    if len(affected) > 0:
        html_bundle.process(affected)
    else:
        print('no bundle affected by tracker, not generating bundle html')
    if len(new_ids) > 0:
        rebuild_index()
    else:
        print('no new bundle, not rebuilding index')


def import_update():
    print('checking incoming data ...')
    needs_update = set()
    for fname, bid in mylib.enum_newly_added():
        if bid == '_manually':
            # TODO: notify admin that manual action is required
            mylib.err('import', 'manual action required!')
        elif bid == '_longterm':
            mylib.err('import', 'manual action required! (background)')
        else:
            print('  ' + bid)
            needs_update.add(bid)
        os.remove(fname)
    print('')
    if len(needs_update) > 0:
        combine_and_update(needs_update)


def tracker_update():
    new_trackers = tracker_download.process()
    if new_trackers:
        combine_and_update(['*'], where=new_trackers)


try:
    if __name__ == '__main__':
        args = sys.argv[1:]
        if len(args) == 0:
            print_usage_and_exit()
        cmd = args[0]
        params = args[1:]
        if cmd == 'import':
            import_update()
        elif cmd == 'tracker':
            tracker_update()
            # tracker_download.combine_all('x')
        elif cmd == 'icons':
            if bundle_download.download_missing_icons(force=False):
                rebuild_index()
        elif cmd == 'index':
            rebuild_index(inclRoot=True)
        elif cmd == 'run':
            if len(params) == 0:
                print_usage_and_exit()
            combine_and_update(params)  # ['*'], where=['test.com']
        elif cmd == 'del':
            if len(params) == 0:
                print_usage_and_exit()
            del_id(params)  # ['_manually']
except Exception as e:
    mylib.err('critical', e)
