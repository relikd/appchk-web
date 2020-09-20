#!/usr/bin/env python3

import common_lib as mylib
import index_app_names
import index_domains
import index_meta


def a_app(bundle_id):
    return '<a href="/app/{}/">{}</a>'.format(
        bundle_id, index_app_names.get_name(bundle_id))


def a_dom(domain, key):
    return '<a href="/{0}/#{1}">{1}</a>'.format(key, domain)


def div_dom(domain, count, key):
    return '{} <span>found in {} {}</span>'.format(
        a_dom(domain, key), count, 'apps' if count > 1 else 'app')


def dropdown_choose(button):
    return f'''
<label for="dropdown">Choose list:</label>
<div class="dropdown" name="dropdown">
  <button class="bg1 border">{button}</button>
  <nav class="bg1 no-ul-all">
    <a href="index.html">Most frequent</a>
    <a href="by_name.html">Full list (A–Z)</a>
    <a href="by_count.html">Full list (by count)</a>
  </nav>
</div>'''


def duo_list(list1, list2):
    txt1 = '<br>\n'.join([div_dom(dom, len(ids), 'subdomain') for dom, ids in list1])
    txt2 = '<br>\n'.join([div_dom(dom, len(ids), 'domain') for dom, ids in list2])
    return '''
<div id="dom-toc" class="found-in">
  <div id="subdomains">
    <h3>Subdomains ({}) <a class="snd mg_lr" href="#domains">go to Domains</a></h3>
    {}
  </div><div id="domains">
    <h3>Domains ({}) <a class="snd mg_lr" href="#subdomains">go to Subdomains</a></h3>
    {}
  </div>
</div>'''.format(len(list1), txt1, len(list2), txt2)


def gen_html_index(l1, l2, fname, title, button):
    with open(fname, 'w') as fp:
        fp.write(mylib.template_with_base(
            f'<h2>{title}</h2>' + dropdown_choose(button) + duo_list(l1, l2),
            title=title))


def gen_html_top_10(subset, fname, total, title):

    def div_loadbar(percent):
        return '<span class="loadbar"><span style="width: {0}%">{0}%</span></span>'.format(percent)

    with open(fname, 'w') as fp:
        txt = f'''
<div class="div-center">
<h2 class="center">{ title }</h2>
<div id="dom-top10" class="found-in">'''
        for dom, ids in subset:
            dom_str = div_dom(dom, len(ids), 'domain')
            pct_bar = div_loadbar(round(len(ids) / total * 100))
            txt += f'\n<p>{dom_str} {pct_bar}</p>'
        fp.write(mylib.template_with_base(txt + '''
</div>
<p class="mg_top">Get full list
sorted by <a class="snd" href="by_count.html">Occurrence frequency</a>
or in <a class="snd" href="by_name.html">Alphabetical order</a>.</p>
</div>
<p class="right snd">Download: <a href="data.json" download="domains.json">json</a></p>
''', title=title))


def gen_html_trinity(json, idx_dir, app_count, title):
    # Full list (A–Z)
    list1 = sorted(json['subdom'].items(), key=lambda x: x[0])
    list2 = sorted(json['pardom'].items(), key=lambda x: x[0])
    gen_html_index(list1, list2, mylib.path_add(idx_dir, 'by_name.html'),
                   title='{} (A–Z)'.format(title),
                   button='Full list (A–Z)')
    # Full list (by count)
    list1.sort(key=lambda x: -len(x[1]))
    list2.sort(key=lambda x: -len(x[1]))
    gen_html_index(list1, list2, mylib.path_add(idx_dir, 'by_count.html'),
                   title='{} (most apps)'.format(title),
                   button='Full list (by count)')
    # Top 10
    gen_html_top_10(list2[:25], mylib.path_add(idx_dir, 'index.html'),
                    app_count, title='Top 25 {}'.format(title))


def gen_html_lookup(html_dir, json, key, title):
    mylib.mkdir(html_dir)
    names = [[x, index_app_names.get_name(x)] for x in json['bundle']]
    mylib.json_write(mylib.path_add(html_dir, 'apps.json'), names)
    mylib.json_write(mylib.path_add(html_dir, 'doms.json'), json[key])
    with open(mylib.path_add(html_dir, 'index.html'), 'w') as fp:
        fp.write(mylib.template_with_base(f'''
<h2 id="name"></h2>
<p>Present in: <b id="num_apps">… applications</b></p>
<h3>Apps containing this domain:</h3>
<div id="app_list" class="no-ul-all">loading…</div>
<script type="text/javascript" src="/static/lookup-domain.js?1"></script>
<script type="text/javascript">
  lookup_domain_fragment('doms.json', 'apps.json', 'name', 'num_apps', 'app_list');
</script>
''', title=title))


def gen_html_stats(c_apps, c_domains):
    [c_recordings, c_logs] = index_meta.get_total_counts()
    title = 'Statistics'
    mylib.mkdir(mylib.path_out('stats'))
    with open(mylib.path_out('stats', 'index.html'), 'w') as fp:
        fp.write(mylib.template_with_base('''
<h2>{}</h2>
<p>
  The AppCheck database currently contains <b>{:,}&nbsp;apps</b> with a total of <b>{:,} unique domains</b>.
</p>
<p>
  Collected through <b>{:,}&nbsp;recordings</b> with <b>{:,} individual requests</b>.
</p>
<ul>
  <li>List of <a href="/index/apps/1/">Apps</a></li>
  <li>List of <a href="/index/domains/all/">Requested Domains</a></li>
  <li>List of <a href="/index/domains/tracker/">Trackers</a></li>
</ul>'''.format(title, c_apps, c_domains, c_recordings, c_logs), title=title))


def process():
    # bundle_combine assures domain name is [a-zA-Z0-9.-]
    print('generating domain-index ...')
    # Data export
    all_dom_dir = mylib.path_out('index', 'domains', 'all')
    trkr_dir = mylib.path_out('index', 'domains', 'tracker')
    mylib.mkdir(all_dom_dir)
    mylib.mkdir(trkr_dir)
    mylib.symlink(index_domains.fname_all(),
                  mylib.path_out_app(all_dom_dir, 'data.json'))
    mylib.symlink(index_domains.fname_tracker(),
                  mylib.path_out_app(trkr_dir, 'data.json'))

    json = index_domains.load()
    app_count = index_domains.number_of_apps(json)
    dom_count = len(json['subdom'])

    print('  Lookup')
    gen_html_lookup(mylib.path_out('domain'), json, 'pardom',
                    title='Domain Lookup')
    gen_html_lookup(mylib.path_out('subdomain'), json, 'subdom',
                    title='Subdomain Lookup')

    print('  All Domains')
    index_domains.enrich_with_bundle_ids(json)
    gen_html_trinity(json, all_dom_dir, app_count,
                     title='Requested Domains')

    print('  Trackers Only')
    json = index_domains.load(tracker=True)
    index_domains.enrich_with_bundle_ids(json)
    gen_html_trinity(json, trkr_dir, app_count,
                     title='Tracker')
    # Stats
    print('  Stats')
    gen_html_stats(app_count, dom_count)
    print('')


if __name__ == '__main__':
    process()
