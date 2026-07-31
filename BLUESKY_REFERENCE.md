# BlueSky — مرجع کامل دستورات و پیکربندی

> منبع: [مخزن رسمی TUDelft-CNS-ATM/bluesky](https://github.com/TUDelft-CNS-ATM/bluesky)،
> فایل [`docs/BLUESKY-COMMAND-TABLE.TXT`](https://github.com/TUDelft-CNS-ATM/bluesky/blob/master/docs/BLUESKY-COMMAND-TABLE.TXT)،
> [`bluesky/settings.py`](https://github.com/TUDelft-CNS-ATM/bluesky/blob/master/bluesky/settings.py)،
> و [Wiki رسمی](https://github.com/TUDelft-CNS-ATM/bluesky/wiki)
> — بعلاوهٔ `settings.cfg` واقعی این پروژه.

---

## بخش ۱ — دستورات Stack (Command Reference)

دستورات همگی از طریق کنسول متنی BlueSky، یا با timestamp داخل فایل سناریوی `.SCN`
(فرمت `HH:MM:SS.hh> COMMAND`) قابل استفاده‌اند.

### ۱.۱ — کنترل هواپیما (Aircraft & Autopilot)

| دستور | توضیح | نحوهٔ استفاده |
|---|---|---|
| `CRE` (مترادف: `CREATE`) | ساخت هواپیما | `CRE acid,type,lat,lon,hdg,alt,spd` |
| `MCRE` | ساخت چند هواپیمای تصادفی هم‌زمان | `MCRE n,[type/*,alt/*,spd/*,dest/*]` |
| `DEL` (مترادف: `DELETE`) | حذف هواپیما/باد/ناحیه | `DEL acid/WIND/shape` |
| `MOVE` | جابه‌جایی فوری هواپیما به موقعیت جدید | `MOVE acid,lat,lon,[alt,hdg,spd,vspd]` |
| `ALT` | فرمان ارتفاع (autopilot) | `ALT acid,alt,[vspd]` |
| `HDG` (مترادف: `HEADING`, `TURN`) | فرمان heading | `HDG acid,hdg` |
| `SPD` (مترادف: `SPEED`) | فرمان سرعت (CAS-kts/Mach) | `SPD acid,spd` |
| `VS` | فرمان سرعت عمودی (ft/min) | `VS acid,vspd` |
| `LNAV` | روشن/خاموش‌کردن حالت افقی FMS | `LNAV acid,[ON/OFF]` |
| `VNAV` | روشن/خاموش‌کردن حالت عمودی FMS | `VNAV acid,[ON/OFF]` |
| `ORIG` | تعیین فرودگاه مبدأ | `ORIG acid,latlon/airport` |
| `DEST` | تعیین فرودگاه مقصد | `DEST acid,latlon/airport` |
| `ENG` | تغییر نوع موتور | `ENG acid,[engine_id]` |
| `NOM` | بازگشت به شتاب استاندارد (مدل perf) | `NOM acid` |
| `POS` | نمایش اطلاعات کامل هواپیما | `POS acid` |
| `ND` | نمایش Navigation Display با CDTI | `ND acid` |
| `SSD` | نمایش State-Space Diagram (پیش‌بینی تعارض) | `SSD acid/ALL/OFF` |

### ۱.۲ — مسیر و FMS (Route / Waypoints)

| دستور | توضیح | نحوهٔ استفاده |
|---|---|---|
| `ADDWPT` | افزودن waypoint به مسیر | `ADDWPT acid,(wpname/lat,lon),[alt,spd,afterwp]` |
| `AFTER` | افزودن waypoint بعد از یک waypoint خاص | `acid AFTER afterwp ADDWPT (wpname/lat,lon),[alt,spd]` |
| `DELWPT` (مترادف: `DELWP`) | حذف یک waypoint | `DELWPT acid,wpname` |
| `DELRTE` (مترادف: `DELROUTE`) | حذف کامل مسیر/مقصد/مبدأ | `DELRTE acid` |
| `DIRECT` (مترادف: `DIRECTTO`, `DIRTO`) | رفتن مستقیم به یک waypoint | `DIRECT acid,wpname` |
| `AT` | ویرایش/حذف/نمایش قیود سرعت-ارتفاع در یک waypoint | `acid AT wpname [DEL] SPD/ALT [spd/alt]` |
| `LISTRTE` | نمایش مسیر (۵ waypoint در هر صفحه) | `LISTRTE acid,[pagenr]` |
| `DUMPRTE` | ذخیرهٔ مسیر در `output/routelog.txt` | `DUMPRTE acid` |
| `DEFWPT` | تعریف waypoint موقت فقط برای این سناریو | `DEFWPT wpname,[lat,lon,type,refapt,countrycode]` |
| `RUNWAYS` | فهرست باندهای یک فرودگاه | `RUNWAYS ICAO` |

### ۱.۳ — کنترل زمان و اجرای شبیه‌سازی

| دستور | توضیح | نحوهٔ استفاده |
|---|---|---|
| `OP` (مترادف: `RUN`, `START`, `CONTINUE`) | شروع/ادامهٔ شبیه‌سازی | `OP` |
| `HOLD` (مترادف: `PAUSE`) | توقف موقت | `HOLD` |
| `RESET` | بازنشانی کامل شبیه‌سازی | `RESET` |
| `QUIT` (مترادف: `STOP`, `END`, `EXIT`, `CLOSE`, `Q`) | خروج از برنامه | `QUIT` |
| `IC` (مترادف: `LOAD`, `OPEN`) | شروع مجدد و باز کردن یک سناریو | `IC [filename]` |
| `SAVEIC` (مترادف: `SAVE`) | ذخیرهٔ وضعیت فعلی به‌عنوان IC | `SAVEIC filename` |
| `BATCH` | اجرای دسته‌ای یک فایل سناریو | `BATCH filename` |
| `PCALL` | فراخوانی دستورات از فایل سناریوی دیگر | `PCALL filename,[REL/ABS]` |
| `SCEN` | نام‌گذاری سناریوی فعلی | `SCEN scenname` |
| `FF` (مترادف: `FWD`) | حرکت سریع‌تر از زمان واقعی | `FF [tend]` |
| `DT` | تنظیم گام زمانی شبیه‌سازی | `DT dt` |
| `DTMULT` | ضریب سرعت شبیه‌سازی fast-time | `DTMULT multiplier` |
| `FIXDT` | ثابت‌کردن گام زمانی | `FIXDT ON/OFF,[tend]` |
| `TIME` | تنظیم ساعت شبیه‌سازی | `TIME RUN / HH:MM:SS.hh / REAL / UTC` |
| `BENCHMARK` | اجرای بنچمارک عملکرد | `BENCHMARK [scenfile,time]` |
| `SEED` | تنظیم seed تصادفی (برای MCRE/NOISE) | `SEED value` |

### ۱.۴ — تعارض و جداسازی (ASAS / Conflict Resolution)

| دستور | توضیح |
|---|---|
| `ASAS` | روشن/خاموش‌کردن سیستم جداسازی هوایی |
| `CDMETHOD` | تعیین روش تشخیص تعارض |
| `RESO` | تعیین روش قطع‌نامه (resolution) |
| `RESOOFF` | خاموش‌کردن resolution برای یک هواپیمای خاص |
| `NORESO` | خاموش‌کردن conflict resolution برای هواپیمای خاص |
| `RMETHH` (مترادف: `HMETH`, `HRESOM`, `HRESOMETH`) | روش resolution افقی |
| `RMETHV` (مترادف: `VMETH`, `VRESOM`, `VRESOMETH`) | روش resolution عمودی |
| `RFACH` (مترادف: `RESOFACH`) | ضریب margin افقی |
| `RFACV` (مترادف: `RESOFACV`) | ضریب margin عمودی |
| `ZONER` | شعاع افقی منطقهٔ حفاظت‌شده (NM) |
| `ZONEDH` | نیمهٔ ارتفاع منطقهٔ حفاظت‌شده (ft) |
| `RSZONER` | شعاع افقی منطقهٔ resolution (NM) |
| `RSZONEDH` | نیمهٔ ارتفاع منطقهٔ resolution (ft) |
| `DTLOOK` | افق زمانی تشخیص تعارض (ثانیه) |
| `DTNOLOOK` | فاصلهٔ زمانی بین بررسی‌های تعارض |
| `PRIORULES` | قوانین اولویت (حق تقدم) |

### ۱.۵ — نواحی و اشکال هندسی (Area / Shapes)

| دستور | توضیح | نحوهٔ استفاده |
|---|---|---|
| `AREA` | تعریف ناحیهٔ آزمایش (منطقهٔ مورد علاقه) | `AREA shapename/OFF` یا `AREA lat,lon,lat,lon,[top,bottom]` |
| `BOX` | تعریف ناحیهٔ مستطیلی | `BOX name,lat,lon,lat,lon,[top,bottom]` |
| `CIRCLE` | تعریف ناحیهٔ دایره‌ای | `CIRCLE name,lat,lon,radius,[top,bottom]` |
| `POLY` | تعریف ناحیهٔ چندضلعی | `POLY name,lat,lon,lat,lon,...` |
| `POLYALT` | چندضلعی سه‌بعدی (بین دو ارتفاع) | `POLYALT name,top,bottom,lat,lon,...` |
| `LINE` | رسم خط روی نقشهٔ رادار | `LINE name,lat,lon,lat,lon` |

### ۱.۶ — نمایش رادار (Qt/OpenGL GUI)

| دستور | توضیح |
|---|---|
| `SWRAD` (مترادف: `DISP`) | روشن/خاموش‌کردن لایه‌های نقشه (GEO/GRID/APT/VOR/WPT/LABEL/ADSBCOVERAGE/TRAIL) |
| `SYMBOL` | تغییر نماد هواپیما |
| `TRAIL` | روشن/خاموش‌کردن دنبالهٔ پرواز، یا تنظیم رنگ per-aircraft |
| `PAN` | حرکت دوربین به یک نقطه/جهت/هواپیما |
| `ZOOM` | بزرگ‌نمایی نقشه (`ZOOM IN/OUT` یا فاکتور عددی) |

### ۱.۷ — سایر (متفرقه)

| دستور | توضیح |
|---|---|
| `WIND` | تعریف بردار باد در میدان دوبعدی/سه‌بعدی |
| `GETWIND` | دریافت مقدار باد در یک نقطه/ارتفاع خاص |
| `NOISE` | روشن/خاموش‌کردن اغتشاش (turbulence) |
| `TAXI` | روشن/خاموش‌کردن حالت زمینی (جلوگیری از حذف خودکار زیر ۱۵۰۰ft) |
| `METRIC` | ماژول معیارهای پیچیدگی ترافیک |
| `SYN` | تولید سناریوهای هندسی مصنوعی (زیردستورها: `HELP, SIMPLE, SIMPLED, DIFG, SUPER, MATRIX, FLOOR, TAKEOVER, WALL, ROW, COLUMN, DISP`) |
| `DIST` | محاسبهٔ فاصله و جهت بین دو موقعیت |
| `CALC` | ماشین‌حساب ساده داخل خط فرمان |
| `ECHO` | نمایش متن در پنجرهٔ کنسول |
| `HELP` | راهنمای یک دستور، یا خروجی PDF/فایل کامل دستورات |
| `INSEDIT` | درج متن در خط ویرایش کنسول |
| `INSTLOG` / `SKYLOG` / `SNAPLOG` | ثبت داده (data logging) با تنظیمات مختلف |
| `DATAFEED` | فعال/غیرفعال‌کردن منبع دادهٔ ADS-B خارجی |
| `ADDNODES` | افزودن یک نمونهٔ شبیه‌سازی جدید (multi-node) |

---

## بخش ۲ — پیکربندی (Configuration)

### ۲.۱ — فایل `settings.cfg`

محل: ریشهٔ پروژه (کنار `BlueSky.py`)، تولید خودکار در اولین اجرا اگر وجود نداشته باشد.

**تنظیمات فعلی این پروژه** (Tehran FIR):

```ini
# --- شبکه ---
recv_port = 11000       # پورت دریافت رویداد (event) — client به این پورت وصل می‌شود
send_port = 11001       # پورت پخش جریان داده (stream) — ACDATA و غیره

# --- مدل عملکرد پرواز ---
performance_model = 'openap'      # گزینه‌ها: 'openap', 'bada', 'legacy'

# --- لاگ و verbose ---
verbose = False

# --- مسیرها (نسبت به ریشهٔ پروژه) ---
log_path       = 'output'
scenario_path  = 'scenario'
gfx_path       = 'graphics'
cache_path     = 'cache'
navdata_path   = 'navdata'
perf_path      = 'performance'
perf_path_bada = 'performance/BADA'   # خالی بگذارید اگر BADA ندارید
plugin_path    = 'plugins'

# --- پلاگین‌های فعال در startup ---
enabled_plugins = ['area', 'datafeed', 'atc_extras']

# --- شروع نقشه ---
start_location = 'OIII'    # می‌تواند [lat, lon] یا کد ICAO فرودگاه باشد

# --- گام‌های زمانی ---
simdt          = 0.05      # گام زمانی شبیه‌سازی (ثانیه)
performance_dt = 1.0       # گام محاسبهٔ عملکرد
fms_dt         = 1.0       # گام محاسبهٔ FMS

# --- عملکرد ---
prefer_compiled = True     # استفاده از ماژول‌های کامپایل‌شده (cgeo, casas) در صورت وجود
max_nnodes       = 999     # حداکثر تعداد node های موازی

# --- ASAS (جداسازی هوایی) ---
asas_dtlookahead = 300.0   # افق زمانی تشخیص تعارض (ثانیه)
asas_dt          = 1.0     # گام به‌روزرسانی ASAS
asas_pzr         = 5.0     # شعاع منطقهٔ حفاظت‌شدهٔ افقی (NM)
asas_pzh         = 1000.0  # نیمهٔ منطقهٔ حفاظت‌شدهٔ عمودی (ft)
asas_marh        = 1.05    # ضریب margin افقی
asas_marv        = 1.05    # ضریب margin عمودی

# --- ظاهر رابط Qt/OpenGL ---
text_size              = 13
apt_size               = 10
wpt_size                = 10
ac_size                = 16
stack_text_color       = 0, 255, 0
stack_background_color = 102, 102, 102
```

> نکته: مسیرهای بالا (`navdata_path` و غیره) از نسخهٔ ۲۰۲۲.۹.۱۹ به بعد **نسبی به پوشهٔ
> `bluesky/resources/`** حل می‌شوند (نه پوشهٔ `data/` قدیمی).

### ۲.۲ — پیکربندی شبکه (Network)

BlueSky از **ZMQ** برای ارتباط بین هستهٔ شبیه‌سازی (sim node) و کلاینت‌ها
(GUI یا ابزارهای بیرونی مثل Bridge ما) استفاده می‌کند:

| پورت (پیش‌فرض این پروژه) | جهت | محتوا |
|---|---|---|
| **11000** (`recv_port`) | client → server | کانال رویداد (event) — دستورات، وضعیت اتصال |
| **11001** (`send_port`) | server → client | کانال جریان (stream) — پخش ACDATA (وضعیت هواپیماها) |

> نکته: در برخی نسخه‌ها/نصب‌های پیش‌فرض BlueSky، این پورت‌ها `9000`/`9001` (کانال
> رویداد اصلی) و `10000`/`10001` (کانال node های شبیه‌سازی) هستند؛ در پروژهٔ ما با
> `recv_port`/`send_port` در `settings.cfg` صراحتاً به `11000`/`11001` ست شده‌اند.

**پورت‌های اضافهٔ این پروژه (خارج از خود BlueSky، توسط پلاگین/Bridge ما):**

| پورت | ساخته‌شده توسط | محتوا |
|---|---|---|
| 11005 | `atc_extras.py` (ZMQ PUB) | داده‌های تکمیلی ATC (squawk, CFL, ETA, ...) به فرمت JSON |
| 8080 | `bluesky-bridge.py` (WebSocket) | داده merge‌شدهٔ flat JSON برای `flat(BlueSky).html` و BlipDriver |

**Discovery:** BlueSky قابلیت discovery خودکار سرور در شبکه دارد (`enable_discovery`)،
که در این پروژه به‌طور پیش‌فرض غیرفعال است (`Discovery is disabled` در لاگ اجرا) —
چون آدرس/پورت‌ها به‌صورت صریح در Bridge تنظیم شده‌اند.

### ۲.۳ — ساختار فایل سناریو (`.SCN`)

هر خط: `HH:MM:SS.hh> COMMAND`
مثال:
```
00:00:00.00> CRE IRB952,A300,OIII,290,35000,340
00:00:05.00> ALT IRB952,FL210
00:00:10.00> ADDWPT IRB952,RASMO
```

### ۲.۴ — سیستم پلاگین

هر پلاگین یک ماژول پایتون در `plugin_path` (پیش‌فرض: `plugins/`) با یک تابع
`init_plugin()` است که یک dict پیکربندی برمی‌گرداند (`plugin_name`, `plugin_type`).
BlueSky به‌صورت خودکار پلاگین‌های این پوشه را تشخیص می‌دهد؛ فعال‌سازی با دستور
`PLUGIN LOAD <NAME>` یا از طریق `enabled_plugins` در `settings.cfg` برای بارگذاری
خودکار در startup.

---

## پیوست — منابع

- [مخزن اصلی BlueSky (upstream)](https://github.com/TUDelft-CNS-ATM/bluesky)
- [جدول کامل دستورات (رسمی)](https://github.com/TUDelft-CNS-ATM/bluesky/blob/master/docs/BLUESKY-COMMAND-TABLE.TXT)
- [Wiki رسمی — Sim Commands](https://github.com/TUDelft-CNS-ATM/bluesky/wiki/Sim-commands)
- [Wiki رسمی — Plugin development](https://github.com/TUDelft-CNS-ATM/bluesky/wiki/plugin)
- [Wiki رسمی — Running BlueSky](https://github.com/TUDelft-CNS-ATM/bluesky/wiki/Running-BlueSky)
