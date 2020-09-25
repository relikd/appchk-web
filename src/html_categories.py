#!/usr/bin/env python3

import lib_common as mylib
import lib_html as HTML


def process(affected=None, per_page=60):
    print('generating html: category-index ...')
    base = mylib.path_out('category')
    parent = 'All Categories'
    arr = []
    for json in mylib.enum_categories():
        cid, cname = json['cat']
        arr.append((cid, cname))
        if affected and cid not in affected:
            continue
        pre = HTML.h2(HTML.a_path([(parent, '../')], cname))
        _, a = HTML.write_app_pages(mylib.path_add(base, cid), json['apps'],
                                    cname, per_page, pre=pre)
        print('  {} ({})'.format(cname, a))

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
