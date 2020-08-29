#!/usr/bin/env python3

import sys
import common_lib as mylib


def download_info(bundle_id, lang, force=False):
    if force or not mylib.meta_json_exists(bundle_id, lang):
        url = 'https://itunes.apple.com/lookup?bundleId={}&country={}'.format(
            bundle_id, lang.upper())
        json = mylib.download(url, isJSON=True)
        json = json['results'][0]
        # delete unused keys to save on storage
        for key in ['supportedDevices', 'releaseNotes', 'description',
                    'screenshotUrls']:
            try:
                del(json[key])
            except KeyError:
                continue
        mylib.json_write_meta(bundle_id, json, lang)


def download_icon(bundle_id, force=False, langs=['us', 'de']):
    # icon_file = mylib.path_data_app(bundle_id, 'icon.png')
    icon_file = mylib.path_out_app(bundle_id, 'icon.png')
    if force or not mylib.file_exists(icon_file):
        json = None
        for lang in langs:
            if not json:
                try:
                    json = mylib.json_read_meta(bundle_id, lang)
                except Exception:
                    continue
        mylib.download_file(json['artworkUrl100'], icon_file)


def download_missing_icons(force=False, langs=['us', 'de']):
    didAny = False
    for bid in mylib.enum_appids():
        if not mylib.file_exists(mylib.path_out_app(bid, 'icon.png')):
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
        return

    mylib.printf('  {} => '.format(bundle_id))
    for lang in ['us', 'de']:
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
        download_icon(bundle_id, force=force)
        mylib.printf('[✔] ')
    except Exception:
        mylib.printf('[✘] ')
        mylib.err('apple-download', 'img for ' + bundle_id, logOnly=True)
    print('')  # end printf line


def process(bundle_ids, force=False):
    print('downloading bundle info ...')
    if bundle_ids == ['*']:
        bundle_ids = list(mylib.enum_data_appids())

    for bid in bundle_ids:
        download(bid, force=force)
    print('')


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) > 0:
        process(args)
    else:
        # process(['*'], force=False)
        mylib.usage(__file__, '[bundle_id] [...]')
