#!/usr/bin/env python3

import lib_common as mylib
import lib_html as HTML


def process(affected=None, per_page=60):
    print('generating html: category-index ...')
    base = mylib.path_out('category')
    parent = 'All Categories'
    arr = []
    for fname, json in mylib.enum_categories():
        cid, cname = json['meta']
        arr.append((cid, cname))
        if affected and cid not in affected:
            continue
        out_dir = mylib.path_add(base, cid)
        A = HTML.h2(HTML.a_path([(parent, '../')], cname))
        Z = HTML.p_download_json('data.json', 'category_{}.json'.format(cid))
        _, a = HTML.write_app_pages(out_dir, json['apps'],
                                    cname, per_page, pre=A, post=Z)
        print('  {} ({})'.format(cname, a))
        mylib.symlink(fname, mylib.path_add(out_dir, 'data.json'))

    print('  .. {} categories'.format(len(arr)))
    mylib.sort_by_name(arr, 1)
    src = ''.join([HTML.a_category(*x) for x in arr])
    HTML.write(base, '''
<h2>{}</h2>
<div class="tags large center">
  {}
</div>'''.format(parent, src), parent)
    print('')


if __name__ == '__main__':
    process()
