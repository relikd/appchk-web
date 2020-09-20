#!/usr/bin/env python3

import common_lib as mylib
import index_app_names


def gen_obj(bundle_id):
    if mylib.file_exists(mylib.path_out_app(bundle_id, 'icon.png')):
        icon = '/app/{0}/icon.png'.format(bundle_id)
    else:
        icon = '/static/app-template.svg'
    return {
        'id': bundle_id,
        'name': index_app_names.get_name(bundle_id),
        'img': icon
    }


def gen_entry(obj):
    return '''
<a href="/app/{id}/">
  <div>
    <img src="{img}" width="100" height="100">
    <span class="name">{name}</span><br />
    <span class="detail">{id}</span>
  </div>
</a>'''.format(**obj)


def gen_pager(current, total):

    def mklink(i, name, active=False):
        clss = ' class="active"' if active else ''
        return '<a href="../{}/"{}>{}</a>'.format(i, clss, name)

    links = ''
    # if current > 1:
    #     links += mklink(current - 1, 'Previous')
    start = max(1, current - 5)
    for i in range(start, min(total, start + 10) + 1):
        links += mklink(i, i, active=i == current)
    # if current < total:
    #     links += mklink(current + 1, 'Next')
    return '<div id="pagination">{}</div>'.format(links)


def gen_page(arr, base, page_id=1, total=1):
    title = 'Apps (A–Z)'
    path = mylib.path_add(base, str(page_id))
    mylib.mkdir(path)
    with open(mylib.path_add(path, 'index.html'), 'w') as fp:
        content = ''.join([gen_entry(x) for x in arr])
        pagination = gen_pager(page_id, total)  # if total > 1 else ''
        fp.write(mylib.template_with_base('''
<h2 class="center">{}</h2>
<div id="app-toc" class="center no-ul-all">
  {}
</div>
{}'''.format(title, content, pagination), title=title))


def process(per_page=60):
    print('generating app-index ...')
    index_dir = mylib.path_out('index', 'apps')
    mylib.rm_dir(index_dir)
    mylib.mkdir(index_dir)

    apps = [gen_obj(x) for x in mylib.enum_appids()]
    apps_total = len(apps)
    pages_total, rest = divmod(apps_total, per_page)
    if rest > 0:
        pages_total += 1
    print('  {} apps'.format(apps_total))
    print('  {} pages'.format(pages_total))

    apps_sorted = sorted(apps, key=lambda x: (x['name'].lower(), x['id']))
    for x in range(1, pages_total + 1):
        start = (x - 1) * per_page
        batch = apps_sorted[start:start + per_page]
        gen_page(batch, index_dir, x, pages_total)
    print('')


if __name__ == '__main__':
    process()
