#!/usr/bin/env python3

import sys
import common_lib as mylib

AVAILABLE_LANGS = ['us', 'de']  # order matters


def fname_for(bundle_id, lang):
    return mylib.path_data_app(bundle_id, 'info_{}.json'.format(lang))


def read_from_disk(bundle_id, lang):
    return mylib.json_read(fname_for(bundle_id, lang))


def enum_all_from_disk(bundle_id):
    for lang in AVAILABLE_LANGS:
        try:
            yield lang, read_from_disk(bundle_id, lang)
        except Exception:
            pass


def get_app_names(bundle_id):
    return {lang: json['trackCensoredName']
            for lang, json in enum_all_from_disk(bundle_id)}


def enum_genres(bundle_id):
    for lang, json in enum_all_from_disk(bundle_id):
        for gid, name in zip(json['genreIds'], json['genres']):
            yield lang, gid, name


def download_info(bundle_id, lang, force=False):
    fname = fname_for(bundle_id, lang)
    if force or not mylib.file_exists(fname):
        url = 'https://itunes.apple.com/lookup?bundleId={}&country={}'.format(
            bundle_id, lang.upper())
        json = mylib.download(url, isJSON=True)
        json = json['results'][0]
        # delete unused keys to save on storage
        mylib.try_del(json, ['supportedDevices', 'releaseNotes', 'description',
                             'screenshotUrls', 'ipadScreenshotUrls'])
        mylib.json_write(fname, json, pretty=True)


def needs_icon_path(bundle_id):
    icon_file = mylib.path_out_app(bundle_id, 'icon.png')
    return (mylib.file_exists(icon_file), icon_file)


def download_icon(bundle_id, force=False, langs=AVAILABLE_LANGS):
    exists, icon_file = needs_icon_path(bundle_id)
    if force or not exists:
        json = None
        for lang in langs:
            if not json:
                try:
                    json = read_from_disk(bundle_id, lang)
                except Exception:
                    continue
        image_url = json['artworkUrl100']  # fail early on KeyError
        is_new = mylib.mkdir_out_app(bundle_id)
        mylib.download_file(image_url, icon_file)
        return is_new
    return False


def download_missing_icons(force=False, langs=AVAILABLE_LANGS):
    didAny = False
    for bid in mylib.appids_in_out():
        exists, _ = needs_icon_path(bid)
        if not exists:
            if not didAny:
                print('downloading missing icons ...')
                didAny = True
            print('  ' + bid)
            download_icon(bid, force=force, langs=langs)
    if didAny:
        print('')
    return didAny


def download(bundle_id, force=False):
    if not mylib.valid_bundle_id(bundle_id):
        mylib.err('apple-download', 'invalid id: ' + bundle_id)
        return False

    exists, _ = needs_icon_path(bundle_id)
    if exists and not force:
        return False

    mylib.printf('  {} => '.format(bundle_id))
    for lang in AVAILABLE_LANGS:
        try:
            mylib.printf(lang)
            download_info(bundle_id, lang, force=force)
            mylib.printf('[✔] ')
        except Exception:
            mylib.printf('[✘] ')
            mylib.err('apple-download', 'json {}: {}'.format(
                      lang.upper(), bundle_id), logOnly=True)
    try:
        mylib.printf('icon')
        index_needs_update = download_icon(bundle_id, force=force)
        mylib.printf('[✔] ')
    except Exception:
        index_needs_update = False
        mylib.printf('[✘] ')
        mylib.err('apple-download', 'img for ' + bundle_id, logOnly=True)
    print('')  # end printf line
    return index_needs_update


def process(bundle_ids, force=False):
    print('downloading bundle info ...')
    newly_created = set()
    for bid in mylib.appids_in_data(bundle_ids):
        if download(bid, force=force):
            newly_created.add(bid)
    print('')
    return newly_created


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) > 0:
        process(args)
    else:
        # process(['*'], force=False)
        mylib.usage(__file__, '[bundle_id] [...]')
