#!/usr/bin/env python3

import lib_common as mylib
import lib_html as HTML
import index_rank  # fname_rank_list


def make_groupby_table_html(json, struct):
    sep = ' class="sep"'
    par_tr = ''
    sub_tr = ''
    for par_col, cols in struct:
        par_tr += f'<th{sep} colspan="{len(cols)}">{par_col}</th>'
        for i, x in enumerate(cols):
            sub_tr += '<th{}>{}</th>'.format(sep if i == 0 else '', x[0])
    src = f'''
<div class="xscroll">
<table class="cluster alternate">
  <tr><th></th>{par_tr}</tr>
  <tr><th></th>{sub_tr}</tr>
'''
    for group in json:
        ident = group[0]
        if isinstance(ident, list):
            ident = f'<a href="{ident[1]}">{ident[0]}</a>'
        src += f'<tr><td>{ident}</td>'
        for _, cols in struct:
            first = True
            for _, col_i, fn in cols:
                val = group[col_i]
                src += '<td{}>{}</td>'.format(sep if first else '', fn(val))
                first = False
        src += '</tr>\n'
    return src + '</table></div>\n'


def prefill_groupby_table(cluster_file):
    return make_groupby_table_html(mylib.json_read(cluster_file), [
        ['Apps', [
            (' ', 1, int)]],
        ['Number of Recordings', [
            ('avg', 2, HTML.fmt_round_num),
            ('total', 3, int)]],
        ['Number of Requests', [
            ('avg', 4, HTML.fmt_round_num),
            ('total', 5, int)]],
        ['Recording Time', [
            ('avg', 6, HTML.seconds_to_time),
            ('total', 7, HTML.seconds_to_time)]],
        ['Requests per Minute', [
            ('min', 9, HTML.fmt_as_pm),
            ('avg', 8, HTML.fmt_as_pm),
            ('max', 10, HTML.fmt_as_pm)]],
        ['Number of Domains', [
            ('min', 12, int),
            ('avg', 11, HTML.fmt_round_num),
            ('max', 13, int)]],
        ['Number of Subdomains', [
            ('min', 15, int),
            ('avg', 14, HTML.fmt_round_num),
            ('max', 16, int)]],
        ['Tracker Percentage', [
            ('min', 18, HTML.fmt_as_percent),
            ('avg', 17, HTML.fmt_as_percent),
            ('max', 19, HTML.fmt_as_percent)]],
    ])


def gen_and_link_groupby(cluster_id, base, raw_fname='data'):
    json_file = index_rank.fname_rank_list('groupby', cluster_id)
    raw_fname += '.json'
    mylib.symlink(json_file, mylib.path_add(base, raw_fname))
    named_download = 'compare-{}.json'.format(cluster_id)
    return prefill_groupby_table(json_file) + HTML.p_download_json(
        raw_fname, named_download)


def write_groupby_multi(base_dir, h2_paths, h2_title, page_title, groups_arr):
    mylib.mkdir(base_dir)
    src = '<h2>{}</h2>'.format(HTML.a_path(h2_paths, h2_title))
    for gid, name in groups_arr:
        raw_name = gid if len(groups_arr) > 1 else 'data'
        src += f'\n<h3>{name}</h3>'
        src += gen_and_link_groupby(gid, base_dir, raw_name)
    HTML.write(base_dir, src, title='Compare: ' + page_title)


def write_groupby_single(base_dir, gid, name, parent):
    base = mylib.path_add(base_dir, gid)
    write_groupby_multi(base,
                        [('/results/', 'Results'), ('/compare/', parent)],
                        name, name, [(gid, '')])


def process():
    print('generating html: group compare ...')
    print('  lists')
    base_custom = mylib.path_out('compare')
    title_custom = 'Compare'
    arr = []
    for list_id, json in mylib.enum_custom_lists('groupby_'):
        try:
            if json['hidden']:
                continue
        except KeyError:
            pass
        list_name = json['name']
        print('    ' + list_name)
        grp_count = len(json['groups'])
        app_count = sum([len(x['apps']) for x in json['groups']])
        try:
            desc = json['desc']
        except KeyError:
            desc = None
        arr.append((list_id, list_name, grp_count, app_count, desc))
        write_groupby_single(base_custom, list_id, list_name, title_custom)

    print('  index page')
    mylib.sort_by_name(arr, 1)
    src = f'''
<h2>{HTML.a_path([('/results/', 'Results')], title_custom)}</h2>
<p class="squeeze">
  Comparison groups do not compare a single application against another.
  Instead comparison groups cluster multiple applications into a single, logical group.
  For example, paid-vs-free apps could be a comparison group.
</p>
<div>'''
    for x in arr:
        src += HTML.h4_a_title_sub_desc(
            x[0], x[1], f'has {x[2]} groups with {x[3]} apps', x[4])
    HTML.write(base_custom, src + '</div>', title=title_custom)
    print('')


if __name__ == '__main__':
    process()
