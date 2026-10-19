#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""جلسه ۲۱ — متریک‌های ارزیابی مدل با پایتون استاندارد (بدون هیچ کتابخانه‌ای).

این اسکریپت روی داده‌ی ساختگی (سینتکتیک) و کاملاً قطعی (seed ثابت) کار می‌کند:
  1) ماتریس درهم‌ریختگی (Confusion Matrix) را می‌سازد.
  2) دقت (Accuracy)، حساسیت (Sensitivity/Recall/TPR)، ویژگی (Specificity/TNR)،
     PPV، NPV و F1 را حساب می‌کند.
  3) با جاروب آستانه (Threshold sweep) نقاط ROC را می‌دهد و منحنی ROC
     را به‌صورت ASCII رسم می‌کند (AUC به روش ذوزنقه).
  4) سناریوی نامتوازن (Prevalence = 5٪) نشان می‌دهد چرا Accuracy گمراه‌کننده است.

مثال پزشکی صرفاً آموزشی و غیرتشخیصی است؛ داده‌ها واقعی نیستند.

اجرا:
    python3 code/session_21_ml_metrics.py
"""
from __future__ import annotations


# ---------------------------------------------------------------- داده ساختگی
def lcg(seed: int):
    """تولیدکننده اعداد شبه‌تصادفی قطعی (Linear Congruential Generator)."""
    state = seed & 0x7FFFFFFF
    while True:
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        yield state / 0x7FFFFFFF


def make_scores(n_pos: int, n_neg: int, seed: int, overlap: float = 0.35):
    """امتیاز مدل برای دو کلاس می‌سازد: بیمار (label=1) و سالم (label=0).

    overlap کنترل می‌کند دو توزیع چقدر روی هم می‌افتند؛
    overlap بزرگ‌تر ⇒ مدل ضعیف‌تر ⇒ AUC کمتر.
    """
    rng = lcg(seed)
    pos, neg = [], []
    for _ in range(n_pos):        # بیمار: امتیاز بالا
        pos.append(0.55 + overlap * (2.0 * next(rng) - 1.0) + 0.25 * next(rng))
    for _ in range(n_neg):        # سالم: امتیاز پایین
        neg.append(0.40 - overlap * (2.0 * next(rng) - 1.0) + 0.20 * next(rng))
    return [min(max(p, 0.0), 1.0) for p in pos], [min(max(n, 0.0), 1.0) for n in neg]


# ------------------------------------------------------- ماتریس درهم‌ریختگی
def confusion_matrix(y_true, y_pred, pos_label=1):
    """TP, FN, FP, TN را از پیش‌بینی‌ها حساب می‌کند (نظم «مثبت اول»)."""
    tp = fn = fp = tn = 0
    for t, p in zip(y_true, y_pred):
        if t == pos_label and p == pos_label:
            tp += 1
        elif t == pos_label:
            fn += 1
        elif p == pos_label:
            fp += 1
        else:
            tn += 1
    return tp, fn, fp, tn


# ------------------------------------------------------------- متریک‌های اصلی
def safe_div(a: float, b: float) -> float:
    return a / b if b else float("nan")


def accuracy(tp, fn, fp, tn):
    return safe_div(tp + tn, tp + fn + fp + tn)


def sensitivity(tp, fn, fp, tn):
    """حساسیت = Recall = TPR = TP / (TP + FN) — از میان بیماران چند نفر را گرفتیم؟"""
    return safe_div(tp, tp + fn)


def specificity(tp, fn, fp, tn):
    """ویژگی = TNR = TN / (TN + FP) — از میان سالم‌ها چند نفر را درست رد کردیم؟"""
    return safe_div(tn, tn + fp)


def precision_ppv(tp, fn, fp, tn):
    """PPV = TP / (TP + FP) — از مثبت‌پیش‌بینی‌شده‌ها چند نفر واقعاً بیمار بودند؟"""
    return safe_div(tp, tp + fp)


def npv(tp, fn, fp, tn):
    """NPV = TN / (TN + FN) — از منفی‌پیش‌بینی‌شده‌ها چند نفر واقعاً سالم بودند؟"""
    return safe_div(tn, tn + fn)


def f1_score(tp, fn, fp, tn):
    """F1 = 2·P·R / (P+R)؛ میانگین همساز (Harmonic mean) دقت و بازیابی."""
    p = precision_ppv(tp, fn, fp, tn)
    r = sensitivity(tp, fn, fp, tn)
    return safe_div(2.0 * p * r, p + r)


def print_confusion(tp, fn, fp, tn, title: str):
    print(f"\n=== {title} ===")
    print(f"{'':18}| پیش‌بینی: مثبت | پیش‌بینی: منفی")
    print("-" * 52)
    print(f"{'واقعیت: بیمار':<18}| TP = {tp:<10}| FN = {fn}")
    print(f"{'واقعیت: سالم':<18}| FP = {fp:<10}| TN = {tn}")
    m = dict(tp=tp, fn=fn, fp=fp, tn=tn)
    rows = [
        ("Accuracy (دقت کل)", accuracy(**m), "(TP+TN)/همه"),
        ("Sensitivity (حساسیت)", sensitivity(**m), "TP/(TP+FN)"),
        ("Specificity (ویژگی)", specificity(**m), "TN/(TN+FP)"),
        ("Precision/PPV", precision_ppv(**m), "TP/(TP+FP)"),
        ("NPV", npv(**m), "TN/(TN+FN)"),
        ("F1-score", f1_score(**m), "2PR/(P+R)"),
    ]
    print("\n{:26}{:>10}   {}".format("متریک", "مقدار", "فرمول"))
    print("-" * 66)
    for name, val, formula in rows:
        print("{:<26}{:>10.3f}   {}".format(name, val, formula))


# ------------------------------------------------------- ROC و جاروب آستانه
def roc_points(y_true, scores, steps: int = 21):
    """نقاط (FPR, TPR) برای آستانه‌های 0.00 تا 1.00."""
    points = []
    for i in range(steps + 1):
        thr = i / steps
        preds = [1 if s >= thr else 0 for s in scores]
        tp, fn, fp, tn = confusion_matrix(y_true, preds)
        points.append((safe_div(fp, fp + tn), safe_div(tp, tp + fn), thr))
    return points


def auc_trapezoid(points):
    """AUC به روش ذوزنقه (نقاط باید بر حسب FPR صعودی باشند)."""
    pts = sorted(points, key=lambda p: p[0])
    area = 0.0
    for (x0, y0, _), (x1, y1, _) in zip(pts, pts[1:]):
        area += (x1 - x0) * (y0 + y1) / 2.0
    return area


def plot_roc_ascii(points, width: int = 61, height: int = 17):
    """منحنی ROC را در یک شبکه‌ی ASCII رسم می‌کند (Y=TPR، X=FPR)."""
    grid = [[" "] * width for _ in range(height)]
    # محورها
    for x in range(width):
        grid[height - 1][x] = "-"
    for y in range(height):
        grid[y][0] = "|"
    grid[height - 1][0] = "+"
    for x, y, _thr in points:
        col = min(width - 1, int(round(x * (width - 1))))
        row = min(height - 1, height - 1 - int(round(y * (height - 1))))
        grid[row][col] = "*"
    print("\nROC (TPR در برابر FPR) — خط قطری = شانس تصادفی:")
    for row in grid:
        print("".join(row))
    print("(0,0) پایین-چپ؛ (1,1) بالا-راست؛ * = یک آستانه")


def threshold_sweep(y_true, scores, thr_list=(0.2, 0.3, 0.5, 0.7, 0.8)):
    print("\nجاروب آستانه (Threshold sweep):")
    print(f"{'آستانه':>8} {'TP':>4} {'FN':>4} {'FP':>4} {'TN':>4} "
          f"{'Sens':>7} {'Spec':>7} {'PPV':>7} {'F1':>7}")
    for thr in thr_list:
        preds = [1 if s >= thr else 0 for s in scores]
        tp, fn, fp, tn = confusion_matrix(y_true, preds)
        print(f"{thr:>8.1f} {tp:>4} {fn:>4} {fp:>4} {tn:>4} "
              f"{sensitivity(tp, fn, fp, tn):>7.3f} {specificity(tp, fn, fp, tn):>7.3f} "
              f"{precision_ppv(tp, fn, fp, tn):>7.3f} {f1_score(tp, fn, fp, tn):>7.3f}")


# ---------------------------------------------------------- سناریوهای نمایشی
def scenario_balanced():
    """داده‌ی متوازن: ۳۰ بیمار و ۳۰ سالم."""
    pos, neg = make_scores(n_pos=30, n_neg=30, seed=42, overlap=0.30)
    y_true = [1] * 30 + [0] * 30
    scores = pos + neg
    preds = [1 if s >= 0.5 else 0 for s in scores]
    tp, fn, fp, tn = confusion_matrix(y_true, preds)
    print_confusion(tp, fn, fp, tn, "سناریوی ۱: داده‌ی متوازن (آستانه ۰٫۵)")
    threshold_sweep(y_true, scores)
    pts = roc_points(y_true, scores)
    plot_roc_ascii(pts)
    print(f"\nAUC (ذوزنقه) = {auc_trapezoid(pts):.3f}")
    return pts


def scenario_imbalanced():
    """نامتوازن: شیوع ۵٪ — چرا Accuracy گمراه می‌کند؟"""
    pos, neg = make_scores(n_pos=5, n_neg=95, seed=7, overlap=0.30)
    y_true = [1] * 5 + [0] * 95
    scores = pos + neg
    # «مدل تنبل»: همیشه منفی می‌گوید!
    preds = [0] * len(y_true)
    tp, fn, fp, tn = confusion_matrix(y_true, preds)
    print_confusion(tp, fn, fp, tn, "سناریوی ۲: مدل تنبل (همیشه «سالم») با شیوع ۵٪")
    print("\nنکته: دقت ۹۵٪ اما حساسیت ۰٪ — تمام بیماران از دست رفتند. "
          "در داده‌ی نامتوازن، Accuracy به‌تنهایی گمراه‌کننده است.")
    # مدل واقعی با آستانه ۰٫۵ روی همان داده
    preds2 = [1 if s >= 0.5 else 0 for s in scores]
    tp2, fn2, fp2, tn2 = confusion_matrix(y_true, preds2)
    print_confusion(tp2, fn2, fp2, tn2, "سناریوی ۲-ب: مدل واقعی روی همان داده (آستانه ۰٫۵)")
    pts = roc_points(y_true, scores)
    plot_roc_ascii(pts)
    print(f"\nAUC (ذوزنقه) = {auc_trapezoid(pts):.3f}")


def main():
    print(__doc__)
    pts = scenario_balanced()
    scenario_imbalanced()
    print("\nپایان — همه‌ی اعداد از داده‌ی ساختگی قطعی (seed ثابت) تولید شده‌اند.")


if __name__ == "__main__":
    main()
