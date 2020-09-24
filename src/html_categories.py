#!/usr/bin/env python3

import lib_common as mylib
import lib_html as HTML
import index_categories  # enum_all_categories


def process(affected=None, per_page=60):
    print('generating html: category-index ...')
    base = mylib.path_out('category')
    parent = 'All Categories'
    arr = []
    for cid, cat, apps in sorted(index_categories.enum_all_categories(),
                                 key=lambda x: x[1].lower()):
        arr.append((cid, cat))
        if affected and cid not in affected:
            continue
        pre = HTML.h2(HTML.a_path([(parent, '..')], cat))
        _, a = HTML.write_app_pages(mylib.path_add(base, cid), apps, cat,
                                    per_page, pre=pre)
        print('  {} ({})'.format(cat, a))

    print('  .. {} categories'.format(len(arr)))
    src = ''.join([HTML.a_category(cid, n) for cid, n in arr])
    HTML.write(base, '''
<h2>{}</h2>
<div class="tags large center">
  {}
</div>'''.format(parent, src), parent)
    print('')


if __name__ == '__main__':
    process()
