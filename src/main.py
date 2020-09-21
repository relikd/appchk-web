#!/usr/bin/env python3

import sys
import traceback
import common_lib as mylib
import bundle_combine
import download_itunes
import download_tracker
import html_bundle
import html_index_apps
import html_index_domains
import html_root
import index_app_names
import index_domains
import index_meta


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


def rebuild_app_index_html(inclRoot=False):
    html_index_apps.process()
    if inclRoot:  # TODO: remove check if root contains dynamic content
        html_root.process()


def rebuild_domain_index(bundle_ids, deleteOnly=False):
    index_domains.process(bundle_ids, deleteOnly=deleteOnly)
    html_index_domains.process()


def del_id(bundle_ids):
    print('removing apps from website:')
    update_app_index = False
    for bid in mylib.appids_in_out(bundle_ids):
        dest = mylib.path_out_app(bid)
        if mylib.dir_exists(dest):
            print('  ' + bid)
            mylib.rm_dir(dest)
            update_app_index = True
    print('')
    index_meta.process(bundle_ids, deleteOnly=True)
    rebuild_domain_index(bundle_ids, deleteOnly=True)
    if update_app_index:
        rebuild_app_index_html(inclRoot=True)


def combine_and_update(bundle_ids):
    # 1. download meta data from iTunes store, incl. app icons
    new_ids = download_itunes.process(bundle_ids)
    # 2. if new apps, update bundle name index
    if bundle_ids == ['*']:
        new_ids = ['*']  # special case needed to force rebuilt index
    if len(new_ids) > 0:
        index_app_names.process(new_ids)  # after download_itunes
    # 3. re-calculate combined.json and evaluated.json files
    bundle_combine.process(bundle_ids)
    # 4. make html and update domain index
    index_meta.process(bundle_ids)  # after bundle_combine
    html_bundle.process(bundle_ids)  # after index_app_names
    rebuild_domain_index(bundle_ids)  # after bundle_combine
    # 5. make all apps index
    if len(new_ids) > 0:
        rebuild_app_index_html()  # after bundle_combine
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
    new_trackers = download_tracker.process()
    affected = index_domains.all_bundles_containing(new_trackers)
    if len(affected) > 0:
        combine_and_update(affected)
    else:
        print('no bundle affected by tracker, not generating bundle html')


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
            # download_tracker.combine_all()
        elif cmd == 'icons':
            if download_itunes.download_missing_icons(force=False):
                rebuild_app_index_html()
        elif cmd == 'index':
            index_meta.process(['*'])
            rebuild_domain_index(['*'])
            rebuild_app_index_html(inclRoot=True)
        elif cmd == 'run':
            if len(params) == 0:
                print_usage_and_exit()
            combine_and_update(params)
        elif cmd == 'del':
            if len(params) == 0:
                print_usage_and_exit()
            del_id(params)  # ['_manually']
        else:
            print_usage_and_exit()
except Exception:
    mylib.err('critical', traceback.format_exc(), logOnly=True)
    raise
