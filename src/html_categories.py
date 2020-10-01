#!/usr/bin/env python3

import lib_common as mylib
import lib_html as HTML


def write_overview_page(base_dir, category_tuples, title):
    cluster = {}
    for x in category_tuples:
        i = int(int(x[0]) / 1000)
        try:
            cluster[i].append(x)
        except KeyError:
            cluster[i] = [x]
    src = '<h2>{}</h2><div id="categories">'.format(title)
    for i, arr in sorted(cluster.items()):
        mylib.sort_by_name(arr, 1)
        kind = 'Apps' if i == 6 else 'Games' if i == 7 else 'Other'
        src += '<h3 class="center">{}</h3>'.format(kind)
        src += '<div class="tags large center">'
        src += ''.join([HTML.a_category(*x) for x in arr]) + '</div>'
    HTML.write(base_dir, src + '</div>', title)


def process(affected=None, per_page=60):
    print('generating html: category-index ...')
    base = mylib.path_out('category')
    parent = 'All Categories'
    arr = []
    for fname, json in mylib.enum_categories():
        cid, cname = json['meta']
        arr.append([cid, cname])
        if affected and cid not in affected:
            continue
        out_dir = mylib.path_add(base, cid)
        # full url since categories can have page 2, 3, etc.
        A = HTML.h2_path_n_rank(cname, [(parent, '/category/')], 'ranking/')
        Z = HTML.p_download_json('data.json', 'category-{}.json'.format(cid))
        _, a = HTML.write_app_pages(out_dir, json['apps'],
                                    cname, per_page, pre=A, post=Z)
        # write_app_pages breaks html_ranking!! call html_ranking after this!
        print('  {} ({})'.format(cname, a))
        if a > 1:
            arr[-1][-1] += ' ({})'.format(a)  # append count
        mylib.symlink(fname, mylib.path_add(out_dir, 'data.json'))

    print('  .. {} categories'.format(len(arr)))
    write_overview_page(base, arr, parent)
    print('')


if __name__ == '__main__':
    process()
