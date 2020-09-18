#!/usr/bin/env python3

import sys
import common_lib as mylib

_reverse_domain_dict = None


def index_fname():
    return mylib.path_data_index('reverse_domains.json')


def load_json_if_not_already():
    global _reverse_domain_dict
    if not _reverse_domain_dict:
        index_file = index_fname()
        if mylib.file_exists(index_file):
            _reverse_domain_dict = mylib.json_read(index_file)
        else:
            _reverse_domain_dict = {'bundle': [], 'pardom': {}, 'subdom': {}}


def write_json_to_disk():
    mylib.json_write(index_fname(), _reverse_domain_dict, pretty=False)


def delete_from_index(bundle_ids, deleteOnly=False):
    global _reverse_domain_dict
    ids_to_delete = set()
    for bid in bundle_ids:
        try:
            i = _reverse_domain_dict['bundle'].index(bid)
        except ValueError:  # index not found
            continue
        ids_to_delete.add(i)
        if deleteOnly:
            _reverse_domain_dict['bundle'][i] = '_'

    if len(ids_to_delete) == 0:
        return False

    for key in ['pardom', 'subdom']:
        for domain in list(_reverse_domain_dict[key].keys()):
            for i in ids_to_delete:
                try:
                    _reverse_domain_dict[key][domain].remove(i)
                except ValueError:  # ignore if not present
                    continue
            if not _reverse_domain_dict[key][domain]:
                del(_reverse_domain_dict[key][domain])
    return True


def insert_in_index(bundle_ids):
    global _reverse_domain_dict
    has_changes = False
    for bid in bundle_ids:
        try:
            i = _reverse_domain_dict['bundle'].index(bid)
        except ValueError:  # index not found
            i = len(_reverse_domain_dict['bundle'])
            _reverse_domain_dict['bundle'].append(bid)
        json, _ = mylib.json_read_evaluated(bid)
        for key in ['pardom', 'subdom']:  # assuming keys are identical
            for domain, _, _ in json[key]:
                try:
                    _reverse_domain_dict[key][domain].append(i)
                except KeyError:
                    _reverse_domain_dict[key][domain] = [i]
                has_changes = True
    return has_changes


def raw():
    load_json_if_not_already()
    return _reverse_domain_dict


def number_of_apps():
    load_json_if_not_already()
    return sum(1 for x in _reverse_domain_dict['bundle'] if x != '_')


def enumerate(key):
    load_json_if_not_already()
    for dom, bundles in _reverse_domain_dict[key].items():
        yield [dom, [_reverse_domain_dict['bundle'][i] for i in bundles]]


def process(bundle_ids, deleteOnly=False):
    print('writing index: reverse domains ...')
    if bundle_ids == ['*']:
        bundle_ids = list(mylib.enum_data_appids())
        print('  full reset')
        mylib.rm_file(index_fname())  # rebuild from ground up

    load_json_if_not_already()
    did_change = delete_from_index(bundle_ids, deleteOnly=deleteOnly)
    if not deleteOnly:
        did_change |= insert_in_index(bundle_ids)
    if did_change:
        write_json_to_disk()
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
