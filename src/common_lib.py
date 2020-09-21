#!/usr/bin/env python3

import os
import re
import glob
import json
import shutil
import logging
from pathlib import Path
import urllib.request as curl

base_dir = os.path.realpath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), os.pardir))


# Paths

def path_add(base, *parts):
    return os.path.join(base, *parts)


def path_root(*parts):
    return os.path.join(base_dir, *parts)


def path_data(*path_components):
    return path_root('data', *path_components)


def path_data_app(bundle_id, filename=None):
    pth = path_root('data', *bundle_id.split('.'))
    return path_add(pth, filename) if filename else pth


def path_data_index(filename):
    pth = path_root('data', '_eval')
    mkdir(pth)
    return path_add(pth, filename)


def path_out(*path_components):
    return path_root('out', *path_components)


def path_out_app(bundle_id, filename=None):
    pth = path_root('out', 'app', bundle_id)
    return path_add(pth, filename) if filename else pth


def path_len(path, isDir=True):
    return len(path) + (len(os.sep) if isDir else 0)


# Tempaltes

def template(html_file):
    return path_root('templates', html_file)


def template_with_base(content, title=None):
    with open(template('base.html'), 'r') as fp:
        return fp.read().replace(
            '#_TITLE_#', title + ' – ' if title else '').replace(
            '#_CONTENT_#', content)


# Other

# same regex as in `api/v1/contribute/index.php`
regex_bundle_id = re.compile(r'^[A-Za-z0-9\.\-]{1,155}$')
logging.basicConfig(filename=path_root('error.log'),
                    format='%(asctime)s %(message)s',
                    filemode='a')
logger = logging.getLogger()


def usage(_file_, params=''):
    print(' usage: ' + os.path.basename(_file_) + ' ' + params)


def valid_bundle_id(bundle_id):
    return regex_bundle_id.match(bundle_id)


def err(scope, msg, logOnly=False):
    logger.error('[{}] {}'.format(scope, msg))
    if not logOnly:
        print(' [ERROR] ' + msg)


def printf(msg):
    print(msg, end='', flush=True)


# Binary Tree Search

def read_list(list_name):
    path = path_root('src', 'lists', list_name)
    if not file_exists(path):
        return []
    with open(path, 'r') as fp:
        return [x.strip() for x in fp.readlines()]


def bintree_lookup(tree, needle):
    lo = 0
    hi = len(tree) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if tree[mid] < needle:
            lo = mid + 1
        elif needle < tree[mid]:
            hi = mid - 1
        else:
            return True  # mid
    if lo > 0 and needle.startswith(tree[lo - 1] + '.'):
        return True  # lo - 1
    return False  # -1


# Filesystem

def mkdir(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def mv(path, to, printOmitPrefix=None):
    if printOmitPrefix:
        print('  mv ' + path[printOmitPrefix:] + ' -> ' + to[printOmitPrefix:])
    Path(path).rename(to)


def rm_file(file_path):
    try:
        os.remove(file_path)
    except FileNotFoundError:
        pass


def rm_dir(path):
    try:
        shutil.rmtree(path)
    except Exception:
        pass


def dir_exists(path):
    return os.path.isdir(path)


def file_exists(path):
    return os.path.isfile(path) and os.path.getsize(path) > 0


def symlink(source, target):
    if not file_exists(target):
        rm_file(target)  # file_exists is false if symlink cant be followed
        os.symlink(source, target)


def mkdir_out_app(bundle_id):
    out_dir = path_out_app(bundle_id)
    if not dir_exists(out_dir):
        mkdir(out_dir)
        return True
    return False


def next_path(path_pattern):
    i = 1
    while os.path.exists(path_pattern % i):
        i = i * 2
    a, b = (i // 2, i)
    while a + 1 < b:
        c = (a + b) // 2  # interval midpoint
        a, b = (c, b) if os.path.exists(path_pattern % c) else (a, c)
    return path_pattern % b


def diff_files(fileA, fileB):
    with open(fileA, 'r') as fpA:
        with open(fileB, 'r') as fpB:
            a = '_'
            b = '_'
            diff = []
            while a != '' and b != '':
                a = fpA.readline()
                b = fpB.readline()
                if a == b:
                    continue
                while a != b:
                    if a == '' or b == '':
                        break
                    if a < b:
                        diff.append(a.strip())
                        a = fpA.readline()
                    elif b < a:
                        diff.append(b.strip())
                        b = fpB.readline()
            while a != '':
                a = fpA.readline()
                diff.append(a.strip())
            while b != '':
                b = fpB.readline()
                diff.append(b.strip())
            return diff


# Download

def download(url, isJSON=False):
    req = curl.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with curl.urlopen(req) as response:
        data = response.read()
    return json.loads(data.decode()) if isJSON else data


def download_file(url, path):
    curl.urlretrieve(url, path)


# Enumerator

def enum_newly_added():
    for fname in glob.glob(path_data('_in', 'in_*')):
        yield fname, os.path.basename(fname)[3:]  # del prefix 'in_'


def enum_appids():
    for x in glob.glob(path_out_app('*')):
        yield os.path.basename(x)


def enum_jsons(bundle_id):
    for fname in glob.glob(path_data_app(bundle_id, 'id_*.json')):
        with open(fname, 'r') as fp:
            yield fname, json.load(fp)


def enum_data_appids():
    data_root = path_data()
    prfx = path_len(data_root)
    for path, dirs, files in os.walk(data_root):
        if 'combined.json' in files:
            yield path[prfx:].replace(os.sep, '.')


# JSON read

def json_read(path):
    with open(path, 'r') as fp:
        return json.load(fp)


def json_read_combined(bundle_id):
    return json_read(path_data_app(bundle_id, 'combined.json'))


def json_read_evaluated(bundle_id):
    pth = path_data_app(bundle_id, 'evaluated.json')
    return json_read(pth), pth


# JSON write

def json_write(path, obj, pretty=False):
    with open(path, 'w') as fp:
        json.dump(obj, fp, indent=2 if pretty else None, sort_keys=pretty)


def json_write_combined(bundle_id, obj):
    fname = path_data_app(bundle_id, 'combined.json')
    json_write(fname, obj, pretty=False)


def json_write_evaluated(bundle_id, obj):
    fname = path_data_app(bundle_id, 'evaluated.json')
    json_write(fname, obj, pretty=False)
