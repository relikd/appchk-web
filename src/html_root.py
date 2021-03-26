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


def gen_privacy():
    HTML.write(mylib.path_out(), '''
<h2>Datenschutzerklärung (Webseite)</h2>
<p>Auf dieser Webseite werden keine personenbezogenen Daten erhoben.</p>
<p class="squeeze">
  Einige Daten werden jedoch technisch bedingt automatisch erfasst.
  Diese Daten werden von Ihrem Browser automatisch gesendet und beinhalten Browsertyp und -version, die Referrer-URL, Ihre IP-Adresse sowie Datum und Uhrzeit der Anfrage.
  Diese Daten werden explizit weder ausgewertet noch gespeichert.
</p>
<p>Bei offenen Fragen wenden Sie sich bitte an <a href="mailto:dominik.herrmann@uni-bamberg.de">dominik.herrmann@uni-bamberg.de</a>.</p>

<h2>Privacy Policy (Website)</h2>
<p>This website does not collect any personally identifiable information.</p>
<p class="squeeze">
  Some data is collected automatically by our IT systems when you visit the website.
  This technical data is sent automatically by your browser and includes the browser type and version, a referrer URL, your IP address, and date and time when you accessed the page.
  This data is explicitly neither evaluated nor stored.
</p>
<p>If you have further questions write an email to <a href="mailto:dominik.herrmann@uni-bamberg.de">dominik.herrmann@uni-bamberg.de</a>.</p>
''', fname='privacy.html')


def gen_appprivacy():
    HTML.write(mylib.path_out(), '''
<h2>Datenschutzerklärung (App)</h2>
<p>Die appchk app verarbeitet potentiell personenbeziehbare Daten.</p>
<p class="squeeze">
  Im Nachfolgenden werden diese Daten gelistet, die von der App erhoben und verarbeitet werden.
  Dies beinhaltet die Domainnamen der angesurften Webseiten bzw. von anderen Apps kontaktierte Domains, sowie das Datum und die Uhrzeit der Anfrage.
  Sofern ein App-Recording gestartet wird, wird außerdem die aktuelle Version des iOS Betriebssystems gespeichert.
  Andere als die genannten Daten werden nicht erhoben.
  Weiterhin werden diese Daten nur erhoben, solange der (lokale) VPN-Service aktiv ist.
  Wenn dieser Service inaktiv ist, werden keine Daten erhoben.
</p>
<p class="squeeze">
  Im Gegensatz zu einem konventionellen VPN Provider, verbindet sich dieser VPN-Service <strong>nicht</strong> zu einem anderen Server.
  Alle Daten werden ausschließlich auf dem eigenen Endgerät erfassten und gespeichert.
  Das heißt, diese Daten verlassen das eigene Gerät nicht und können demnach auch nicht von uns ausgewertet werden.
</p>
<p class="squeeze">
  Diese Daten werden nur an unsere Server (appchk.de) übermittelt, sofern der Nutzer / die Nutzerin der Übermittlung explizit zustimmt.
  Nutzer:innen haben weiterhin die Möglichkeit die erfassten Daten vor dem Upload zu filtern.
  Beim Übermitteln der Daten erhält der Server einen Zeitstempel der Anfrage.
  Andere Attribute wie Browsertyp, IP-Adresse, etc. werden, wie bei der Webseite, nicht ausgewertet oder gespeichert.
</p>
<p>Bei offenen Fragen wenden Sie sich bitte an <a href="mailto:dominik.herrmann@uni-bamberg.de">dominik.herrmann@uni-bamberg.de</a>.</p>

<h2>Privacy Policy (App)</h2>
<p>The appchk app collects potentially personally identifiable information.</p>
<p class="squeeze">
  The following section contains a list of the collected and processed data.
  This data includes the domain names of websites the user or another app contacted, as well as the date and time of the query.
  If the user starts an app-recording, the app will also store the current iOS version.
  Other than the listed data is not collected.
  Further, this data is only collected as long as the (local) VPN-service is active.
  As soon as this service is deactivated, no more data is collected.
</p>
<p class="squeeze">
  Contrary to conventional VPN providers, this VPN-service does <strong>not</strong> connect to another server.
  All collected data is processed and stored solely on the users end-device.
  This means that this data never leaves a user’s device and can therefore not be evaluated by us.
</p>
<p class="squeeze">
  This data is transmitted to our servers (appchk.de) only in the case if the user explicitly chooses to submit the data.
  Furthermore, users have the option to filter the data prior to upload.
  If the data is submitted, the server will also receive a timestamp of the upload.
  Other attributes like browser type, IP-address, etc. are, similarly to the website, not evaluated nor stored, similar.
</p>
<p>If you have further questions write an email to <a href="mailto:dominik.herrmann@uni-bamberg.de">dominik.herrmann@uni-bamberg.de</a>.</p>
''', fname='app-privacy.html')


def gen_imprint():
    HTML.write(mylib.path_out(), '''
<h2>Imprint / Impressum</h2>
<p>
  <strong>Lehrstuhl für Privatsphäre und Sicherheit in Informationssystemen (PSI)</strong><br>
  Otto-Friedrich Universität Bamberg<br>
  Kapuzinerstr. 16<br>
  96047 Bamberg<br>
  Germany
</p>
<p>Tel.: +49 951 863-2661</p>

<h3>Inhaltliche Verantwortlichkeit i.S.v. § 5 TMG und § 55 Abs. 2 RStV</h3>
<p>Für die Richtigkeit und Aktualität der Inhalte sind die jeweiligen Erstellerinnen und Ersteller der einzelnen Seiten verantwortlich.</p>
<p>
  Otto-Friedrich Universität Bamberg<br>
  Lehrstuhl für Privatsphäre und Sicherheit in Informationssystemen (PSI)<br>
  Prof. Dr. Dominik Herrmann<br>
  An der Weberei 5<br>
  96047 Bamberg<br>
  Deutschland<br>
  Tel.: +49 951 863-2661<br>
  E-Mail: <a href="mailto:dominik.herrmann@uni-bamberg.de">dominik.herrmann@uni-bamberg.de</a>
</p>

<h3>Technische Verantwortlichkeit</h3>
<p>
  <strong>Webmaster/in:</strong><br>
  Prof. Dr. Dominik Herrmann<br>
  Tel.: +49 951 863-2661<br>
  E-Mail: <a href="mailto:dominik.herrmann@uni-bamberg.de">dominik.herrmann@uni-bamberg.de</a>
</p>''', fname='imprint.html')


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
    Make sure to update to the lastest appchk version (v.34) which includes a check for the iOS version.
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
        print('  imprint.html')
        gen_imprint()
        print('  privacy.html')
        gen_privacy()
        print('  app-privacy.html')
        gen_appprivacy()
    # print('  /help/')  # dynamic content
    # gen_help()
    print('  /results/')  # dynamic content
    gen_results(mylib.path_out('results'), app_count, dom_count,
                title='Results')
    print('')


if __name__ == '__main__':
    process(-1, -1, inclStatic=True)
