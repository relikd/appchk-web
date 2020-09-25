#!/usr/bin/env python3

import sys
import lib_common as mylib
import bundle_combine  # get_evaluated
import index_app_names


def fname_app_summary():
    return mylib.path_data_index('app_summary.json')


def fname_app_rank():
    return mylib.path_data_index('app_rank.json')


def fname_ranking_list():
    return mylib.path_data_index('ranking_list.json')


def json_to_list(json):
    return [
        json['sum_rec'],  # 0
        json['avg_time'],  # 1
        json['sum_time'],  # 2
        json['avg_logs_pm'],  # 3
        json['sum_logs_pm'],  # 4
        len(json['pardom']),  # 5
        len(json['subdom']),  # 6
        json['tracker_percent'],  # 7
        # v- not part of rank -v
        json['sum_logs'],  # 8
        json['avg_logs'],  # 9
        json['last_date'],  # 10
    ]


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
        total[1] += val[8]
    index['_sum'] = total
    mylib.json_write(fname_app_summary(), index, pretty=False)
    mylib.try_del(index, ['_sum'])


def write_ranking_list(index):
    ret = []
    for bid, values in index.items():
        ret.append([bid, index_app_names.get_name(bid)] + values)
        del(values[8:])
    ret.sort(key=lambda x: -x[2 + 10])  # sort by last update
    # TODO: doesnt scale well, 100'000 apps ~> 12mb
    if len(ret) > 500:  # limit to most recent X entries
        ret = ret[:500]
    # mylib.sort_by_name(ret, 1)
    mylib.json_write(fname_ranking_list(), ret, pretty=False)


def write_rank_index(index):
    mylib.try_del(index, ['_ranks', '_min', '_max'])
    mins = []
    maxs = []
    if len(index) > 0:
        for i in range(8):  # exclude unused columns
            tmp = {}
            # make temporary reverse index
            for bid, val in index.items():
                try:
                    tmp[val[i]].append(bid)
                except KeyError:
                    tmp[val[i]] = [bid]
            # read index position from temp reverse index
            r = 1
            ordered = sorted(tmp.items(), reverse=i in [0, 1, 2])
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
        return mylib.json_safe_read(fname_app_summary(), {})['_sum']
    except KeyError:
        return [0, 0]


def process(bundle_ids, deleteOnly=False):
    print('writing index: meta ...')
    fname = fname_app_summary()
    if bundle_ids == ['*']:
        print('  full reset')
        mylib.rm_file(fname)  # rebuild from ground up

    index = mylib.json_safe_read(fname, {})
    ids = mylib.appids_in_data(bundle_ids)
    write_summary_index(index, ids, deleteOnly=deleteOnly)
    write_ranking_list(index)
    write_rank_index(index)
    print('')


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) > 0:
        process(args)
    else:
        # process(['*'], deleteOnly=False)
        mylib.usage(__file__, '[bundle_id] [...]')
