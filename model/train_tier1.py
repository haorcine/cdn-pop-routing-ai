import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_PIVOT = os.path.join(GOC, "data", "data_pivot.csv")


def chuan_bi_du_lieu(df):
    le_vung, le_isp = LabelEncoder(), LabelEncoder()
    df = df.copy()
    df["vung_ma"] = le_vung.fit_transform(df["vung_dia_ly"])
    df["isp_ma"] = le_isp.fit_transform(df["isp"])
    X = df[["vung_ma", "isp_ma", "gio", "thu_trong_tuan"]]
    y = df["pop_toi_uu"]

    print("Phan bo nhan (truoc khi chia train/test):")
    print(y.value_counts())

    so_mau_it_nhat = y.value_counts().min()
    if so_mau_it_nhat < 2:
        print(f"\nCANH BAO: lop hiem nhat chi co {so_mau_it_nhat} mau, khong the stratify.")
        print("Se chia ngau nhien (khong stratify) - ket qua danh gia lop hiem se khong dang tin cay.")
        return train_test_split(X, y, test_size=0.2, random_state=42)

    return train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)


def danh_gia(ten_mo_hinh, mo_hinh, X_test, y_test):
    du_doan = mo_hinh.predict(X_test)
    print(f"\n--- {ten_mo_hinh} ---")
    print(f"Accuracy: {accuracy_score(y_test, du_doan):.3f}")
    print("Bao cao chi tiet theo tung lop (precision/recall/f1):")
    print(classification_report(y_test, du_doan, zero_division=0))
    nhan = sorted(y_test.unique())
    print("Ma tran nham lan (hang = thuc te, cot = du doan):")
    print(pd.DataFrame(confusion_matrix(y_test, du_doan, labels=nhan), index=nhan, columns=nhan))


def train_mo_hinh(X_train, y_train, X_test, y_test):
    dt = DecisionTreeClassifier(max_depth=5, random_state=42, class_weight="balanced")
    dt.fit(X_train, y_train)
    danh_gia("Decision Tree", dt, X_test, y_test)

    rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
    rf.fit(X_train, y_train)
    danh_gia("Random Forest", rf, X_test, y_test)

    return dt, rf


if __name__ == "__main__":
    df = pd.read_csv(FILE_PIVOT)
    print(f"Doc {len(df)} dong tu {FILE_PIVOT}\n")
    X_train, X_test, y_train, y_test = chuan_bi_du_lieu(df)
    print(f"\nTap train: {len(X_train)} dong, tap test: {len(X_test)} dong")
    train_mo_hinh(X_train, y_train, X_test, y_test)