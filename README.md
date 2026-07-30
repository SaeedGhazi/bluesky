# BlueSky - The Open Air Traffic Simulator

[![Open in Visual Studio Code](https://img.shields.io/static/v1?logo=visualstudiocode&label=&message=Open%20in%20Visual%20Studio%20Code&labelColor=2c2c32&color=007acc&logoColor=007acc)](https://open.vscode.dev/TUDelft-CNS-ATM/bluesky)
[![GitHub release](https://img.shields.io/github/release/TUDelft-CNS-ATM/bluesky.svg)](https://GitHub.com/TUDelft-CNS-ATM/bluesky/releases/)
![GitHub all releases](https://img.shields.io/github/downloads/TUDelft-CNS-ATM/bluesky/total?style=social)
[![Discord](https://img.shields.io/discord/1359446056877690970?style=flat&logo=discord&logoColor=green&logoSize=auto&label=BlueSky%20discussion)](https://discord.gg/wkBKgXCHYN)


[![PyPI version shields.io](https://img.shields.io/pypi/v/bluesky-simulator.svg)](https://pypi.python.org/pypi/bluesky-simulator/)
![PyPI - Downloads](https://img.shields.io/pypi/dm/bluesky-simulator?style=plastic)
[![PyPI license](https://img.shields.io/pypi/l/bluesky-simulator?style=plastic)](https://pypi.python.org/pypi/bluesky-simulator/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/bluesky-simulator?style=plastic)](https://pypi.python.org/pypi/bluesky-simulator/)

BlueSky is meant as a tool to perform research on Air Traffic Management and Air Traffic Flows, and is distributed under the MIT license.

The goal of BlueSky is to provide everybody who wants to visualize, analyze or simulate air
traffic with a tool to do so without any restrictions, licenses or limitations. It can be copied,
modified, cited, etc. without any limitations.

**Citation info:** J. M. Hoekstra and J. Ellerbroek, "[BlueSky ATC Simulator Project: an Open Data and Open Source Approach](https://www.researchgate.net/publication/304490055_BlueSky_ATC_Simulator_Project_an_Open_Data_and_Open_Source_Approach)", Proceedings of the seventh International Conference for Research on Air Transport (ICRAT), 2016.

## BlueSky Releases
BlueSky is also available as a pip package, for which periodically version releases are made. You can find the latest release here:
https://github.com/TUDelft-CNS-ATM/bluesky/releases
The BlueSky pip package is installed with the following command:

    pip install bluesky-simulator[full]

Using ZSH? Add quotes around the package name: `"bluesky-simulator[full]"`. For more installation instructions go to the Wiki.

## BlueSky Wiki
Installation and user guides are accessible at:
https://github.com/TUDelft-CNS-ATM/bluesky/wiki

## Some features of BlueSky:
- Written in the freely available, ultra-simple-hence-easy-to-learn, multi-platform language
Python 3 (using numpy and either pygame or Qt+OpenGL for visualisation) with source
- Extensible by means of self-contained [plugins](https://github.com/TUDelft-CNS-ATM/bluesky/wiki/plugin)
- Contains open source data on navaids, performance data of aircraft and geography
- Global coverage navaid and airport data
- Contains simulations of aircraft performance, flight management system (LNAV, VNAV under construction),
autopilot, conflict detection and resolution and airborne separation assurance systems
- Compatible with BADA 3.x data
- Compatible wth NLR Traffic Manager TMX as used by NLR and NASA LaRC
- Traffic is controlled via user inputs in a console window or by playing scenario files (.SCN)
containing the same commands with a time stamp before the command ("HH:MM:SS.hh>")
- Mouse clicks in traffic window are use in console for lat/lon/heading and position inputs

## Questions or suggestions?
Visit us on [Discord](https://discord.gg/wkBKgXCHYN), open a topic on the GitHub discussion board, or open an issue.

## Contributions
BlueSky can be considered 'perpetual beta'. We would like to encourage anyone with a strong interest in
ATM and/or Python to join us. Please feel free to comment, criticise, and contribute to this project. Please send suggestions, proposed changes or contributions through GitHub pull requests, preferably after debugging it and optimising it for run-time performance.

---

# BlueSky Fork — Tehran FIR ATC Simulation

> این یک fork سفارشی از [TUDelft-CNS-ATM/bluesky](https://github.com/TUDelft-CNS-ATM/bluesky)
> است که برای شبیه‌سازی کنترل ترافیک هوایی منطقهٔ **Tehran FIR** با داده‌های
> واقعی AIP ایران سفارشی‌سازی شده است.

---

## این فورک چیست و چرا وجود دارد

BlueSky در این پروژه **فقط موتور فیزیک/محاسبات پرواز** است — نه واسط کاربری نهایی.
خروجی آن از طریق یک لایهٔ Bridge به یک نمایشگر رادار وب‌محور (MapLibre GL JS) و
یک کنسول عملیاتی خلبان مجازی (BlipDriver) منتقل می‌شود.

```
┌─────────────────────────────────────────────────────────┐
│  این ریپو: BlueSky (فورک)                                │
│  - navdata سفارشی‌شده بر اساس AIP ایران                  │
│  - atc_extras.py (plugin سفارشی)                         │
└───────────────┬─────────────────────┬────────────────────┘
                │ ZMQ 11000           │ ZMQ 11005
                ▼                     ▼
         ┌──────────────────────────────────┐
         │  bluesky-bridge.py (ریپوی جدا)   │
         │  merge → WebSocket (port 8080)   │
         └───────────────┬───────────────────┘
                         │
           ┌─────────────┴─────────────┐
           ▼                           ▼
  flat(BlueSky).html          BlipDriver (ریپوی جدا،
  نمایشگر رادار وب            کنسول خلبان مجازی)
```

اکوسیستم کامل شامل چند ریپوی مرتبط است:
| ریپو | نقش |
|---|---|
| **این ریپو (bluesky fork)** | موتور شبیه‌سازی + دادهٔ ناوبری ایران |
| `bluesky-bridge` + `atc_extras` | لایهٔ پل بین BlueSky و نمایشگرها |
| `flat(BlueSky).html` | نمایشگر رادار وب مشترک |
| `BlipDriver` (در دست ساخت) | کنسول خلبان مجازی — سطح فرمان، نه کنترل مستقیم |
| فورک FlightGear (جدا) | نمایش بصری برج مراقبت ۳بعدی |

---

## تغییرات این فورک نسبت به upstream

### ۱. داده‌های ناوبری (navdata) بازنویسی‌شده بر اساس AIP ایران
مسیر: `bluesky/resources/navdata/`

| فایل | تغییر |
|---|---|
| `apt.dat` | محدود به فرودگاه‌های ایران (پیشوند ICAO `OI`)، به‌روزشده طبق AIP — **نگاه کنید به بخش «مشکلات شناخته‌شده» پایین** |
| `fix.dat` | نقاط گزارش‌دهی/waypoint های ایران طبق AIP |
| `awy.dat` | مسیرهای هوایی (airways) ایران |
| `nav.dat` | کمک‌ناوبری‌ها (VOR/NDB/ILS و...) ایران |

**چرا:** داده‌های پیش‌فرض BlueSky جهانی و عمومی هستند؛ برای شبیه‌سازی دقیق Tehran FIR باید مطابق AIP رسمی ایران باشند.

### ۲. Plugin سفارشی: `atc_extras.py`
مسیر: `bluesky/plugins/atc_extras.py`

منتشرکنندهٔ داده‌های تکمیلی ATC روی ZMQ PUB (پورت `11005`) که در acdata استاندارد BlueSky نیست:
- `squawk`, `situation`, `ident` (با auto-cancel ۲۰ ثانیه‌ای)
- `CFL` (Cleared Flight Level) — با دستور جدید `CFL <acid> <FL>`
- `orig`/`dest`
- ETA **زنجیره‌ای per-waypoint** (leg-by-leg بر اساس GS، نه فاصلهٔ مستقیم)

دستورات stack جدید: `SQWK`, `SITSIT`, `CFL`, `IDENT`, `RTEDEBUG` (دیباگ ساختار route).

فعال‌سازی (در `settings.cfg`):
```python
enabled_plugins = ['area', 'datafeed', 'atc_extras']
```

---

## نصب و اجرا

```bash
git clone git@github.com:SaeedGhazi/bluesky.git
cd bluesky
python -m venv venv #(python3.11 , requirements(Python3.11).txt)
source venv/bin/activate
pip install -e .

# مهم: BlueSky مسیرهای plugin/cache را نسبت به working directory حل می‌کند
# همیشه از ریشهٔ همین پوشه اجرا کنید:
cd bluesky-master/    # یا مسیر معادل
python BlueSky.py
```

در کنسول BlueSky:
```
PLUGIN LOAD ATC_EXTRAS
```

راه‌اندازی کامل اکوسیستم (این ریپو + Bridge + نمایشگر):
```bash
# ترمینال ۱
python BlueSky.py

# ترمینال ۲ (ریپوی bluesky-bridge)
python bluesky-bridge.py

# ترمینال ۳
python -m http.server 8000
# مرورگر: http://localhost:8000/flat(BlueSky).html
```

---

## مشکلات شناخته‌شده و راه‌حل در دست اجرا

### ⚠️ خطای ساخت cache در `aptsurface.p`
**علت:** `apt.dat` سفارشی فاقد ردیف‌های هندسی pavement/taxiway (کدهای X-Plane format
`110-116`, `120`, `130`) است که مفسر BlueSky برای ساخت polygon سطح فرودگاه به آن‌ها نیاز دارد.
این هندسه در فایل ما نیست چون به‌جای آن، یک `Iran_Airports_Layouts.geojson` مستقل
برای نمایش در نقشهٔ وب (MapLibre) ساخته شده — نه برای مصرف داخل BlueSky.

**راه‌حل در حال اعمال:** به‌جای بازنویسی apt.dat از صفر، نسخهٔ اصلی جهانی apt.dat
(از upstream یا history گیت) با اسکریپت `filter_apt_dat.py` به ۲۸ فرودگاه ایران
(پیشوند `OI`) محدود می‌شود — geometry اصلی سالم حفظ و حجم فایل به‌شدت کاهش می‌یابد.
سپس اصلاحات AIP (runway heading/threshold، فرکانس‌ها) روی همین فایل فیلترشده
اعمال می‌شود، نه بازسازی کامل.

فرودگاه‌های هدف (۲۸ فرودگاه، از `Iran_Airports_Layouts.geojson` استخراج‌شده):
```
OIAW OICC OICI OICS OIFM OIGG OIHH OIIA OIIB OIIC OIID OIIE OIIF OIII
OIIM OIIP OIKB OIMM OISS OITK OITL OITM OITP OITR OITT OITU OITZ OIYY
```

---

## اصول این فورک (برای هرکسی/هر AI که ادامه می‌دهد)

1. **این ریپو فقط موتور فیزیک است.** منطق فرمان/تصمیم‌گیری در ریپوهای BlipDriver
   و لایهٔ میانی است، نه اینجا. تغییرات این ریپو باید محدود به: navdata، پلاگین‌های
   ATC، و تنظیمات مربوط به دقت شبیه‌سازی بماند.
2. **سازگاری با upstream را تا حد امکان حفظ کنید** — تغییرات را در فایل‌های جدید
   (پلاگین‌ها) یا داده (navdata) متمرکز کنید، نه در هستهٔ کد BlueSky، تا merge کردن
   به‌روزرسانی‌های آیندهٔ upstream ساده بماند.
3. واحدهای داخلی BlueSky را به خاطر بسپارید: `gs`, `cas`, `vs` به **m/s**، `alt` به
   **متر** هستند — تبدیل واحد در لایهٔ Bridge انجام می‌شود، نه اینجا.

---

## مستندات مرتبط (ریپوهای دیگر)

- `PROJECT_STATUS.md`, `ARCHITECTURE.md`, `BD_UI_SPEC.md` — در ریپوی BlipDriver
- این فایل‌ها معماری کامل اکوسیستم، تصمیمات طراحی با دلیل، و کارهای باز را نگه می‌دارند.
