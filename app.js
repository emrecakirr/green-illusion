/* The Green Illusion – app logic (Emre Çakır, NASA Space Apps 2026) */
const G = window.GI, OBS = G.obs, NOW = 2026;

/* ---------------- texts ---------------- */
const T = {
en: {
 navTry: "Try a place", navPast: "Past fires", navWhy: "Why radar", navTrust: "How sure are we",
 h1: "When does a burned forest really come back?",
 intro: `<p>Every summer we watch forests burn in Türkiye, Greece and California. A few years later the hills look green again, and it is easy to think the forest is back. Most of that green is grass and shrubs. The trees take much longer.</p>
<p>I wanted a simple way to see the real number. So I compared two kinds of satellite data over burned forests: ordinary optical images, which see color, and the new NASA-ISRO NISAR radar, which sees trunks and branches. Then I turned the result into a tool: click anywhere on the map and see how long a forest there would need after a fire.</p>`,
 kOptT: "years until optical satellites call the forest “recovered”", kRadT: "years until NISAR radar sees the forest structure back", kPxT: "burned forest pixels studied, from fires in Türkiye, Greece and California",
 s1: "1 · TRY IT", tryH: "Pick a place. What if it burned today?",
 tryLead: "Click any forest on the map, or use one of the shortcuts below. The tool reads the elevation and the slope direction of that spot, finds the most similar forest type we studied, and estimates two dates: when it will look green again, and when the trees will really be back.",
 tryEmpty: "<b>Click somewhere on the map</b>Try a forest near you.",
 loading: "Reading the terrain…",
 resH: "If this place burned today", resMeta: (z, asp, reg, km) => `Elevation ${z} m · ${asp} · closest forest type we learned from: ${reg} (${km} km away)`,
 north: "north-facing slope", south: "south-facing slope", flat: "flat or mixed slope",
 greenBy: "looks green again (optical)", backBy: "trees really back (NISAR radar)",
 gapTxt: (g) => `For about <b>${g} years</b> this place would look recovered from space while the forest is still missing. That gap is the green illusion.`,
 child: (y) => `A child born the year it burns would be <b>${y}</b> when the forest is back.`,
 placeChart: "Recovery over time at this place",
 warnSea: "This point looks like water or sea level. Try a spot on land.",
 warnFar: "This place is far from the forests we studied, so treat the numbers as a rough guess.",
 warnHigh: "This elevation is outside what we saw in burned areas, so the estimate is less certain.",
 warnFail: "Could not read the terrain here (no internet or no data). Showing the average for the closest forest type.",
 s2: "2 · LOOK BACK", pastH: "What happened after past fires?",
 pastLead: "These are real forest fires seen by NASA's MODIS satellite since 2001. For each burned square we measured how much of the forest has come back by summer 2026, once with optical data and once with NISAR radar. Switch between the two views and watch how much forest is still missing.",
 eyeOpt: "Optical view", eyeRad: "NISAR radar view", lgMissing: "forest still missing", lgBack: "recovered",
 pastHint: "Click any orange square to see when it burned and when the forest should be back.",
 barsH: "How much has come back so far", optShort: "optical (MODIS NDVI)", radShort: "radar (NISAR HV)",
 barsNote: "100% means the burned area looks the same as the nearby forest that did not burn.",
 evLabel: (y, age, n) => `${y} fire <span>${age} years ago · ${n} pixels</span>`,
 ppBurn: "Burned in", ppOpt: "Optical says", ppRad: "Radar says", ppBack: "Trees back by about", ppRec: "recovered",
 s3: "3 · WHY RADAR", whyH: "Same place, two satellites, two answers",
 whyLead: "Drag the white handle. On the left is what an optical satellite sees in August 2026: green. On the right is the NISAR radar image of the same hills on the same days. The burn scar is still clearly there.",
 swL1: "Optical · MODIS NDVI", swL2: "“It looks green again”", swR1: "Radar · NISAR L-band HV", swR2: "“The trees are still missing”",
 swNote: "In the radar image, dark means little wood. Water and bare rock are dark too.",
 whyText: `<p>Optical satellites measure color. After a fire, grass and bushes grow back within a few years, and from space they are just as green as a pine forest. So the scar disappears from optical maps long before the forest is back.</p>
<p>NISAR's L-band radar works differently. It sends its own microwaves, about 24 cm long. They pass through leaves and bounce back from trunks and branches. The more wood there is, the stronger the echo in the HV channel. Green ground with a weak radar echo means: bushes, not yet a forest.</p>
<p>NISAR images almost every place on land every 12 days, day and night, through clouds and smoke. That makes it possible to follow recovery everywhere, not only where someone counts trees on the ground.</p>`,
 ilL: "Mature forest", ilR: "5 years after a fire", ilStrong: "strong echo: wood", ilWeak: "weak echo", ilG1: "optical: green", ilG2: "optical: also green",
 s4: "4 · HOW SURE ARE WE", trustH: "What the data says, and what it cannot say yet",
 trustLead: "Each dot below is one fire, measured in 2026. Fires of different ages, side by side, show how recovery moves over time. The lines are the curves we fitted to them.",
 evH: "Recovery of every fire we studied", evNote: "Shaded area: the green illusion",
 xAx: "Years since the fire", yAx: "Recovered", ttYrs: "years after the fire",
 howH: "How it works, in five steps",
 m1: "<b>Where and when did it burn?</b> MODIS burned-area maps (2001–2025) give every 500 m square its last fire date.",
 m2: "<b>What does it look like now?</b> For August 2026 I took MODIS greenness (NDVI) and the NISAR radar image (HV channel).",
 m3: "<b>Compared to what?</b> The reference is forest within 5 km that did not burn. 100% means “same as the neighbors”.",
 m4: "<b>Turning space into time.</b> A fire from 18 years ago shows what today's young burn scar may look like in 2044. Putting all fires together gives one recovery curve per forest type. The ranges come from leaving out whole fires and refitting (bootstrap by fire).",
 m5: "<b>Local conditions.</b> NASADEM elevation and slope direction adjust the forecast. In our data, higher forests recovered faster. A slope effect also showed up, but I left it out because it is most likely a radar geometry effect on steep terrain.",
 limH: "Limits I want to be clear about",
 lim: `<p>The long end of the curves is an extrapolation. We do not yet have 50-year-old burns in the data. I used one NISAR date per region from NISAR's first months of public data. Burn severity, soil and rainfall are not in the model yet. Forecasts for places far from the studied forests are rough guesses.</p><p>Next steps: more NISAR dates and both orbit directions, more regions, rainfall data from NASA GPM, and checks against forest inventory plots on the ground.</p>`,
 tblH: "Results by region",
 th: ["Region", "Burned pixels", "Fires", "Optical: 90% back", "Radar: 90% back", "Green illusion"],
 yrs: "yrs",
 vidH: "30-second demo", vidLead: "A short walk through the idea and the app.",
 dataH: "Data and code",
 srcOther: "Elevation for any clicked place: AWS Terrain Tiles (based on SRTM and other sources). Basemap: Esri World Imagery.",
 srcCode: `All code is open: <a href="https://github.com/emrecakirr/green-illusion" target="_blank" rel="noopener">github.com/emrecakirr/green-illusion</a>. Python (earthaccess, asf_search, h5py, numpy, scipy), Leaflet. I used Claude (Anthropic) as an AI assistant for code and text. All numbers come from the NASA data above.`,
 foot: "The Green Illusion · Emre Çakır · NASA Space Apps Challenge 2026, “Dancing with the SARs” · Not an official NASA product.",
 regions: {antalya: "Antalya, Türkiye", mugla: "Muğla, Türkiye", evia: "Evia, Greece", california: "N. Sierra, California"},
 noTrendBox: "not clear", noTrendLbl: "trees back (NISAR radar)",
 noTrendTxt: "Here NISAR radar does not show the trees coming back with time: burn scars from 2001 look no more forested than ones from 2020. Optical data still call it “recovered” in about 12 years, because shrubs grow fast. In the Sierra Nevada, researchers have documented severe fires turning conifer forest into long-lasting shrub fields.",
 caNote: `<b>A warning from California.</b> Optical data say these burns recover in about 12 years. NISAR radar sees no steady return of trees: older scars are not further along than younger ones. This fits field studies from the Sierra Nevada showing that after high-severity fires, many forest stands were replaced by shrub fields (<a href="https://doi.org/10.1002/ecs2.2882" target="_blank" rel="noopener">Richter et al. 2019, Ecosphere</a>). Here the green illusion may be permanent unless people replant.`,
 unclear: "unclear", noTrendCell: "no clear trend", eviaNote: `<b>Evia.</b> Five years after the 2021 fire, the burn scar is still mostly dry grass and bare ground in late summer, so even optical data show little green yet. NISAR radar already sees some woody regrowth (about 13% of the neighbors' level).`,
 smallFires: (n) => `${n} smaller fires (under 150 pixels) are used in the curves but not listed here, because single small fires are noisy.`,
 groups: {med: "Mediterranean pine", sierra: "Sierra Nevada conifer"},
},
tr: {
 navTry: "Bir yer dene", navPast: "Geçmiş yangınlar", navWhy: "Neden radar", navTrust: "Ne kadar eminiz",
 h1: "Yanan bir orman gerçekten ne zaman geri gelir?",
 intro: `<p>Her yaz Türkiye'de, Yunanistan'da, Kaliforniya'da ormanların yanışını izliyoruz. Birkaç yıl sonra tepeler yeniden yeşeriyor ve orman geri geldi sanıyoruz. Oysa o yeşilin çoğu ot ve çalı. Ağaçların dönmesi çok daha uzun sürüyor.</p>
<p>Bu süreyi gerçek veriyle görmek istedim. Yanmış ormanlarda iki tür uydu verisini karşılaştırdım: rengi gören normal optik görüntüler ve gövdeyi, dalları gören yeni NASA-ISRO NISAR radarı. Sonra bunu bir araca dönüştürdüm: haritada herhangi bir yere tıkla, orada yangın çıksa ormanın kaç yılda geri geleceğini gör.</p>`,
 kOptT: "yıl sonra optik uydular ormana “toparlandı” diyor", kRadT: "yıl sonra NISAR radarı orman yapısının geri geldiğini görüyor", kPxT: "yanmış orman pikseli incelendi: Türkiye, Yunanistan ve Kaliforniya",
 s1: "1 · DENE", tryH: "Bir yer seç. Bugün yansa ne olur?",
 tryLead: "Haritada herhangi bir ormana tıkla ya da aşağıdaki kısayollardan birini seç. Araç o noktanın yüksekliğini ve yamaç yönünü okuyor, incelediğimiz orman tiplerinden en benzerini buluyor ve iki tarih tahmin ediyor: ne zaman yeniden yeşil görüneceği ve ağaçların gerçekten ne zaman geri geleceği.",
 tryEmpty: "<b>Haritada bir yere tıkla</b>Yakınındaki bir ormanı dene.",
 loading: "Arazi okunuyor…",
 resH: "Burası bugün yansaydı", resMeta: (z, asp, reg, km) => `Yükseklik ${z} m · ${asp} · en yakın öğrendiğimiz orman tipi: ${reg} (${km} km)`,
 north: "kuzeye bakan yamaç", south: "güneye bakan yamaç", flat: "düz ya da karışık yamaç",
 greenBy: "yeniden yeşil görünür (optik)", backBy: "ağaçlar gerçekten geri gelir (NISAR radar)",
 gapTxt: (g) => `Yaklaşık <b>${g} yıl</b> boyunca burası uzaydan bakınca toparlanmış görünecek, ama orman hâlâ eksik olacak. Bu fark, yeşil yanılsama.`,
 child: (y) => `Yangın yılında doğan bir çocuk, orman geri geldiğinde <b>${y}</b> yaşında olacak.`,
 placeChart: "Bu noktada zamanla toparlanma",
 warnSea: "Bu nokta su ya da deniz seviyesi gibi görünüyor. Karada bir yer dene.",
 warnFar: "Burası incelediğimiz ormanlardan uzak, rakamları kaba bir tahmin olarak düşün.",
 warnHigh: "Bu yükseklik yanık alanlarda gördüğümüz aralığın dışında, tahmin daha belirsiz.",
 warnFail: "Bu noktanın arazisi okunamadı (internet ya da veri yok). En yakın orman tipinin ortalaması gösteriliyor.",
 s2: "2 · GERİYE BAK", pastH: "Geçmiş yangınlardan sonra ne oldu?",
 pastLead: "Bunlar NASA'nın MODIS uydusunun 2001'den beri gördüğü gerçek orman yangınları. Her yanık kare için ormanın 2026 yazına kadar ne kadar geri geldiğini ölçtüm: bir kez optik veriyle, bir kez NISAR radarıyla. İki görünüm arasında geçiş yap ve hâlâ ne kadar ormanın eksik olduğuna bak.",
 eyeOpt: "Optik görünüm", eyeRad: "NISAR radar görünümü", lgMissing: "orman hâlâ eksik", lgBack: "toparlandı",
 pastHint: "Ne zaman yandığını ve ormanın ne zaman geri geleceğini görmek için turuncu bir kareye tıkla.",
 barsH: "Şimdiye kadar ne kadarı geri geldi", optShort: "optik (MODIS NDVI)", radShort: "radar (NISAR HV)",
 barsNote: "%100, yanık alanın yakındaki hiç yanmamış ormanla aynı göründüğü anlamına geliyor.",
 evLabel: (y, age, n) => `${y} yangını <span>${age} yıl önce · ${n} piksel</span>`,
 ppBurn: "Yandığı yıl", ppOpt: "Optik diyor ki", ppRad: "Radar diyor ki", ppBack: "Ağaçların dönüşü yaklaşık", ppRec: "toparlandı",
 s3: "3 · NEDEN RADAR", whyH: "Aynı yer, iki uydu, iki farklı cevap",
 whyLead: "Beyaz tutamağı sürükle. Solda optik uydunun Ağustos 2026'da gördüğü var: yeşil. Sağda aynı tepelerin aynı günlerdeki NISAR radar görüntüsü. Yangın izi hâlâ açıkça orada.",
 swL1: "Optik · MODIS NDVI", swL2: "“Yeniden yeşil görünüyor”", swR1: "Radar · NISAR L-bandı HV", swR2: "“Ağaçlar hâlâ yok”",
 swNote: "Radar görüntüsünde koyu, az odun demek. Su ve çıplak kaya da koyu görünür.",
 whyText: `<p>Optik uydular rengi ölçer. Yangından sonra ot ve çalı birkaç yılda geri gelir ve uzaydan bakınca bir çam ormanı kadar yeşil görünür. Bu yüzden yangın izi, orman geri gelmeden çok önce optik haritalardan kaybolur.</p>
<p>NISAR'ın L-bandı radarı farklı çalışır. Kendi mikrodalgasını gönderir, dalga boyu yaklaşık 24 cm. Bu dalgalar yaprakların arasından geçer ve gövdeden, dallardan yansır. Odun ne kadar çoksa HV kanalındaki yankı o kadar güçlüdür. Yeşil zemin ama zayıf radar yankısı şu demek: çalı var, henüz orman yok.</p>
<p>NISAR karaların neredeyse her yerini 12 günde bir, gece gündüz, bulutun ve dumanın arasından görüntüler. Bu sayede toparlanmayı sadece birilerinin yerde ağaç saydığı yerlerde değil, her yerde takip etmek mümkün.</p>`,
 ilL: "Olgun orman", ilR: "Yangından 5 yıl sonra", ilStrong: "güçlü yankı: odun", ilWeak: "zayıf yankı", ilG1: "optik: yeşil", ilG2: "optik: yine yeşil",
 s4: "4 · NE KADAR EMİNİZ", trustH: "Veri ne diyor, henüz neyi söyleyemiyor",
 trustLead: "Aşağıdaki her nokta 2026'da ölçülmüş bir yangın. Farklı yaşlardaki yangınlar yan yana konunca toparlanmanın zamanla nasıl ilerlediği görünüyor. Çizgiler bu noktalara uydurduğum eğriler.",
 evH: "İncelediğimiz her yangının toparlanması", evNote: "Gölgeli alan: yeşil yanılsama",
 xAx: "Yangından bu yana geçen yıl", yAx: "Toparlanma", ttYrs: "yıl sonra",
 howH: "Beş adımda nasıl çalışıyor",
 m1: "<b>Nerede ve ne zaman yandı?</b> MODIS yanık alan haritaları (2001–2025) her 500 m'lik kareye son yangın tarihini veriyor.",
 m2: "<b>Şimdi nasıl görünüyor?</b> Ağustos 2026 için MODIS yeşillik (NDVI) verisini ve NISAR radar görüntüsünü (HV kanalı) aldım.",
 m3: "<b>Neye göre?</b> Referans, 5 km içinde hiç yanmamış orman. %100 “komşularıyla aynı” demek.",
 m4: "<b>Mekânı zamana çevirmek.</b> 18 yıl önce yanmış bir alan, bugünkü genç yangın izinin 2044'te nasıl görünebileceğini gösteriyor. Tüm yangınlar bir araya gelince her orman tipi için bir toparlanma eğrisi çıkıyor. Aralıklar, yangınları tek tek dışarıda bırakıp yeniden hesaplayarak bulundu (yangın bazlı bootstrap).",
 m5: "<b>Yerel koşullar.</b> NASADEM yüksekliği ve yamaç yönü tahmini ayarlıyor. Verimizde daha yüksekteki ormanlar daha hızlı toparlandı. Bir eğim etkisi de çıktı ama dahil etmedim, çünkü büyük ihtimalle dik arazide radarın bakış açısından kaynaklanıyor.",
 limH: "Açık olmak istediğim sınırlar",
 lim: `<p>Eğrilerin uzun ucu bir tahmin, veride henüz 50 yıllık yanık alan yok. Her bölge için NISAR'ın ilk aylardaki açık verisinden tek bir tarih kullandım. Yangının şiddeti, toprak ve yağış henüz modelde yok. İncelenen ormanlardan uzak yerler için tahminler kaba.</p><p>Sonraki adımlar: daha çok NISAR tarihi ve iki yörünge yönü, daha çok bölge, NASA GPM yağış verisi ve yerdeki orman envanteri ölçümleriyle karşılaştırma.</p>`,
 tblH: "Bölgelere göre sonuçlar",
 th: ["Bölge", "Yanık piksel", "Yangın", "Optik: %90 dönüş", "Radar: %90 dönüş", "Yeşil yanılsama"],
 yrs: "yıl",
 vidH: "30 saniyelik tanıtım", vidLead: "Fikrin ve uygulamanın kısa bir turu.",
 dataH: "Veri ve kod",
 srcOther: "Tıklanan her noktanın yüksekliği: AWS Terrain Tiles (SRTM ve diğer kaynaklar). Altlık harita: Esri World Imagery.",
 srcCode: `Tüm kod açık: <a href="https://github.com/emrecakirr/green-illusion" target="_blank" rel="noopener">github.com/emrecakirr/green-illusion</a>. Python (earthaccess, asf_search, h5py, numpy, scipy), Leaflet. Kod ve metin için yapay zekâ asistanı olarak Claude'u (Anthropic) kullandım. Tüm sayılar yukarıdaki NASA verilerinden geliyor.`,
 foot: "The Green Illusion · Emre Çakır · NASA Space Apps Challenge 2026, “Dancing with the SARs” · Resmî bir NASA ürünü değildir.",
 regions: {antalya: "Antalya, Türkiye", mugla: "Muğla, Türkiye", evia: "Evia (Eğriboz), Yunanistan", california: "Kuzey Sierra, Kaliforniya"},
 noTrendBox: "belirsiz", noTrendLbl: "ağaçların dönüşü (NISAR radar)",
 noTrendTxt: "Burada NISAR radarı ağaçların zamanla geri geldiğini göstermiyor: 2001'de yanmış alanlar, 2020'de yanmışlardan daha ormanlık görünmüyor. Optik veri ise çalılar hızlı büyüdüğü için yaklaşık 12 yılda “toparlandı” diyor. Sierra Nevada'da araştırmacılar şiddetli yangınların iğne yapraklı ormanı uzun süre kalan çalılıklara dönüştürdüğünü belgelemiş.",
 caNote: `<b>Kaliforniya'dan bir uyarı.</b> Optik veri bu yanık alanların yaklaşık 12 yılda toparlandığını söylüyor. NISAR radarı ise ağaçların düzenli bir şekilde geri geldiğini görmüyor: eski yanık alanlar gençlerden daha ileride değil. Bu, Sierra Nevada'daki saha çalışmalarıyla uyumlu: şiddetli yangınlardan sonra birçok orman alanının yerini çalılıklar almış (<a href="https://doi.org/10.1002/ecs2.2882" target="_blank" rel="noopener">Richter ve ark. 2019, Ecosphere</a>). Burada yeşil yanılsama, insanlar fidan dikmezse kalıcı olabilir.`,
 unclear: "belirsiz", noTrendCell: "net eğilim yok", eviaNote: `<b>Evia.</b> 2021 yangınından beş yıl sonra yanık alan yaz sonunda hâlâ büyük ölçüde kuru ot ve çıplak toprak, bu yüzden optik veri bile henüz pek yeşillik görmüyor. NISAR radarı ise biraz odunsu büyüme görüyor (komşu ormanın yaklaşık %13'ü kadar).`,
 smallFires: (n) => `${n} küçük yangın (150 pikselden az) eğrilerde kullanıldı ama burada listelenmedi, çünkü tek tek küçük yangınlar gürültülü.`,
 groups: {med: "Akdeniz çamı", sierra: "Sierra Nevada iğne yapraklı"},
}};
const FIRE_NAMES = {antalya: {2021: "Manavgat", 2008: "Serik–Taşağıl"}, mugla: {2021: "Marmaris · Köyceğiz · Milas"}, evia: {2021: "North Evia"}, california: {2018: "Camp Fire", 2020: "North Complex", 2021: "Dixie Fire"}};
const QUICK = [["Ankara · Beynam", 39.70, 32.88], ["İzmir · Seferihisar", 38.15, 26.88], ["Kazdağları", 39.70, 26.85], ["Athens · Parnitha", 38.17, 23.72], ["Paradise, CA", 39.76, -121.62]];

let L_ = (navigator.language || "en").toLowerCase().startsWith("tr") ? "tr" : "en";
const t = k => T[L_][k];
const pct = r => Math.round(Math.max(0, Math.min(1, r)) * 100) + "%";
const Rf = (age, tau) => age <= 0 ? 0 : 1 - Math.exp(-age / tau);
const toYrs = (r, tau) => { const rr = Math.max(0, Math.min(0.9, r)); return Math.max(0, tau * Math.LN10 + tau * Math.log(1 - rr)); };
const ESRI = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}";
const ATTR = "Imagery © Esri, Maxar, Earthstar Geographics";
const REG = Object.fromEntries(G.regions.map(r => [r.key, r]));

/* ---------------- 1. TRY ANY PLACE ---------------- */
const tryMap = L.map("tryMap", {scrollWheelZoom: false, worldCopyJump: true}).setView([38.6, 20], 4);
L.tileLayer(ESRI, {maxZoom: 16, attribution: ATTR}).addTo(tryMap);
for (const r of G.regions){
  const b = r.bbox;
  L.rectangle([[b[1], b[0]], [b[3], b[2]]], {color: "#f4b860", weight: 1.5, fill: false, dashArray: "4 4", interactive: false}).addTo(tryMap);
}
let tryMarker = null, lastPlace = null;
function hav(a, b){ const R = 6371, dl = (b[0] - a[0]) * Math.PI / 180, dn = (b[1] - a[1]) * Math.PI / 180;
  const x = Math.sin(dl / 2) ** 2 + Math.cos(a[0] * Math.PI / 180) * Math.cos(b[0] * Math.PI / 180) * Math.sin(dn / 2) ** 2; return 2 * R * Math.asin(Math.sqrt(x)); }
const tileCache = new Map();
async function tile(z, x, y){
  const k = `${z}/${x}/${y}`; if (tileCache.has(k)) return tileCache.get(k);
  const p = new Promise((res, rej) => { const im = new Image(); im.crossOrigin = "anonymous";
    im.onload = () => { const c = document.createElement("canvas"); c.width = c.height = 256; const g = c.getContext("2d"); g.drawImage(im, 0, 0); res(g.getImageData(0, 0, 256, 256).data); };
    im.onerror = rej; im.src = `https://s3.amazonaws.com/elevation-tiles-prod/terrarium/${z}/${x}/${y}.png`; });
  tileCache.set(k, p); return p;
}
async function terrain(lat, lon){
  const z = 12, n = 2 ** z, X = (lon + 180) / 360 * n, lr = lat * Math.PI / 180, Y = (1 - Math.log(Math.tan(lr) + 1 / Math.cos(lr)) / Math.PI) / 2 * n;
  const get = async (dx, dy) => { const px = (X - Math.floor(X)) * 256 + dx, py = (Y - Math.floor(Y)) * 256 + dy;
    const tx = Math.floor(X) + Math.floor(px / 256), ty = Math.floor(Y) + Math.floor(py / 256);
    const d = await tile(z, ((tx % n) + n) % n, ty); const i = ((Math.floor(py) % 256 + 256) % 256 * 256 + (Math.floor(px) % 256 + 256) % 256) * 4;
    return d[i] * 256 + d[i + 1] + d[i + 2] / 256 - 32768; };
  const [c, nN, sS, e, w] = await Promise.all([get(0, 0), get(0, -4), get(0, 4), get(4, 0), get(-4, 0)]);
  const gy = (sS - nN), gx = (e - w), h = Math.hypot(gx, gy);
  return {z: Math.round(c), north: h > 1 ? gy / h : 0};
}
function forecast(lat, lon, ter){
  let best = null;
  for (const r of G.regions){ const d = hav([lat, lon], r.center); if (!best || d < best.d) best = {r, d}; }
  const grp = G.groups[best.r.group];
  const out = {region: best.r, km: Math.round(best.d), grp, warn: []};
  let mO = 1, mR = 1;
  if (ter){
    const zc = Math.max(grp.cond.zlo, Math.min(grp.cond.zhi, ter.z));
    if (ter.z > grp.cond.zhi + 300) out.warn.push("warnHigh");
    mO = Math.exp(grp.cond.bz_opt * (zc - grp.cond.zmean) + grp.cond.bk_opt * (ter.north - grp.cond.kmean));
    mR = Math.exp(grp.cond.bz_rad * (zc - grp.cond.zmean) + grp.cond.bk_rad * (ter.north - grp.cond.kmean));
    mO = Math.max(0.6, Math.min(1.6, mO)); mR = Math.max(0.6, Math.min(1.6, mR));
  }
  out.opt = grp.opt.t90 * mO; out.rad = grp.rad.noTrend ? null : grp.rad.t90 * mR;
  if (best.d > 1500) out.warn.push("warnFar");
  return out;
}
function aspectText(n){ return n > 0.3 ? t("north") : n < -0.3 ? t("south") : t("flat"); }
async function pick(lat, lon){
  lastPlace = [lat, lon];
  if (tryMarker) tryMarker.remove();
  tryMarker = L.circleMarker([lat, lon], {radius: 8, color: "#fff", weight: 2, fillColor: "#ff7a1a", fillOpacity: 1}).addTo(tryMap);
  const box = document.getElementById("tryRes"); box.innerHTML = `<div class="empty">${t("loading")}</div>`;
  let ter = null, fail = false;
  try { ter = await terrain(lat, lon); } catch (e) { fail = true; }
  if (ter && ter.z <= 2){ box.innerHTML = `<h3>${t("resH")}</h3><div class="warn">${t("warnSea")}</div>`; return; }
  const f = forecast(lat, lon, ter);
  const yG = Math.round(NOW + f.opt), yB = f.rad == null ? null : Math.round(NOW + f.rad), gap = f.rad == null ? null : Math.round(f.rad - f.opt);
  const meta = ter ? t("resMeta")(ter.z, aspectText(ter.north), t("groups")[f.region.group] + " · " + t("regions")[f.region.key], f.km.toLocaleString()) : "";
  box.innerHTML = `<h3>${t("resH")}</h3><div class="meta">${meta}</div>
    <div class="big2"><div><div class="y" style="color:var(--optL)">~${yG}</div><div class="l">${t("greenBy")}</div></div>
    <div><div class="y" style="color:var(--radL)">${yB == null ? t("noTrendBox") : "~" + yB}</div><div class="l">${yB == null ? t("noTrendLbl") : t("backBy")}</div></div></div>
    <div>${gap == null ? t("noTrendTxt") : t("gapTxt")(gap)}</div>
    <div class="note" style="margin-top:12px">${t("placeChart")}</div>
    <svg id="placeChart" viewBox="0 0 440 190" style="width:100%;height:auto"></svg>
    ${f.rad == null ? "" : `<div class="note">${t("child")(Math.round(f.rad))}</div>`}
    ${fail ? `<div class="warn">${t("warnFail")}</div>` : ""}${f.warn.map(w => `<div class="warn">${t(w)}</div>`).join("")}`;
  drawPlace(f);
}
tryMap.on("click", e => pick(e.latlng.lat, ((e.latlng.lng + 540) % 360) - 180));
function renderQuick(){
  const q = document.getElementById("quick"); q.innerHTML = "";
  for (const [n, la, lo] of QUICK){ const b = document.createElement("button"); b.textContent = n; b.onclick = () => { tryMap.setView([la, lo], 9); pick(la, lo); }; q.appendChild(b); }
}
function drawPlace(f){
  const s = document.getElementById("placeChart"); if (!s) return;
  const W = 440, H = 190, m = {l: 36, r: 12, t: 12, b: 28}, XM = f.rad == null ? 60 : Math.max(60, Math.ceil(f.rad * 1.25 / 10) * 10);
  const X = a => m.l + a / XM * (W - m.l - m.r), Y = r => m.t + (1 - r) * (H - m.t - m.b);
  const tO = f.opt / Math.LN10, tR = f.rad == null ? null : f.rad / Math.LN10;
  let h = "";
  for (const r of [0, .5, 1]) h += `<line x1="${m.l}" x2="${W - m.r}" y1="${Y(r)}" y2="${Y(r)}" stroke="#28322d"/><text x="${m.l - 6}" y="${Y(r) + 4}" text-anchor="end" fill="#86928b" font-size="11">${r * 100}%</text>`;
  for (let a = 0; a <= XM; a += XM > 60 ? 20 : 10) h += `<text x="${X(a)}" y="${H - 8}" text-anchor="middle" fill="#86928b" font-size="11">${NOW + a}</text>`;
  if (tR != null){
    let up = "", dn = "";
    for (let a = 0; a <= XM; a += 1){ up += `${X(a)},${Y(Rf(a, tO))} `; }
    for (let a = XM; a >= 0; a -= 1){ dn += `${X(a)},${Y(Rf(a, tR))} `; }
    h += `<polygon points="${up}${dn}" fill="#f4b860" opacity=".12"/>`;
  } else {
    h += `<line x1="${m.l}" x2="${W - m.r}" y1="${Y(.15)}" y2="${Y(.35)}" stroke="#9775fa" stroke-width="2.5" stroke-dasharray="5 5"/><text x="${W - m.r}" y="${Y(.35) - 8}" text-anchor="end" fill="#c5b3ff" font-size="11.5">${t("noTrendLbl")}: ${t("noTrendBox")}</text>`;
  }
  for (const [tau, col] of [[tO, "#2f9e44"], [tR, "#9775fa"]].filter(x => x[0] != null)){ let d = ""; for (let a = 0; a <= XM; a += 1) d += (a ? "L" : "M") + X(a).toFixed(1) + "," + Y(Rf(a, tau)).toFixed(1); h += `<path d="${d}" fill="none" stroke="${col}" stroke-width="2.5"/>`; }
  h += `<line x1="${m.l}" x2="${W - m.r}" y1="${Y(.9)}" y2="${Y(.9)}" stroke="#4a5650" stroke-dasharray="3 3"/>`;
  for (const [yr, col] of [[f.opt, "#8ce99a"], [f.rad, "#c5b3ff"]].filter(x => x[0] != null)){ h += `<circle cx="${X(yr)}" cy="${Y(.9)}" r="4.5" fill="${col}"/><text x="${X(yr)}" y="${Y(.9) - 8}" text-anchor="middle" fill="${col}" font-size="11.5" font-weight="700">${Math.round(NOW + yr)}</text>`; }
  s.innerHTML = h;
}

/* ---------------- 2. PAST FIRES ---------------- */
const pastMap = L.map("pastMap", {scrollWheelZoom: false, preferCanvas: true});
L.tileLayer(ESRI, {maxZoom: 16, attribution: ATTR}).addTo(pastMap);
const rend = L.canvas({padding: 0.3});
let curReg = G.regions[0].key, eye = 0, cells = [];
const pxLayer = L.layerGroup().addTo(pastMap);
function showRegion(key){
  curReg = key; const r = REG[key];
  document.querySelectorAll("#tabs button").forEach(b => b.classList.toggle("on", b.dataset.k === key));
  pastMap.fitBounds([[r.bbox[1], r.bbox[0]], [r.bbox[3], r.bbox[2]]]);
  pxLayer.clearLayers(); cells = [];
  const dLat = 0.00435 / 2, dLon = 0.00435 / Math.cos(r.center[0] * Math.PI / 180) / 2;
  for (const p of r.px){
    const c = L.rectangle([[p[1] - dLat, p[0] - dLon], [p[1] + dLat, p[0] + dLon]], {renderer: rend, stroke: false, fillColor: "#ff7a1a", fillOpacity: .5});
    c.p = p; c.on("click", e => popPixel(r, p, e.latlng)); c.addTo(pxLayer); cells.push(c);
  }
  paint(); bars();
}
function paint(){ for (const c of cells){ const v = Math.max(0, Math.min(1, eye ? c.p[4] : c.p[3])); c.setStyle({fillOpacity: 0.08 + 0.85 * (1 - v)}); } }
function popPixel(r, p, ll){
  const y = Math.floor(p[2]);
  const back = r.rad.noTrend ? t("unclear") : Math.round(NOW + toYrs(p[4], r.rad.tau));
  L.popup().setLatLng(ll).setContent(`<div class="pp"><b>${t("ppBurn")} ${y}</b>
    <div class="r"><span>${t("ppOpt")}</span><span style="color:var(--optL)">${pct(p[3])} ${t("ppRec")}</span></div>
    <div class="r"><span>${t("ppRad")}</span><span style="color:var(--radL)">${pct(p[4])} ${t("ppRec")}</span></div>
    <div class="r"><span>${t("ppBack")}</span><span>${back}</span></div></div>`).openOn(pastMap);
}
function bars(){
  const r = REG[curReg], el = document.getElementById("bars");
  const big = r.events.filter(e => e.n >= 150), small = r.events.length - big.length;
  el.innerHTML = big.slice().sort((a, b) => b.y - a.y).map(e => {
    const nm = (FIRE_NAMES[curReg] || {})[e.y];
    return `<div class="ev"><div class="hd"><b>${nm ? nm + " · " : ""}${t("evLabel")(e.y, e.age, e.n.toLocaleString())}</b></div>
      <div class="bar"><span>${L_ === "tr" ? "Optik" : "Optical"}</span><div class="tr"><div class="fl" style="width:${Math.max(0, Math.min(100, e.opt * 100))}%;background:var(--opt)"></div></div><b>${pct(e.opt)}</b></div>
      <div class="bar"><span>Radar</span><div class="tr"><div class="fl" style="width:${Math.max(0, Math.min(100, e.rad * 100))}%;background:var(--rad)"></div></div><b>${pct(e.rad)}</b></div></div>`;
  }).join("") + (small ? `<div class="note">${t("smallFires")(small)}</div>` : "") + (curReg === "california" ? `<div class="warn" style="margin-top:12px;color:var(--ink2)">${t("caNote")}</div>` : "") + (curReg === "evia" ? `<div class="warn" style="margin-top:12px;color:var(--ink2)">${t("eviaNote")}</div>` : "");
}
document.querySelectorAll("#eye button").forEach(b => b.onclick = () => { eye = +b.dataset.v; document.querySelectorAll("#eye button").forEach(x => x.classList.toggle("on", x === b)); paint(); });

/* ---------------- 3. SWIPE ---------------- */
const sm = L.map("swipeMap", {scrollWheelZoom: false, zoomSnap: 0.25});
sm.createPane("optP"); sm.createPane("radP");
sm.getPane("optP").style.zIndex = 400; sm.getPane("radP").style.zIndex = 410;
L.tileLayer(ESRI, {maxZoom: 16, attribution: ATTR + " · NASA MODIS · NASA-ISRO NISAR"}).addTo(sm);
let swO = null, swR = null, frac = 0.5, swReg = null;
const handle = document.getElementById("handle"), knob = handle.querySelector(".knob");
function clip(){
  const nw = sm.containerPointToLayerPoint([0, 0]), se = sm.containerPointToLayerPoint(sm.getSize());
  const x = nw.x + (se.x - nw.x) * frac;
  sm.getPane("radP").style.clip = `rect(${nw.y}px, ${se.x}px, ${se.y}px, ${x}px)`;
  handle.style.left = (frac * 100) + "%";
}
function swShow(key){
  swReg = key; const r = REG[key], B = [[r.bbox[1], r.bbox[0]], [r.bbox[3], r.bbox[2]]];
  document.querySelectorAll("#swTabs button").forEach(b => b.classList.toggle("on", b.dataset.k === key));
  if (swO) swO.remove(); if (swR) swR.remove();
  swO = L.imageOverlay(`img/${key}/optik_ndvi.png`, B, {pane: "optP", opacity: .95}).addTo(sm);
  swR = L.imageOverlay(`img/${key}/radar_hv.jpg`, B, {pane: "radP"}).addTo(sm);
  sm.fitBounds(r.focus || B); clip();
}
sm.on("move zoom resize zoomanim", clip);
let dragging = false;
knob.addEventListener("pointerdown", e => { dragging = true; sm.dragging.disable(); knob.setPointerCapture(e.pointerId); e.preventDefault(); });
knob.addEventListener("pointermove", e => { if (!dragging) return; const b = sm.getContainer().getBoundingClientRect(); frac = Math.max(.02, Math.min(.98, (e.clientX - b.left) / b.width)); clip(); });
knob.addEventListener("pointerup", () => { dragging = false; sm.dragging.enable(); });
let animated = false;
new IntersectionObserver(es => { if (es[0].isIntersecting && !animated){ animated = true; let t0 = null;
  const step = ts => { if (!t0) t0 = ts; const k = (ts - t0) / 2400; if (k < 1 && !dragging){ frac = .5 + .3 * Math.sin(k * Math.PI * 2); clip(); requestAnimationFrame(step); } else if (!dragging){ frac = .5; clip(); } };
  requestAnimationFrame(step); } }, {threshold: .5}).observe(document.getElementById("swipeMap"));

/* ---------------- 4. EVIDENCE CHART ---------------- */
const ev = document.getElementById("evChart"), tt = document.getElementById("tt");
function drawEvidence(){
  const W = 600, H = 380, m = {l: 50, r: 16, t: 16, b: 46}, XM = 60;
  const X = a => m.l + a / XM * (W - m.l - m.r), Y = r => m.t + (1.05 - r) / 1.15 * (H - m.t - m.b);
  const g = G.groups.med; const tO = g.opt.tau, tR = g.rad.tau;
  let h = "";
  for (const r of [0, .25, .5, .75, 1]) h += `<line x1="${m.l}" x2="${W - m.r}" y1="${Y(r)}" y2="${Y(r)}" stroke="#28322d"/><text x="${m.l - 8}" y="${Y(r) + 4}" text-anchor="end" fill="#86928b" font-size="12">${r * 100}%</text>`;
  for (let a = 0; a <= XM; a += 10) h += `<text x="${X(a)}" y="${H - m.b + 18}" text-anchor="middle" fill="#86928b" font-size="12">${a}</text>`;
  h += `<text x="${(m.l + W - m.r) / 2}" y="${H - 6}" text-anchor="middle" fill="#bcc6c0" font-size="13">${t("xAx")}</text>`;
  let up = "", dn = ""; for (let a = 0; a <= XM; a++) up += `${X(a)},${Y(Rf(a, tO))} `; for (let a = XM; a >= 0; a--) dn += `${X(a)},${Y(Rf(a, tR))} `;
  h += `<polygon points="${up}${dn}" fill="#f4b860" opacity=".10"/>`;
  for (const [tau, col] of [[tO, "#2f9e44"], [tR, "#9775fa"]]){ let d = ""; for (let a = 0; a <= XM; a += .5) d += (a ? "L" : "M") + X(a).toFixed(1) + "," + Y(Rf(a, tau)).toFixed(1); h += `<path d="${d}" fill="none" stroke="${col}" stroke-width="2.5"/>`; }
  h += `<line x1="${m.l}" x2="${W - m.r}" y1="${Y(.9)}" y2="${Y(.9)}" stroke="#4a5650" stroke-dasharray="3 4"/><text x="${W - m.r}" y="${Y(.9) - 6}" text-anchor="end" fill="#86928b" font-size="11">90%</text>`;
  for (const [t90, col] of [[g.opt.t90, "#8ce99a"], [g.rad.t90, "#c5b3ff"]]) h += `<line x1="${X(t90)}" x2="${X(t90)}" y1="${Y(.9)}" y2="${Y(0)}" stroke="${col}" stroke-dasharray="2 3" opacity=".7"/><text x="${X(t90)}" y="${Y(0) + 16}" text-anchor="middle" fill="${col}" font-size="12" font-weight="700">${Math.round(t90)}</text>`;
  h += `<text x="${X(g.opt.t90 * .55)}" y="${Y(Rf(g.opt.t90 * .55, tO)) - 12}" fill="#8ce99a" font-size="12.5" font-weight="600">${t("optShort")}</text>`;
  h += `<text x="${X(g.rad.t90 * .7)}" y="${Y(Rf(g.rad.t90 * .7, tR)) + 22}" fill="#c5b3ff" font-size="12.5" font-weight="600">${t("radShort")}</text>`;
  const pts = [];
  for (const r of G.regions){ if (r.group !== "med") continue; for (const e of r.events){ if (!r.opt.noTrend) pts.push({r, e, k: "opt", v: e.opt}); if (!r.rad.noTrend) pts.push({r, e, k: "rad", v: e.rad}); } }
  for (const p of pts){
    const rad = Math.max(5, Math.min(11, Math.sqrt(p.e.n) / 6));
    h += `<circle class="pt" data-i="${pts.indexOf(p)}" cx="${X(p.e.age + (p.k === "opt" ? -.35 : .35))}" cy="${Y(Math.max(-.08, Math.min(1.04, p.v)))}" r="${rad}" fill="${p.k === "opt" ? "#2f9e44" : "#9775fa"}" stroke="#18201c" stroke-width="2"/>`;
  }
  ev.innerHTML = h;
  ev.querySelectorAll(".pt").forEach(c => {
    c.addEventListener("mouseenter", e => { const p = pts[+c.dataset.i]; const nm = (FIRE_NAMES[p.r.key] || {})[p.e.y];
      tt.innerHTML = `<b>${t("regions")[p.r.key]} · ${p.e.y}${nm ? " (" + nm + ")" : ""}</b><br>${p.e.age} ${t("ttYrs")} · ${p.e.n} px<br><span style="color:var(--optL)">●</span> ${pct(p.e.opt)} &nbsp; <span style="color:var(--radL)">●</span> ${pct(p.e.rad)}`;
      tt.style.display = "block"; const b = ev.getBoundingClientRect(), x = e.clientX - b.left; tt.style.left = (x > b.width * .6 ? x - 230 : x + 12) + "px"; tt.style.top = (e.clientY - b.top - 20) + "px"; });
    c.addEventListener("mouseleave", () => tt.style.display = "none");
  });
}
function table(){
  const th = t("th"); let h = `<tr>${th.map((x, i) => `<th${i ? ' style="text-align:right"' : ""}>${x}</th>`).join("")}</tr>`;
  for (const r of G.regions) h += `<tr><td>${t("regions")[r.key]}</td><td class="n">${r.n.toLocaleString()}</td><td class="n">${r.events.length}</td>
    <td class="n">${r.opt.noTrend ? t("noTrendCell") : `${Math.round(r.opt.t90)} ${t("yrs")} <span style="color:var(--ink3)">(${Math.round(r.opt.lo)}–${Math.round(r.opt.hi)})</span>`}</td>
    <td class="n">${r.rad.noTrend ? t("noTrendCell") : `${Math.round(r.rad.t90)} ${t("yrs")} <span style="color:var(--ink3)">(${Math.round(r.rad.lo)}–${Math.round(r.rad.hi)})</span>`}</td>
    <td class="n"><b>${(r.rad.noTrend || r.opt.noTrend) ? "?" : `+${Math.round(r.rad.t90 - r.opt.t90)} ${t("yrs")}`}</b></td></tr>`;
  for (const [k, g] of Object.entries(G.groups)) h += `<tr style="background:rgba(255,255,255,.03)"><td><b>${t("groups")[k]}</b></td><td class="n">${g.n.toLocaleString()}</td><td class="n">${g.nEv}</td>
    <td class="n"><b>${Math.round(g.opt.t90)} ${t("yrs")}</b> <span style="color:var(--ink3)">(${Math.round(g.opt.lo)}–${Math.round(g.opt.hi)})</span></td>
    <td class="n">${g.rad.noTrend ? t("noTrendCell") : `<b>${Math.round(g.rad.t90)} ${t("yrs")}</b> <span style="color:var(--ink3)">(${Math.round(g.rad.lo)}–${Math.round(g.rad.hi)})</span>`}</td>
    <td class="n"><b>${g.rad.noTrend ? "?" : `+${Math.round(g.rad.t90 - g.opt.t90)} ${t("yrs")}`}</b></td></tr>`;
  document.getElementById("tbl").innerHTML = h;
}

/* ---------------- language & init ---------------- */
function tabsInit(){
  for (const [id, fn] of [["tabs", showRegion], ["swTabs", swShow]]){
    const el = document.getElementById(id); el.innerHTML = "";
    for (const r of G.regions){ if (id === "swTabs" && !r.img) continue; const b = document.createElement("button"); b.dataset.k = r.key; b.textContent = t("regions")[r.key]; b.onclick = () => fn(r.key); el.appendChild(b); }
  }
}
function applyLang(){
  document.documentElement.lang = L_;
  document.querySelectorAll("[data-i]").forEach(e => { const v = t(e.dataset.i); if (typeof v === "string") e.innerHTML = v; });
  document.querySelectorAll(".lang button").forEach(b => b.classList.toggle("on", b.dataset.l === L_));
  for (const id of ["ilL", "ilR", "ilStrong", "ilWeak", "ilG1", "ilG2"]) document.getElementById(id).textContent = t(id);
  const g = G.groups.med;
  document.getElementById("kOpt").innerHTML = `~${Math.round(g.opt.t90)}`;
  document.getElementById("kRad").innerHTML = `~${Math.round(g.rad.t90)}`;
  document.getElementById("kPx").textContent = G.nPx.toLocaleString();
  tabsInit();
  document.querySelectorAll("#tabs button").forEach(b => b.classList.toggle("on", b.dataset.k === curReg));
  document.querySelectorAll("#swTabs button").forEach(b => b.classList.toggle("on", b.dataset.k === swReg));
  bars(); drawEvidence(); table(); renderQuick();
  if (lastPlace) pick(lastPlace[0], lastPlace[1]); else document.getElementById("tryRes").innerHTML = `<div class="empty">${t("tryEmpty")}</div>`;
  pastMap.closePopup();
}
document.querySelectorAll(".lang button").forEach(b => b.onclick = () => { L_ = b.dataset.l; applyLang(); });
tabsInit(); showRegion(G.regions[0].key); swShow(G.regions[0].key); applyLang();
