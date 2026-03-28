ORBITA-R PRD
Regional Constellation Optimization System

1. Ürün özeti

ORBITA-R, kullanıcı tarafından seçilen coğrafi bölge ve görev amacına göre, 7/24 kesintisiz kapsama sağlayacak optimum uydu takım mimarisini tasarlayan bir karar destek sistemidir.

Sistem iki ana modda çalışır:

Mission-Based Design
Kullanıcının girdiği bölge, görev ve teorik uydu kabiliyetlerine göre sıfırdan constellation üretir.

Real-World Scenario
Mevcut aktif uydu varsayımları veya önceden tanımlanmış uydu setleri üzerinden, olağanüstü durumlarda en iyi kapsama ve yönlendirme planını çıkarır.

Bu ürünün ana değeri, sadece “uydu yerleştirmek” değil; kapsama, boşluk süresi, maliyet, dayanıklılık ve arıza toleransı arasında denge kuran optimum yapı önermesidir.

1. Problem tanımı

Belirli bir bölge için 24/7 kapsama sağlamak zordur. Bunun temel nedenleri:

yanlış yörünge tipi seçimi
yetersiz uydu sayısı
plane dağılımının kötü olması
düşük kapsama sürekliliği
arıza halinde sistemin tek noktadan çökmesi
bozulmuş koşullarda hizmetin düşmesi

Hackathon başlığı doğrudan “bölgesel uydu takımı optimizasyonu” olduğu için ürünün ana sorusu şudur:

“Bu bölge için, bu görev amacıyla, 7/24 kapsama sağlayacak en iyi yörünge dizilimi nedir?”

1. Ürün amacı
Ana amaç

Belirli bir coğrafi bölge için, görev amacına göre minimum maliyetle maksimum kapsama sürekliliği sağlayan uydu takım mimarisini bulmak.

Alt amaçlar
optimum uydu sayısını bulmak
optimum irtifa ve eğimi belirlemek
plane sayısını ve faz dağılımını önermek
kapsama boşluklarını minimize etmek
kritik bölgeler için ağırlıklı kapsama hesabı yapmak
bozulmuş koşullarda dayanıklılığı ölçmek
arıza senaryosunda hizmet düşüşünü hesaplamak
4. Ürün kapsamı
Kapsam içinde
bölge seçimi veya koordinat girişi
görev tipi seçimi
kullanıcı tanımlı uydu kabiliyetleri
sıfırdan constellation üretimi
mevcut uydu kümesine göre yeniden optimizasyon
kapsama simülasyonu
failure simulation
weighted coverage
degradation / blackout zone mantığı
trade-off analizi
explainable sonuç üretimi
Kapsam dışında
gerçek uyduya komut gönderme
gerçek zamanlı uydu kontrolü
askeri operasyon planlama
radar bastırma / saldırı senaryosu
fiziksel uydu CAD tasarımı
chatbot katmanı
5. Kullanıcı senaryoları

Senaryo 1 — Sıfırdan tasarım
Kullanıcı bölgeyi seçer, görevi belirler, uydu kabiliyetlerini girer. Sistem sıfırdan optimum constellation önerir.

Senaryo 2 — Olağanüstü durum optimizasyonu
Kullanıcı mevcut aktif uydu setini veya ön tanımlı uydu havuzunu seçer. Sistem, afet veya kritik kesinti anında bu uydularla en iyi kapsama planını çıkarır.

Senaryo 3 — Trade-off değerlendirmesi
Kullanıcı “ucuz”, “dengeli” veya “dayanıklı” modlardan birini seçer. Sistem alternatif tasarımlar üretir.

1. Fonksiyonel gereksinimler

FR-01
Kullanıcı haritadan bölge seçebilmeli veya koordinat/polygon girebilmelidir.

FR-02
Kullanıcı görev amacını seçebilmelidir:

communication
observation
emergency
balanced

FR-03
Kullanıcı uydu kabiliyetlerini girebilmelidir:

min/max altitude
max inclination
coverage radius
min elevation
bandwidth
reliability
cost factor

FR-04
Sistem aday constellation’lar üretmelidir.

FR-05
Sistem 24 saatlik veya belirlenen zaman penceresinde kapsama simülasyonu yapmalıdır.

FR-06
Sistem coverage ratio, continuity, revisit, redundancy ve gap sürelerini hesaplamalıdır.

FR-07
Sistem minimum uydu sayısını bulabilmelidir.

FR-08
Sistem blackout/degradation zone’ları dikkate almalıdır.

FR-09
Sistem kritik noktalar için weighted coverage hesaplamalıdır.

FR-10
Sistem bir uydu arızası halinde yeniden değerlendirme yapmalıdır.

FR-11
Sistem en az 3 alternatif çözüm sunmalıdır:

Cost Optimized
Balanced
Resilient

FR-12
Sistem neden bu çözümü seçtiğini açıklayabilmelidir.

1. Non-functional gereksinimler

NFR-01 Performans
MVP düzeyinde tek bir senaryo analizi makul sürede dönmelidir. Hedef, kaba grid çözünürlüğünde hızlı hesaplama almaktır.

NFR-02 Modülerlik
UI, API ve optimizasyon çekirdeği birbirinden ayrılmalıdır.

NFR-03 Genişletilebilirlik
İleride gerçek TLE, daha gelişmiş perturbation modelleri ve yeni senaryo katmanları eklenebilmelidir.

NFR-04 Kullanılabilirlik
Dashboard sade olmalı; ana ekranda sadece iki temel akış bulunmalıdır.

NFR-05 Görsellik
Sonuçlar 2D/3D uzay temalı arayüzde açık biçimde gösterilmelidir.

1. Dashboard yapısı

Ana dashboard’da hamburger menü olmayacaktır. Ana ekranda uzay temalı arka plan üzerinde iki büyük şeffaf buton bulunacaktır.

Button 1 — Mission-Based Design
Elle girilen veriler ve kullanıcı tanımlı kısıtlara göre sıfırdan yörünge ve constellation tasarımı yapar.

Button 2 — Real-World Scenario
Mevcut aktif uydu varsayımlarına göre, olağanüstü bir durumda mevcut kaynaklarla en iyi kapsama planını çıkarır.

Bu iki mod, ürünün iki temel çalışma biçimini temsil eder:

yeni yapı kurma
mevcut yapıyı optimize etme
9. Kullanılacak teknolojiler
Backend

Backend dili Python olacaktır.

Python tarafında bağımlılık yönetimi için virtual environment + pip yapısı kullanılacaktır. Gerektiğinde bağımlılıkların sabit sürümlerle yönetilebilmesi için requirements.txt kullanılacaktır. Bu yaklaşım, geliştirme ortamının yeniden üretilebilir olmasını ve proje bağımlılıklarının kontrollü biçimde yönetilmesini sağlar.

HTTP API katmanı için FastAPI seçilecektir. FastAPI; yüksek performanslı asenkron yapı desteği, otomatik OpenAPI/Swagger dokümantasyonu, Pydantic tabanlı veri doğrulama, request/response modelleme ve modern Python geliştirme deneyimi gibi özellikleriyle REST API ve servis katmanı için uygundur.

ASGI sunucusu olarak Uvicorn kullanılacaktır. Uvicorn, FastAPI uygulamalarını hızlı ve hafif biçimde çalıştırmak için uygun bir sunucu katmanı sağlar.

Frontend

Frontend tarafında React + TypeScript + Vite kullanılacaktır. Vite hızlı geliştirme deneyimi, anlık dev server başlangıcı ve hızlı HMR sunar; ayrıca React/TypeScript şablonlarıyla kolay proje kurulumu sağlar.

Stil katmanında Tailwind CSS kullanılacaktır. Tailwind’in güncel Vite entegrasyonu @tailwindcss/vite eklentisiyle yapılır.

3D dünya ve yörünge görselleştirmesi için CesiumJS kullanılacaktır. CesiumJS npm ile kurulabilir; ion tabanlı terrain ve bazı 3D içerikler için access token gerekir.

Veri formatları
GeoJSON
JSON
isteğe bağlı TLE referans verileri
opsiyonel statik scenario datasetleri
10. Kullanılacak veriler
10.1 Bölge verileri
kullanıcı tarafından seçilen polygon
bbox
koordinat listesi
ön tanımlı bölge sınırları
10.2 Grid verileri

Bölge polygonu içinden dinamik olarak üretilecek örnekleme noktaları.

10.3 Uydu verileri

İki tip veri kullanılacaktır:

A. Kullanıcı girdisi

altitude range
inclination limit
coverage radius
min elevation
bandwidth
energy level
reliability
cost factor

B. Ön tanımlı aktif uydu senaryosu

varsayımsal aktif uydu listesi
temel yörünge parametreleri
görev tipi etiketi
operasyonel kabiliyet profili
10.4 Öncelik verileri
hastane
havaalanı
merkez
kritik altyapı
kullanıcı işaretlemeleri
10.5 Degradation verileri
blackout zone
communication degradation zone
düşük kalite alanlar
11. Teknik mimari
Üst seviye mimari

Frontend (React + Vite + Tailwind + Cesium)
↓
REST API (FastAPI + Uvicorn)
↓
Application / Service Layer
↓
Simulation + Coverage + Optimization Core
↓
Static Data / Scenario Data

Katmanlar

11.1 Presentation Layer
React tabanlı dashboard, harita ve sonuç ekranları.

11.2 API Layer
FastAPI üzerinden REST endpoint’leri:

request parsing
validation
route organization
middleware
response shaping

11.3 Application Layer
Use-case bazlı servisler:

mission design service
scenario optimization service
coverage analysis service
risk analysis service

11.4 Domain / Core Layer
İş mantığı burada bulunur:

grid generation
orbit candidate generation
coverage computation
scoring
optimization
failure analysis

11.5 Data Layer
Statik JSON/GeoJSON dosyaları, config dosyaları ve gerekirse hafif kalıcı veri saklama.

1. Python backend servis tasarımı

Python tarafında servis odaklı ve modüler bir yapı kurulacaktır.

Önerilen paket yapısı
backend/
  app/
    main.py
    api/
      routes/
      deps/
      schemas/
    services/
    domain/
      models/
      optimizer/
      coverage/
      orbit/
      risk/
      grid/
    core/
      config.py
      logger.py
    data/
      geojson/
      scenarios/
Paket sorumlulukları

app/main.py
Uygulamanın entrypoint’i.

app/api/routes
HTTP endpoint tanımları.

app/api/deps
Dependency injection ve ortak bağımlılıklar.

app/api/schemas
Pydantic request-response modelleri.

app/services
Use-case orchestration.

app/domain/orbit
Aday yörünge üretimi ve temel yörünge hesapları.

app/domain/grid
Polygon içi grid üretimi.

app/domain/coverage
Görünürlük, coverage ratio, revisit, redundancy.

app/domain/optimizer
Skorlama ve aday çözümlerin sıralanması.

app/domain/risk
Failure simulation, worst-case gap, weak zone analizi.

app/core/config.py
Ortam değişkenleri ve uygulama ayarları.

1. Çekirdek algoritmalar
13.1 Grid generation

Polygon veya bbox, belirli çözünürlükte grid noktalarına çevrilir.

13.2 Candidate generation

Aday tasarımlar şu parametreler üzerinden üretilir:

satellite count
plane count
altitude
inclination
phase offset
13.3 Coverage calculation

Her zaman adımında grid noktalarının görünürlüğü hesaplanır.

Temel metrikler:

coverage ratio
continuity
revisit time
redundancy
worst gap
13.4 Weighted coverage

Tüm noktalar eşit kabul edilmez. Kritik bölgeler daha yüksek ağırlık alır.

13.5 Optimization

Önerilen skor mantığı:

Score =
  w1 * Coverage

+ w2 * Continuity
+ w3 * Redundancy

+ w4 * Cost

+ w5 * MaxGap
13.6 Minimum satellite finder

Hedef kapsamayı sağlayan en küçük uydu sayısı aranır.

13.7 Failure simulation

Belirli bir uydu devre dışı bırakılarak sistem tekrar değerlendirilir.

1. API taslağı

POST /api/v1/design/run
Mission-Based Design akışını çalıştırır.

Input:

region
missionType
satelliteProfile
constraints

Output:

recommended constellation
metrics
alternatives
explanation

POST /api/v1/scenario/run
Real-World Scenario akışını çalıştırır.

Input:

region
scenarioType
activeSatellites
constraints

Output:

optimized usage plan
metrics
risk analysis

POST /api/v1/coverage/analyze
Sadece coverage analizi döner.

POST /api/v1/risk/failure
Failure simulation çalıştırır.

POST /api/v1/optimizer/min-satellites
Minimum uydu sayısını bulur.

1. Arayüz ekranları

Screen 1 — Home

İki büyük şeffaf buton:

Mission-Based Design
Real-World Scenario

Screen 2 — Region Selection

harita üzerinden seçim
polygon/bbox girişi

Screen 3 — Mission / Scenario Input

görev tipi
kısıtlar
uydu bilgileri
priority points
degradation zones

Screen 4 — Results

recommended orbit
constellation diagram
coverage heatmap
trade-off cards
risk panel
explanation panel
16. Çıktılar

Sistem aşağıdaki çıktıları üretmelidir:

A. Constellation summary
orbit type
altitude
inclination
plane count
satellite count
phase layout
B. Performance
coverage %
continuity
revisit
redundancy
max gap
C. Risk
weak zones
failure impact
worst-case summary
D. Trade-off
cost optimized
balanced
resilient
E. Explainability

Örnek:

neden bu eğim seçildi
neden bu uydu sayısı seçildi
neden bu çözüm daha dayanıklı
17. Başarı metrikleri
sistem bölge ve görev girdisinden anlamlı constellation önerisi üretebilmeli
en az 3 alternatif çözüm verebilmeli
minimum satellite analysis çalışmalı
failure mode hesaplanmalı
sonuçlar heatmap ve kartlarla görselleştirilmeli
demo akışı tek ekrandan rahat yönetilebilmeli
18. Riskler ve azaltma planı

Risk 1
Fizik modeli çok ağır olabilir
Önlem: Basit ama savunulabilir model; kaba grid ve makul timestep.

Risk 2
3D arayüz geliştirme süresi uzatabilir
Önlem: Önce 2D sonuç ekranı, sonra Cesium entegrasyonu.

Risk 3
FastAPI tarafında domain logic servis katmanına sızabilir
Önlem: domain (saf hesap fonksiyonları) ile services (use-case orchestration) ayrımını baştan korumak. Router’lar doğrudan domain fonksiyonlarını çağırmamalıdır.

Risk 4
Proje kapsamı dağılabilir
Önlem: Chatbot, askeri operasyon, gerçek uydu komutu gibi alanlara girmemek.

1. Son ürün tanımı

ORBITA-R, seçilen bölge ve görev amacına göre 7/24 kapsama sağlayacak optimum uydu takım mimarisini tasarlayan; bozulmuş koşullar, öncelikli bölgeler ve arıza senaryolarını da dikkate alan bir bölgesel constellation optimization platformudur.

Malatyalı44.
