#!/usr/bin/env python3

import sys
import common_lib as mylib


with open(mylib.path_root('src', '3rd-domains.txt'), 'r') as fp:
    level3_doms = set([x.strip() for x in fp.readlines()])


def dom_in_3rd_domain(needle):
    # TODO: binary tree lookup
    return needle in level3_doms


def get_parent_domain(subdomain):
    parts = subdomain.split('.')
    if len(parts) < 3:
        return x
    elif dom_in_3rd_domain('.'.join(parts[-2:])):
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
    res = dict()
    domA = dict()  # unique sub domains
    domB = dict()  # total sub domains
    domC = dict()  # unique parent domains
    domD = dict()  # total parent domains
    for fname, jdata in mylib.enum_jsons(bundle_id):
        res['name'] = jdata['app-name']
        dict_increment(res, '#rec', 1)
        dict_increment(res, 'rec-total', jdata['duration'])
        try:
            logs = jdata['logs']
            uniq_par = set()
            for subdomain in logs:
                occurs = len(logs[subdomain])
                dict_increment(res, '#logs', occurs)
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
    return res


def process(bundle_ids):
    print('writing combined json ...')
    if bundle_ids == ['*']:
        bundle_ids = list(mylib.enum_appids())
    for bid in bundle_ids:
        print('  ' + bid)
        mylib.json_write_combined(bid, json_combine(bid))
    print('')


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) > 0:
        process(args)
    else:
        # process(['*'])
        mylib.usage(__file__, '[bundle_id] [...]')
