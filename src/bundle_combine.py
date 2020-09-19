#!/usr/bin/env python3

import os
import re
import sys
import common_lib as mylib
import tracker_download


THRESHOLD_PERCENT_OF_LOGS = 0.33  # domain appears in % recordings
THRESHOLD_MIN_AVG_LOGS = 0.4  # at least x times in total (after %-thresh)

level3_doms = None
re_domain = re.compile(r'[^a-zA-Z0-9.-]')


def dom_in_3rd_domain(needle):
    global level3_doms
    if not level3_doms:
        level3_doms = mylib.read_list('3rd-domains.txt')
    return mylib.bintree_lookup(level3_doms, needle)


def get_parent_domain(subdomain):
    parts = subdomain.split('.')
    if len(parts) < 3:
        return subdomain
    elif parts[-1].isdigit():
        return subdomain  # ip address
    elif dom_in_3rd_domain(parts[-1] + '.' + parts[-2]):
        return '.'.join(parts[-3:])
    else:
        return '.'.join(parts[-2:])


def cleanup_domain_name(domain):
    safe_domain = re_domain.sub('', domain)
    if domain == safe_domain:
        return domain
    mylib.err('bundle-combine', 'invalid character in domain name: ' + domain)
    without_null = domain.replace('(null)', '')
    if domain != without_null:
        return cleanup_domain_name(without_null)
    return safe_domain


def json_combine(bundle_id):
    def inc_dic(ddic, key, num):
        try:
            ddic[key][1].append(num)
        except KeyError:
            ddic[key] = (tracker_download.is_tracker(key), [num])

    res = {'rec_len': []}
    pardom = {}
    subdom = {}
    latest = 0
    for fname, jdata in mylib.enum_jsons(bundle_id):
        # TODO: load combined and append newest only, then update evaluated
        latest = max(latest, os.path.getmtime(fname))  # or getctime
        res['rec_len'].append(jdata['duration'])
        try:
            logs = jdata['logs']
            uniq_par = {}
            for subdomain in logs:
                occurs = len(logs[subdomain])
                subdomain = cleanup_domain_name(subdomain)
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


def json_evaluate_inplace(obj):
    rec_count = len(obj['rec_len'])
    time_total = sum(obj['rec_len'])
    del(obj['rec_len'])
    obj['sum_rec'] = rec_count
    obj['sum_logs'] = sum([sum(x[1]) for x in obj['pardom'].values()])
    obj['sum_logs_pm'] = obj['sum_logs'] / (time_total or 1) * 60
    obj['sum_time'] = time_total
    obj['avg_time'] = time_total / rec_count

    def transform(ddic):
        res = []
        c_sum = 0
        c_trkr = 0
        for name, (is_tracker, counts) in ddic.items():
            rec_percent = len(counts) / rec_count
            if rec_percent < THRESHOLD_PERCENT_OF_LOGS:
                continue
            avg = sum(counts) / rec_count  # len(counts)
            if avg < THRESHOLD_MIN_AVG_LOGS:
                continue
            res.append([name, round(avg + 0.001), is_tracker])
            c_sum += avg
            c_trkr += avg if is_tracker else 0
        res.sort(key=lambda x: (-x[1], x[0]))  # sort by count desc, then name
        return res, c_trkr, c_sum

    obj['pardom'], p_t, p_c = transform(obj['pardom'])
    obj['subdom'], s_t, s_c = transform(obj['subdom'])
    obj['tracker_percent'] = s_t / (s_c or 1)
    obj['avg_logs'] = s_c
    obj['avg_logs_pm'] = s_c / (obj['avg_time'] or 1) * 60


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
            json_evaluate_inplace(obj)
            mylib.json_write_evaluated(bid, obj)
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
