#!/usr/bin/env python3

import os
import sys
import timeit
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')  # disable interactive mode


def split_arr(arr):
    arr.sort(key=lambda x: -x[1])
    ret = []
    while len(arr) > 0:
        ret.append(arr[0])
        del(arr[0])
        if len(arr) > 0:
            ret.append(arr[-1])
            del(arr[-1])
    return [x[0] for x in ret], [x[1] for x in ret]


def gen_graph(arr, outfile):
    keys, vals = split_arr(arr)
    pie1, _ = plt.pie(vals, labels=keys, colors=['#AAA', '#444'], normalize=True)
    plt.setp(pie1, width=0.5)
    plt.subplots_adjust(left=0, right=1, top=0.7, bottom=0.3)
    plt.savefig(outfile, bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close()


def test(times, value):
    ret = []
    for x, y in [
        ('index_app_names', f"['{value}']"),
        ('index_categories', f"['{value}']"),
        ('bundle_combine', f"['{value}']"),
        ('index_rank', f"['{value}']"),
        ('index_domains', f"['{value}']"),
        ('html_bundle', f"['{value}']"),
        ('html_categories', ''),
        ('html_index_apps', ''),
        ('html_ranking', ''),
        ('html_group_compare', ''),
        ('html_index_domains', ''),
        ('html_root', '1, 1, inclStatic=True')
    ]:
        sys.stdout = open(os.devnull, 'w')
        t = timeit.timeit(f'process({y})',
                          setup=f'from {x} import process',
                          number=times) / times
        sys.stdout = sys.__stdout__
        print(f"('{x}', {t}),")
        ret.append((x, t))
    return ret


pre_calc = [  # 1.7468616582500003
    ('index_app_names', 0.05087930704999999),
    ('index_categories', 0.03988175075),
    ('bundle_combine', 0.89672237075),
    ('index_rank', 0.09671105084999994),
    ('index_domains', 0.08596107025000013),
    ('html_bundle', 0.23503021030000007),
    ('html_categories', 0.10772542440000006),
    ('html_index_apps', 0.014855155450000091),
    ('html_ranking', 0.04087204415000016),
    ('html_group_compare', 0.004021174899999735),
    ('html_index_domains', 0.04882671115000008),
    ('html_root', 0.12537538825),
]
post_calc = [  # 0.5836890604499999
    ('index_app_names', 0.0006852585000000022),
    ('index_categories', 0.0008334453500000005),
    ('bundle_combine', 0.0136475935),
    ('index_rank', 0.0012115025499999988),
    ('index_domains', 0.0800649297),
    ('html_bundle', 0.002384871350000006),
    ('html_categories', 0.15204053159999997),
    ('html_index_apps', 0.020598785899999993),
    ('html_ranking', 0.059948232549999994),
    ('html_group_compare', 0.004277908699999999),
    ('html_index_domains', 0.06897567679999997),
    ('html_root', 0.17902032395000003),
]
# gen_graph(pre_calc, 'times.svg')
# result = pre_calc
result = test(20, '*')
# result = test(20, 'com.amazon.AmazonDE')
print('pre_calc', sum([x for _, x in pre_calc]))
print('measure ', sum([x for _, x in result]))
gen_graph(result, 'times.svg')
# result1 = test(10, '*')
# result2 = test(10, 'com.amazon.AmazonDE')
# a = sum([x for _, x in result1])
# b = sum([x for _, x in result2])
# result2.append((' ', a - b))
# gen_graph(result1, 'times1.svg')
# gen_graph(result2, 'times2.svg')
