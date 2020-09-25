#!/usr/bin/env python3

import math  # ceil
import time  # strftime, gmtime
import lib_common as mylib


# REFS

def a_app(bundle_id, inner, attr_str=''):
    return '<a{} href="/app/{}/">{}</a>'.format(attr_str, bundle_id, inner)


def a_category(cat_id, inner, attr_str=''):
    return '<a{} href="/category/{}/">{}</a>'.format(attr_str, cat_id, inner)


def a_domain(x, inner=None, attr_str=''):
    return '<a{} href="/domain/#{}">{}</a>'.format(attr_str, x, inner or x)


def a_subdomain(x, inner=None, attr_str=''):
    return '<a{} href="/subdomain/#{}">{}</a>'.format(attr_str, x, inner or x)


def p_download_json(href, download_name):
    return '<p class="right snd">Download: <a href="{}" download="{}">json</a></p>'.format(
        href, download_name)


# Data object preparation


def attr_and(a, b):
    res = {}
    for d in [a, b]:
        for key, val in d.items():
            try:
                res[key] += ' ' + val
            except KeyError:
                res[key] = val
    return res


# Basic building blocks

def xml(tag, inner, attr=None):
    src = ''
    if attr:
        for key, val in attr.items():
            if val:
                src += ' {}="{}"'.format(key, val)
    return '<{0}{1}>{2}</{0}>'.format(tag, src, inner)


def div(inner, attr=None):
    return xml('div', inner, attr)


def h2(inner, attr=None):
    return xml('h2', inner, attr)


def a_path(parts, suffix):
    ''' expects (name, url) tuples '''
    return ' / '.join(['<a href="{}">{}</a>'.format(url, title)
                       for title, url in parts] + [suffix])


# Simple constructs

def tr(columns, tag='td'):
    return f'''
<tr>{''.join(['<{0}>{1}</{0}>'.format(tag, c) for c in columns])}</tr>'''


def date_utc(ctime):
    return '<time datetime="{}">{} UTC</time>'.format(
        time.strftime('%Y-%m-%d %H:%M', time.gmtime(ctime)),
        time.strftime('%Y-%m-%d, %H:%M', time.gmtime(ctime)))


# Higher level constructs

def pagination(current, total):
    if total == 1:
        return ''

    def _lnk(i, name, active=False):
        C = ' class="active"' if active else ''
        if i == current:
            link = './'
        elif current == 1:
            link = f'./{i}/'
        else:
            link = '../' if i == 1 else f'../{i}/'
        return f'<a href="{link}"{C}>{name}</a>'

    links = ''
    # if current > 1:
    #     links += _lnk(current - 1, 'Previous')
    start = max(1, current - 5)
    for i in range(start, min(total, start + 10) + 1):
        links += _lnk(i, i, active=i == current)
    # if current < total:
    #     links += _lnk(current + 1, 'Next')
    return '<div class="pagination">{}</div>'.format(links)


def url_for_icon(bundle_id):
    if mylib.file_exists(mylib.path_out_app(bundle_id, 'icon.png')):
        return '/app/{0}/icon.png'.format(bundle_id)
    else:
        return '/static/app-template.svg'


def app_tile(bundle_id, name):
    return f'''
<a href="/app/{bundle_id}/">
  <div>
    <img src="{url_for_icon(bundle_id)}" width="100" height="100">
    <span class="name">{name}</span><br />
    <span class="detail">{bundle_id}</span>
  </div>
</a>'''


def app_tile_template():
    return f'''<a><div>
  <img width="100" height="100">
  <span class="name"></span><br />
  <span class="detail"></span>
</div></a>'''


def app_tiles_all(apps, per_page=60):
    attr = {'id': 'app-toc', 'class': 'no-ul-all'}
    c_apps = len(apps)
    c_pages = int(math.ceil(c_apps / per_page))
    for offset in range(0, len(apps), per_page):
        idx = int(offset / per_page) + 1
        batch = apps[offset:offset + per_page]
        src = ''
        for x in batch:
            src += app_tile(x[0], x[1])
        yield idx, len(batch), div(src, attr) + pagination(idx, c_pages)


# Write html to disk

_base_template = None


def base_template(content, title=None):
    global _base_template
    if not _base_template:
        with open(mylib.path_root('templates', 'base.html'), 'r') as fp:
            _base_template = fp.read()
    return _base_template.replace(
        '#_TITLE_#', title + ' – ' if title else '').replace(
        '#_CONTENT_#', content)


def write(path, content, title=None, fname='index.html'):
    mylib.mkdir(path)
    with open(mylib.path_add(path, fname), 'w') as fp:
        fp.write(base_template(content, title=title))


def write_app_pages(base, apps, title, per_page=60, pre='', post=''):
    pages = 0
    entries = 0
    mylib.rm_dir(base)
    for i, count, src in app_tiles_all(apps, per_page):
        pages += 1
        entries += count
        pth = base if i == 1 else mylib.path_add(base, str(i))
        mylib.mkdir(pth)
        write(pth, pre + '\n' + src + '\n' + post, title=title)
    return pages, entries
