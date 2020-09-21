#!/usr/bin/env python3

import sys
import common_lib as mylib
import bundle_combine  # get_evaluated

_rank_dict = None


def fname_app_summary():
    return mylib.path_data_index('app_summary.json')


def fname_app_rank():
    return mylib.path_data_index('app_rank.json')


def load_json_from_disk(fname):
    return mylib.json_read(fname) if mylib.file_exists(fname) else {}


def json_to_list(json):
    return [
        json['sum_rec'],
        json['sum_logs'],
        json['sum_logs_pm'],
        json['sum_time'],
        json['avg_logs'],
        json['avg_logs_pm'],
        json['avg_time'],
        json['last_date'],
        len(json['pardom']),
        len(json['subdom']),
        json['tracker_percent']
    ]


def list_to_json(list):
    return {
        'sum_rec': list[0],
        'sum_logs': list[1],
        'sum_logs_pm': list[2],
        'sum_time': list[3],
        'avg_logs': list[4],
        'avg_logs_pm': list[5],
        'avg_time': list[6],
        'last_date': list[7],
        'pardom': list[8],
        'subdom': list[9],
        'tracker_percent': list[10]
    }


def write_summary_index(index, bundle_ids, deleteOnly=False):
    for bid in bundle_ids:
        # delete old value
        mylib.try_del(index, [bid])
        if deleteOnly:
            continue
        # set new value
        index[bid] = json_to_list(bundle_combine.get_evaluated(bid))

    # sum of counts
    mylib.try_del(index, ['_sum'])
    total = [0, 0]
    for val in index.values():
        total[0] += val[0]
        total[1] += val[1]
    index['_sum'] = total
    mylib.json_write(fname_app_summary(), index, pretty=False)


def write_rank_index(index):
    mylib.try_del(index, ['_sum', '_ranks', '_min', '_max'])
    mins = []
    maxs = []
    if len(index) > 0:
        for i in range(11):  # equal to number of array entries
            tmp = {}
            # make temporary reverse index
            for bid, val in index.items():
                try:
                    tmp[val[i]].append(bid)
                except KeyError:
                    tmp[val[i]] = [bid]
            # read index position from temp reverse index
            r = 1
            ordered = sorted(tmp.items(), reverse=i in [0, 3, 6, 7])
            for idx, (_, ids) in enumerate(ordered):
                for bid in ids:
                    index[bid][i] = r
                r += len(ids)
            mins.append(ordered[0][0])
            maxs.append(ordered[-1][0])
    index['_ranks'] = len(index)
    index['_min'] = mins
    index['_max'] = maxs
    mylib.json_write(fname_app_rank(), index, pretty=False)


def get_total_counts():
    try:
        return load_json_from_disk(fname_app_summary())['_sum']
    except KeyError:
        return [0, 0]


def get_rank(bundle_id):
    ''' Return tuples with (rank, max_rank, min_value, max_value) '''
    global _rank_dict
    if not _rank_dict:
        _rank_dict = load_json_from_disk(fname_app_rank())
    return list_to_json(list(zip(
        _rank_dict[bundle_id],
        _rank_dict['_min'],
        _rank_dict['_max'],
    ))), _rank_dict['_ranks']


def process(bundle_ids, deleteOnly=False):
    print('writing index: meta ...')
    fname = fname_app_summary()
    if bundle_ids == ['*']:
        print('  full reset')
        mylib.rm_file(fname)  # rebuild from ground up

    index = load_json_from_disk(fname)
    ids = mylib.appids_in_data(bundle_ids)
    write_summary_index(index, ids, deleteOnly=deleteOnly)
    write_rank_index(index)
    print('')


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) > 0:
        process(args)
    else:
        # process(['*'], deleteOnly=False)
        mylib.usage(__file__, '[bundle_id] [...]')
