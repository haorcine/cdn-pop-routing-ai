import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

from baseline import baseline_khoang_cach, baseline_latency_trung_binh

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_PIVOT = os.path.join(GOC, "data", "data_pivot.csv")


def latency_thuc_te(df, ten_cot_du_doan):
    """Voi moi dong, lay latency_ms cua PoP ma cot du doan chi ra."""
    return df.apply(lambda dong: dong[f"latency_ms_{dong[ten_cot_du_doan]}"], axis=1)


def main():
    df = pd.read_csv(FILE_PIVOT)
    le_vung, le_isp = LabelEncoder(), LabelEncoder()
    df["vung_ma"] = le_vung.fit_transform(df["vung_dia_ly"])
    df["isp_ma"] = le_isp.fit_transform(df["isp"])
    X = df[["vung_ma", "isp_ma", "gio", "thu_trong_tuan"]]
    y = df["pop_toi_uu"]

    so_mau_it_nhat = y.value_counts().min()
    if so_mau_it_nhat < 2:
        X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
            X, y, df.index, test_size=0.2, random_state=42
        )
    else:
        X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
            X, y, df.index, test_size=0.2, random_state=42, stratify=y
        )
    df_test = df.loc[idx_test].copy()
    df_train = df.loc[idx_train].copy()

    dt = DecisionTreeClassifier(max_depth=5, random_state=42, class_weight="balanced")
    dt.fit(X_train, y_train)
    rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
    rf.fit(X_train, y_train)

    df_test["du_doan_dt"] = dt.predict(X_test)
    df_test["du_doan_rf"] = rf.predict(X_test)
    df_test["baseline_kc"] = baseline_khoang_cach()
    df_test["baseline_tb"] = baseline_latency_trung_binh(df_train)

    ket_qua = {}
    for ten, cot in [
        ("Decision Tree", "du_doan_dt"),
        ("Random Forest", "du_doan_rf"),
        ("Baseline khoang cach", "baseline_kc"),
        ("Baseline latency trung binh", "baseline_tb"),
    ]:
        lat = latency_thuc_te(df_test, cot)
        ket_qua[ten] = lat.mean()
        print(f"{ten:32s}: latency TB = {lat.mean():6.1f} ms (trung vi {lat.median():5.1f} ms)")

    print("\n% cai thien so voi tung baseline (so voi latency TB tren cung tap test):")
    for ten_ai in ["Decision Tree", "Random Forest"]:
        for ten_bl in ["Baseline khoang cach", "Baseline latency trung binh"]:
            cai_thien = (ket_qua[ten_bl] - ket_qua[ten_ai]) / ket_qua[ten_bl] * 100
            print(f"  {ten_ai} vs {ten_bl}: {cai_thien:+.1f}%")


if __name__ == "__main__":
    main()