#!/usr/bin/env python3

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


def dict_increment(ddic, key, num):
    try:
        ddic[key]
    except KeyError:
        ddic[key] = 0
    ddic[key] += num


def json_combine(bundle_id):
    res = dict({'#rec': 0, '#logs': 0})
    domA = dict()  # unique sub domains
    domB = dict()  # total sub domains
    domC = dict()  # unique parent domains
    domD = dict()  # total parent domains
    for fname, jdata in mylib.enum_jsons(bundle_id):
        res['name'] = jdata['app-name']
        res['#rec'] += 1
        dict_increment(res, 'rec-total', jdata['duration'])
        try:
            logs = jdata['logs']
            uniq_par = set()
            for subdomain in logs:
                occurs = len(logs[subdomain])
                sub_tracker = tracker.is_tracker(subdomain)
                res['#logs'] += 1
                dict_increment(domA, subdomain, 1)
                dict_increment(domB, subdomain, occurs)
                par_dom = get_parent_domain(subdomain)
                uniq_par.add(par_dom)
                dict_increment(domD, par_dom, occurs)
            for par in uniq_par:
                dict_increment(domC, par, 1)
        except KeyError:
            mylib.err('bundle-combine', 'skip: ' + fname)
    res['uniq_subdom'] = domA
    res['uniq_pardom'] = domC
    res['total_subdom'] = domB
    res['total_pardom'] = domD
    sub_tracker = dict()
    par_tracker = dict()
    for x in domA:
        sub_tracker[x] = tracker.is_tracker(x)
    for x in domC:
        par_tracker[x] = tracker.is_tracker(x)
    res['tracker_subdom'] = sub_tracker
    res['tracker_pardom'] = par_tracker
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
            for x in obj['uniq_subdom']:
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
