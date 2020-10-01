#!/usr/bin/env python3

import sys
import traceback
import lib_common as mylib
import bundle_combine
import download_itunes
import download_tracker
import html_bundle
import html_categories
import html_index_apps
import html_index_domains
import html_ranking
import html_root
import index_app_names
import index_categories
import index_domains
import index_rank


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


def rebuild_html(bundle_ids=None, cat_ids=None, inclIApp=True):
    # all of these must happen after index_app_names
    if bundle_ids:
        html_bundle.process(bundle_ids)  # after index_rank
    html_categories.process(affected=cat_ids)  # after index_categories
    if inclIApp:
        html_index_apps.process()  # after index_categories
    else:
        print('no new bundle, not rebuilding index')
    html_ranking.process()  # after html_categories & html_index_apps
    app_count, dom_count = html_index_domains.process()  # after index_domains
    html_root.process(app_count, dom_count, inclStatic=True)


def del_id(bundle_ids):
    def delete_from_all_indices(bundle_ids):
        index_rank.process(bundle_ids, deleteOnly=True)
        index_domains.process(bundle_ids, deleteOnly=True)
        index_app_names.process(bundle_ids, deleteOnly=True)

    print('removing apps from website:')
    for bid in mylib.appids_in_out(bundle_ids):
        dest = mylib.path_out_app(bid)
        if mylib.dir_exists(dest):
            print('  ' + bid)
            mylib.rm_dir(dest)
    print('')
    delete_from_all_indices(bundle_ids)
    rebuild_html()


def combine_and_update(bundle_ids):
    # 1. download meta data from iTunes store, incl. app icons
    new_ids = download_itunes.process(bundle_ids)
    # 2. if new apps, update bundle name index & categories
    if bundle_ids == ['*']:
        new_ids = ['*']  # special case needed to force rebuilt index
    if len(new_ids) > 0:
        index_app_names.process(new_ids)  # after download_itunes
        index_categories.process(new_ids)  # after index_app_names
    # 3. re-calculate combined.json
    bundle_combine.process(bundle_ids)
    # 4. re-build indices
    index_rank.process(bundle_ids)  # after bundle_combine & index_app_names
    index_domains.process(bundle_ids)  # after bundle_combine
    # 5. make all html files
    rebuild_html(bundle_ids, inclIApp=len(new_ids) > 0)


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
            bundle_ids = download_itunes.download_missing_icons(force=False)
            if bundle_ids:
                rebuild_html(bundle_ids)
        elif cmd == 'index':
            index_categories.process(['*'], force=True)
            index_rank.process(['*'])
            index_domains.process(['*'])
            rebuild_html()
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
