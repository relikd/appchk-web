#!/usr/bin/env python3

import common_lib as mylib
# import hashlib

known_trackers = None


def is_tracker(domain):
    global known_trackers
    if not known_trackers:
        known_trackers = mylib.read_list('tracker_all.txt')
    return mylib.bintree_lookup(known_trackers, domain[::-1])


# def md5(fname):
#     hash_md5 = hashlib.md5()
#     with open(fname, 'rb') as f:
#         for chunk in iter(lambda: f.read(4096), b''):
#             hash_md5.update(chunk)
#     return hash_md5.hexdigest()


def save_list(result_set, fname, binary=False):
    if not result_set:
        return []
    out = mylib.path_root('src', 'lists', 'tracker_' + fname)
    with open(out + '_tmp', 'wb' if binary else 'w') as fp:
        end = b'\n' if binary else '\n'
        for domain in sorted(result_set):
            fp.write(domain + end)
    try:
        changes = mylib.diff_files(out, out + '_tmp')
    except Exception:
        changes = [str(x) if binary else x for x in result_set]
    mylib.mv(out + '_tmp', out)
    # md5_old = md5(out) if mylib.file_exists(out) else None
    # md5_new = md5(out)
    if changes:
        print('  updating: ' + fname)
    else:
        print('  no-change: ' + fname)
    return changes


def enum_lines(url, ignore=None):
    try:
        whole = mylib.download(url)
        for line in whole.split(b'\n'):
            if not line or ignore and line.startswith(ignore):
                continue
            yield line
    except Exception as e:
        mylib.err('tracker-download', str(e) + ' in ' + url)


def github(path):
    return 'https://raw.githubusercontent.com/' + path


def lockdown(fname, urlname):
    url = github('confirmedcode/lockdown-ios/master/LockdowniOS/') + urlname
    return save_list(set(enum_lines(url)), fname, binary=True)


def customlist(fname):
    # We could access the 'list.txt' file directly on this server
    # However, we can't separate the api from the website then
    url = 'https://appchk.de/api/v1/trackers/'
    return save_list(set(enum_lines(url)), fname, binary=True)


def easylist(fname, urlname):
    url = github('easylist/easylist/master/') + urlname
    res = set()
    for x in enum_lines(url):
        if not x.startswith(b'||'):
            continue
        x = x[2:]
        parts = x.split(b'^')
        if len(parts) == 1:
            parts = x.split(b'$')
        res.add(parts[0].split(b'/')[0])
    return save_list(res, fname, binary=True)


def lowe(fname):
    res = set()
    for x in enum_lines('https://pgl.yoyo.org/adservers/serverlist.php'
                        '?hostformat=hosts&mimetype=plaintext', b'#'):
        p = x.split()
        if len(p) != 2:
            mylib.err('tracker-list', 'Lowe: parsing error')
            continue
        res.add(p[1])
    return save_list(res, fname, binary=True)


def exodus(fname):
    res = set()
    url = 'https://etip.exodus-privacy.eu.org/trackers/export'
    json = mylib.download(url, isJSON=True)
    try:
        for entry in json['trackers']:
            net = entry['network_signature']
            if not net:
                continue
            net = net.replace('\\.', '.').replace('\\-', '-')
            for dom in net.split('|'):
                if dom[-1] in '/.':
                    continue
                if dom[0] in '\\.':
                    dom = dom[1:]
                res.add(dom)
    except KeyError:
        pass
    return save_list(res, fname, binary=False)


def combine_all(changes):
    final = mylib.path_root('src', 'lists', 'tracker_all.txt')
    if changes or not mylib.file_exists(final):
        print('  updating: tracker_all.txt')
    else:
        print('  no-change: tracker_all.txt')
        return
    res = set()
    for fname in ['custom.txt', 'lowe.txt',
                  'easylist.txt', 'easyprivacy', 'easyprivacy_int',
                  'exodus.txt', 'lockdown_clickbait.txt',
                  'lockdown_marketing.txt', 'lockdown_game_ads.txt']:
        for dom in mylib.read_list('tracker_' + fname):
            if dom == 'google.com':
                continue  # added by exodus, not a tracker per se
            res.add(dom[::-1])  # reverse for bintree lookup
    with open(final, 'w') as fp:
        for domain in sorted(res):
            fp.write(domain + '\n')


def process():
    print('downloading tracker domains ...')
    changes = []
    changes += customlist('custom.txt')
    changes += lowe('lowe.txt')
    changes += easylist('easylist.txt',
                        'easylist/easylist_adservers.txt')
    changes += easylist('easyprivacy.txt',
                        'easyprivacy/easyprivacy_trackingservers.txt')
    changes += easylist('easyprivacy_int.txt',
                        'easyprivacy/easyprivacy_trackingservers_international.txt')
    changes += exodus('exodus.txt')
    # changes += lockdown('lockdown_clickbait.txt', 'clickbait.txt')
    # changes += lockdown('lockdown_marketing.txt', 'marketing.txt')
    # changes += lockdown('lockdown_game_ads.txt', 'game_ads.txt')
    combine_all(changes)
    print('')
    return changes


if __name__ == "__main__":
    # combine_all()
    process()
