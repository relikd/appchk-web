#!/usr/bin/env python3

import sys
import lib_common as mylib
import bundle_combine  # get_evaluated
import index_app_names  # get_name

MAX_RANKING_LIMIT = 500


def fname_app_summary():
    return mylib.path_data_index('app_summary.json')


def fname_app_rank():
    return mylib.path_data_index('app_rank.json')


def fname_ranking_all():
    return mylib.path_data_index('rank', 'all.json')


def fname_rank_list(sublist, cid):
    return mylib.path_data_index('rank', sublist, 'id_{}.json'.format(cid))


def make_rank_list_dir(sublist, reset=False):
    pth = mylib.path_data_index('rank', sublist)
    if reset:
        mylib.rm_dir(pth)
    mylib.mkdir(pth)


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


def group_multiple_apps(values_array):
    c = len(values_array)
    asum = [0] * 10
    amin = [float('inf')] * 10
    amax = [0] * 10
    for values in values_array:
        for i in range(10):
            asum[i] += values[i]
            amin[i] = min(amin[i], values[i])
            amax[i] = max(amax[i], values[i])

    def flt(val):
        return int(val * 1000) / 1000
    return [
        # app-count
        c,
        # rec-count (avg, sum)
        flt(asum[0] / c), asum[0],
        # req-count (avg, sum)
        flt(asum[9] / c), asum[8],
        # rec-time (avg, sum)
        int(asum[1] / c), asum[2],
        # req-pm (avg, min, max)
        flt(asum[3] / c), flt(amin[3]), flt(amax[3]),
        # pardom-count (avg, min, max)
        flt(asum[5] / c), amin[5], amax[5],
        # subdom-count (avg, min, max)
        flt(asum[6] / c), amin[6], amax[6],
        # tracker-percent (avg, min, max)
        flt(asum[7] / c), flt(amin[7]), flt(amax[7]),
    ]


def update_summary_index(index, bundle_ids, deleteOnly=False):
    did_change = False
    if deleteOnly:
        did_change = mylib.try_del(index, bundle_ids)
    else:
        for bid in bundle_ids:
            # set new value
            new_value = json_to_list(bundle_combine.get_evaluated(bid))
            try:
                if new_value == index[bid]:
                    continue
            except KeyError:
                pass
            index[bid] = new_value
            did_change = True
    if did_change:
        mylib.try_del(index, ['_sum'])
        total = [0, 0]
        for val in index.values():
            total[0] += val[0]
            total[1] += val[8]
        index['_sum'] = total
        mylib.json_write(fname_app_summary(), index, pretty=False)
        mylib.try_del(index, ['_sum'])
    return did_change


def filter_by_list(index, list_ids, updated_ids):
    if len(list_ids) == 0 or len(updated_ids) == 0:
        return
    if updated_ids != ['*'] and not any(x in list_ids for x in updated_ids):
        return
    c = 0
    for x in index:
        if x[0] in list_ids:
            yield x
            c += 1
            if c >= MAX_RANKING_LIMIT:
                break


def write_ranking_category_list(index, affected_ids):
    make_rank_list_dir('category', reset=affected_ids == ['*'])
    for _, json in mylib.enum_categories():
        ids = [bid for bid, _ in json['apps']]
        ret = list(filter_by_list(index, ids, affected_ids))
        if len(ret) == 0:
            continue
        cid = json['meta'][0]
        mylib.json_write(fname_rank_list('category', cid), ret, pretty=False)


def write_ranking_custom_lists(index, affected_ids):
    make_rank_list_dir('custom', reset=affected_ids == ['*'])
    for list_id, json in mylib.enum_custom_lists('list_'):
        ret = list(filter_by_list(index, json['apps'], affected_ids))
        if len(ret) == 0:
            continue
        mylib.json_write(fname_rank_list('custom', list_id), ret, pretty=False)


def write_ranking_groupby_lists(index, affected_ids):
    make_rank_list_dir('groupby', reset=affected_ids == ['*'])
    for listid, json in mylib.enum_custom_lists('groupby_'):
        ret = []
        anyone = affected_ids == ['*']
        for group in json['groups']:
            arr = []
            for x in index:
                if not anyone and x[0] in affected_ids:
                    anyone = True
                if x[0] in group['apps']:
                    arr.append(x[2:])
            if len(arr) > 0:
                ident = group['name']
                try:
                    url = group['url']
                    ident = [ident, url]
                except KeyError:
                    pass
                ret.append([ident] + group_multiple_apps(arr))
        if len(ret) == 0 or not anyone:
            continue
        mylib.json_write(fname_rank_list('groupby', listid), ret, pretty=False)


def write_ranking_list(index, affected_ids):
    # prepend bundle-id and app name
    ret = [[b, index_app_names.get_name(b)] + v for b, v in index.items()]

    # TODO: return list of updated files
    print('  write group-by lists')
    write_ranking_groupby_lists(ret, affected_ids)

    print('  write custom lists')
    # sort by  %-tracker asc,  #-pardom asc,  avg-req-per-min asc
    ret.sort(key=lambda x: (x[2 + 7], x[2 + 5], x[2 + 3]))
    write_ranking_custom_lists(ret, affected_ids)

    print('  write category lists')
    ret.sort(key=lambda x: -x[2 + 10])  # sort by last update desc
    write_ranking_category_list(ret, affected_ids)
    if len(ret) > MAX_RANKING_LIMIT:  # limit to most recent X entries
        ret = ret[:MAX_RANKING_LIMIT]
    # mylib.sort_by_name(ret, 1)
    print('  write overall list')
    mylib.json_write(fname_ranking_all(), ret, pretty=False)


def write_rank_index(index):
    print('  generate bundle ranks')
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


def save_groupby_list(gid, title, groups, hidden=False):
    base = mylib.path_data('_lists')
    mylib.mkdir(base)
    fname = mylib.path_add(base, f'groupby_{gid}.json')
    json = {'name': title, 'hidden': hidden, 'groups': groups}
    mylib.json_write(fname, json, pretty=False)


def process(bundle_ids, deleteOnly=False):
    print('writing index: ranking ...')
    fname = fname_app_summary()
    if bundle_ids == ['*']:
        print('  full reset')
        mylib.rm_file(fname)  # rebuild from ground up

    index = mylib.json_safe_read(fname, {})
    ids = mylib.appids_in_data(bundle_ids)
    if update_summary_index(index, ids, deleteOnly=deleteOnly):
        write_ranking_list(index, bundle_ids)
        for values in index.values():
            del(values[8:])
        write_rank_index(index)
    print('')


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) > 0:
        process(args)
    else:
        # process(['*'], deleteOnly=False)
        mylib.usage(__file__, '[bundle_id] [...]')
