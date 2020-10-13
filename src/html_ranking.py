#!/usr/bin/env python3

import lib_common as mylib
import lib_html as HTML
import index_rank  # fname_rank_list, fname_ranking_all


def html_h2_path(pathlist, title='Ranking'):
    return '<h2>{}</h2>'.format(HTML.a_path(pathlist, title))


def html_default_description():
    return '''
<p>
  This ranking shows only 500 of the most recently updated applications.<br>
  If you're missing an app, feel free to contribute a new app recording.
</p>'''


def html_table():
    return '''
<div class="xscroll yscroll">
  <table id="rank-list" class="alternate stick-first"><tr><td>Loading …</td></tr></table>
</div>'''


def html_script_chunk(fname, sort_col, sort_order):
    return '''
<script type="text/javascript" src="/static/ranking.js"></script>
<script type="text/javascript" src="/static/lozad.js"></script>
<script type="text/javascript">
  rank_js('{}', {}, {});
</script>'''.format(fname, sort_col, sort_order)


def write_ranking_all(title, base_dir):
    # full urls since app index can have page 2, 3, etc.
    src = html_h2_path([('/results/', 'Results'),
                        ('/index/apps/', 'Apps (A–Z)')])
    src += html_default_description()
    src += html_table()
    src += HTML.p_download_json('data.json', 'raw-apps.json')
    src += html_script_chunk('data.json', 12, -1)  # last update desc
    HTML.write(base_dir, src, title=title)
    mylib.symlink(index_rank.fname_ranking_all(),
                  mylib.path_add(base_dir, 'data.json'))


def write_ranking_category(cid, category_name):
    base = mylib.path_out('category', cid, 'ranking')
    # full urls since categories can have page 2, 3, etc.
    src = html_h2_path([('/category/', 'All Categories'),
                        ('/category/{}/'.format(cid), category_name)])
    src += html_default_description()
    src += html_table()
    src += HTML.p_download_json('data.json',
                                'raw-category-{}.json'.format(cid))
    src += html_script_chunk('data.json', 12, -1)  # last update desc
    HTML.write(base, src, title='Category Ranking: ' + category_name)
    mylib.symlink(index_rank.fname_rank_list('category', cid),
                  mylib.path_add(base, 'data.json'))


def write_ranking_custom_lists(base_dir, list_id, list_name, parent_title):
    base = mylib.path_add(base_dir, list_id)
    src = html_h2_path([('/results/', 'Results'),
                        ('/lists/', parent_title)], list_name)
    src += html_table()
    src += HTML.p_download_json('data.json',
                                'raw-list-{}.json'.format(list_id))
    src += html_script_chunk('data.json', 9, 1)  # tracker percent asc
    HTML.write(base, src, title='Compare: ' + list_name)
    mylib.symlink(index_rank.fname_rank_list('custom', list_id),
                  mylib.path_add(base, 'data.json'))


def process():
    print('generating html: ranking ...')
    print('  overall ranking')
    write_ranking_all('Ranking', mylib.path_out('index', 'apps', 'ranking'))

    print('  category ranking')
    for _, json in mylib.enum_categories():
        cid, name = json['meta']
        write_ranking_category(cid, name)

    print('  custom lists')
    base_custom = mylib.path_out('lists')
    title_custom = 'Lists'
    arr = []
    for list_id, json in mylib.enum_custom_lists('list_'):
        list_name = json['name']
        try:
            desc = json['desc']
        except KeyError:
            desc = None
        arr.append((list_id, list_name, len(json['apps']), desc))
        write_ranking_custom_lists(base_custom, list_id, list_name,
                                   parent_title=title_custom)

    print('    index page')
    mylib.sort_by_name(arr, 1)
    src = html_h2_path([('/results/', 'Results')], title_custom)
    src += '''
<p class="squeeze">
  App lists compare individual applications against each other.
  These curated lists group together, at least in some aspect, similar applications.
  This could be all instant messengers, health related apps, or apps from a common developer or country.
</p>
<div class="found-in">'''
    for x in arr:
        src += HTML.h4_a_title_sub_desc(x[0], x[1], f'contains {x[2]} apps', x[3])
    HTML.write(base_custom, src + '</div>', title=title_custom)
    print('')


if __name__ == '__main__':
    process()
