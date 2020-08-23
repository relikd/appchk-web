#!/usr/bin/env python3

import sys
import common_lib as mylib
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg')  # disable interactive mode


def sort_dict(count_dict):
    sorted_count = sorted(count_dict.items(), key=lambda x: (-x[1], x[0]))
    names = ['{} ({})'.format(*x) for x in sorted_count]
    sizes = [x[1] for x in sorted_count]
    return names, sizes


def gen_graph(count_dict, outfile):
    names, sizes = sort_dict(count_dict)
    pie1, _ = plt.pie(sizes, labels=names)
    plt.setp(pie1, width=0.5, edgecolor='white')
    plt.subplots_adjust(left=0, right=1, top=0.7, bottom=0.3)
    plt.savefig(outfile, bbox_inches='tight', pad_inches=0)  # transparent=True
    plt.close()


def seconds_to_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)


def gen_domain_tags(unsorted_dict):
    for x in sorted(unsorted_dict):
        yield '<i>{}</i>'.format(x)


def gen_html(bundle_id, obj):
    return mylib.template_with_base(f'''
<h2>{obj['name']}</h2>
<div id="meta">
  <table>
    <tr><td>Bundle-id:</td><td>{
        bundle_id
    }</td></tr>
    <tr><td>Number of recordings:</td><td>{
        obj['#rec']
    }</td></tr>
    <tr><td>Total number of logs:</td><td>{
        obj['#logs']
    }</td></tr>
    <tr><td>Cumulative recording time:</td><td>{
        seconds_to_time(obj['rec-total'])
    }</td></tr>
    <tr><td>Average recording time:</td><td>{
         round(obj['rec-total'] / obj['#rec'], 1)
    } s</td></tr>
  </table>
</div>
<h3>Connections</h3>
<div id="connections">
  <table>
    <tr><td>Domains:</td><td>{
        ''.join(gen_domain_tags(obj['uniq_pardom']))
    }</td></tr>
    <tr><td>Subdomains:</td><td>{
        ''.join(gen_domain_tags(obj['uniq_subdom']))
    }</td></tr>
    <tr><td>Known Trackers:</td><td>{
        '...'
    }</td></tr>
  </table>
  <figure><img src="par.svg"></figure>
  <figure><img src="sub.svg"></figure>
</div>''', title=obj['name'])


def make_bundle_out(bundle_id):
    jdata = mylib.json_read_combined(bundle_id)
    out_dir = mylib.path_out_app(bundle_id)
    needs_update_index = False
    if not mylib.dir_exists(out_dir):
        needs_update_index = True
        mylib.mkdir(out_dir)
    try:
        gen_graph(jdata['total_subdom'], mylib.path_add(out_dir, 'sub.svg'))
        gen_graph(jdata['total_pardom'], mylib.path_add(out_dir, 'par.svg'))
    except KeyError:
        mylib.err('bundle-generate-page', 'skip: ' + bundle_id)

    with open(mylib.path_add(out_dir, 'index.html'), 'w') as fp:
        fp.write(gen_html(bundle_id, jdata))
    return needs_update_index


def process(bundle_ids):
    print('generating html pages ...')
    if bundle_ids == ['*']:
        bundle_ids = list(mylib.enum_appids())

    ids_new_in_index = set()
    for bid in bundle_ids:
        print('  ' + bid)
        if make_bundle_out(bid):
            ids_new_in_index.add(bid)
    print('')
    return ids_new_in_index


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) > 0:
        process(args)
    else:
        # process(['*'])
        mylib.usage(__file__, '[bundle_id] [...]')
