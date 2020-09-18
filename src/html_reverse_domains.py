#!/usr/bin/env python3

import common_lib as mylib
import index_bundle_names
import index_reverse_domains


def a_app(bundle_id):
    return '<a href="/app/{}/">{}</a>'.format(
        bundle_id, index_bundle_names.get_name(bundle_id))


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
  <div class="bg1 no_ul_all">
    <a href="index.html">Most frequent</a>
    <a href="by_name.html">Full list (A–Z)</a>
    <a href="by_count.html">Full list (by count)</a>
  </div>
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


def gen_html_top_domains(subset, fname, total, title):

    def div_loadbar(percent):
        return '<span class="loadbar"><span style="width: {0}%">{0}%</span></span>'.format(percent)

    with open(fname, 'w') as fp:
        txt = f'''
<div id="dom-top10" class="found-in">
<h2>{ title }</h2>'''
        for dom, ids in subset:
            dom_str = div_dom(dom, len(ids), 'subdomain')
            pct_bar = div_loadbar(round(len(ids) / total * 100))
            txt += f'\n<p>{dom_str} {pct_bar}</p>'
        fp.write(mylib.template_with_base(txt + '''
<p class="mg_top">Get full list
sorted by <a class="snd" href="by_count.html">Occurrence frequency</a>
or in <a class="snd" href="by_name.html">Alphabetical order</a>.</p>
</div>
<p class="right snd">Download: <a href="data.json" download="appcheck_domains_full.json">json</a></p>
''', title=title))


def gen_html_lookup(html_dir, json, key, title):
    mylib.mkdir(html_dir)
    names = [[x, index_bundle_names.get_name(x)] for x in json['bundle']]
    mylib.json_write(mylib.path_add(html_dir, 'apps.json'), names)
    mylib.json_write(mylib.path_add(html_dir, 'doms.json'), json[key])
    with open(mylib.path_add(html_dir, 'index.html'), 'w') as fp:
        fp.write(mylib.template_with_base(f'''
<h2 id="name"></h2>
<p>Present in: <b id="num_apps">… applications</b></p>
<h3>Apps containing this domain:</h3>
<div id="app_list">loading…</div>
<script type="text/javascript" src="/static/lookup-domain.js?1"></script>
<script type="text/javascript">
  lookup_domain_fragment('doms.json', 'apps.json', 'name', 'num_apps', 'app_list');
</script>
''', title=title))


def process():
    # bundle_combine assures domain name is [a-zA-Z0-9.-]
    print('generating reverse-domain-index ...')
    idx_dir = mylib.path_out('index', 'domains')
    mylib.mkdir(idx_dir)

    # Data export
    mylib.symlink(mylib.path_data_index('reverse_domains.json'),
                  mylib.path_out_app(idx_dir, 'data.json'))

    par_arr = list(index_reverse_domains.enumerate('pardom'))
    sub_arr = list(index_reverse_domains.enumerate('subdom'))

    # Full list (A–Z)
    sub_arr.sort(key=lambda x: x[0])
    par_arr.sort(key=lambda x: x[0])
    gen_html_index(sub_arr, par_arr, mylib.path_add(idx_dir, 'by_name.html'),
                   title='Requested Domains (A–Z)',
                   button='Full list (A–Z)')

    # Full list (by count)
    sub_arr.sort(key=lambda x: -len(x[1]))
    par_arr.sort(key=lambda x: -len(x[1]))
    gen_html_index(sub_arr, par_arr, mylib.path_add(idx_dir, 'by_count.html'),
                   title='Requested Domains (most apps)',
                   button='Full list (by count)')

    # Top 10
    del(sub_arr[20:])
    del(par_arr)
    total = index_reverse_domains.number_of_apps()
    gen_html_top_domains(sub_arr, mylib.path_add(idx_dir, 'index.html'),
                         total, 'Top 20 Requested Domains')

    # Lookup
    json = index_reverse_domains.raw()
    gen_html_lookup(mylib.path_out('domain'), json, 'pardom',
                    title='Domain Lookup')
    gen_html_lookup(mylib.path_out('subdomain'), json, 'subdom',
                    title='Subdomain Lookup')
    print('')


if __name__ == '__main__':
    process()
