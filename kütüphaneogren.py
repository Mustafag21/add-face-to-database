import cv2
import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt
import sqlite3
veritabani="MYDATABASE'M.db" #burada veritabanı adını belirtiyoruz.
veritabani_var_mi = False    #bu kod ile veri tabanın varlığını yok olarak atıyoruz.
try:
    with open(veritabani):   # try except ile veri tabanın varlığını sorgulayıp açıyoruz.
        veritabani_var_mi = True
except FileNotFoundError:
    veritabani_var_mi = False  #
veritabani = sqlite3.connect(veritabani) #Bu kod ile veri tabanı oluşturuyoruz.
imlec = veritabani.cursor() #veri tabanıma üzerinden sorgu yapmak için bir bağlantı sağlıyoruz.
beklem_suresi=3             #işlem yapıldıktan sonra kullanıcının yeni işlem için beklme süresi
if not veritabani_var_mi:   #burada veritabanının varlığını kontrol eder ve eğer oluşturulmamış ise oluşturur
    imlec.execute('''
            CREATE TABLE IF NOT EXISTS fotograflar (
                id INTEGER PRIMARY KEY,
                dosya_yolu BLOB,
                ad TEXT,
                soyad TEXT,
                kayit_tarihi TEXT,
                kullanici_id INTEGER
            
            )
        ''')
    foto_sayac = 0
else:                       #Eğer veri tabanı var ise
    imlec.execute("SELECT MAX(id) FROM fotograflar") # veri tabanında ki en büyük ID değerini bulmak için
    son_foto_id = imlec.fetchone()[0]     # Bu ifade, SELECT sorgusundan dönen sonucun ilk satırını alır. Bu durumda, en büyük ID değerini içerir.
    foto_sayac = son_foto_id if son_foto_id is not None else 0 #Bu ifade, eğer son_foto_id değeri None değilse, foto_sayac değişkenine son_foto_id değerini atar; aksi halde foto_sayac'ı 0 olarak ayarlar.

deneme_sayacı=0
while (True):
    gecerli_zaman = time.localtime() #Burda ki  kod ile güncel saat ve tarih bilsini istiyoruz.
    biçimli_zaman = time.strftime("%d-%m-%Y ", gecerli_zaman)#burada ki kod ile gelen zaman bilgisini GÜN/AY/YIL şeklinde biçimlendirme yapıyoruz.
    biçimli_zaman2=time.strftime("%H:%M:%S")#burada ki kod ile gelen zaman bilgisini SAAT/DAKİKA/SANİYE olarak biçimlendirme yapıyoruz.
    print("\nMERHABA Kullanıcı Bugün'ün Tarihi:", biçimli_zaman, "Ve Şuan Saat:", biçimli_zaman2) #Burada güncel tarih ve saat bildisini kullanıcıya gönderiyoruz
    print("\n VERİ TABANINA YÜZ KAYDETMEK İSİYORSANIZ 1 TUŞUNA BASININZ \n "   # yazdır fonk. ile kullanıcaya şeçenekler sunuyoruz.
          "VERİ TABANINDAKİ GÖRÜNTÜLERİ GÖRMEK İSTİYORSANIZ 2 TUŞUNA BASINIZ\n "
          "VERİ TABANINDAKİ VERİLERİ SİLMEK İÇİN 3'E BASINIZ\n ")
    cevap = int(input("lütfen şeçiminizi giriniz:"))                    # Kullanıcıdan bir şeçim için cevap istiyoruz.
    if cevap==1:        #Kullanıcının cevabı 1 ise
        kaydedilen_fotograflar = set(row[0] for row in imlec.fetchall()) #Kod ile veri tabanına kaydedilen fotoğrafların benzersiz olmasını sağlıyoruz
        kaydetme = False
        yuz_detektoru = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml') #Görüntü kaydetmek için bir yüz dedektörü tanımlıyoruz
        camera=cv2.VideoCapture(0) #bu ifade ile Kameraya erişip camera değişkenine atıyoruz.

        while True: # içteki kodların tekrarlanması için bir sonsuz döngü açıyoruz
            ret, frame = camera.read() #camerayı açıyoruz ve dönen 2 değeri ret, frame değişkenlerine atıyoruz.
            if not ret:# burada ret değeriyle görüntü alınımında sorun olup olmadığını kontrol ediyoruz eğer sorun var ise
                break #kontrolden çık
            frame = cv2.resize(frame, (1000, 500)) # burda gelen görüntü çerçevesini boyutlandırır
            frame = cv2.flip(frame, 1)  # bu kod ile görüntüyü ekranda yatay olarak yani düz görmemize yardımcı olur
            faces = yuz_detektoru.detectMultiScale(frame, scaleFactor=1.1, minNeighbors=5, minSize=(150, 150)) # burda yüz çerçevesi için bir boyutladırma yaptık ve faces değişkenine atadık
            for (x, y, w, h) in faces: # Bu dögü ile bir yüz tespiti için kordinat belirlermek için dögü açtık
                cv2.rectangle(frame, (x, y), (x + w + 10, y + h + 20 ), (50, 200, 50), 2) #bu oluşturlacak diktörgenin başlangıç ve bitiş kordinatlarını ve renk bilgilerini girdik
                face_image = frame[y:y + h , x:x + w ] # burda ise yüzün sınırlarını belirledik
                k = cv2.waitKey(1) # burda bir tuşa basmak için bekleyen durumun ASCII kodunu k değişkenine atadık
                if k & 0xFF == ord('q'): # burada eğer kullanıcı q tuşuna basar ise
                    camera.release() #camera yı kapat
                    cv2.destroyAllWindows() # tüm pencereleri kapat
                    continue # ve devam et
                elif k & 0xFF == ord('k') and not kaydetme: #eğer kullanıcı K tuşuna basar ise
                    gecerli_zaman = time.strftime("%d-%m-%Y", time.localtime()) #gecerli_zaman değişkenine şuan ki tarih bilgisini ata
                    kaydetme = True
                    foto_sayac += 1
                    kullanici_id = 1
                    if kaydetme: # eğer kaydetme aktif ise
                        _, buffer = cv2.imencode('.jpg', face_image) #alınınan görüntüyü jpeg formatında buffer değişkenine ata
                        resim_blob = buffer.tobytes() # gelen jpeg fotmatındaki görüntüyü byte dizisine dönüşütr ve resim_blob değişkenine ata

                        if resim_blob not in kaydedilen_fotograflar: #gelen resim_blob görüntüsünü kaydedilen fotoğralarda yok ise
                            kaydedilen_fotograflar.add(resim_blob) #kaydedilen fotoğraflar değişkenine ekle
                            ad = str(input("\nLÜTFEN İSİM GİRİNİZ:")) #ekleme işleminden sonra veri tabanındaki fotoğrafa ait isim
                            soyad = str(input("LÜTFEN SOYİSİM GİRİNİZ:")) #ve soy isim bilgilerini kullanıcıdan iste
                            imlec.execute("INSERT INTO fotograflar (ad,soyad,dosya_yolu,kayit_tarihi,kullanici_id) VALUES (?, ?,?,?,?)",(ad,soyad,resim_blob,gecerli_zaman,kullanici_id)) # gelen değerlerini veri tabanına işle
                            veritabani.commit() # yapılan değişikleri kalıcı olarak veri tabanına işle
                            camera.release() #işlemlerden sonra camera kapa
                            cv2.destroyAllWindows()# ve tüm pencereleri kapa
                            print(f"{foto_sayac}.Yüz kayıt işlemi tamamlandı. Lütfen bekleyin...") # kaçıncı fotoğrafın kaydedildiğini yazdır
                            time.sleep(beklem_suresi) #işlemler bittikten sonra kullanıcının bekleme süresi ile beklet
                            continue # ve devam et
                        else: # eğer görüntü kaydedilen fotoğraflarda var ise
                            print(f"{foto_sayac}. Görüntü zaten kaydedildi.") # kullanıcıya yüzün zaten veri tabanında olduğunu bildir
                        kaydetme = False # ve kaydetmeyi tekrar false durumuna döndür
            cv2.imshow("Camera", frame) #camera adılı pencereye gelen görüntüyü aç
        continue # ve devam et


    elif cevap == 2: # kullanıcının cevabı 2 ise

        imlec.execute("SELECT dosya_yolu FROM fotograflar") #fotoğraflar tablosundan dosyalundaki verileri sorgula
        resim_kayitlari = imlec.fetchall() # çekilen verileri resim_kayıtları değişkenine ata

        if resim_kayitlari:  # Eğer resim kayıtları varsa
            for i, resim_kaydi in enumerate(resim_kayitlari): # bu döngü ile her bir kayıdın ve kayıt numarasını içinde dön
                resim_blob = resim_kaydi[0] # her resim kaydının ilk sütununu resim_blob a ata
                buffer = np.frombuffer(resim_blob, dtype=np.uint8) # gelen resim_blob formatını numpy dizisine çevir
                resim = cv2.imdecode(buffer, flags=cv2.IMREAD_GRAYSCALE)#Bu satır, resim verisini NumPy dizisinden okuyarak bir resim nesnesine dönüştürür. cv2.IMREAD_GRAYSCALE ifadesi, resmi gri tonlamalı (grayscale) olarak okumak için kullanılır.
                if resim is not None: #resim başarılı bir şekilde okunmuş ise kod bloğunu çalıştırır
                    plt.imshow(resim, cmap='gray') # resim değişkenini gri şekilde ekrana yazdırır
                    plt.title(f"Resim {i + 1}") # kaçıncı resim bilgisini verir
                    plt.show() # ve görüntüler
        else: # eğer resim kayıtları yok ise
            print("Veri Tabanında hiç resim bulunmamaktadır.") # veri tabanında resim olmadığını kullanıcıya bildirir
        print("Görüntü bukadardı. Lütfen bekleyin...") # ve kullanıcıyı beklemesi için bilgilendirir
        time.sleep(beklem_suresi) # kullanıcı bekleme zamanı
        continue #ve devam et
    elif cevap==3: #eğer kullanıcı cevap olara 3 verirse
        imlec.execute("DELETE FROM fotograflar")  # VERİ TABANINDAN SİLME İŞLEMİ YAPAR
        veritabani.commit()  # VERİYİ Silmek için erişim sağlar
        print("kayıt silme işlemi tamamlandı. Lütfen bekleyin...") # ve kullanıcının beklemesini bildirir
        time.sleep(beklem_suresi) #kullanıcı bekleme süresi
        continue # ve devam et
    else:
        print("HATALI TUŞLAMA YAPTINIZ TEKRAR DENEYİNİZ") # kullanıcı cevap olarak yanlış değer girerse uyayrır
        deneme_sayacı+=1 # kullanıcı yanlış değer girme sayısını tutar
        if deneme_sayacı==3: # eğer kullanıcı 3 defa yanlış değer girerse
            print("MAALESEF YARDIMCI OLAMIYORUZ") #kod bloğunu kapatır
            break