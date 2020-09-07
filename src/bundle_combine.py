#!/usr/bin/env python3

import os
import sys
import common_lib as mylib
import tracker_download as tracker


level3_doms = None


def dom_in_3rd_domain(needle):
    global level3_doms
    if not level3_doms:
        level3_doms = mylib.read_list('3rd-domains.txt')
    return mylib.bintree_lookup(level3_doms, needle)


def get_parent_domain(subdomain):
    parts = subdomain.split('.')
    if len(parts) < 3:
        return subdomain
    elif dom_in_3rd_domain(parts[-1] + '.' + parts[-2]):
        return '.'.join(parts[-3:])
    else:
        return '.'.join(parts[-2:])


def json_combine(bundle_id):
    def inc_dic(ddic, key, num):
        try:
            ddic[key][1].append(num)
        except KeyError:
            ddic[key] = (tracker.is_tracker(key), [num])

    res = dict({'rec_len': [], 'name': mylib.app_name(bundle_id)})
    pardom = dict()
    subdom = dict()
    latest = 0
    for fname, jdata in mylib.enum_jsons(bundle_id):
        latest = max(latest, os.path.getmtime(fname))  # or getctime
        # if not res['name']:
        #     res['name'] = jdata['app-name']
        res['rec_len'].append(jdata['duration'])
        try:
            logs = jdata['logs']
            uniq_par = dict()
            for subdomain in logs:
                occurs = len(logs[subdomain])
                inc_dic(subdom, subdomain, occurs)
                par_dom = get_parent_domain(subdomain)
                try:
                    uniq_par[par_dom] += occurs
                except KeyError:
                    uniq_par[par_dom] = occurs
            for name, val in uniq_par.items():
                inc_dic(pardom, name, val)
        except KeyError:
            mylib.err('bundle-combine', 'skip: ' + fname)
    res['pardom'] = pardom
    res['subdom'] = subdom
    res['last_date'] = latest
    return res


def process(bundle_ids, where=None):
    print('writing combined json ...')
    if bundle_ids == ['*']:
        bundle_ids = list(mylib.enum_data_appids())

    affected_ids = []
    haystack = sorted([x[::-1] for x in where]) if where else None
    for bid in bundle_ids:
        obj = json_combine(bid)
        should_update = False
        if not haystack:
            should_update = True
        else:
            for x in obj['subdom']:
                if mylib.bintree_lookup(haystack, x[::-1]):
                    should_update = True
                    break
        if should_update:
            print('  ' + bid)
            mylib.json_write_combined(bid, obj)
            affected_ids.append(bid)
    print('')
    return affected_ids


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) > 0:
        process(args)
    else:
        # process(['*'])
        mylib.usage(__file__, '[bundle_id] [...]')
