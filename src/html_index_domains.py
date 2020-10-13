#!/usr/bin/env python3

import lib_common as mylib
import lib_graphs as Graph
import lib_html as HTML
import index_app_names  # get_name
import index_domains


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
{ HTML.p_download_json('data.json', 'domains.json') }
''', title=title)


def gen_html_trinity(idx_dir, app_count, json, title, symlink):
    list1 = [(dom, len(ids)) for dom, ids in json['subdom'].items()]
    list2 = [(dom, len(ids)) for dom, ids in json['pardom'].items()]

    def write_index(fname, title, button):
        HTML.write(idx_dir, '<h2>{}</h2>{}{}'.format(
            HTML.a_path([('/results/', 'Results')], title),
            dropdown_choose(button), duo_list(list1, list2)
        ), title=title, fname=fname)

    # Full list (A–Z)
    list1.sort(key=lambda x: x[0])
    list2.sort(key=lambda x: x[0])
    write_index('by_name.html', title='{} (A–Z)'.format(title),
                button='Full list (A–Z)')
    # Full list (by count)
    list1.sort(key=lambda x: -x[1])
    list2.sort(key=lambda x: -x[1])
    write_index('by_count.html', title='{} (by count)'.format(title),
                button='Full list (by count)')
    # Top 10
    gen_html_top_10(idx_dir, list2[:25], app_count, 'Top 25 {}'.format(title))
    mylib.symlink(symlink, mylib.path_out(idx_dir, 'data.json'))


def gen_lookup(html_dir, doms_dict, flag, title):
    HTML.write(html_dir, f'''
<h2>{ HTML.a_path([('/index/domains/all/', 'All Domains')],
                  '<span id="name"></span>') }</h2>
<p>Known Tracker: <b id="known">?</b></p>
<p>Present in: <b id="num-apps">… applications</b></p>
{ '<h3>Subdomains:</h3><div id="subdoms" class="tags"></div>' if flag else '' }
<h3>Apps containing this domain:</h3>
<div id="app-toc" class="no-ul-all">
  { HTML.app_tile_template() }
</div>
<script type="text/javascript" src="/static/lookup-domain.js?2"></script>
<script type="text/javascript" src="/static/lozad.js"></script>
<script type="text/javascript">
  lookup_domain_js('doms.json', '/results/lookup-apps.json', '/results/subdoms.json');
</script>
''', title=title)
    mylib.json_write(mylib.path_add(html_dir, 'doms.json'), doms_dict)


def process():
    # bundle_combine assures domain name is [a-zA-Z0-9.-]
    print('generating html: domain-index ...')
    json = index_domains.loadAll()
    app_count = index_domains.number_of_apps(json)
    dom_count = len(json['subdom'])

    # Prepare for lookup
    names = [[x, index_app_names.get_name(x)] for x in json['bundle']]
    dest_dir = mylib.path_out('results')
    mylib.mkdir(dest_dir)
    mylib.json_write(mylib.path_add(dest_dir, 'lookup-apps.json'), names)
    mylib.symlink(index_domains.fname_dom_subdoms(),
                  mylib.path_add(dest_dir, 'subdoms.json'))
    names = None

    print('  Lookup')
    gen_lookup(mylib.path_out('domain'), json['pardom'], True,
               title='Domain Lookup')
    gen_lookup(mylib.path_out('subdomain'), json['subdom'], False,
               title='Subdomain Lookup')

    print('  All Domains')
    for key in ['subdom', 'pardom']:
        for x in json[key].keys():
            json[key][x] = json[key][x][1:]
    gen_html_trinity(mylib.path_out('index', 'domains', 'all'), app_count,
                     json=json, title='Requested Domains',
                     symlink=index_domains.fname_all())
    json = None

    print('  Trackers Only')
    gen_html_trinity(mylib.path_out('index', 'domains', 'tracker'), app_count,
                     json=index_domains.loadTracker(), title='Tracker',
                     symlink=index_domains.fname_tracker())

    print('  Highly Used')
    gen_html_trinity(mylib.path_out('index', 'domains', 'highly-used'),
                     app_count, json=index_domains.loadNonTracker(),
                     title='Highly Used Domains',
                     symlink=index_domains.fname_no_tracker())
    print('')
    return app_count, dom_count


if __name__ == '__main__':
    process()
