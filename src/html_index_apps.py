#!/usr/bin/env python3

import lib_common as mylib
import lib_html as HTML
import index_app_names  # get_sorted_app_names


def process(per_page=60):
    print('generating html: app-index ...')
    title = 'Apps (A–Z)'
    header = '<h2>' + HTML.a_path([('Results', '/results/')], title) + '</h2>'
    p, a = HTML.write_app_pages(mylib.path_out('index', 'apps'),
                                index_app_names.get_sorted_app_names(),
                                title, per_page=per_page, pre=header)
    print('  {} apps'.format(a))
    print('  {} pages'.format(p))
    print('')


if __name__ == '__main__':
    process()
