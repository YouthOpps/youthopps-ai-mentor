# YouthOpp AI Mentor — Araştırma ve teknik plan

Durum: Araştırma planı korundu; kullanıcı onayıyla mock verili ilk prototip geliştirildi.
Araştırma tarihi: 15 Ekim 2026.
Hedef kaynak: https://www.youthopps.org/

## 1. Güncel araştırma sonucu ve erişim

Kullanıcının ağ izni değişikliğinden sonra yeniden test edildi. Hem
https://youthopps.org/ hem https://www.youthopps.org/ ana sayfası HTTP 200
verdi. Alt sayfalar www üzerinden HTTP 200 ile incelendi; çıplak alan
adındaki alt sayfa denemelerinde HTTP 403 alındı. Bu farkın nedeni
belirlenmedi; sitenin genel olarak erişilemez olduğu sonucu çıkarılmadı.
HTML canonical adresleri çıplak alan adını gösteriyor.

Önceki proxy engeli güncel araştırmayı artık durdurmuyor. Ana sayfa,
kategori ve detay HTML'leri, mimari belgeleri, kaynak politikası,
robots.txt, sitemap, istemci JavaScript'i ve bir statik JSON indeksi
okundu. Tarayıcıda görsel/etkileşimli test yapılmadı; listeleme davranışı
HTML, JavaScript ve yayımlanmış belgeler üzerinden araştırıldı.

Site kendini “YouthOpp / Open opportunity index” olarak tanımlıyor.
Youth Opportunities (youthop.com), bu indeksin kaynaklarından yalnızca
biri; youthopps.org ile aynı site kabul edilmemeli. Ayrıca doğrudan kurum
kaynakları ve başka derleyiciler var. Site kayıtları bağımsız keşif
kayıtlarıdır; başvuru ve uygunluk için yayıncıya yönlendirir.

## 2. Fırsatlar nasıl listeleniyor?

Ana sayfada araştırma anında **7.663 listing** yazıyordu. Bu sayı zamanla
değişebilir; başvurusu açık fırsat sayısı anlamına gelmez.

- Kategoriler: scholarships, internships, fellowships, volunteering,
  training, jobs, competitions, grants; filtrede ayrıca other bulunuyor.
- Liste tablosu: fırsat başlığı/türü, kaynak kurum ve web sitesi,
  destination (hedef ülke), deadline. Başlık /opportunity/<id>/ detayına,
  kaynak kurum /sources/publisher/<source-id>/ sayfasına bağlanıyor.
- /opportunities/ ve kategori sayfalarında 30 kayıt/sayfa; staj arşivinin
  HTML gezinmesinde 33 sayfa var. Statik yollar /page/2/ biçiminde;
  JavaScript arama durumunu URL sorgu parametreleriyle de saklıyor.
- Filtre adları: q (metin), country (yayıncı ülkesi), destination (hedef),
  category, source, eligible (başvuran ülkesi). Yayıncı ülkesini kişinin
  vatandaşlığı veya fırsatın gerçekleştiği ülke sanmamak gerekiyor.
- Belgelenen ve JavaScript'in çağırdığı sıralama: süresi dolmamış tarihli
  kayıtlar yakın tarihe göre, tarihi bilinmeyenler, sonra süresi geçmişler;
  eşit tarihte kayıt kimliği. Filtreler tüm koleksiyona sayfalamadan önce
  uygulanıyor. Statik sayfalar JS olmadan okunabiliyor; arama ve canlı
  süre kontrolü JavaScript gerektiriyor.
- Detaylar: başlık, tür, varsa kısa özet; Destination, Who may apply,
  Deadline, Published, Last checked, Publisher, kaynak atfı ve dış
  “Read the original & apply” bağlantısı. Bu bağlantı bazen başka bir
  derleyiciye gidiyor; mutlaka doğrudan organizatör başvurusu değil.

İncelenen örnekler (hepsi www üzerinde HTTP 200):

| Tür | Fırsat / detay yolu | Gözlem |
| --- | --- | --- |
| Burs | [DAAD EPOS 2027](https://www.youthopps.org/opportunity/youth-opportunities-59140/) | Özet uygun ülkeleri metinle veriyor; yapılandırılmış uygunluk ve destination eksik; youthop.com'a yönlendiriyor |
| Burs | [Fulbright – Indiana University](https://www.youthopps.org/opportunity/0e4a05e909f2d1e9c849375e/) | İkinci burs detay örneği; özgün dilde başlık |
| Fellowship | [UMAPS 2027–2028](https://www.youthopps.org/opportunity/youth-opportunities-59479/) | Ülke ve aday gösterilme koşulu özette; Who may apply alanı bilinmiyor |
| Fellowship | [African Climate Collaborative](https://www.youthopps.org/opportunity/youth-opportunities-59546/) | İkinci fellowship detay örneği |
| Staj | [WBI CIRC SEE](https://www.youthopps.org/opportunity/c4ecbf2fc9104fe59f63eb2e/) | Fransa; aylık 1.400 avro ve 500 avroya kadar seyahat desteği özette; son tarih 2026-11-13; öğrenci koşulu özette |
| Staj | [Remote journalist/content creator](https://www.youthopps.org/opportunity/youth-for-europe-97980/) | Ücretsiz/uzaktan bilgisi başlıkta; destination ve uygunluk bilinmiyor; son tarih 2026-12-02 |

Önemli ayrıştırma ayrıntısı: ham HTML'de `Expired` etiketi `hidden`
özniteliğiyle bulunabiliyor. Sadece düz metinde bu kelimeyi bulmak,
fırsatın süresinin geçtiği anlamına gelmez. Tarih ve görünürlük mantığı
kullanılmalı. Site belgeleri yalnızca gün içeren tarihler için UTC gün
sonunu kullanıyor; özgün yayıncının gerçek saat dilimi yine teyit edilmeli.

## 3. API, RSS, JSON ve izinler

### Doğrulanan teknik erişim yolları

| Yol | Sonuç | Değerlendirme |
| --- | --- | --- |
| [robots.txt](https://www.youthopps.org/robots.txt) | 200; User-agent: *, Allow: /; sitemap bağlantısı | Genel tarama engeli yok; yeniden kullanım lisansı değil |
| [sitemap.xml](https://www.youthopps.org/sitemap.xml) | 200; sayfa ve kaynak bazlı alt sitemap'ler | URL keşfi için kullanılabilir |
| https://www.youthopps.org/feed/ | 404 | Bu aday RSS adresi yok; tüm olası RSS adreslerinin yokluğunu kanıtlamaz |
| https://www.youthopps.org/wp-json/ | 404 | Bu WordPress API adayı yok; başka API yok demek değildir |
| /assets/collection.966583482b8b7416.json | 200; 966 staj kaydı | Kategori HTML'inin data-index özniteliğinden keşfedilen gerçek arama indeksi |
| GitHub data-source JSON | 200; örnek kaynakta 417 kayıt | Site mimari belgesinin doğrudan bağlantı verdiği yapılandırılmış anlık görüntü |

İncelenen ana sayfa, docs, mimari, kaynak politikası ve kategori sayfalarında
belgelenmiş bir genel sorgu API'si veya RSS/Atom keşif bağlantısı bulunmadı.
“Resmî API kesinlikle yok” sonucu çıkarılmıyor. Bu mimari statik web
sayfaları ve koleksiyon indeksleri kullanıyor; canlı uygulama sunucusu
veya belgelenmiş API sözleşmesi sunulduğuna dair kanıt bulunmadı.

Statik staj indeksi alanları: id, deadline (sayısal zaman), html, search,
category, source, country, destination, eligible. Filtrelenmiş sonuçlar
istemcide hesaplanıyor; URL'deki q parametresini sunucu API'si sanmamalı.
İndeks adresi içerik hash'i taşıyor; sabit kodlanmamalı, ilgili HTML'den
keşfedilmeli. html parçası uygulamada güvenilir komut veya doğrudan
render edilebilir içerik kabul edilmemeli.

### Tercih edilen veri adayı: data-source

[Mimari belgesi](https://www.youthopps.org/docs/architecture/) şu akışı
anlatıyor: yayıncı → data-pipeline → data-source → statik site.
[Veri deposu](https://github.com/YouthOpps/data-source) her kaynak için
`datas/<source-id>/data.json` ve `metadata.json` yayımlıyor.

Doğrudan okunan örnekler:
- https://raw.githubusercontent.com/YouthOpps/data-source/main/README.md
- https://raw.githubusercontent.com/YouthOpps/data-source/main/datas/youth-opportunities/data.json
- https://raw.githubusercontent.com/YouthOpps/data-source/main/datas/youth-opportunities/metadata.json

Örnek metadata: status=success, record_count=417,
last_success_at=2026-10-14T22:15:44.203Z; publisher_country=BD ve
publisher_type=aggregator. Başarı, uygulamaların hâlâ açık olduğunu
kanıtlamıyor. Hatalı sonraki toplamada son başarılı kayıtlar korunuyor.

Örnek kayıt alanları: id, title, url, source, source_url, published_at,
summary, tags, location, deadline, language, category/categories, kind,
host_countries, eligible_countries, publisher_country, created_at,
updated_at, first_seen_at, last_seen_at, last_checked_at, status,
classification. Boş eligible_countries, “tüm ülkeler başvurabilir” demek
değil: örneklerde ülke şartları yalnızca summary içinde kalabiliyor.

README kökte catalog.json/aggregate manifest olmadığını belirtiyor.
Kaynak keşfi için desteklenen yöntem netleştirilmeli; MVP'de açıkça seçilmiş
kaynak kimlikleri kullanılabilir. Site belgesi yeni yerleşimi anlatırken
README tüketicinin eski katalogdan taşınması gerektiğine dair bir not da
barındırıyor. Bu doküman farkı nedeniyle tüketim sürümü commit SHA ile
sabitleyip gerçek dosya şemasıyla test edilmeli. Site ile main dalındaki
verinin aynı anlık görüntü olduğu varsayılmamalı.

### Yeniden kullanım sınırları

[Trust policy](https://www.youthopps.org/docs/trust/) kamuya açık GitHub
erişiminin yeniden kullanım lisansı olmadığını ve bu rehberin lisans
vermediğini açıkça söylüyor. data-source/main/LICENSE denemesi 404 verdi;
bu, başka isimde lisans bulunmadığının kapsamlı kanıtı değil. Veri için
geçerli açık lisans veya üçüncü taraf tüketim koşulları henüz doğrulanmadı.
Bu nedenle JSON'a teknik erişim doğrulandı, yeniden dağıtım izni doğrulanmadı.
Tam yazıların, marka ve görsellerin kopyalanması önerilmiyor.

[Bot belgesi](https://www.youthopps.org/bot/) kendi toplayıcıları için
robots/koşul incelemesi, en az 6 saniye aralık, kayan bir dakikada en çok
10 istek başlangıcı, Retry-After'a uyma ve erişim reddinde durma politikası
anlatıyor. Bu belge üçüncü taraflar için otomatik lisans veya API kullanım
sözleşmesi değil. Bizim olası HTML adaptörümüz için de en az bu muhafazakâr
sınırlar ve varsa daha sıkı kaynak koşulları öneriliyor. Araştırma sınırlı
okuma istekleriyle yapıldı; toplu tarama ve koruma aşma yapılmadı.

**Karar:** Öncelikle veri anlık görüntülerinin üçüncü taraf kullanım/lisans
şartlarını site sahibinin belgelerinden veya açıklamasından netleştir.
İzin uygunsa kaynak bazlı JSON tüket; bu, binlerce detay sayfasını taramayı
gereksiz kılar. JSON kullanımı uygun değilse izinli statik indeks/HTML
seçeneklerini değerlendir. RSS/WordPress üzerine uygulama kurma.
Bu araştırmada site işletmecisine mesaj gönderilmedi.

## 4. Önerilen Python mimarisi

Başlangıç için mikroservisler yerine tek Python projesi önerilir:

İzin koşulları netleştirilmiş JSON anlık görüntü adaptörü → normalizasyon/doğrulama → SQLite → eşleştirme servisi
→ FastAPI → ChatGPT GPT Actions veya başka bir istemci.

- **Araçlar:** desteklenen Python 3.12+, sanal ortam, kilitli bağımlılıklar;
  FastAPI, Pydantic, SQLAlchemy ve Alembic. Veri erişimine göre httpx,
  JSON tüketimi önceliklidir; feedparser yalnızca RSS doğrulanırsa eklenir.
  HTML ayrıştırıcı yalnızca gerekirse seçilir. Sürümler uygulama aşamasında
  doğrulanıp sabitlenir; bu aşamada kurulum/dependency dosyası oluşturulmaz.
- **Toplama:** izinli kaynağa özel adaptör; kaynak kimliği, cursor/sayfa,
  son başarılı senkronizasyon ve hata kaydı. Komut satırı işiyle başlar;
  gerekirse zamanlanmış görev eklenir. Ağır kuyruk altyapısı gerekmiyor.
- **Saklama:** MVP için SQLite ve migration; çok kullanıcılı dağıtım veya
  eşzamanlı yazma gereksiniminde PostgreSQL. Kaynak kimliği ya da normalize
  edilmiş kaynak URL'si üzerinde benzersizlik; tekrar çalıştırma idempotent.
- **Servis:** arama, detay ve profil üzerinden öneri. Veri toplama işi
  kullanıcı sorgusu sırasında tüm siteyi yeniden taramaz.
- **Gözlenebilirlik:** son güncelleme, kayıt sayıları, toplama hataları,
  kaynak durumu ve gecikme; loglarda anahtar veya kişisel profil bulunmaz.

### Fırsat modeli

id, source, source_id, source_url, publisher_record_url, application_url, title, organization,
publisher_country, publisher_type, host_countries, source_revision,
opportunity_type, summary, subjects, location, remote, funding,
eligible_countries, residency_rules, education_levels, age_min/age_max,
language_requirements, deadline_at, deadline_precision, deadline_timezone,
rolling_deadline, published_at, fetched_at, last_verified_at, status.

Kaynak `url` alanı başlangıçta publisher_record_url olarak eşlenir;
başvuru bağlantısı olduğu teyit edilmeden application_url sayılmaz.
Kaynak metadata durumu ve son başarılı toplama zamanı ayrıca saklanır.
Eksik değerler null/bilinmiyor olarak tutulur. Ülke ve alanlar normalize
edilir; metindeki kanıt ve kaynak bağlantısı alanlarla ilişkilendirilir.
Tarih saat dilimi belli değilse yapay bir saat dilimi atanmaz. Süresi
geçen fırsatlar varsayılan önerilerden çıkarılır; tarihi bilinmeyenler
ayrı işaretlenir. Kaybolan kayıt hemen silinmez; durum değişimi izlenir.

### Kullanıcı profili ve eşleştirme

Asgari profil: eğitim seviyesi, alan/ilgi, vatandaşlık ve gerekiyorsa
ikamet, tercih edilen ülkeler, fırsat türleri, finansman/uzaktan katılım
tercihi. Yaş yalnızca uygunluk için gerektiğinde istenir; doğum tarihi,
pasaport veya CV ilk sürüm için gerekli değildir. MVP'de profil istek
boyunca kullanılır, varsayılan olarak kalıcı saklanmaz.

Önce açık uygunsuzluklar elenir: süre dolması veya kesin vatandaşlık,
yaş, eğitim kuralı ihlali. Eksik kural/profil alanı uygunsuzluk ya da
kesin uygunluk sayılmaz; sonuç “uygunluğu kontrol edilmeli” olarak döner.
Ardından ilgi, fırsat türü, konum ve finansman tercihleriyle açıklanabilir
puanlama yapılır. Her sonuç eşleşme nedenleri, kontrol edilmesi gereken
şartlar, güncellik ve kaynak bağlantısını taşır. Puan olasılık değildir.

İlk sürüm için LLM zorunlu değil. Daha sonra Türkçe özet ve doğal dil
sorgusu eklenebilir; model doğrulanmamış şart/tarih üretemez. Sayfa içeriği
ve haricî metinler talimat kabul edilmez; prompt injection'a karşı güven
sınırı korunur. Vektör veritabanı ve embedding ilk aşamada gereksiz.

## 5. ChatGPT entegrasyonu

Eski ChatGPT Plugins beta yaklaşımı kullanımdan kaldırılmıştır; yeni bir
proje için eski plugin manifestini temel almak önerilmez. Bu bilgi canlı
belgelerle bu oturumda doğrulanamadı. Güncel hesap/plan desteği, yayınlama
koşulları ve tercih edilen entegrasyon uygulama öncesinde resmî belgelerden
teyit edilecek. Önerilen başlangıç: özel GPT içinden **GPT Actions** ile
FastAPI'ye erişim. ChatGPT Apps SDK/MCP ayrı bir entegrasyon seçeneğidir;
Actions ile aynı protokol değildir ve ilk sürüme zorunlu eklenmez.

GPT Actions için planlanan bileşenler:

- İnternetten ulaşılabilir HTTPS API ve geçerli TLS sertifikası.
- FastAPI'den türetilecek, Actions'ın desteklediği OpenAPI özellikleriyle
  doğrulanmış şema; kararlı operationId, açıklamalar ve örnekler.
- GET /opportunities: tür, ülke, alan, tarih ve sayfalama filtreleri.
- GET /opportunities/{id}: kaynaklı fırsat detayı.
- POST /recommendations: asgari profil ve tercihleri alıp açıklamalı
  sonuç döndürür; ilk sürümde veri değiştiren işlem içermez.
- GET /health: süreç sağlığı; veri güncelliği ayrıca raporlanır.
- Her sonuçta kaynak URL'si, başvuru URL'si, güncelleme zamanı ve
  uygunluk belirsizlikleri; sınırlı yanıt boyutu ve anlaşılır hata modeli.
- Kişisel olmayan pilot için kota korumalı API anahtarı; kalıcı kullanıcı
  hesapları gerekirse kullanıcı bazlı OAuth. Anahtarları şemaya veya
  depoya koyma; sunucu sır yöneticisi ve Actions ayarlarında yönet.
- GPT talimatları: profil için yalnızca eksik gerekli alanı sor, API'den
  gelen kaynağı göster, uygunluk/başarı garantisi verme, otomatik başvurma.
- Kamuya açılış gerekiyorsa gizlilik politikası, destek iletişimi ve
  platformun o tarihte istediği alan adı/yayınlama doğrulamaları.

Tarihsel Plugins uyumluluğu ayrıca istenirse /.well-known/ai-plugin.json,
OpenAPI belgesi, kimlik doğrulama, logo ve hukukî iletişim alanları
incelenebilir. Bunlar eski yaklaşımın bileşenleridir; bugün ChatGPT'ye
kurulabilir bir plugin sağlayacağı taahhüt edilmez.

Resmî doğrulama adresleri (bu oturumda içerikleri okunamadı):
- https://help.openai.com/en/articles/8988022-winding-down-the-chatgpt-plugins-beta
- https://platform.openai.com/docs/actions

## 6. Uygulama aşamaları ve kabul ölçütleri

1. **Kaynağı doğrula:** ağ erişimi, hedef site kimliği, kategori örnekleri,
   erişim belgeleri ve kullanım izni. Sonuçları bu plana kaynaklarıyla ekle.
   Bu adım tamamlanmadan canlı veri toplayıcıyı uygulama.
2. **Veri katmanı:** doğrulanmış şema ve izinli adaptör. Tür, eksik tarih,
   saat dilimi, tekrarlı kayıt ve değişen sayfa için anlamlı testler.
3. **Eşleştirme:** sentetik profillerle açık uygunsuzluğun elenmesi, belirsiz
   uygunluğun işaretlenmesi ve puan açıklamalarının tutarlılığı.
4. **API:** arama, detay, öneri, doğrulama hataları, sayfalama, kota ve
   kimlik doğrulama testleri. Son kullanıcının gördüğü kaynakları doğrula.
5. **Actions pilotu:** gerçek HTTPS uçta uçtan uca profil → öneri → detay
   akışı. Şema uyumluluğunu ve hata/timeout davranışını ChatGPT'de dene.

Ayrıca: toplama tekrarında duplikasyon oluşmamalı; süresi geçen fırsat
aktif öneriye girmemeli; kaynak erişilemezse önbellek yaşı görünmeli;
403/429 davranışı test edilmeli; loglarda profil/sır bulunmamalı.
MVP için dağıtık sistem, ödeme, CV yükleme, otomatik başvuru ve bildirim
altyapısı kapsam dışıdır.

## 7. Güncellenen kararlar ve sonraki adım

- Ağ erişimi www üzerinden doğrulandı; önceki genel erişim engeli giderildi.
- Teknik tercih: kullanım şartları netleşirse kaynak bazlı JSON anlık
  görüntüleri + SQLite + kural tabanlı eşleştirme + FastAPI + GPT Actions.
  HTML scraping veya RSS ilk tercih değil.
- Kaynak ülkesi, hedef ülke ve uygun vatandaşlık/ikamet ayrı tutulacak.
  Metindeki koşullar ile boş yapılandırılmış alanlar çelişirse kesin
  uygunluk iddia edilmeyecek; kanıt ve kontrol gereksinimi gösterilecek.
- JSON senkronizasyonu tek bir commit/revizyondan yapılacak; data ile
  metadata tutarlı okunacak. Şema hatasında son başarılı yerel kopya
  korunacak ve eski veri olduğu kullanıcıya bildirilecek.
- Açık kalanlar: veri yeniden kullanım lisansı/koşulları, desteklenen
  kaynak keşfi ve güncelleme sözleşmesi, asıl yayıncıdan örnek uygunluk/
  tarih doğrulaması. Yayıncı siteleri bu araştırmada ayrıca taranmadı.
- ChatGPT platform belgeleri bu takip çalışmasının kapsamı içinde yeniden
  doğrulanmadı; önceki entegrasyon önerisi koşullu kalıyor.

Bu planın ardından kullanıcı ilk çalışan prototipi onayladı. Prototip
yalnızca kurgusal yerel JSON kullanır; canlı kaynak entegrasyonu yapılmadı.
Uygulama ve doğrulama komutları README.md içinde belgelenmiştir.
