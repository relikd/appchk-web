#!/usr/bin/env python3

import common_lib as mylib


def gen_root():
    with open(mylib.path_out('index.html'), 'w') as fp:
        fp.write(mylib.template_with_base('''
<h2>About</h2>
<p class="squeeze">
  Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
  tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
  quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
  consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
  cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
  proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
</p>
  <a id="get-appcheck" href="https://testflight.apple.com/join/9jjaFeHO">
    <img src="/static/appcheck.svg" alt="app-icon" width="30" height="30">
    <p>
      Get the app and contribute.<br />
      Join the TestFlight Beta.
    </p>
  </a>{}'''. format('')))


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


if __name__ == '__main__':
    process()
