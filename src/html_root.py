#!/usr/bin/env python3

import os
import lib_common as mylib
import lib_html as HTML
import index_rank  # get_total_counts


def gen_root():
    with open(mylib.path_root('templates', 'root.html'), 'r') as fp:
        HTML.write(mylib.path_out(), fp.read())


def gen_redirect():
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
        txt += '\n<h3>{}:</h3>\n<table class="alternate">'.format(land)
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


def gen_results(base_dir, c_apps, c_domains, title):
    [c_recs, c_logs] = index_rank.get_total_counts()
    print('    {} apps'.format(c_apps))
    print('    {} domains'.format(c_domains))
    print('    {} recordings'.format(c_recs))
    print('    {} logs'.format(c_logs))
    HTML.write(base_dir, '''
<h2>{}</h2>
<p>The appchk database currently contains <b>{:,}&nbsp;apps</b> with a total of <b>{:,} unique domains</b>.</p>
<p>Collected through <b>{:,}&nbsp;recordings</b> with <b>{:,} individual requests</b>.</p>
<ul>
  <li>List of <a href="/index/apps/">Apps</a></li>
  <li>List of <a href="/category/">Categories</a></li>
  <li>List of <a href="/index/domains/all/">All Domains</a>, 
  only <a href="/index/domains/tracker/">Trackers</a>,
  or <a href="/index/domains/highly-used/">Highly-used Domains</a> <br>which appear in at least 5 apps but are not considered tracker <i>yet</i>.</li>
</ul>
<ul>
  <li>Compare <a href="/lists/">App Lists</a></li>
  <li>Compare <a href="/compare/">Group Lists</a></li>
</ul>
'''.format(title, c_apps, c_domains, c_recs, c_logs), title=title)
    mylib.symlink(index_rank.fname_app_rank(),
                  mylib.path_add(base_dir, 'rank.json'))  # after HTML.write


def process(app_count, dom_count, inclStatic=False):
    print('generating root html ...')
    if inclStatic:
        print('  index.html')
        gen_root()  # root index.thml
        print('  redirect.html')
        gen_redirect()  # root redirect.html?id=my.bundle.id
        print('  404.html')
        gen_404()
    # print('  /help/')  # dynamic content
    # gen_help()
    print('  /results/')  # dynamic content
    gen_results(mylib.path_out('results'), app_count, dom_count,
                title='Results')
    print('')


if __name__ == '__main__':
    process(-1, -1, inclStatic=True)
