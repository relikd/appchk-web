#!/usr/bin/env python3

import sys
import lib_common as mylib
import lib_graphs as Graph
import lib_html as HTML
import bundle_combine  # get_evaluated, fname_evaluated
import index_app_names  # get_name
import index_categories  # get_categories


def trkr_if(flag):
    return ' class="trckr"' if flag else ''


def domain_w_count(domain, count):
    if count > 1:
        return '{} ({})'.format(domain, count)
    return domain


def gen_dom_tags(sorted_arr, fn_a_html, onlyTrackers=False):
    src = ''
    anyMark = False
    for name, count, mark in sorted_arr:
        anyMark |= mark
        src += fn_a_html(name, domain_w_count(name, count),
                         attr_str=trkr_if(mark and not onlyTrackers)) + ' '
    if src:
        if anyMark:
            src += '<p class="trckr">* Potential trackers are highlighted</p>'
        clss = ' trckr' if onlyTrackers else ''
        return f'<div class="tags{clss}">{src}</div>'
    else:
        return '<i>– None –</i>'


def gen_dotgraph(arr):
    return Graph.dotgraph([(domain_w_count(title, num), num, trkr_if(f))
                           for title, num, f in arr])


def stat(col, title, ident, value, optional=None):
    return Graph.rank_tile(title, value, optional, {
        'id': ident, 'class': 'col' + str(col)})


def gen_page(bundle_id, obj):

    def round_num(num):
        return format(num, '.1f')  # .rstrip('0').rstrip('.')

    def as_pm(value):
        return round_num(value) + '/min'

    def as_percent(value):
        return round_num(value * 100) + '%'

    def seconds_to_time(seconds):
        seconds = int(seconds)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)

    name = index_app_names.get_name(bundle_id)
    gernes = index_categories.get_categories(bundle_id)
    obj['tracker'] = list(filter(lambda x: x[2], obj['subdom']))

    HTML.write(mylib.path_out_app(bundle_id), f'''
<h2 class="title">{name}</h2>
<p class="subtitle snd"><i class="mg_lr">Bundle-id:</i>{ bundle_id }</p>
<div id="meta">
  <div class="icons">
    { Graph.pie_chart_tracker(obj['tracker_percent']) }
    <img class="app-icon" src="icon.png" alt="app-icon" width="100" height="100">
  </div>
  <table>
    <tr><td>App Categories:</td><td>{
      ', '.join([HTML.a_category(i, name) for i, name in gernes])
    }</td></tr>
    <tr><td>Last Update:</td><td>{HTML.date_utc(obj['last_date'])}</td></tr>
  </table>
</div>
<div id="stats">
  { stat(1, 'Number of recordings:', 'sum_rec', obj['sum_rec']) }
  { stat(1, 'Average recording time:', 'avg_time', seconds_to_time(obj['avg_time'])) }
  { stat(2, 'Cumulative recording time:', 'sum_time', seconds_to_time(obj['sum_time'])) }
  { stat(1, 'Average number of requests:', 'avg_logs_pm', round_num(obj['avg_logs']), as_pm(obj['avg_logs_pm'])) }
  { stat(2, 'Total number of requests:', 'sum_logs_pm', str(obj['sum_logs']), as_pm(obj['sum_logs_pm'])) }
  { stat(1, 'Number of domains:', 'pardom', len(obj['pardom'])) }
  { stat(2, 'Number of subdomains:', 'subdom', len(obj['subdom'])) }
  { stat(3, 'Tracker percentage:', 'tracker_percent', as_percent(obj['tracker_percent'])) }
</div>
<h3>Connections</h3>
<div>
  <h4>Potential Trackers ({ len(obj['tracker']) }):</h4>
  { gen_dom_tags(obj['tracker'], HTML.a_subdomain, onlyTrackers=True) }
  <h4>Domains ({ len(obj['pardom']) }):</h4>
  { gen_dotgraph(obj['pardom']) }
  { gen_dom_tags(obj['pardom'], HTML.a_domain) }
  <h4>Subdomains ({ len(obj['subdom']) }):</h4>
  { gen_dotgraph(obj['subdom']) }
  { gen_dom_tags(obj['subdom'], HTML.a_subdomain) }
</div>
{ HTML.p_download_json('data.json', bundle_id + '.json') }
<script type="text/javascript" src="/static/lookup-rank.js"></script>
<script type="text/javascript">
  lookup_rank_js('{bundle_id}');
</script>''', title=name)


def process(bundle_ids):
    print('generating html: apps ...')
    i = 0
    for bid in mylib.appids_in_out(bundle_ids):
        gen_page(bid, bundle_combine.get_evaluated(bid))
        mylib.symlink(bundle_combine.fname_evaluated(bid),
                      mylib.path_out_app(bid, 'data.json'))
        mylib.printf('  .' if i == 0 else '.')
        i = (i + 1) % 50
        if i == 0:
            print('')  # close printf
    print('')  # close printf
    print('')


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) > 0:
        process(args)
    else:
        # process(['*'])
        mylib.usage(__file__, '[bundle_id] [...]')
