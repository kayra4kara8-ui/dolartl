"""
TCMB EVDS API Debug Script
Çalıştır: python test_evds.py
"""
import requests
from urllib.parse import urlencode

API_KEY = "EDS05ZLAlI"

print("=" * 60)
print("TCMB EVDS API DEBUG")
print("=" * 60)

# ── TEST 1: Klasik params= yöntemi ──────────────────────────
print("\n[TEST 1] params= yöntemi, header key")
try:
    r = requests.get(
        "https://evds2.tcmb.gov.tr/service/evds/series",
        params={
            "series": "TP.DK.USD.A",
            "startDate": "01-01-2024",
            "endDate": "01-03-2024",
            "type": "json",
        },
        headers={"key": API_KEY},
        timeout=15,
    )
    print(f"  Status : {r.status_code}")
    print(f"  C-Type : {r.headers.get('content-type', '-')}")
    print(f"  Body   : {r.text[:300]}")
except Exception as e:
    print(f"  HATA   : {e}")

# ── TEST 2: urlencode path yöntemi ──────────────────────────
print("\n[TEST 2] urlencode path, header key")
try:
    params = {
        "series": "TP.DK.USD.A-TP.DK.USD.S",
        "startDate": "01-01-2024",
        "endDate": "01-03-2024",
        "type": "json",
        "frequency": "1",
    }
    url = f"https://evds2.tcmb.gov.tr/service/evds/{urlencode(params)}"
    print(f"  URL    : {url}")
    r = requests.get(url, headers={"key": API_KEY}, timeout=15)
    print(f"  Status : {r.status_code}")
    print(f"  C-Type : {r.headers.get('content-type', '-')}")
    print(f"  Body   : {r.text[:300]}")
except Exception as e:
    print(f"  HATA   : {e}")

# ── TEST 3: Key URL'de parametre olarak ─────────────────────
print("\n[TEST 3] key URL'de, klasik params")
try:
    r = requests.get(
        "https://evds2.tcmb.gov.tr/service/evds/series",
        params={
            "series": "TP.DK.USD.A",
            "startDate": "01-01-2024",
            "endDate": "01-03-2024",
            "type": "json",
            "key": API_KEY,
        },
        timeout=15,
    )
    print(f"  Status : {r.status_code}")
    print(f"  C-Type : {r.headers.get('content-type', '-')}")
    print(f"  Body   : {r.text[:300]}")
except Exception as e:
    print(f"  HATA   : {e}")

# ── TEST 4: Doğrudan tam URL ─────────────────────────────────
print("\n[TEST 4] Doğrudan tam URL + key hem header hem param")
try:
    url = (
        f"https://evds2.tcmb.gov.tr/service/evds/series=TP.DK.USD.A"
        f"&startDate=01-01-2024&endDate=01-03-2024&type=json&key={API_KEY}"
    )
    print(f"  URL    : {url}")
    r = requests.get(url, timeout=15)
    print(f"  Status : {r.status_code}")
    print(f"  C-Type : {r.headers.get('content-type', '-')}")
    print(f"  Body   : {r.text[:300]}")
except Exception as e:
    print(f"  HATA   : {e}")

# ── TEST 5: Sadece header, farklı endpoint ───────────────────
print("\n[TEST 5] /service/evds/dataindex endpoint")
try:
    r = requests.get(
        "https://evds2.tcmb.gov.tr/service/evds/dataindex",
        params={"type": "json"},
        headers={"key": API_KEY},
        timeout=15,
    )
    print(f"  Status : {r.status_code}")
    print(f"  C-Type : {r.headers.get('content-type', '-')}")
    print(f"  Body   : {r.text[:300]}")
except Exception as e:
    print(f"  HATA   : {e}")

print("\n" + "=" * 60)
print("Hangi test çalıştı? Sonuçları paylaşın.")
print("=" * 60)
