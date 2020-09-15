#!/usr/bin/env python3

import os
import sys
import time
import math
import common_lib as mylib
import index_bundle_names


def seconds_to_time(seconds):
    seconds = int(seconds)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)


def round_num(num):
    return format(num, '.1f')  # .rstrip('0').rstrip('.')


def gen_dotgraph(sorted_arr):
    txt = ''
    for name, count, mark in sorted_arr:
        title = '{} ({})'.format(name, count) if count > 1 else name
        clss = ' class="trckr"' if mark else ''
        txt += '<span{0} title="{1}"><p>{1}</p>'.format(clss, title)
        txt += '<i></i>' * count
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
    return '<svg viewBox="0 0 {0} {0}" width="100" height="100">{1}</svg>'.format(size, txt)


def gen_radial_graph(percent):
    return '<div class="pie-chart">{}</div>'.format(
        gen_pie_chart([1 - percent, percent], ['cs0', 'cs1']))


def gen_dom_tags(sorted_arr, onlyTrackers=False):
    txt = ''
    anyMark = False
    for i, (name, count, mark) in enumerate(sorted_arr):
        title = '{} ({})'.format(name, count) if count > 1 else name
        clss = ' class="trckr"' if mark and not onlyTrackers else ''
        txt += '<i{}>{}</i> '.format(clss, title)
        anyMark |= mark
    if txt:
        note = '<p class="trckr">* Potential trackers are highlighted</p>'
        return '<div class="{}tags">{}{}</div>'.format(
            'trckr ' if onlyTrackers else '', txt, note if anyMark else '')
    else:
        return '<i>– None –</i>'


def gen_html(bundle_id, obj):
    name = index_bundle_names.get_name(bundle_id)
    obj['tracker'] = list(filter(lambda x: x[2], obj['subdom']))
    return mylib.template_with_base(f'''
<h2 class="title">{name}</h2>
<p class="subtitle snd"><i class="mg_lr">Bundle-id:</i>{ bundle_id }</p>
<div id="meta">
  <div class="icons">
    <img src="icon.png" width="100" height="100">
    { gen_radial_graph(obj['tracker_percent']) }
  </div>
  <table>
    <tr><td>Last update:</td><td><time datetime="{
        time.strftime('%Y-%m-%d %H:%M', time.gmtime(obj['last_date']))
    }">{
        time.strftime('%Y-%m-%d, %H:%M', time.gmtime(obj['last_date']))
    }</time></td></tr>
    <tr><td>Number of recordings:</td><td>{ obj['sum_rec'] }</td></tr>
    <tr><td>Total number of requests:</td><td>{
        obj['sum_logs'] }<i class="snd mg_lr">({
            round_num(obj['sum_logs_pm'])} / min)</i></td></tr>
    <tr><td>Average number of requests:</td><td>{
        round_num(obj['avg_logs'])}<i class="snd mg_lr">({
            round_num(obj['avg_logs_pm'])} / min)</i></td></tr>
    <tr><td>Average recording time:</td><td>{
        seconds_to_time(obj['avg_time']) }</td></tr>
    <tr><td>Cumulative recording time:</td><td>{
        seconds_to_time(obj['sum_time']) }</td></tr>
  </table>
</div>
<h3>Connections</h3>
<div>
  <h4>Potential Trackers ({ len(obj['tracker']) }):</h4>
  { gen_dom_tags(obj['tracker'], onlyTrackers=True) }
  <p></p>

  <h4>Overlapping Domains ({ len(obj['pardom']) }):</h4>
  { gen_dotgraph(obj['pardom']) }
  { gen_dom_tags(obj['pardom']) }

  <h4>Overlapping Subdomains ({ len(obj['subdom']) }):</h4>
  { gen_dotgraph(obj['subdom']) }
  { gen_dom_tags(obj['subdom']) }
</div>
<p class="right snd">Download: <a href="data.json" download="{bundle_id}.json">json</a></p>''', title=name)


def process(bundle_ids):
    print('generating html pages ...')
    if bundle_ids == ['*']:
        bundle_ids = list(mylib.enum_appids())

    for bid in bundle_ids:
        print('  ' + bid)
        json, json_data_path = mylib.json_read_evaluated(bid)
        mylib.mkdir_out_app(bid)
        with open(mylib.path_out_app(bid, 'index.html'), 'w') as fp:
            fp.write(gen_html(bid, json))
        download_link = mylib.path_out_app(bid, 'data.json')
        if not mylib.file_exists(download_link):
            os.symlink(json_data_path, download_link)
    print('')


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) > 0:
        process(args)
    else:
        # process(['*'])
        mylib.usage(__file__, '[bundle_id] [...]')
