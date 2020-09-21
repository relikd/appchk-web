#!/usr/bin/env python3

import sys
import time
import math
import common_lib as mylib
import download_itunes  # get_genres
import bundle_combine  # get_evaluated, fname_evaluated
import index_app_names  # get_name
import index_meta  # get_rank


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
    return gen_pie_chart([1 - percent, percent], ['cs0', 'cs1'])


def gen_dom_tags(sorted_arr, isSub, onlyTrackers=False):
    txt = ''
    anyMark = False
    for i, (name, count, mark) in enumerate(sorted_arr):
        title = '{} ({})'.format(name, count) if count > 1 else name
        clss = ' class="trckr"' if mark and not onlyTrackers else ''
        txt += '<a{} href="/{}/#{}">{}</a> '.format(
            clss, 'subdomain' if isSub else 'domain', name, title)
        anyMark |= mark
    if txt:
        note = '<p class="trckr">* Potential trackers are highlighted</p>'
        return '<div class="{}tags">{}{}</div>'.format(
            'trckr ' if onlyTrackers else '', txt, note if anyMark else '')
    else:
        return '<i>– None –</i>'


def gen_html(bundle_id, obj):

    def round_num(num):
        return format(num, '.1f')  # .rstrip('0').rstrip('.')

    def as_pm(value):
        return round_num(value) + '/min'

    def as_percent(value):
        return round_num(value * 100) + '%'

    def as_date(value):
        return '<time datetime="{}">{} UTC</time>'.format(
            time.strftime('%Y-%m-%d %H:%M', time.gmtime(value)),
            time.strftime('%Y-%m-%d, %H:%M', time.gmtime(value))
        )

    def seconds_to_time(seconds):
        seconds = int(seconds)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)

    def stat(col, title, rank, value, optional=None, fmt=str, fmt2=None):
        # percent = int(rank[0] / max_rank * 100)
        r = rank[0] / max_rank
        detail = fmt2(value) if fmt2 else fmt(value)
        if optional:
            x = fmt(optional) if fmt2 else optional
            detail += '<i class="snd mg_lr">({})</i>'.format(x)
        return f'''
<div class="col{col}">
  <h4>{title}</h4>
  <div class="percentile {'g' if r < 0.5 else 'b'}"><div style="left: {as_percent(r)}"></div></div>
  <b class="mg_lr">{detail}</b>
  <p class="snd">
    Rank:&nbsp;<b>{rank[0]}</b>,
    best:&nbsp;<i>{fmt(rank[1])}</i>,
    worst:&nbsp;<i>{fmt(rank[2])}</i></p>
</div>'''

    name = index_app_names.get_name(bundle_id)
    gernes = download_itunes.get_genres(bundle_id)
    rank, max_rank = index_meta.get_rank(bundle_id)
    obj['tracker'] = list(filter(lambda x: x[2], obj['subdom']))
    return mylib.template_with_base(f'''
<h2 class="title">{name}</h2>
<p class="subtitle snd"><i class="mg_lr">Bundle-id:</i>{ bundle_id }</p>
<div id="meta">
  <div class="icons">
    { gen_radial_graph(obj['tracker_percent']) }
    <img class="app-icon" src="icon.png" alt="app-icon" width="100" height="100">
  </div>
  <table>
    <tr><td>App Categories:</td><td>{
      ', '.join([name for i, name in gernes])
    }</td></tr>
    <tr><td>Last Update:</td><td>{as_date(obj['last_date'])}</td></tr>
  </table>
</div>
<div id="stats">
  { stat(1, 'Number of recordings:', rank['sum_rec'], obj['sum_rec']) }
  { stat(1, 'Average recording time:', rank['avg_time'], obj['avg_time'], fmt=seconds_to_time) }
  { stat(2, 'Cumulative recording time:', rank['sum_time'], obj['sum_time'], fmt=seconds_to_time) }
  { stat(1, 'Average number of requests:', rank['avg_logs_pm'], obj['avg_logs'], obj['avg_logs_pm'], fmt=as_pm, fmt2=round_num) }
  { stat(2, 'Total number of requests:', rank['sum_logs_pm'], obj['sum_logs'], obj['sum_logs_pm'], fmt=as_pm, fmt2=str) }
  { stat(1, 'Number of domains:', rank['pardom'], len(obj['pardom'])) }
  { stat(2, 'Number of subdomains:', rank['subdom'], len(obj['subdom'])) }
  { stat(3, 'Tracker percentage:', rank['tracker_percent'], obj['tracker_percent'], fmt=as_percent) }
</div>
<h3>Connections</h3>
<div>
  <h4>Potential Trackers ({ len(obj['tracker']) }):</h4>
  { gen_dom_tags(obj['tracker'], isSub=True, onlyTrackers=True) }
  <h4>Domains ({ len(obj['pardom']) }):</h4>
  { gen_dotgraph(obj['pardom']) }
  { gen_dom_tags(obj['pardom'], isSub=False) }
  <h4>Subdomains ({ len(obj['subdom']) }):</h4>
  { gen_dotgraph(obj['subdom']) }
  { gen_dom_tags(obj['subdom'], isSub=True) }
</div>
<p class="right snd">Download: <a href="data.json" download="{bundle_id}.json">json</a></p>''', title=name)


def process(bundle_ids):
    print('generating html: apps ...')
    for bid in mylib.appids_in_out(bundle_ids):
        print('  ' + bid)
        mylib.mkdir_out_app(bid)
        json = bundle_combine.get_evaluated(bid)
        with open(mylib.path_out_app(bid, 'index.html'), 'w') as fp:
            fp.write(gen_html(bid, json))
        mylib.symlink(bundle_combine.fname_evaluated(bid),
                      mylib.path_out_app(bid, 'data.json'))
    print('')


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) > 0:
        process(args)
    else:
        # process(['*'])
        mylib.usage(__file__, '[bundle_id] [...]')
