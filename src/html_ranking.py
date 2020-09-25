#!/usr/bin/env python3

import lib_common as mylib
import lib_html as HTML
import index_rank  # fname_ranking_category, fname_ranking_all


def html_base(*pathlist):
    return '''
<h2>{}</h2>
<p>
  This ranking shows only 500 of the most recently updated applications.<br>
  If you're missing an app, feel free to contribute a new app recording.
</p>
<div class="xscroll yscroll">
  <table id="rank-list" class="alternate"><tr><td>Loading …</td></tr></table>
</div>
'''.format(HTML.a_path(pathlist, 'Ranking'))


def html_script_chunk(fname):
    return '''
<script type="text/javascript" src="/static/ranking.js"></script>
<script type="text/javascript" src="/static/lozad.js"></script>
<script type="text/javascript">
  rank_js('{}');
</script>'''.format(fname)


def write_ranking_category(cid, category_name):
    base = mylib.path_out('category', cid, 'ranking')
    # full urls since categories can have page 2, 3, etc.
    src = html_base(('All Categories', '/category/'),
                    (category_name, '/category/{}/'.format(cid)))
    src += HTML.p_download_json('data.json',
                                'results-category-{}.json'.format(cid))
    src += html_script_chunk('data.json')
    HTML.write(base, src, title='Category Ranking: ' + category_name)
    mylib.symlink(index_rank.fname_ranking_category(cid),
                  mylib.path_add(base, 'data.json'))


def write_ranking_all(title, base_dir):
    src = html_base(('Results', '/results/'))
    src += HTML.p_download_json('data.json', 'results-all.json')
    src += html_script_chunk('data.json')
    HTML.write(base_dir, src, title=title)
    mylib.symlink(index_rank.fname_ranking_all(),
                  mylib.path_add(base_dir, 'data.json'))


def process():
    print('generating html: ranking ...')
    write_ranking_all('Ranking', mylib.path_out('ranking'))
    for _, json in mylib.enum_categories():
        cid, name = json['meta']
        write_ranking_category(cid, name)
    print('')


if __name__ == '__main__':
    process()
