#!/usr/bin/env python3

import lib_common as mylib
import lib_html as HTML


def process(per_page=60):
    print('generating html: app-index ...')
    title = 'Apps (A–Z)'
    header = HTML.h2(HTML.a_path([('Results', '/results/')], title))
    p, a = HTML.write_app_pages(mylib.path_out('index', 'apps'),
                                mylib.appids_in_out(), title,
                                per_page=per_page, pre=header)
    print('  {} apps'.format(a))
    print('  {} pages'.format(p))
    print('')


if __name__ == '__main__':
    process()
