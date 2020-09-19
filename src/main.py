#!/usr/bin/env python3

import sys
import traceback
import common_lib as mylib
import bundle_combine
import bundle_download
import html_root
import html_index_apps
import html_bundle
import html_index_domains
import index_app_names
import index_domains
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


def rebuild_app_index(inclRoot=False):
    html_index_apps.process()
    if inclRoot:  # TODO: remove check if root contains dynamic content
        html_root.process()


def rebuild_domain_index(bundle_ids, deleteOnly=False):
    index_domains.process(bundle_ids, deleteOnly=deleteOnly)
    html_index_domains.process()


def rebuild_name_index(new_ids):
    if index_app_names.missing():
        index_app_names.process(['*'])
    elif len(new_ids) > 0:
        index_app_names.process(new_ids)  # after bundle_download


def del_id(bundle_ids):
    print('removing apps from website:')
    if bundle_ids == ['*']:
        bundle_ids = list(mylib.enum_appids())

    update_app_index = False
    for bid in bundle_ids:
        dest = mylib.path_out_app(bid)
        if mylib.dir_exists(dest):
            print('  ' + bid)
            mylib.rm_dir(dest)
            update_app_index = True
    print('')
    rebuild_domain_index(bundle_ids, deleteOnly=True)
    if update_app_index:
        rebuild_app_index(inclRoot=True)


def combine_and_update(bundle_ids, where=None):
    # 1. download meta data from iTunes store, incl. app icons
    new_ids = bundle_download.process(bundle_ids)
    # 2. if new apps, update bundle name index
    rebuild_name_index(new_ids)  # after bundle_download
    # 3. re-calculate combined.json and evaluated.json files
    affected = bundle_combine.process(bundle_ids, where=where)
    # special case needed for domain index. '*' will force rebuilt index
    if not where and bundle_ids == ['*']:
        affected = ['*']
    # 4. was any json updated? if so, make html and update domain index
    if len(affected) > 0:
        rebuild_domain_index(affected)  # after bundle_combine
        html_bundle.process(affected)  # after index_app_names
    else:
        print('no bundle affected by tracker, not generating bundle html')
    # 5. make all apps index
    if len(new_ids) > 0:
        rebuild_app_index()  # must be called after bundle_combine
    else:
        print('no new bundle, not rebuilding index')


def import_update():
    print('checking incoming data ...')
    needs_update = set()
    then_delete = set()
    for fname, bid in mylib.enum_newly_added():
        if bid == '_manually':
            # TODO: notify admin that manual action is required
            mylib.err('import', 'manual action required!')
        elif bid == '_longterm':
            mylib.err('import', 'manual action required! (background)')
        else:
            print('  ' + bid)
            needs_update.add(bid)
        then_delete.add(fname)
    print('')
    if len(needs_update) > 0:
        combine_and_update(needs_update)
        html_root.gen_help()
    if len(then_delete) > 0:
        print('cleanup _in folder ...')
        for x in then_delete:
            mylib.rm_file(fname)
        print('')


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
            # tracker_download.combine_all()
        elif cmd == 'icons':
            if bundle_download.download_missing_icons(force=False):
                rebuild_app_index()
        elif cmd == 'index':
            rebuild_domain_index(['*'])
            rebuild_app_index(inclRoot=True)
        elif cmd == 'run':
            if len(params) == 0:
                print_usage_and_exit()
            combine_and_update(params)  # ['*'], where=['test.com']
        elif cmd == 'del':
            if len(params) == 0:
                print_usage_and_exit()
            del_id(params)  # ['_manually']
except Exception:
    mylib.err('critical', traceback.format_exc(), logOnly=True)
    raise
