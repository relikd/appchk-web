#!/usr/bin/env python3

import common_lib as mylib


def gen_root():
    with open(mylib.path_out('index.html'), 'w') as fp:
        fp.write(mylib.template_with_base('''
<h2>About</h2>
<p>
  Information about the research project will be added soon. Stay tuned.
</p>
<a id="get-appcheck" class="no-ul" href="https://testflight.apple.com/join/9jjaFeHO" target="_blank">
  <img src="/static/appcheck.svg" alt="app-icon" width="30" height="30">
  <p>
    Get the iOS App and contribute.<br />
    Join the TestFlight Beta.
  </p>
</a>
<p>
  The source code of the app is available <a href="https://github.com/relikd/appcheck" target="_blank">on GitHub</a>.
</p>
<h2>Results</h2>
<p>
  If you're just interested in the results, go ahead to <a href="/index/page/1">all apps</a>.
</p>
<h2>Current research</h2>
<p>
  We have an ongoing research project open. Your help is highly appreciated. <br>
  For mor infos follow <a href="/help">this link</a>.
</p>
'''))


def gen_help():
    many = 7
    txt = '''<h2>Help needed!</h2>
<p>
    This study contains two stages. This is the first one.
    We have selected a random sample of applications for evaluation.
    We want to track the app behviour over a longer period of time.
</p><p>
    You can help us by providing app recordings of the following application.
    The more you record the better. 
    Ideally you could do recordings for all the apps below.
    But really, even if you only find time for a single recording, anything helps!
</p><p>
    We need at least {} recordings per app. Stage 2 will follow in a few weeks.
    Get the <a href="https://testflight.apple.com/join/9jjaFeHO" target="_blank">Testflight beta</a>.
</p>
<div class="help-links">'''.format(many)
    obj = mylib.json_read(mylib.path_root('src', 'help.json'))
    for land in sorted(obj.keys()):
        txt += '\n<h3>{}:</h3>\n<table>'.format(land)
        for i, x in enumerate(obj[land]):
            bid = x[2]
            asurl = 'https://apps.apple.com/de/app/id{}'.format(x[1])
            try:
                count = len(mylib.json_read_combined(bid)['rec_len'])
            except Exception:
                count = 0

            rr = '<span class="{}"><b>{}</b>/{}</span> recordings'.format(
                'done' if count >= many else 'notyet', count, many)

            txt += '''
<tr><td>{0}</td>
<td><a href="/app/{1}/index.html">{2}</a></td>
<td>{3}</td>
<td><a href="{4}" target="_blank">{4}</a></td>
</tr>'''.format(i + 1, bid, x[0], rr, asurl)

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
  if (GET["id"]) { window.location = "/app/" + GET["id"] + "/index.html"; }
</script>'''))


def process():
    print('generating root html ...')
    gen_root()  # root index.thml
    gen_search()  # root redirect.html?id=my.bundle.id
    gen_help()


if __name__ == '__main__':
    process()
