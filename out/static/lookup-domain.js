function lookup_domain_js(fname_doms, fname_apps, fname_subs) {
  let dom = window.location.hash.substr(1); // domain name
  document.getElementById('name').innerHTML = dom;
  let dom_num_apps = document.getElementById('num-apps');
  let dom_app_list = document.getElementById('app-toc');
  let dom_sub_doms = document.getElementById('subdoms');
  let dom_known_trkr = document.getElementById('known');
  let template = dom_app_list.firstElementChild;
  dom_app_list.innerHTML = 'loading…';

  // load reverse domains json
  loadJSON(fname_doms, function(response) {
    let elem = JSON.parse(response)[dom];
    let count = elem.length - 1;
    if (!elem || count < 1) {
      dom_num_apps.innerHTML = '0 applications';
      dom_app_list.innerHTML = '– None –';
      return;
    } else if (count == 1) {
      dom_num_apps.innerHTML = '1 application';
    } else {
      dom_num_apps.innerHTML = elem.length - 1 + ' applications';
    }
    dom_known_trkr.innerHTML = elem[0] ? 'Yes' : 'No';

    // load app name json
    loadJSON(fname_apps, function(response) {
      let name_list = JSON.parse(response);
      var apps = [];
      for (var i = elem.length - 1; i >= 0; i--) {
        let bndl = name_list[elem[i]];
        if (!bndl) { continue; }
        apps.push([bndl[0], bndl[1], bndl[1].toLowerCase()]);
      }
      apps.sort(function(a, b){return a[2] < b[2] ? -1 : a[2] > b[2] ? 1 : 0});

      dom_app_list.innerHTML = null;
      for (var i = 0; i < apps.length; i++) {
        let bid = apps[i][0];
        let item = template.cloneNode(true);
        item.href = '/app/'+bid+'/';
        let img = item.querySelector('img');
        img.classList = 'lozad';
        img.setAttribute('data-src', '/app/'+bid+'/icon.png');
        item.querySelector('.name').innerHTML = apps[i][1];
        item.querySelector('.detail').innerHTML = bid;
        dom_app_list.appendChild(item);
      }
      const observer = lozad(); observer.observe();

      if (!dom_sub_doms) { return }
      loadJSON(fname_subs, function(response) {
        let subdomains_list = JSON.parse(response)[dom];
        if (subdomains_list) {
          var src = '';
          for (var i = 0; i < subdomains_list.length; i++) {
            let sub = subdomains_list[i];
            let full = sub ? sub + '.' + dom : dom;
            let lnk = '<a href="/subdomain/#' + full + '">' + sub + '.</a> ';
            src += lnk;
          }
          dom_sub_doms.innerHTML = src;
        } else {
          dom_sub_doms.innerHTML = '– None –';
        }
      });
    });
  });
}