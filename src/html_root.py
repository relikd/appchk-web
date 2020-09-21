#!/usr/bin/env python3

import os
import common_lib as mylib


def gen_root():
    with open(mylib.path_out('index.html'), 'w') as fp:
        fp.write(mylib.template_with_base('''
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
    If you're just interested in the results, go ahead to see <a href="/index/apps/1/">all apps</a>.
  </p>
  <h2>Current research</h2>
  <p>
    We have an ongoing research project open. Your help is highly appreciated. <br>
    For mor infos follow <a href="/help/">this link</a>.
  </p>
</div>
'''))


def gen_help():
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
    many = 7
    obj = mylib.json_read(mylib.path_root('src', 'help.json'))
    for land in sorted(obj.keys()):
        txt += '\n<h3>{}:</h3>\n<table>'.format(land)
        txt += '\n<tr><th></th><th>App Name</th><th>pre iOS 14</th><th>post iOS 14</th></tr>'
        for i, x in enumerate(obj[land]):
            bid = x[2]
            asurl = 'https://apps.apple.com/de/app/id{}'.format(x[1])
            count = [0, 0]
            for fname, json in mylib.enum_jsons(bid):
                try:
                    ios14 = int(json['ios'].split('.')[0]) >= 14
                except KeyError:
                    # assume everything submitted after release date is iOS14
                    ios14 = os.path.getmtime(fname) > 1600258000
                count[1 if ios14 else 0] += 1
            s1 = '<span class="{}"><b>{}</b>/{}</span> recordings'.format(
                'done' if count[0] >= many else 'notyet', count[0], many)
            s2 = '<span class="{}"><b>{}</b>/{}</span> recordings'.format(
                'done' if count[1] >= many else 'notyet', count[1], many)

            txt += '''
<tr><td>{}</td>
<td><a href="/app/{}/">{}</a> <span class="snd">Download from <a href="{}" target="_blank">AppStore</a></span></td>
<td>{}</td>
<td>{}</td>
</tr>'''.format(i + 1, bid, x[0], asurl, s1, s2)

        txt += '</table>'

    txt += '</div>'
    mylib.mkdir(mylib.path_out('help'))
    with open(mylib.path_out('help', 'index.html'), 'w') as fp:
        fp.write(mylib.template_with_base(txt))


def gen_search():
    with open(mylib.path_out('redirect.html'), 'w') as fp:
        fp.write(mylib.template_with_base('''
<h2>Redirecting …</h2>
<script type="text/javascript">
  var GET={};
  window.location.search.substr(1).split("&").forEach(function(x){GET[x.split("=")[0]]=x.split("=")[1]});
  if (GET["id"]) { window.location = "/app/" + GET["id"] + "/"; }
</script>'''))


def gen_404():
    with open(mylib.path_out('404.html'), 'w') as fp:
        fp.write(mylib.template_with_base('''
<h2>404 – Not Found</h2>
<p>Go back to <a href="/">start page</a></p>'''))


def process():
    print('generating root html ...')
    gen_root()  # root index.thml
    gen_search()  # root redirect.html?id=my.bundle.id
    gen_help()
    gen_404()
    print('')


if __name__ == '__main__':
    process()
