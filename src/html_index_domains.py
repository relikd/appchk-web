#!/usr/bin/env python3

import lib_common as mylib
import lib_graphs as Graph
import lib_html as HTML
import index_app_names  # get_name
import index_domains
import index_meta  # get_total_counts


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


def div_dom(fn_a_html, domain, count):
    return '{} <span>found in {} {}</span>'.format(
        fn_a_html(domain), count, 'apps' if count > 1 else 'app')


def duo_list(list1, list2):
    def full(fn_a_html, arr):
        return '<br>\n'.join([div_dom(fn_a_html, domain, count)
                              for domain, count in arr])
    return f'''
<div id="dom-toc" class="found-in">
  <div id="subdomains">
    <h3 class="stick-top">Subdomains ({len(list1)})
      <a class="snd mg_lr" href="#domains">go to Domains</a></h3>
    { full(HTML.a_subdomain, list1) }
  </div><div id="domains">
    <h3 class="stick-top">Domains ({len(list2)})
      <a class="snd mg_lr" href="#subdomains">go to Subdomains</a></h3>
    { full(HTML.a_domain, list2) }
  </div>
</div>'''


def gen_html_top_10(path, subset, total, title):
    src = ''
    for dom, count in subset:
        src += '\n<div>{} {}</div>'.format(
            div_dom(HTML.a_domain, dom, count), Graph.fill_bar(count / total))

    HTML.write(path, f'''
<h2 class="center">{ title }</h2>
<div class="div-center">
  <div id="dom-top10" class="found-in">
    { src }
  </div>
  <p class="mg_top">Get full list sorted by
    <a class="snd" href="by_count.html">Occurrence frequency</a> or in
    <a class="snd" href="by_name.html">Alphabetical order</a>.
  </p>
</div>
<p class="right snd">Download: <a href="data.json" download="domains.json">json</a></p>
''', title=title)


def gen_html_trinity(idx_dir, app_count, json, title, symlink):
    list1 = [(dom, len(ids)) for dom, ids in json['subdom'].items()]
    list2 = [(dom, len(ids)) for dom, ids in json['pardom'].items()]

    def write_index(fname, title, button):
        HTML.write(idx_dir, '<h2>{}</h2>{}{}'.format(
            title, dropdown_choose(button), duo_list(list1, list2)
        ), title=title, fname=fname)

    # Full list (A–Z)
    list1.sort(key=lambda x: x[0])
    list2.sort(key=lambda x: x[0])
    write_index('by_name.html', title='{} (A–Z)'.format(title),
                button='Full list (A–Z)')
    # Full list (by count)
    list1.sort(key=lambda x: -x[1])
    list2.sort(key=lambda x: -x[1])
    write_index('by_count.html', title='{} (most apps)'.format(title),
                button='Full list (by count)')
    # Top 10
    gen_html_top_10(idx_dir, list2[:25], app_count, 'Top 25 {}'.format(title))
    mylib.symlink(symlink, mylib.path_out(idx_dir, 'data.json'))


def gen_lookup(html_dir, doms_dict, names_dict, title):
    HTML.write(html_dir, '''
<h2 id="name"></h2>
<p>Present in: <b id="num-apps">… applications</b></p>
<h3>Apps containing this domain:</h3>
<div id="app-toc" class="no-ul-all">
  {}
</div>
<script type="text/javascript" src="/static/lookup-domain.js"></script>
<script type="text/javascript">
  lookup_domain_js('doms.json', 'apps.json', 'name', 'num-apps', 'app-toc');
</script>
'''.format(HTML.app_tile_template()), title=title)
    # after html write which will create the dir
    mylib.json_write(mylib.path_add(html_dir, 'apps.json'), names_dict)
    mylib.json_write(mylib.path_add(html_dir, 'doms.json'), doms_dict)


def gen_results(c_apps, c_domains, title):
    [c_recordings, c_logs] = index_meta.get_total_counts()
    print('    {} apps'.format(c_apps))
    print('    {} domains'.format(c_domains))
    print('    {} recordings'.format(c_recordings))
    print('    {} logs'.format(c_logs))
    HTML.write(mylib.path_out('results'), '''
<h2>{}</h2>
<p>The AppCheck database currently contains <b>{:,}&nbsp;apps</b> with a total of <b>{:,} unique domains</b>.</p>
<p>Collected through <b>{:,}&nbsp;recordings</b> with <b>{:,} individual requests</b>.</p>
<ul>
  <li>List of <a href="/index/apps/">Apps</a></li>
  <li>List of <a href="/category/">Categories</a></li>
  <li>List of <a href="/index/domains/all/">Requested Domains</a></li>
  <li>List of <a href="/index/domains/tracker/">Trackers</a></li>
</ul>'''.format(title, c_apps, c_domains, c_recordings, c_logs), title=title)
    mylib.symlink(index_meta.fname_app_rank(),
                  mylib.path_out('results', 'rank.json'))  # after HTML.write


def process():
    # bundle_combine assures domain name is [a-zA-Z0-9.-]
    print('generating html: domain-index ...')
    json = index_domains.load()
    app_count = index_domains.number_of_apps(json)
    dom_count = len(json['subdom'])

    print('  Lookup')
    names = [[x, index_app_names.get_name(x)] for x in json['bundle']]
    gen_lookup(mylib.path_out('domain'), json['pardom'], names,
               title='Domain Lookup')
    gen_lookup(mylib.path_out('subdomain'), json['subdom'], names,
               title='Subdomain Lookup')
    names = None

    print('  All Domains')
    gen_html_trinity(mylib.path_out('index', 'domains', 'all'), app_count,
                     json=json, title='Requested Domains',
                     symlink=index_domains.fname_all())
    json = None

    print('  Trackers Only')
    gen_html_trinity(mylib.path_out('index', 'domains', 'tracker'), app_count,
                     json=index_domains.load(tracker=True), title='Tracker',
                     symlink=index_domains.fname_tracker())
    # Stats
    print('  Results')
    gen_results(app_count, dom_count, title='Results')
    print('')


if __name__ == '__main__':
    process()
