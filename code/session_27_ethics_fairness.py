#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""جلسه ۲۷ — نمایش سوگیری (Bias) و محاسبه‌ی یک معیار انصاف با پایتون استاندارد.

سناریوی آموزشی و غیرتشخیصی: «ابزار غربالگری فرضی» روی داده‌ی کاملاً ساختگی با
دو زیرگروه مصنوعی:
  - گروه A (اکثریت): اندازه‌گیری تمیز، شیوع بالاتر
  - گروه B (اقلیت): همان کمیت با نویز بیشتر و شیوع پایین‌تر (شبیه‌سازی
    کم‌نمایی و تفاوت کیفیت داده بین زیرگروه‌ها)

یک طبقه‌بند آستانه‌ای (Threshold Classifier) روی «امتیاز خطر» آموزش می‌بیند و
سپس عملکرد کل و هر زیرگروه جداگانه گزارش می‌شود:
  1) Accuracy کل روی آزمون
  2) دقت، حساسیت (TPR) و نرخ انتخاب (Selection Rate) هر زیرگروه
  3) شکاف فرصت برابر (Equal-Opportunity Gap) = |TPR_A - TPR_B|
  4) شکاف برابری جمعیتی (Demographic-Parity Gap) = |P(pred=1|A) - P(pred=1|B)|

قطعی: seed ثابت؛ تفکیک آموزش/آزمون با شناسه‌ی پایدار هر نمونه (نه ترتیب فهرست)
انجام می‌شود، پس خروجی نسبت به جابه‌جایی ترتیب داده‌ها تغییر نمی‌کند
(در پایان، با یک اجرای وارون‌شده کنترل می‌شود).

داده‌ها واقعی نیستند؛ هیچ کاربرد تشخیصی یا بالینی ندارند.

اجرا:
    python3 code/session_27_ethics_fairness.py
"""
from __future__ import annotations

import math


# ------------------------------------------------- تولید داده‌ی ساختگی قطعی
def lcg(seed: int):
    """تولیدکننده اعداد شبه‌تصادفی قطعی (Linear Congruential Generator)."""
    state = seed & 0x7FFFFFFF
    while True:
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        yield state / 0x7FFFFFFF


def gauss(rng, mu: float, sigma: float) -> float:
    """نمونه‌ی گاوسی با تبدیل Box-Muller (قطعی، بر پایه‌ی دو عدد یکنواخت)."""
    u1 = max(next(rng), 1e-12)   # جلوگیری از ln(0)
    u2 = next(rng)
    z = (-2.0 * math.log(u1)) ** 0.5 * math.cos(2.0 * math.pi * u2)
    return mu + sigma * z


def clamp01(x: float) -> float:
    return min(max(x, 0.0), 1.0)


def make_subgroups():
    """دو زیرگروه ساختگی می‌سازد؛ شناسه (gid) پایدارِ هر نمونه است.

    گروه A: ۲۴۰ نمونه، ۴۰٪ بیمار (label=1)، نویز کم (sigma=0.12)
    گروه B: ۱۲۰ نمونه، ۲۵٪ بیمار (label=1)، نویز زیاد (sigma=0.22)
    """
    samples = []  # (gid, group, score, label)
    rng_a = lcg(2027)
    for gid in range(240):
        if gid < 96:                     # ۴۰٪ بیمار
            score = gauss(rng_a, 0.62, 0.12)
            label = 1
        else:
            score = gauss(rng_a, 0.38, 0.12)
            label = 0
        samples.append((gid, "A", clamp01(score), label))
    rng_b = lcg(777)
    for gid in range(1000, 1120):        # شناسه‌های جدا برای گروه B
        if gid < 1030:                   # ۲۵٪ بیمار
            score = gauss(rng_b, 0.62, 0.22)
            label = 1
        else:
            score = gauss(rng_b, 0.38, 0.22)
            label = 0
        samples.append((gid, "B", clamp01(score), label))
    return samples


# ------------------------------------------------------- تفکیک آموزش/آزمون
def is_test(gid: int) -> bool:
    """تفکیک پایدار بر اساس شناسه‌ی نمونه؛ مستقل از ترتیب فهرست (~۳۰٪ آزمون)."""
    h = (gid * 2654435761 + 40503) % 4294967296
    return (h % 10) < 3


# --------------------------------------- طبقه‌بند آستانه‌ای (یک پارامتر)
def predict(score: float, thr: float) -> int:
    return 1 if score >= thr else 0


def counts(samples, thr):
    """(tp, fn, fp, tn) روی همه‌ی نمونه‌های داده‌شده."""
    tp = fn = fp = tn = 0
    for _gid, _g, score, label in samples:
        p = predict(score, thr)
        if label == 1 and p == 1:
            tp += 1
        elif label == 1:
            fn += 1
        elif p == 1:
            fp += 1
        else:
            tn += 1
    return tp, fn, fp, tn


def balanced_accuracy(samples, thr) -> float:
    tp, fn, fp, tn = counts(samples, thr)
    tpr = (tp + fn) and tp / (tp + fn)
    tnr = (tn + fp) and tn / (tn + fp)
    return (tpr + tnr) / 2.0


def train_threshold(train_samples):
    """بهترین آستانه بر پایه‌ی بیشینه‌کردن دقت متوازن روی داده‌ی آموزش.

    نامزدها از میانگین نقاط مرتب‌شده ساخته می‌شوند؛ چون مرتب‌سازی می‌کنیم،
    نتیجه به ترتیب ورود نمونه‌ها وابسته نیست. تساوی: اولین (کمینه) آستانه.
    """
    pts = sorted(s[2] for s in train_samples)
    cands = [0.0] + [(a + b) / 2.0 for a, b in zip(pts, pts[1:])] + [1.0]
    best_thr, best_ba = 0.5, -1.0
    for c in cands:
        ba = balanced_accuracy(train_samples, c)
        if ba > best_ba + 1e-12:
            best_ba, best_thr = ba, c
    return best_thr, best_ba


# --------------------------------------------------------------- متریک‌ها
def group_metrics(test_samples, thr):
    """نام زیرگروه → (n, accuracy, TPR, نرخ انتخاب)."""
    out = {}
    for grp in ("A", "B"):
        g = [s for s in test_samples if s[1] == grp]
        tp, fn, fp, tn = counts(g, thr)
        n = len(g)
        out[grp] = {
            "n": n,
            "pos": tp + fn,
            "acc": (n and (tp + tn) / n) or 0.0,
            "tpr": ((tp + fn) and tp / (tp + fn)) or 0.0,
            "sel": (n and (tp + fp) / n) or 0.0,
        }
    return out


def run_pipeline(samples):
    """چرخه‌ی کامل: تفکیک → آموزش آستانه → ارزیابی کل و زیرگروه‌ها."""
    train = [s for s in samples if not is_test(s[0])]
    test = [s for s in samples if is_test(s[0])]
    thr, best_ba = train_threshold(train)
    gm = group_metrics(test, thr)
    tp, fn, fp, tn = counts(test, thr)
    acc = (tp + tn) / len(test)
    return {
        "threshold": thr,
        "train_ba": best_ba,
        "n_train": len(train),
        "n_test": len(test),
        "accuracy": acc,
        "gm": gm,
        "acc_gap": abs(gm["A"]["acc"] - gm["B"]["acc"]),
        "eo_gap": abs(gm["A"]["tpr"] - gm["B"]["tpr"]),
        "dp_gap": abs(gm["A"]["sel"] - gm["B"]["sel"]),
    }


def print_report(res):
    gm = res["gm"]
    print("=== داده‌ی آموزش (ساختگی) ===")
    print(f"نمونه‌های آموزش: {res['n_train']}   نمونه‌های آزمون: {res['n_test']}")
    print(f"آستانه‌ی آموخته‌شده: {res['threshold']:.3f}"
          f"   (دقت متوازن آموزش: {res['train_ba']:.3f})")
    print("\n=== ارزیابی روی آزمون ===")
    print(f"Accuracy کل: {res['accuracy']:.3f}")
    header = f"{'گروه':<6}{'n':>5}{'بیمار':>7}{'Acc':>8}{'TPR':>8}{'انتخاب':>9}"
    print(header)
    print("-" * len(header))
    for grp in ("A", "B"):
        m = gm[grp]
        print(f"{grp:<6}{m['n']:>5}{m['pos']:>7}{m['acc']:>8.3f}{m['tpr']:>8.3f}{m['sel']:>9.3f}")
    print("\n=== معیارهای انصاف (شکاف زیرگروه‌ها) ===")
    print(f"شکاف دقت (Accuracy Gap):        {res['acc_gap']:.3f}")
    print(f"شکاف فرصت برابر (EO Gap):       {res['eo_gap']:.3f}")
    print(f"شکاف برابری جمعیتی (DP Gap):    {res['dp_gap']:.3f}")
    print("\nتفسیر آموزشی: اختلاف TPR یعنی مدل برای زیرگروهِ اقلیت «بیمار را کمتر"
          "\nکشف می‌کند»؛ علت نمونه‌ی ما نویز بیشتر و کم‌نمایی گروه B است — نه جادو،"
          "\nنه بدجنسی: فقط داده‌ی نامتوازن.")


# ------------------------------------------------------------- خودآزمون کد
def self_checks(samples, res):
    """کنترل‌های assert — شکست هرکدام یعنی اسکریپت خراب است، نه سوگیری جدید."""
    gm = res["gm"]
    # ۱) آستانه و متریک‌ها در بازه‌ی معتبر
    assert 0.0 <= res["threshold"] <= 1.0, "آستانه خارج از [0,1]"
    vals = [res["accuracy"], res["acc_gap"], res["eo_gap"], res["dp_gap"],
            res["train_ba"], gm["A"]["acc"], gm["B"]["acc"],
            gm["A"]["tpr"], gm["B"]["tpr"], gm["A"]["sel"], gm["B"]["sel"]]
    for v in vals:
        assert 0.0 <= v <= 1.0, f"متریک خارج از [0,1]: {v}"
    # ۲) شکاف‌ها دقیقاً از تعریف بازمحاسبه می‌شوند
    assert abs(res["eo_gap"] - abs(gm["A"]["tpr"] - gm["B"]["tpr"])) < 1e-12
    assert abs(res["dp_gap"] - abs(gm["A"]["sel"] - gm["B"]["sel"])) < 1e-12
    assert abs(res["acc_gap"] - abs(gm["A"]["acc"] - gm["B"]["acc"])) < 1e-12
    # ۳) تفکیک آموزش/آزمون سهم منطقی دارد
    assert res["n_train"] + res["n_test"] == len(samples)
    assert 0.25 <= res["n_test"] / len(samples) <= 0.35
    # ۴) سوگیری واقعاً در این داده‌ی ساختگی دیده می‌شود
    assert res["eo_gap"] > 0.05 or res["acc_gap"] > 0.05, \
        "شکاف زیرگروه‌ها محو شده — پارامترهای داده را بررسی کنید"
    # ۵) بی‌تغییر نسبت به ترتیب داده‌ها (اجراهای وارون/بریده‌شده)
    for perm in (list(reversed(samples)), samples[100:] + samples[:100]):
        r2 = run_pipeline(perm)
        assert r2["threshold"] == res["threshold"]
        assert r2["accuracy"] == res["accuracy"]
        assert r2["eo_gap"] == res["eo_gap"]
        assert r2["dp_gap"] == res["dp_gap"]
        assert r2["gm"]["A"]["n"] == gm["A"]["n"] and r2["gm"]["B"]["n"] == gm["B"]["n"]


def main():
    samples = make_subgroups()
    res = run_pipeline(samples)
    print(__doc__)
    print_report(res)
    self_checks(samples, res)
    print("\nپایان — همه‌ی اعداد از داده‌ی ساختگی قطعی (seed ثابت) تولید شده‌اند.")
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
