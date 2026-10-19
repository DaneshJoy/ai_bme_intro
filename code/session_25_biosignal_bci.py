# -*- coding: utf-8 -*-
"""هوش مصنوعی در سیگنال‌های زیستی و BCI — جلسه ۲۵

دو آزمایش کاملاً ساختگی و آموزشی (غیرتشخیصی) فقط با کتابخانه استاندارد پایتون:

بخش A — سیگنال ECG ساختگی:
  1) سنتز ECG از مجموع چند گاوسی (موج P، کمپلکس QRS، موج T) با الگوی ضربان معلوم
  2) فیلتر میانگین متحرک (Moving Average) و باند-پس ساده (تفاضل دو میانگین متحرک)
  3) آشکارسازی R-peak با آستانه و دوره بازدارنده (Refractory)
  4) ویژگی‌ها: ضربان قلب (HR)، فاصله RR، RMSSD، ضریب تغییرات (CV)،
     نرخ صعود (Rise Rate) و پهنای QRS
  5) طبقه‌بند آستانه‌ای «ریتم منظم/نامنظم» روی پنجره‌های زمانی
     + ماتریس درهم‌ریختگی + جاروب آستانه

بخش B — سیگنال EEG ساختگی (نمونه‌ی BCI):
  نسبت توان باند آلفا به بتا برای تفکیک دو وضعیت فرضی «چشم بسته / چشم باز»
  با توان طیفی نقطه‌ای (DFT در چند فرکانس منتخب).

هیچ داده واقعی بیمار در کار نیست؛ همه‌ی سیگنال‌ها ساختگی‌اند و برچسب
«حقیقت زمینی» آن‌ها از همان لحظه‌ی سنتز معلوم است. هیچ ارزش تشخیصی ندارد.

اجرا:
    python3 code/session_25_biosignal_bci.py

قطعی بودن: همه‌ی اعداد تصادفی از seed ثابت می‌آیند؛ دو بار اجرا = خروجی یکسان.
"""

import math
import random

# --------------------------------------------------- پارامترهای مشترک سیگنال
FS = 250.0        # نرخ نمونه‌برداری (Hz)
WINDOW_S = 4.0    # طول هر پنجره‌ی تحلیل (ثانیه)
RNG_SEED = 42     # seed نویز سیگنال
JITTER_SEED = 7   # seed لرزش فاصله ضربان‌ها
EEG_SEED = 11     # seed بخش EEG

# -------------------------------------------- پارامترهای سنتز ECG (واحد: mV فرضی)
# شکل یک ضربان با جمع گاوسی‌ها نسبت به لحظه‌ی قله R (ثانیه، دامنه، پهنا)
BEAT_WAVES = [
    # (offset_s, amplitude_mV, sigma_s)   نام
    (-0.200, 0.15, 0.025),  # P
    (-0.030, -0.10, 0.008),  # Q
    (0.000, 1.00, 0.012),  # R
    (0.035, -0.25, 0.010),  # S
    (0.300, 0.30, 0.045),  # T
]
BASELINE_AMP = 0.15   # موج آرام نویز تنفسی (wander) روی خط پایه
HUM_AMP = 0.03        # هام 50 هرتزِ برق شهر
NOISE_AMP = 0.04      # نویز سفید کوچک
REGULAR_RR = 0.80     # فاصله ضربان منظم (ثانیه) ≈ 75 bpm
JITTER = 0.03         # لرزش یکنواخت ± روی فاصله منظم (ثانیه)
IRR_SHORT = 0.65      # فاصله کوتاه الگوی نامنظم
IRR_LONG = 1.05       # فاصله بلند الگوی نامنظم
IRR_CV_THRESHOLD = 0.10  # آستانه‌ی طبقه‌بند: CV بزرگ‌تر ⇒ «نامنظم»


def moving_average(x, w):
    """میانگین متحرک ساده با پنجره‌ی w نمونه (لبه‌ها کوتاه‌تر می‌شوند)."""
    half = w // 2
    n = len(x)
    out = []
    for i in range(n):
        lo = max(0, i - half)
        hi = min(n, i + half + 1)
        out.append(sum(x[lo:hi]) / (hi - lo))
    return out


def rms(x):
    """جذر میانگین مربع‌ها."""
    return math.sqrt(sum(v * v for v in x) / len(x))


def mean(xs):
    return sum(xs) / len(xs)


def stdev_sample(xs):
    """انحراف معیار نمونه‌ای (مقسوم‌علیه n-1)؛ برای n<2 صفر."""
    n = len(xs)
    if n < 2:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((v - m) ** 2 for v in xs) / (n - 1))


# ------------------------------------------------------- بخش A: سنتز ECG
def schedule_beats():
    """برنامه‌ی ضربان‌ها بر حسب ثانیه + برچسب ریتم هر قطعه (حقیقت زمینی).

    قطعه‌ها: 0 تا 8 منظم | 8 تا 16 نامنظم (متناوب کوتاه/بلند) | 16 تا 24 منظم
    ضربان‌ها طوری چیده می‌شوند که هیچ‌کدام روی مرز قطعه نیفتد.
    """
    beats = []  # (t_s, rhythm) با rhythm در {"regular", "irregular"}
    t = 0.50
    while t <= 8.0 - 0.30:                     # قطعه ۱: منظم
        beats.append((t, "regular"))
        t += REGULAR_RR
    t = 8.30
    short = True
    while t <= 16.0 - 0.30:                    # قطعه ۲: نامنظم متناوب
        beats.append((t, "irregular"))
        t += IRR_SHORT if short else IRR_LONG
        short = not short
    t = 16.50
    while t <= 24.0 - 0.30:                    # قطعه ۳: منظم
        beats.append((t, "regular"))
        t += REGULAR_RR
    return beats


def beat_value(dt):
    """مقدار یک ضربان در فاصله dt ثانیه از قله R (جمع گاوسی‌ها)."""
    v = 0.0
    for off, amp, sigma in BEAT_WAVES:
        v += amp * math.exp(-0.5 * ((dt - off) / sigma) ** 2)
    return v


def synthesize_ecg():
    """سیگنال ECG ساختگی: ضربان‌ها + wander + هام 50 هرتز + نویز.

    فاصله‌ی ضربان‌های منظم با لرزش یکنواخت ±JITTER ثانیه کمی نامنظم می‌شود
    (هم در سنتز سیگنال و هم در حقیقت زمینی) تا RRها واقعی‌تر از مقدار ثابت باشند.
    """
    beats = schedule_beats()
    jr = random.Random(JITTER_SEED)
    true_times = []
    for bt, rhythm in beats:
        if rhythm == "regular":
            bt = bt + jr.uniform(-JITTER, JITTER)
        true_times.append((bt, rhythm))
    rng = random.Random(RNG_SEED)
    n = int(24.0 * FS)
    clean = [0.0] * n
    for i in range(n):
        t = i / FS
        clean[i] = sum(beat_value(t - bt) for bt, _ in true_times)
    raw = []
    for i in range(n):
        t = i / FS
        wander = BASELINE_AMP * math.sin(2 * math.pi * 0.2 * t)
        hum = HUM_AMP * math.sin(2 * math.pi * 50.0 * t)
        raw.append(clean[i] + wander + hum + rng.uniform(-NOISE_AMP, NOISE_AMP))
    return clean, raw, true_times


def filter_bandpass(raw):
    """باند-پس ساده: تفاضل دو میانگین متحرک.

    MA کوتاه (5 نمونه = 20ms) فرکانس‌های بالا را نگه می‌دارد؛
    MA بلند (75 نمونه = 300ms) خط پایه و هام را دنبال می‌کند؛
    تفاضلشان مؤلفه‌های میانی (انرژی QRS) را برجسته می‌کند.
    """
    ma_short = moving_average(raw, 5)
    ma_long = moving_average(raw, 75)
    return [s - l for s, l in zip(ma_short, ma_long)]


def detect_r_peaks(bp):
    """آشکارسازی قله R: آستانه نسبی + بیشینه محلی + دوره بازدارنده."""
    peak_height = max(bp)
    threshold = 0.40 * peak_height
    refractory = int(0.25 * FS)
    peaks = []
    last = -10 ** 9
    for i in range(1, len(bp) - 1):
        if bp[i] >= threshold and bp[i] >= bp[i - 1] and bp[i] >= bp[i + 1]:
            if i - last >= refractory:
                peaks.append(i)
                last = i
    return peaks, threshold


def count_matched(peaks, true_times, tol_samples=12):
    """تعداد ضربان‌های برنامه‌ریزی‌شده که آشکارسازی آن‌ها را یافته (±48ms)."""
    matched = 0
    for t, _ in true_times:
        target = t * FS
        if any(abs(p - target) <= tol_samples for p in peaks):
            matched += 1
    return matched


def window_features(bp, peaks, w0, w1):
    """ویژگی‌های یک پنجره از پیک‌هایی که کاملاً داخل همان پنجره‌اند."""
    in_win = [p for p in peaks if w0 <= p < w1]
    rrs = [(b - a) / FS for a, b in zip(in_win, in_win[1:])]
    n_beats = len(in_win)
    if not rrs:
        return None
    mean_rr = mean(rrs)
    hr = 60.0 / mean_rr if mean_rr > 0 else 0.0
    cv = stdev_sample(rrs) / mean_rr if mean_rr > 0 else 0.0
    diffs = [b - a for a, b in zip(rrs, rrs[1:])]
    rmssd = math.sqrt(mean([d * d for d in diffs])) if diffs else 0.0
    # نرخ صعود: بیشینه شیب مثبت در 60ms پیش از هر قله (بر حسب mV/s)
    slopes = []
    for p in in_win:
        lo = max(1, p - 15)
        best = max(bp[j] - bp[j - 1] for j in range(lo, p + 1))
        slopes.append(best * FS)
    # پهنای QRS: عرض در نیمه‌ی ارتفاع قله (FWHM) بر حسب ms
    widths = []
    for p in in_win:
        half = bp[p] / 2.0
        l = p
        while l > 0 and bp[l] > half:
            l -= 1
        r = p
        while r < len(bp) - 1 and bp[r] > half:
            r += 1
        widths.append((r - l) / FS * 1000.0)
    return {
        "n_beats": n_beats, "mean_rr": mean_rr, "hr": hr, "cv": cv,
        "rmssd_ms": rmssd * 1000.0, "rise_mv_s": mean(slopes),
        "qrs_ms": mean(widths),
    }


def confusion_metrics(tp, fp, fn, tn):
    """متریک‌های جلسه ۲۱؛ کلاس مثبت = «نامنظم»."""
    total = tp + fp + fn + tn
    acc = (tp + tn) / total if total else 0.0
    sens = tp / (tp + fn) if (tp + fn) else 0.0
    spec = tn / (tn + fp) if (tn + fp) else 0.0
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    f1 = 2 * prec * sens / (prec + sens) if (prec + sens) else 0.0
    return acc, sens, spec, prec, f1


def part_a():
    print("=" * 72)
    print("PART A | synthetic ECG (educational, non-diagnostic)")
    print("=" * 72)
    clean, raw, true_times = synthesize_ecg()
    bp = filter_bandpass(raw)

    # اثر فیلتر: سیگنال پاک هم با همان فیلتر پردازش می‌شود تا مقایسه منصفانه باشد
    clean_bp = filter_bandpass(clean)
    err_raw = [r - c for r, c in zip(raw, clean)]
    err_bp = [b - c for b, c in zip(bp, clean_bp)]
    snr_raw = 10 * math.log10(rms(clean) ** 2 / rms(err_raw) ** 2)
    snr_bp = 10 * math.log10(rms(clean_bp) ** 2 / rms(err_bp) ** 2)
    print(f"sampling rate = {FS:.0f} Hz | duration = 24 s | N = {len(raw)} samples")
    print(f"injected beats = {len(true_times)} "
          f"(regular/irregular/regular segments: 0-8 s / 8-16 s / 16-24 s)")
    print(f"SNR raw    = {snr_raw:6.2f} dB")
    print(f"SNR band-passed = {snr_bp:6.2f} dB  (improvement {snr_bp - snr_raw:+.2f} dB)")

    peaks, thr = detect_r_peaks(bp)
    matched = count_matched(peaks, true_times)
    print(f"detected R-peaks = {len(peaks)} | threshold = {thr:.3f} mV "
          f"| matched to injected beats (±48 ms) = {matched}/{len(true_times)}")

    w = int(WINDOW_S * FS)
    n_windows = len(bp) // w
    rows = []
    for k in range(n_windows):
        w0, w1 = k * w, (k + 1) * w
        feats = window_features(bp, peaks, w0, w1)
        if feats is None:
            continue
        # حقیقت زمینی: «irregular» اگر ضربان‌های داخل پنجره نامنظم چیده شده باشند
        inside = [r for t, r in true_times if w0 / FS <= t < w1 / FS]
        label = "irregular" if inside and all(r == "irregular" for r in inside) else "regular"
        pred = "irregular" if feats["cv"] > IRR_CV_THRESHOLD else "regular"
        rows.append((k, feats, label, pred))

    print()
    print(f"per-window features (window = {WINDOW_S:.0f} s, "
          f"classifier threshold: CV > {IRR_CV_THRESHOLD:.2f} => 'irregular')")
    header = ("{:>3} {:>10} {:>8} {:>7} {:>7} {:>8} {:>9} {:>8} {:>10} {:>10}".format(
        "win", "time (s)", "beats", "RR (s)", "HR", "CV", "RMSSD(ms)",
        "QRS(ms)", "rise(mV/s)", "label/pred"))
    print(header)
    print("-" * len(header))
    for k, f, label, pred in rows:
        t0, t1 = k * WINDOW_S, (k + 1) * WINDOW_S
        print("{:>3} {:>4.0f}-{:>4.0f}  {:>8d} {:>7.3f} {:>7.1f} {:>7.3f} "
              "{:>8.1f} {:>8.1f} {:>10.1f} {:>10}".format(
                  k, t0, t1, f["n_beats"], f["mean_rr"], f["hr"], f["cv"],
                  f["rmssd_ms"], f["qrs_ms"], f["rise_mv_s"], f"{label[:4]}/{pred[:4]}"))

    # ماتریس درهم‌ریختگی (مثبت = irregular)
    tp = sum(1 for _, _, lb, pr in rows if lb == "irregular" and pr == "irregular")
    fp = sum(1 for _, _, lb, pr in rows if lb == "regular" and pr == "irregular")
    fn = sum(1 for _, _, lb, pr in rows if lb == "irregular" and pr == "regular")
    tn = sum(1 for _, _, lb, pr in rows if lb == "regular" and pr == "regular")
    acc, sens, spec, prec, f1 = confusion_metrics(tp, fp, fn, tn)
    print()
    print(f"confusion matrix (positive = irregular): "
          f"TP={tp} FP={fp} FN={fn} TN={tn}")
    print(f"accuracy={acc:.3f} sensitivity={sens:.3f} specificity={spec:.3f} "
          f"precision={prec:.3f} F1={f1:.3f}")

    print()
    print("threshold sweep on CV (window classifier accuracy):")
    for thr in (0.02, 0.05, 0.10, 0.15, 0.20, 0.30):
        tp2 = sum(1 for _, f, lb, _ in rows if lb == "irregular" and f["cv"] > thr)
        fp2 = sum(1 for _, f, lb, _ in rows if lb == "regular" and f["cv"] > thr)
        fn2 = sum(1 for _, f, lb, _ in rows if lb == "irregular" and f["cv"] <= thr)
        tn2 = sum(1 for _, f, lb, _ in rows if lb == "regular" and f["cv"] <= thr)
        acc2, _, _, _, _ = confusion_metrics(tp2, fp2, fn2, tn2)
        print(f"  CV > {thr:.2f} -> accuracy = {acc2:.3f} "
              f"(TP={tp2} FP={fp2} FN={fn2} TN={tn2})")
    print()
    print("takeaway: RR variability (CV) alone separates the two synthetic")
    print("rhythms here; on real recordings it is only a research starting point.")
    return rows


# ------------------------------------------------- بخش B: EEG و نسبت آلفا/بتا
ALPHA_HZ, BETA_HZ = 10.0, 22.0
ALPHA_BAND = (8.0, 12.0)
BETA_BAND = (18.0, 26.0)
EEG_NOISE_UV = 15.0
N_EPOCHS = 10
EPOCH_S = 2.0


def synth_eeg_epoch(alpha_amp, beta_amp, rng):
    """یک epoch دوثانیه‌ای: آلفا + بتا + نویز گاوسی (واحد: µV فرضی)."""
    n = int(EPOCH_S * FS)
    out = []
    phase = rng.uniform(0, 2 * math.pi)
    for i in range(n):
        t = i / FS
        v = alpha_amp * math.sin(2 * math.pi * ALPHA_HZ * t + phase)
        v += beta_amp * math.sin(2 * math.pi * BETA_HZ * t + phase / 2)
        v += rng.gauss(0.0, EEG_NOISE_UV)
        out.append(v)
    return out


def band_power(x, f_lo, f_hi, step=1.0):
    """توان طیفی در یک باند: مجموع |DFT(f)|^2 در چند فرکانس منتخب."""
    n = len(x)
    total = 0.0
    f = f_lo
    while f <= f_hi + 1e-9:
        re = im = 0.0
        w = 2 * math.pi * f / FS
        for i, v in enumerate(x):
            re += v * math.cos(w * i)
            im -= v * math.sin(w * i)
        total += re * re + im * im
        f += step
    return total


def part_b():
    print("=" * 72)
    print("PART B | synthetic EEG epochs — toy BCI feature (educational)")
    print("=" * 72)
    rng = random.Random(EEG_SEED)
    rows = []
    for cond, alpha_amp, beta_amp in (("closed", 20.0, 0.0),
                                      ("open", 5.0, 12.0)):
        for e in range(N_EPOCHS):
            a = alpha_amp * rng.uniform(0.8, 1.2)
            b = beta_amp * rng.uniform(0.8, 1.2)
            x = synth_eeg_epoch(a, b, rng)
            pa = band_power(x, *ALPHA_BAND)
            pb = band_power(x, *BETA_BAND)
            ratio = pa / (pa + pb)
            rows.append((cond, e, ratio))

    print(f"epochs: {N_EPOCHS} per condition, {EPOCH_S:.0f} s each, "
        f"noise sigma = {EEG_NOISE_UV:.0f} uV (synthetic)")
    print("feature r = P(alpha)/(P(alpha)+P(beta)) per epoch:")
    for cond in ("closed", "open"):
        vals = [r for c, _, r in rows if c == cond]
        print(f"  {cond:>6}: " + "  ".join(f"{v:.2f}" for v in vals)
              + f"   (mean {mean(vals):.2f})")

    threshold = 0.5
    print(f"classifier: r > {threshold:.1f} => 'closed' else 'open'")
    tp = sum(1 for c, _, r in rows if c == "closed" and r > threshold)
    fp = sum(1 for c, _, r in rows if c == "open" and r > threshold)
    fn = sum(1 for c, _, r in rows if c == "closed" and r <= threshold)
    tn = sum(1 for c, _, r in rows if c == "open" and r <= threshold)
    acc, sens, spec, prec, f1 = confusion_metrics(tp, fp, fn, tn)
    print(f"confusion matrix (positive = 'closed'): TP={tp} FP={fp} FN={fn} TN={tn}")
    print(f"accuracy={acc:.3f} sensitivity={sens:.3f} specificity={spec:.3f} "
          f"precision={prec:.3f} F1={f1:.3f}")
    print("takeaway: one band-power ratio separates two synthetic states;")
    print("real BCI needs many channels, artefact rejection and calibration.")
    return rows


def main():
    print("session 25 — biosignals & BCI demo (all data synthetic, "
          "educational, non-diagnostic)")
    print()
    part_a()
    print()
    part_b()
    print()
    print("همه‌ی اعداد این خروجی از seedهای ثابت می‌آیند؛ اجرای دوباره همین")
    print("خروجی را تولید می‌کند. این اسکریپت هیچ ارزش تشخیصی ندارد.")


if __name__ == "__main__":
    main()
