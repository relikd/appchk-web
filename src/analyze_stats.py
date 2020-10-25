#!/usr/bin/env python3

import os
import shutil
import lib_common as mylib
import download_tracker

pp = ['flurry.com', 'facebook.com', 'admob.com', 'apple.com', 'tapjoyads.com',
      'crashlytics.com', 'ioam.de', 'amazonaws.com', 'chartboost.com',
      'googleadservices.com',
      'app-measurement.com', 'doubleclick.net', 'adjust.com', 'appsflyer.com'
      ]
study = ["com.amazon.AmazonDE", "com.innersloth.amongus", "ca.gc.hcsc.canada.covid19", "com.instructure.icanvas", "mobi.gameguru.fruitsurgeon", "com.google.GoogleMobile", "com.google.chrome.ios", "com.google.Classroom", "com.burbn.instagram", "com.mcdonalds.mobileapp", "com.microsoft.skype.teams", "com.netflix.Netflix", "com.yourcompany.PPClient", "com.randonautica.app", "com.toyopagroup.picaboo", "com.casual.stairwaytoheaven", "com.tmobile.nameid", "com.burbn.threads", "com.zhiliaoapp.musically", "com.triller.projectx", "com.atebits.Tweetie2", "com.ubercab.UberEats", "net.whatsapp.WhatsApp", "com.google.ios.youtube", "com.zello.client.main",
         "com.apm2studio.runawaychallenge", "com.adidas.app", "com.booking.BookingApp", "com.braindom", "es.aeat.pin24h", "de.rki.coronawarnapp", "com.Atinon.PassOver", "com.greeneking.orderandpay", "com.ingka.ikea.app", "it.ministerodellasalute.immuni", "it.pagopa.app.io", "fr.izly.izlyiphone", "lagamerie.mmv", "au.com.menulog.m", "com.apalonapps.radarfree", "it.poste.postebuy2", "com.neocortext.doublicatapp", "com.Celltop.SpiralRoll", "com.spotify.client", "com.qsdhbdft.stackblocks", "com.redforcegames.stack.colors", "ph.telegra.Telegraph", "com.eightsec.TriviaIO", "com.watched.play", "it.wind.mywind",
         "com.alipay.iphoneclient", "jp.go.mhlw.covid19radar", "au.gov.health.covidsafe", "com.AnkaStudios.DriveThru3D", "ru.mail.mail", "com.phone.lock", "com.magictouch.xfollowers", "video.like", "jp.naver.line", "com.cg.moneybuster", "com.tencent.mqq", "zzkko.com.ZZKKO", "com.viber", "com.vk.vkclient", "com.waze.iphone", "com.tencent.xin", "icacacat.wobble.man.upstairs", "ru.avito.app", "ru.city-mobil.taxi", "com.yueyou.cyreader", "cn.gov.tax.its", "jp.jmty.Jmty", "com.siwuai.duapp", "com.huaxiaozhu.rider", "com.autonavi.amap"]


def eval_analyze():
    ret = {x: 0 for x in pp}
    app_count = 0
    log_count = 0
    rec_count = [0, 0]
    rec_total = [0, 0]
    trkr_total = 0

    for bid in mylib.appids_in_out(['*']):
        app_count += 1
        for fname, json in mylib.enum_jsons(bid):
            # if json['duration'] > 40:
            i = 0 if bid in study else 1
            rec_count[i] += 1
            rec_total[i] += json['duration']
            for dom, logs in json['logs'].items():
                par = mylib.parent_domain(dom)
                l = len(logs)
                if par in pp:
                    ret[par] += l
                if download_tracker.is_tracker(dom):
                    trkr_total += l
                log_count += l

    print('Domain: Percent of requests')
    for k, x in ret.items():
        def in_pct(u):
            return round(u * 10000) / 100
        print(f'  {k}: {in_pct(x / log_count)}%')
    print('')

    print('Avg rec time')
    print(f'  study     {rec_total[0] / rec_count[0]} sec')
    print(f'  not study {rec_total[1] / rec_count[1]} sec')
    print('')

    trkr_prct = in_pct(trkr_total / log_count)
    print(f'Apps: {app_count}, Recordings: {sum(rec_count)}, Logs: {log_count}, Tracker: {trkr_prct}')
    print('')


def write_temporary_lists():
    one = mylib.path_data('_lists', 'groupby_ios-study-os14.json')
    two = mylib.path_data('_lists', 'list_ios-study-os14.json')
    mylib.json_write(one, {
        "name": "iOS 14 Study: Major OS Update",
        "desc": "Compares 75 randomly selected apps before and after iOS update.",
        "groups": [
        {
        "name": "iOS 13",
        "apps": ["com.amazon.AmazonDE", "com.innersloth.amongus", "ca.gc.hcsc.canada.covid19", "com.instructure.icanvas", "mobi.gameguru.fruitsurgeon", "com.google.GoogleMobile", "com.google.chrome.ios", "com.google.Classroom", "com.burbn.instagram", "com.mcdonalds.mobileapp", "com.microsoft.skype.teams", "com.netflix.Netflix", "com.yourcompany.PPClient", "com.randonautica.app", "com.toyopagroup.picaboo", "com.casual.stairwaytoheaven", "com.tmobile.nameid", "com.burbn.threads", "com.zhiliaoapp.musically", "com.triller.projectx", "com.atebits.Tweetie2", "com.ubercab.UberEats", "net.whatsapp.WhatsApp", "com.google.ios.youtube", "com.zello.client.main", "com.apm2studio.runawaychallenge", "com.adidas.app", "com.booking.BookingApp", "com.braindom", "es.aeat.pin24h", "de.rki.coronawarnapp", "com.Atinon.PassOver", "com.greeneking.orderandpay", "com.ingka.ikea.app", "it.ministerodellasalute.immuni", "it.pagopa.app.io", "fr.izly.izlyiphone", "lagamerie.mmv", "au.com.menulog.m", "com.apalonapps.radarfree", "it.poste.postebuy2", "com.neocortext.doublicatapp", "com.Celltop.SpiralRoll", "com.spotify.client", "com.qsdhbdft.stackblocks", "com.redforcegames.stack.colors", "ph.telegra.Telegraph", "com.eightsec.TriviaIO", "com.watched.play", "it.wind.mywind", "com.alipay.iphoneclient", "jp.go.mhlw.covid19radar", "au.gov.health.covidsafe", "com.AnkaStudios.DriveThru3D", "ru.mail.mail", "com.phone.lock", "com.magictouch.xfollowers", "video.like", "jp.naver.line", "com.cg.moneybuster", "com.tencent.mqq", "zzkko.com.ZZKKO", "com.viber", "com.vk.vkclient", "com.waze.iphone", "com.tencent.xin", "icacacat.wobble.man.upstairs", "ru.avito.app", "ru.city-mobil.taxi", "com.yueyou.cyreader", "cn.gov.tax.its", "jp.jmty.Jmty", "com.siwuai.duapp", "com.huaxiaozhu.rider", "com.autonavi.amap"]
        }, {
        "name": "iOS 14",
        "apps": ["com.amazon.AmazonDE.2", "com.innersloth.amongus.2", "ca.gc.hcsc.canada.covid19.2", "com.instructure.icanvas.2", "mobi.gameguru.fruitsurgeon.2", "com.google.GoogleMobile.2", "com.google.chrome.ios.2", "com.google.Classroom.2", "com.burbn.instagram.2", "com.mcdonalds.mobileapp.2", "com.microsoft.skype.teams.2", "com.netflix.Netflix.2", "com.yourcompany.PPClient.2", "com.randonautica.app.2", "com.toyopagroup.picaboo.2", "com.casual.stairwaytoheaven.2", "com.tmobile.nameid.2", "com.burbn.threads.2", "com.zhiliaoapp.musically.2", "com.triller.projectx.2", "com.atebits.Tweetie2.2", "com.ubercab.UberEats.2", "net.whatsapp.WhatsApp.2", "com.google.ios.youtube.2", "com.zello.client.main.2", "com.apm2studio.runawaychallenge.2", "com.adidas.app.2", "com.booking.BookingApp.2", "com.braindom.2", "es.aeat.pin24h.2", "de.rki.coronawarnapp.2", "com.Atinon.PassOver.2", "com.greeneking.orderandpay.2", "com.ingka.ikea.app.2", "it.ministerodellasalute.immuni.2", "it.pagopa.app.io.2", "fr.izly.izlyiphone.2", "lagamerie.mmv.2", "au.com.menulog.m.2", "com.apalonapps.radarfree.2", "it.poste.postebuy2.2", "com.neocortext.doublicatapp.2", "com.Celltop.SpiralRoll.2", "com.spotify.client.2", "com.qsdhbdft.stackblocks.2", "com.redforcegames.stack.colors.2", "ph.telegra.Telegraph.2", "com.eightsec.TriviaIO.2", "com.watched.play.2", "it.wind.mywind.2", "com.alipay.iphoneclient.2", "jp.go.mhlw.covid19radar.2", "au.gov.health.covidsafe.2", "com.AnkaStudios.DriveThru3D.2", "ru.mail.mail.2", "com.phone.lock.2", "com.magictouch.xfollowers.2", "video.like.2", "jp.naver.line.2", "com.cg.moneybuster.2", "com.tencent.mqq.2", "zzkko.com.ZZKKO.2", "com.viber.2", "com.vk.vkclient.2", "com.waze.iphone.2", "com.tencent.xin.2", "icacacat.wobble.man.upstairs.2", "ru.avito.app.2", "ru.city-mobil.taxi.2", "com.yueyou.cyreader.2", "cn.gov.tax.its.2", "jp.jmty.Jmty.2", "com.siwuai.duapp.2", "com.huaxiaozhu.rider.2", "com.autonavi.amap.2"]
        }]}, pretty=True)
    mylib.json_write(two, {
        "name": "iOS 14 Study: Selected Apps",
        "apps": ["com.google.chrome.ios", "com.google.chrome.ios.2", "com.ingka.ikea.app", "com.ingka.ikea.app.2", "com.mcdonalds.mobileapp", "com.mcdonalds.mobileapp.2", "com.microsoft.skype.teams", "com.microsoft.skype.teams.2", "com.Atinon.PassOver", "com.Atinon.PassOver.2", "com.Celltop.SpiralRoll", "com.Celltop.SpiralRoll.2", "com.redforcegames.stack.colors", "com.redforcegames.stack.colors.2"]
        }, pretty=True)


def move_ios14():
    # delete unrelated data
    for bid in mylib.appids_in_data(['*']):
        if bid not in study and bid[:-2] not in study:
            diir = mylib.path_data_app(bid)
            mylib.rm_dir(diir)
            print('del', diir)
            diir = os.path.dirname(diir)
            while not os.listdir(diir):
                print('del', diir)
                mylib.rm_dir(diir)
                diir = os.path.dirname(diir)
    # delete unrelated out
    for bid in mylib.appids_in_out(['*']):
        diir = mylib.path_out_app(bid)
        if bid not in study:
            if bid[:-2] not in study:
                print('del', diir)
            mylib.rm_dir(diir)
    for bid in study:
        diir = mylib.path_out_app(bid)
        try:
            shutil.copytree(diir, diir + '.2')
        except FileExistsError:
            pass
    # copy meta
    for bid in study:
        diir = mylib.path_data_app(bid)
        mylib.mkdir(mylib.path_add(diir, '2'))
        # continue
        for x in ['info_de', 'info_us', 'combined', 'evaluated']:
            try:
                shutil.copy(mylib.path_add(diir, x + '.json'),
                            mylib.path_add(diir, '2', x + '.json'))
            except:
                pass
        # move ios 14
        for fname, json in mylib.enum_jsons(bid):
            fiil = os.path.basename(fname)
            try:
                ios = json['ios'].split('.')[0]
            except KeyError:
                ios = '14'
            if ios == '14' and os.path.getmtime(fname) > 1600258000:
                mylib.mv(fname, mylib.path_add(diir, '2', fiil))
    write_temporary_lists()

# move_ios14()
eval_analyze()
