function lookup_domain_js(fname_a, fname_b, id1, id2, id3) {
  let dom = window.location.hash.substr(1);
  document.getElementById(id1).innerHTML = dom; // domain name
  let dom_app_list = document.getElementById(id3); // apps list
  let template = dom_app_list.firstElementChild;
  dom_app_list.innerHTML = 'loading…';

  // load reverse domains json
  loadJSON(fname_a, function(response) {
    let elem = JSON.parse(response)[dom];
    if (!elem || elem.length == 0) {
      document.getElementById(id2).innerHTML = '0 applications';
      dom_app_list.innerHTML = '– None –';
      return;
    }
    document.getElementById(id2).innerHTML = elem.length + ' applications';

    // load app name json
    loadJSON(fname_b, function(response) {
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
        item.querySelector('img').src = '/app/'+bid+'/icon.png';
        item.querySelector('.name').innerHTML = apps[i][1];
        item.querySelector('.detail').innerHTML = bid;
        dom_app_list.appendChild(item);
      }
    });
  });
}