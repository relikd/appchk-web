#!/usr/bin/env python3

import sys
import time
import math
import common_lib as mylib


def seconds_to_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)


def gen_dom_tags(unsorted_dict, trackers=None, additionalClasses=None):
    sorted_arr = sorted(unsorted_dict, key=lambda x: (-x[1], x[0]))
    txt = ''
    anyMark = False
    for i, (x, y) in enumerate(sorted_arr):
        mark = trackers[x] if trackers else True
        title = x if y == 1 else '{} ({})'.format(x, y)
        txt += '<i{}>{}</i> '.format(' class="trckr"' if mark else '', title)
        anyMark |= mark
    if txt:
        note = '<p class="trckr">known tracker</p>'
        return '<div class="tags{}">{}{}</div>'.format(
            additionalClasses or '', txt, note if anyMark else '')
    else:
        return '<i>– None –</i>'


def gen_dotgraph(count_dict):
    txt = ''
    sorted_count = sorted(count_dict.items(), key=lambda x: (-x[1], x[0]))
    for i, (name, count) in enumerate(sorted_count):
        # TODO: use average not total count
        txt += '<span title="{0} ({1})"><p>{0} ({1})</p>'.format(name, count)
        for x in range(count):
            txt += '<i class="cb{}"></i>'.format(i % 10)
        txt += '</span>'
    return '<div class="dot-graph">{}</div>'.format(txt)


def gen_pie_chart(parts, classes, stroke=0.6):
    size = 1000
    stroke *= size * 0.5
    stroke_p = '{:.0f}'.format(stroke)
    r = (0.99 * size - stroke) / 2
    r_p = '{:.0f},{:.0f}'.format(r, r)
    mid = '{:.0f}'.format(size / 2)

    def arc(deg):
        deg -= 90
        x = r * math.cos(math.pi * deg / 180)
        y = r * math.sin(math.pi * deg / 180)
        return '{:.0f},{:.0f}'.format(size / 2 + x, size / 2 + y)

    txt = ''
    total = 0
    for i, x in enumerate(parts):
        clss = classes[i % len(classes)]
        deg = x * 360
        if x == 0:
            continue
        elif x == 1:
            txt += f'<circle fill="transparent" class="{clss}" stroke-width="{stroke_p}" cx="{mid}" cy="{mid}" r="{r}"/>'
        else:
            txt += f'<path fill="transparent" class="{clss}" stroke-width="{stroke_p}" d="M{arc(total)}A{r_p},0,{1 if deg > 180 else 0},1,{arc(total + deg)}" />'
        total += deg
    return '<svg viewBox="0 0 {0} {0}">{1}</svg>'.format(size, txt)


def gen_radial_graph(obj):
    total = 0
    tracker = 0
    for name, count in obj['total_subdom'].items():
        total += count
        if obj['tracker_subdom'][name]:
            tracker += count
    percent = tracker / total
    return '<div class="pie-chart">{}</div>'.format(
        gen_pie_chart([1 - percent, percent], ['cs0', 'cs1']))


def gen_html(bundle_id, obj):
    track_dom = [(dom, obj['total_subdom'][dom])
                 for dom, known in obj['tracker_subdom'].items() if known]
    return mylib.template_with_base(f'''
<h2>{obj['name']}</h2>
<div id="meta">
  <div class="icons">
    <img src="icon.png" width="100" height="100">
    { gen_radial_graph(obj) }
  </div>
  <table>
    <tr><td>Bundle-id:</td><td class="wrap">{
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
    <tr><td>Last updated:</td><td><time datetime="{
        time.strftime('%Y-%m-%d %H:%M', time.gmtime(obj['last_date']))
    }">{
        time.strftime('%Y-%m-%d, %H:%M', time.gmtime(obj['last_date']))
    }</time></td></tr>
  </table>
</div>
<h3>Connections</h3>
<div>
  <h4>Known Trackers ({ len(track_dom) }):</h4>
  { gen_dom_tags(track_dom, additionalClasses=' trckr') }
  <p></p>

  <h4>Domains:</h4>
  { gen_dotgraph(obj['total_pardom']) }
  { gen_dom_tags(obj['total_pardom'].items(), obj['tracker_pardom']) }

  <h4>Subdomains:</h4>
  { gen_dotgraph(obj['total_subdom']) }
  { gen_dom_tags(obj['total_subdom'].items(), obj['tracker_subdom']) }
</div>''', title=obj['name'])


def make_bundle_out(bundle_id):
    json = mylib.json_read_combined(bundle_id)
    out_dir = mylib.path_out_app(bundle_id)
    needs_update_index = False
    if not mylib.dir_exists(out_dir):
        needs_update_index = True
        mylib.mkdir(out_dir)
    with open(mylib.path_add(out_dir, 'index.html'), 'w') as fp:
        fp.write(gen_html(bundle_id, json))
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
