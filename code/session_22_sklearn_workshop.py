#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""جلسه ۲۲ — کارگاه یادگیری ماشین با scikit-learn روی load_breast_cancer.

چرخه‌ی کامل ML که در جلسه ۲۱ رسم کردیم، اینجا با کد واقعی:
  داده → تفکیک آموزش/آزمون (random_state ثابت) → آموزش → ارزیابی → تفسیر.

مثال صرفاً آموزشی و غیرتشخیصی است؛ این دیتاست برای تمرین برنامه‌نویسی است
و هرگز مبنای تصمیم بالینی قرار نمی‌گیرد.

وابستگی‌ها: numpy, scikit-learn (برای دقت بالاتر بهتر است pandas هم باشد اما لازم نیست).
اجرا:
    python3 code/session_22_sklearn_workshop.py

نکته تألیف: خروجی‌های عددی این اسکریپت باید با اجرای واقعی در Colab/محیط
نصب‌شده به‌دست آید؛ اعداد درون فایل جلسه «نمونه» هستند و کلید تأییدشده نیستند.
"""
from __future__ import annotations

import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

SEED = 42  # seed ثابت برای تکرارپذیری همه‌ی نتایج


def section(title: str) -> None:
    print(f"\n=== {title} ===")


def main() -> None:
    # ---------------------------------------------------------------- گام ۱: داده
    data = load_breast_cancer()
    X, y = data.data, data.target  # y: 0 = بدخیم (malignant)، 1 = خوش‌خیم (benign)
    print("breast_cancer:", X.shape, "نمونه/ویژگی — کلاس‌ها:",
          dict(zip(data.target_names, np.bincount(y))))

    # ------------------------------------------------ گام ۲: تفکیک آموزش/آزمون
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=SEED, stratify=y
    )
    section("گام ۲: تفکیک آموزش/آزمون (۸۰/۲۰، stratify، random_state=42)")
    print("train:", X_train.shape, " test:", X_test.shape)

    # --------------------------------------------------------- گام ۳: آموزش مدل
    models = {
        "LogisticRegression": LogisticRegression(max_iter=5000, random_state=SEED),
        "DecisionTree (deep)": DecisionTreeClassifier(random_state=SEED),  # عمداً بدون محدودیت عمق
        "RandomForest": RandomForestClassifier(n_estimators=100, random_state=SEED),
    }
    results = {}
    section("گام ۳: آموزش و ارزیابی سه مدل")
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        cm = confusion_matrix(y_test, y_pred)
        results[name] = model
        print(f"\n{name}:")
        print(f"  accuracy = {acc:.3f}    f1 = {f1:.3f}")
        print("  confusion matrix (سطر: واقعی، ستون: پیش‌بینی؛ کلاس 0 اول):")
        print(cm)

    # ------------------------------------------- گام ۴: نمایش بیش‌برازش با درخت
    section("گام ۴: بیش‌برازش — درخت بدون محدودیت عمق")
    tree = results["DecisionTree (deep)"]
    print(f"  train accuracy = {tree.score(X_train, y_train):.3f}")
    print(f"  test  accuracy = {tree.score(X_test, y_test):.3f}")
    tree_limited = DecisionTreeClassifier(max_depth=3, random_state=SEED)
    tree_limited.fit(X_train, y_train)
    print(f"  درخت با max_depth=3 → train = {tree_limited.score(X_train, y_train):.3f}"
          f" / test = {tree_limited.score(X_test, y_test):.3f}")

    # -------------------------------------- گام ۵: اهمیت ویژگی‌ها (RandomForest)
    section("گام ۵: ۵ ویژگی مهم‌تر طبق RandomForest")
    rf = results["RandomForest"]
    importances = rf.feature_importances_
    order = np.argsort(importances)[::-1][:5]
    for idx in order:
        print(f"  {data.feature_names[idx]:<25} {importances[idx]:.3f}")

    section("پایان")
    print("همه‌ی seedها ثابت‌اند (42)؛ اجرای دوباره همین اعداد را می‌دهد.")


if __name__ == "__main__":
    main()
