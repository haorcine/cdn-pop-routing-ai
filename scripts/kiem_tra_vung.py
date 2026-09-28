import os
import pandas as pd

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df = pd.read_csv(os.path.join(GOC, "data", "data_pivot.csv"))

pops = ["cloudflare", "vultr_singapore", "vultr_seoul", "linode_singapore"]
cot = [f"latency_ms_{p}" for p in pops]

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", None)

print(df.groupby(["vung_dia_ly", "isp"])[cot].agg(["mean", "median"]).round(1).T)