#!/usr/bin/env python3

import sys
import lib_common as mylib
import bundle_combine  # get_evaluated
import download_tracker  # is_tracker


def fname_all():
    return mylib.path_data_index('domains_all.json')


def fname_tracker():
    return mylib.path_data_index('domains_tracker.json')


def fname_no_tracker():
    return mylib.path_data_index('domains_no_tracker.json')


def fname_dom_subdoms():
    return mylib.path_data_index('domains_subdomains.json')


def load_json_from_disk(index_file):
    return mylib.json_safe_read(
        index_file, fallback={'bundle': [], 'pardom': {}, 'subdom': {}})


def loadAll():
    return load_json_from_disk(fname_all())


def loadTracker():
    return load_json_from_disk(fname_tracker())


def loadNonTracker():
    return load_json_from_disk(fname_no_tracker())


def delete_from_index(index, bundle_ids, deleteOnly=False):
    ids_to_delete = set()
    for bid in bundle_ids:
        try:
            i = index['bundle'].index(bid)
        except ValueError:  # index not found
            continue
        ids_to_delete.add(i)
        if deleteOnly:
            index['bundle'][i] = '_'

    if len(ids_to_delete) == 0:
        return False

    for key in ['pardom', 'subdom']:
        for domain in list(index[key].keys()):
            for i in ids_to_delete:
                try:
                    index[key][domain].remove(i)
                except ValueError:  # ignore if not present
                    continue
            if not index[key][domain]:
                del(index[key][domain])
    return True


def insert_in_index(index, bundle_ids):
    has_changes = False
    for bid in bundle_ids:
        try:
            i = index['bundle'].index(bid)
        except ValueError:  # index not found
            i = len(index['bundle'])
            index['bundle'].append(bid)
        json = bundle_combine.get_evaluated(bid)
        for key in ['pardom', 'subdom']:  # assuming keys are identical
            for domain, _, is_trkr in json[key]:
                try:
                    index[key][domain].append(i)
                except KeyError:
                    index[key][domain] = [is_trkr, i]
                has_changes = True
    return has_changes


def split_trackers(index):
    ret = {'trkr': {'bundle': index['bundle'], 'subdom': {}, 'pardom': {}},
           'no-trkr': {'bundle': index['bundle'], 'subdom': {}, 'pardom': {}}}

    is_par_trkr = {}
    for domain, [is_trkr, *ids] in index['pardom'].items():
        is_par_trkr[domain] = is_trkr
        if is_trkr:
            ret['trkr']['pardom'][domain] = ids

    for domain, [is_trkr, *ids] in index['subdom'].items():
        key = 'trkr' if is_trkr else 'no-trkr'
        ret[key]['subdom'][domain] = ids
        pardom = mylib.parent_domain(domain)
        if is_par_trkr[pardom]:
            continue
        try:
            ret[key]['pardom'][pardom].update(ids)
        except KeyError:
            ret[key]['pardom'][pardom] = set(ids)
    for dic in ret.values():
        for dom, ids in dic['pardom'].items():
            dic['pardom'][dom] = list(ids)
    return ret['trkr'], ret['no-trkr']


def filter_list_at_least(index, min_count):
    sub = {}
    par = {}
    for domain, ids in index['subdom'].items():
        if len(ids) >= min_count:
            sub[domain] = ids
    for domain, ids in index['pardom'].items():
        if len(ids) >= min_count:
            par[domain] = ids
    index['subdom'] = sub
    index['pardom'] = par


def dict_dom_subdomains(index):
    ret = {}
    for subdomain in index['subdom'].keys():
        pardom = mylib.parent_domain(subdomain)
        host = subdomain[:-len(pardom) - 1]  # - '.'
        try:
            ret[pardom].append(host)
        except KeyError:
            ret[pardom] = [host]
    return ret


def number_of_apps(index):
    return sum(1 for x in index['bundle'] if x != '_')


def enrich_with_bundle_ids(index):
    for key in ['pardom', 'subdom']:
        for dom, ids in index[key].items():
            index[key][dom] = [index['bundle'][i] for i in ids]


def all_bundles_containing(list_of_domains):
    affected = set()
    json = load_json_from_disk(fname_all())
    haystack = sorted([x[::-1] for x in list_of_domains])
    for key in ['pardom', 'subdom']:
        for dom, ids in json[key].items():
            if mylib.bintree_lookup(haystack, dom[::-1]):
                affected.update(ids)
    return [json['bundle'][i] for i in affected]


def process(bundle_ids, deleteOnly=False):
    print('writing index: domains ...')
    fname = fname_all()
    if bundle_ids == ['*']:
        print('  full reset')
        mylib.rm_file(fname)  # rebuild from ground up

    index = load_json_from_disk(fname)
    ids = mylib.appids_in_data(bundle_ids)
    did_change = delete_from_index(index, ids, deleteOnly=deleteOnly)
    if not deleteOnly:
        did_change |= insert_in_index(index, ids)
    if did_change:
        mylib.json_write(fname, index, pretty=False)
        dict_trkr, dict_no_trkr = split_trackers(index)
        mylib.json_write(fname_tracker(), dict_trkr, pretty=False)
        filter_list_at_least(dict_no_trkr, 5)  # or 0.1 * len(ids)
        mylib.json_write(fname_no_tracker(), dict_no_trkr, pretty=False)
        mylib.json_write(fname_dom_subdoms(), dict_dom_subdomains(index),
                         pretty=False)

    else:
        print('  no change')
    print('')


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) > 0:
        process(args)
    else:
        # process(['*'], deleteOnly=False)
        mylib.usage(__file__, '[bundle_id] [...]')
