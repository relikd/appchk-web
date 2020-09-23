#!/usr/bin/env python3

import os
import lib_common as mylib
import lib_html as HTML


def gen_root():
    HTML.write(mylib.path_out(), '''
<h2>About</h2>
<div class="squeeze">
  <p>
    Information about the research project will be added soon. Stay tuned.
  </p>
  <a id="get-appcheck" class="no-ul" href="https://testflight.apple.com/join/9jjaFeHO" target="_blank">
    <img class="app-icon" src="/static/appcheck.svg" alt="app-icon" width="30" height="30">
    <p>
      Get the iOS App and contribute.<br />
      Join the TestFlight Beta.
    </p>
  </a>
  <p>
    The source code of the app is available <a href="https://github.com/relikd/appcheck/" target="_blank">on GitHub</a>.
  </p>
  <h2>Results</h2>
  <p>
    If you're just interested in the results, go ahead to see <a href="/index/apps/">all apps</a>.
  </p>
  <h2>Current research</h2>
  <p>
    We have an ongoing research project open. Your help is highly appreciated. <br>
    For mor infos follow <a href="/help/">this link</a>.
  </p>
</div>
''')


def gen_help():
    many = 7
    txt = '''<h2>Help needed!</h2>
<div class="squeeze"><p>
    With the release of iOS 14 some <a href="https://www.apple.com/ios/ios-14/features/#Privacy" target="_blank">Privacy</a> features are put into the spotlight.
    One of these features is making transparent how your data is being used for tracking purposes.
    Developers are now required to self-report their privacy practices.
  </p><p>
    We have selected a random sample of applications for evaluation and want to check whether the app behaviour changes over time.
    This study consists of two stages; this is the second.
    In the first stage we recorded the app communications before iOS 14 was released.
    In the second stage we repeat the process after the launch of iOS 14.
  </p><p>
    You can help us by providing app recordings of the following applications.
    Make sure to update to the lastest AppCheck version (v.34) which includes a check for the iOS version.
    Get the <a href="https://testflight.apple.com/join/9jjaFeHO" target="_blank">Testflight beta</a>.
  </p>
</div>
<div id="help-links">'''

    def app(bundle_id, name, appstore_id):
        iurl = 'https://apps.apple.com/de/app/id{}'.format(appstore_id)
        aref = '<a href="{}" target="_blank">AppStore</a>'.format(iurl)
        return '{} <span class="snd">Download from {}</span>'.format(
            HTML.a_app(bid, name), aref)

    def rec(count):
        return '<span class="{}"><b>{}</b>/{}</span> recordings'.format(
            'done' if count >= many else 'notyet', count, many)

    obj = mylib.json_read(mylib.path_root('src', 'help.json'))
    for land in sorted(obj.keys()):
        txt += '\n<h3>{}:</h3>\n<table>'.format(land)
        txt += HTML.tr(['', 'App Name', 'pre iOS 14', 'post iOS 14'], 'th')
        for i, x in enumerate(obj[land]):
            bid = x[2]
            c = [0, 0]
            for fname, json in mylib.enum_jsons(bid):
                try:
                    ios14 = int(json['ios'].split('.')[0]) >= 14
                except KeyError:
                    # assume everything submitted after release date is iOS14
                    ios14 = os.path.getmtime(fname) > 1600258000
                c[1 if ios14 else 0] += 1
            txt += HTML.tr([i + 1, app(bid, x[0], x[1]), rec(c[0]), rec(c[1])])
        txt += '</table>'
    txt += '</div>'
    HTML.write(mylib.path_out('help'), txt)


def gen_search():
    HTML.write(mylib.path_out(), '''
<h2>Redirecting …</h2>
<script type="text/javascript">
  var GET={};
  window.location.search.substr(1).split("&").forEach(function(x){GET[x.split("=")[0]]=x.split("=")[1]});
  if (GET["id"]) { window.location = "/app/" + GET["id"] + "/"; }
</script>''', fname='redirect.html')


def gen_404():
    HTML.write(mylib.path_out(), '''
<h2>404 – Not Found</h2>
<p>Go back to <a href="/">start page</a></p>''', fname='404.html')


def process():
    print('generating root html ...')
    gen_root()  # root index.thml
    gen_search()  # root redirect.html?id=my.bundle.id
    gen_help()
    gen_404()
    print('')


if __name__ == '__main__':
    process()
