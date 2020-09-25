#!/usr/bin/env python3

import lib_common as mylib
import lib_html as HTML
import index_rank


def process():
    print('generating html: ranking ...')
    title = 'Ranking'
    header = HTML.a_path([('Results', '/results/')], title)
    base = mylib.path_out('ranking')
    HTML.write(base, f'''
<h2>{header}</h2>
<p>
  This ranking shows only the 500 most recently updated applications.<br>
  If you're missing an app, feel free to contribute a new app recording.
</p>
<div class="xscroll yscroll">
  <table id="rank-list" class="alternate"><tr><td>Loading …</td></tr></table>
</div>
{ HTML.p_download_json('data.json', 'ranking-all.json') }
<script type="text/javascript" src="/static/ranking.js"></script>
<script type="text/javascript" src="/static/lozad.js"></script>
<script type="text/javascript">
  rank_js('data.json');
</script>''', title=title)
    mylib.symlink(index_rank.fname_ranking_list(),
                  mylib.path_add(base, 'data.json'))
    print('')


if __name__ == '__main__':
    process()
