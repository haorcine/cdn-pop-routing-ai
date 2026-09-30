import os
import requests
import pandas as pd

from dotenv import load_dotenv
load_dotenv()
TOKEN = os.environ["RADAR_API_TOKEN"]
GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HEADERS = {"Authorization": f"Bearer {TOKEN}"}
BASE = "https://api.cloudflare.com/client/v4"

# Khop voi khoang thu thap thuc te cua nhom (xem meta.days_by_region)
DATE_START = "2026-09-05T00:00:00Z"
DATE_END = "2026-09-21T23:59:59Z"


def lay_latency_iqi():
    """Lay time series latency (RTT, p25/p50/p75) cua Radar cho Viet Nam."""
    r = requests.get(
        f"{BASE}/radar/quality/iqi/timeseries_groups",
        headers=HEADERS,
        params={
            "metric": "LATENCY",
            "location": "VN",
            "dateStart": DATE_START,
            "dateEnd": DATE_END,
            "aggInterval": "1h",   # cung muc chi tiet voi phan tich theo gio o 4.3.2
            "format": "JSON",
        },
    )
    r.raise_for_status()
    data = r.json()["result"]["serie_0"]
    df = pd.DataFrame({
        "thoi_diem": data["timestamps"],
        "latency_p25_ms": data["p25"],
        "latency_p50_ms": data["p50"],
        "latency_p75_ms": data["p75"],
    })
    df.to_csv(os.path.join(GOC, "data", "radar_latency_vn.csv"), index=False)
    print(f"Da luu {len(df)} dong latency Radar vao data/radar_latency_vn.csv")
    return df


def lay_su_co():
    """Lay danh sach su co (outage) Radar ghi nhan, loc rieng Viet Nam."""
    r = requests.get(
        f"{BASE}/radar/annotations/outages",
        headers=HEADERS,
        params={
            "dateStart": DATE_START,
            "dateEnd": DATE_END,
            "limit": 100,
            "format": "JSON",
        },
    )
    r.raise_for_status()
    annotations = r.json()["result"]["annotations"]
    su_co_vn = [a for a in annotations if "VN" in (a.get("locations") or [])]

    print(f"\nTong so su co Radar ghi nhan trong khoang: {len(annotations)}")
    print(f"So su co lien quan Viet Nam: {len(su_co_vn)}")
    for sk in su_co_vn:
        print(f"  {sk['startDate']} -> {sk.get('endDate')}: {sk.get('scope')} "
              f"(nguyen nhan: {sk.get('outage', {}).get('outageCause')})")

    pd.DataFrame(su_co_vn).to_csv(
        os.path.join(GOC, "data", "radar_su_co_vn.csv"), index=False
    )


if __name__ == "__main__":
    lay_latency_iqi()
    lay_su_co()