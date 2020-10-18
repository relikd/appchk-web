#!/usr/bin/env python3

import os
import shutil
import lib_common as mylib

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

    print(f'Apps: {app_count}, Recordings: {sum(rec_count)}, Logs: {log_count}')
    print('')


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
                if json['ios'].split('.')[0] == '14':
                    mylib.mv(fname, mylib.path_add(diir, '2', fiil))
            except KeyError:
                pass


move_ios14()
