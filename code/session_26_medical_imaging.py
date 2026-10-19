# -*- coding: utf-8 -*-
"""هوش مصنوعی در تصاویر پزشکی — جلسه ۲۶

یک خط لوله‌ی کامل پردازش تصویر روی «تصویر ساختگیِ میکروسکوپی‌مانند»، فقط با
کتابخانه استاندارد پایتون (بدون numpy / scikit-learn / matplotlib):

بخش A — خط لوله روی یک صحنه‌ی ساختگی (۳ جسم در پس‌زمینه):
  1) کانولوشن دوبعدی دست‌ساز با کرنل 3x3 (میانگین‌گیر و سوبل)
  2) آستانه‌گذاری اوتسو (Otsu) روی تصویر هموارشده
  3) برچسب‌گذاری اجزای همبند با BFS (همان ایده‌ی جست‌وجوی جلسه ۵)
  4) ویژگی هر جسم: مساحت، مرکز، میانگین شدت، فشردگی
  5) نمایش ASCII تصویر، لبه‌ها و ماسک

بخش B — طبقه‌بند «نزدیک‌ترین مرکز» (Nearest Centroid):
  آموزش روی مجموعه‌ی ساختگی دو کلاس «دایره‌ی تیزمرز» و «لکه‌ی پخش‌شده»
  با دو ویژگی (چگالی لبه، کنتراست اوج) و ارزیابی روی مجموعه‌ی آزمون.

هیچ داده‌ی واقعی بیمار یا تصویر واقعی پزشکی در کار نیست؛ همه‌چیز ساختگی،
آموزشی و غیرتشخیصی است. در Colab همان خط لوله با `load_digits` هم قابل
اجراست، اما این نسخه‌ی ارسالی عمداً std-only است تا همه‌جا اجرا شود.

اجرا:
    python3 code/session_26_medical_imaging.py

قطعی بودن: همه‌ی اعداد تصادفی از seed ثابت می‌آیند؛ دو بار اجرا = خروجی یکسان.
"""

import math
import random
from collections import deque

SIZE = 48          # ابعاد تصویر صحنه‌ی اصلی (نمونه مربع)
MAXV = 255
CHARS = " .:-=+*#%@"  # نوار روشنایی برای نمایش ASCII (تیره → روشن)

BOX3 = [[1 / 9] * 3 for _ in range(3)]          # فیلتر میانگین‌گیر 3x3
SOBEL_X = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]  # مشتق افقی
SOBEL_Y = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]  # مشتق عمودی

SCENE_SEED = 1
TRAIN_SEED = 100
TEST_SEED = 200
N_TRAIN = 24      # تعداد نمونه‌ی آموزش هر کلاس
N_TEST = 8        # تعداد نمونه‌ی آزمون هر کلاس
EDGE_T = 120.0    # آستانه‌ی «پیکسل لبه» روی گرادیان هموارشده؛ نقطه‌ی کار ثابت:
                  # بالاتر از بیشینه‌ی پاسخ لکه‌ی پخش‌شده (~115) و پایین‌تر از
                  # پاسخ حلقه‌ی مرز دایره (~300) در همین خانواده‌ی داده‌ی ساختگی


# ------------------------------------------------- ابزارهای پایه‌ی تصویر
def clamp(v):
    """محدود کردن مقدار به بازه‌ی 0 تا 255."""
    return 0 if v < 0 else (255 if v > MAXV else v)


def convolve2d(img, kernel):
    """کانولوشن دوبعدی دست‌ساز با کرنل 3x3 و مرز تکراری (replicate padding).

    چون جمع ضرایب هر دو کرنل اینجا 1 یا 0 است و مرز کپی می‌شود، میانگین
    شدت تصویر پس از فیلتر میانگین‌گیر تقریباً حفظ می‌شود و لبه‌ی کاذبِ
    تیره‌ی صفرگذاری (zero padding) ساخته نمی‌شود.
    """
    n = len(img)
    m = len(img[0])
    out = [[0] * m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            acc = 0.0
            for u in (-1, 0, 1):
                for v in (-1, 0, 1):
                    ii = min(n - 1, max(0, i + u))
                    jj = min(m - 1, max(0, j + v))
                    acc += kernel[u + 1][v + 1] * img[ii][jj]
            out[i][j] = acc
    return out


def sobel_raw(img):
    """بزرگی گرادیان سوبل بدون نرمال‌سازی (مقیاس شدت خام 0..255).

    نکته: نرمال‌سازی «به ازای هر تصویر» چگالی لبه را بی‌معنا می‌کند، چون
    مقیاس آستانه از تصویری به تصویر دیگر عوض می‌شود؛ برای ویژگی‌ها از
    مقیاس خام و آستانه‌ی ثابت استفاده می‌کنیم.
    """
    gx = convolve2d(img, SOBEL_X)
    gy = convolve2d(img, SOBEL_Y)
    return [[math.hypot(gx[i][j], gy[i][j]) for j in range(len(img[0]))]
            for i in range(len(img))]


def sobel_magnitude(img):
    """بزرگی گرادیان سوبل نرمال‌شده به 0..255 — فقط برای نمایش ASCII."""
    mags = sobel_raw(img)
    peak = max(max(row) for row in mags)
    if peak == 0:
        return mags
    return [[v * MAXV / peak for v in row] for row in mags]


def normalize_map(mags):
    """نرمال‌سازی نقشه‌ی دلخواه به بازه‌ی 0..255 (برای نمایش ASCII)."""
    peak = max(max(row) for row in mags)
    if peak == 0:
        return mags
    return [[v * MAXV / peak for v in row] for row in mags]


def otsu_threshold(img):
    """آستانه‌ی اوتسو: بیشینه‌ی واریانس بین‌کلاسی روی هیستوگرام 256بینه."""
    hist = [0] * 256
    for row in img:
        for v in row:
            hist[min(255, max(0, int(v)))] += 1
    total = len(img) * len(img[0])
    sum_all = sum(i * hist[i] for i in range(256))
    w0 = 0
    sum0 = 0
    best_t, best_var = 0, -1.0
    for t in range(256):
        w0 += hist[t]
        if w0 == 0:
            continue
        w1 = total - w0
        if w1 == 0:
            break
        sum0 += t * hist[t]
        mu0 = sum0 / w0
        mu1 = (sum_all - sum0) / w1
        var_between = (w0 / total) * (w1 / total) * (mu0 - mu1) ** 2
        if var_between > best_var:
            best_var, best_t = var_between, t
    return best_t


def connected_components(mask):
    """برچسب‌گذاری اجزای همبند 4-همسایه با BFS (صف دوتایی جلسه ۵).

    خروجی: فهرست مؤلفه‌ها به‌صورت (label_id, set_of_pixels)
    """
    n = len(mask)
    m = len(mask[0])
    seen = [[False] * m for _ in range(n)]
    comps = []
    for i in range(n):
        for j in range(m):
            if mask[i][j] and not seen[i][j]:
                q = deque([(i, j)])
                seen[i][j] = True
                pixels = []
                while q:
                    y, x = q.popleft()
                    pixels.append((y, x))
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < n and 0 <= nx < m \
                                and mask[ny][nx] and not seen[ny][nx]:
                            seen[ny][nx] = True
                            q.append((ny, nx))
                comps.append(pixels)
    return comps


def component_features(comp, img, blurred):
    """ویژگی‌های یک جسم: مساحت، مرکز، میانگین شدت، فشردگی.

    «فشردگی» = 4πA/P² با P = شمار پیکسل‌های مرزی؛ در تصویر گسسته حتی
    دیسک کامل هم عدد ~1.5 می‌گیرد (نه ~1 پیوسته) — پس فقط مقایسه‌ی نسبی
    اجسام معنا دارد، نه تفسیر مطلق عدد.
    """
    area = len(comp)
    cy = sum(p[0] for p in comp) / area
    cx = sum(p[1] for p in comp) / area
    mean_int = mean([blurred[p[0]][p[1]] for p in comp])
    comp_set = set(comp)
    perimeter = 0
    for (y, x) in comp:
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (y + dy, x + dx) not in comp_set:
                perimeter += 1
                break
    compact = 4 * math.pi * area / (perimeter ** 2) if perimeter else 0.0
    return {"area": area, "cy": cy, "cx": cx, "mean_int": mean_int,
            "perimeter": perimeter, "compact": compact}


def mean(xs):
    return sum(xs) / len(xs)


def median(xs):
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def ascii_art(img, step=2):
    """نمایش ASCII تصویر با نمونه‌برداری پرشده (max-pooling)."""
    lines = []
    for i in range(0, len(img), step):
        row = ""
        for j in range(0, len(img[0]), step):
            block = [img[ii][jj] for ii in range(i, min(i + step, len(img)))
                     for jj in range(j, min(j + step, len(img[0])))]
            v = max(block)
            row += CHARS[min(len(CHARS) - 1, int(v / MAXV * (len(CHARS) - 1)))]
        lines.append(row)
    return "\n".join(lines)


# ------------------------------------------------- بخش A: صحنه‌ی ساختگی
def make_scene():
    """صحنه 48x48: پس‌زمینه‌ی نویزدار + دو دایره‌ی روشن + یک لکه‌ی پخش‌شده."""
    rng = random.Random(SCENE_SEED)
    img = [[30 + rng.randint(-12, 12) for _ in range(SIZE)] for _ in range(SIZE)]
    # دایره ۱: مرکز (14,16) شعاع 7، شدت 210
    for i in range(SIZE):
        for j in range(SIZE):
            r = math.hypot(i - 14, j - 16)
            if r <= 7:
                img[i][j] = 210 - 6 * r
    # دایره ۲: مرکز (34,36) شعاع 4، شدت 185
    for i in range(SIZE):
        for j in range(SIZE):
            r = math.hypot(i - 34, j - 36)
            if r <= 4:
                img[i][j] = 185 - 8 * r
    # لکه‌ی پخش‌شده (گاوسی): مرکز (32,13)، سیگما 6، دامنه 90
    for i in range(SIZE):
        for j in range(SIZE):
            d2 = (i - 32) ** 2 + (j - 13) ** 2
            img[i][j] += 90 * math.exp(-d2 / (2 * 6 ** 2))
    for i in range(SIZE):
        for j in range(SIZE):
            img[i][j] = clamp(int(img[i][j]))
    return img


def part_a():
    print("=" * 72)
    print("PART A | synthetic scene pipeline (educational, non-diagnostic)")
    print("=" * 72)
    img = make_scene()
    blurred = convolve2d(img, BOX3)
    # قاعده‌ی طلایی: اول هموار کن، بعد مشتق بگیر — وگرنه نویز به‌جای لبه می‌بارد
    edges_raw = sobel_raw(blurred)
    edges = normalize_map(edges_raw)

    mean_before = mean([v for row in img for v in row])
    mean_after = mean([v for row in blurred for v in row])
    print(f"scene: {SIZE}x{SIZE} grayscale, 3 objects (2 sharp circles + "
          f"1 diffuse blob)")
    print(f"box blur 3x3: mean intensity {mean_before:.2f} -> {mean_after:.2f} "
          f"(replicate border: mean preserved, kernel sums to 1)")

    edge_px = sum(1 for row in edges_raw for v in row if v > EDGE_T)
    total_px = SIZE * SIZE
    print(f"sobel edges: max grad (norm.) = {max(max(r) for r in edges):.0f}, "
          f"pixels with grad > {EDGE_T:.0f}: {edge_px} ({edge_px / total_px:.3f})")

    threshold = otsu_threshold(blurred)
    mask = [[1 if blurred[i][j] > threshold else 0 for j in range(SIZE)]
            for i in range(SIZE)]
    mask_px = sum(sum(r) for r in mask)
    print(f"otsu threshold on blurred image = {threshold} "
          f"({mask_px} px above = {mask_px / total_px:.3f} of image)")

    comps = [c for c in connected_components(mask) if len(c) >= 5]
    print(f"connected components (area >= 5 px): {len(comps)}")
    header = "{:>3} {:>6} {:>8} {:>8} {:>10} {:>8} {:>10}".format(
        "id", "area", "cy", "cx", "mean_int", "perim", "compact")
    print("  " + header)
    print("  " + "-" * len(header))
    comps_sorted = sorted(comps, key=len, reverse=True)
    for idx, comp in enumerate(comps_sorted, 1):
        f = component_features(comp, img, blurred)
        print("  {:>3} {:>6d} {:>8.1f} {:>8.1f} {:>10.1f} {:>8d} {:>10.3f}".format(
            idx, f["area"], f["cy"], f["cx"], f["mean_int"],
            f["perimeter"], f["compact"]))
    biggest = comps_sorted[0]
    bf = component_features(biggest, img, blurred)
    print(f"largest object: area={bf['area']} px at (y={bf['cy']:.1f}, "
          f"x={bf['cx']:.1f}), compactness={bf['compact']:.3f} "
          f"(discrete perimeter; compare objects relatively)")

    print()
    print("ASCII view (original | edges | mask), each char = 2x2 px max:")
    print("[original]")
    print(ascii_art(img))
    print("[sobel edges]")
    print(ascii_art(edges))
    print("[otsu mask]")
    print(ascii_art([[v * MAXV for v in row] for row in mask]))
    return img, blurred, edges, mask, comps_sorted


# --------------------------------------- بخش B: طبقه‌بند نزدیک‌ترین مرکز
def make_sample(kind, rng, size=32):
    """یک تصویر 32x32 ساختگی از کلاس مشخص.

    'round'   : دایره‌ی تیزمرز با شعاع و شدت تصادفی روی پس‌زمینه‌ی نویزدار
    'diffuse' : لکه‌ی گاوسی پخش‌شده با سیگما و دامنه‌ی تصادفی
    """
    img = [[30 + rng.randint(-10, 10) for _ in range(size)] for _ in range(size)]
    c = size / 2 + rng.uniform(-3, 3)
    if kind == "round":
        radius = rng.choice((5.0, 6.0, 7.0))
        amp = rng.choice((190, 200, 210))
        for i in range(size):
            for j in range(size):
                r = math.hypot(i - c, j - c)
                if r <= radius:
                    img[i][j] = clamp(int(amp - 6 * r))
    else:
        sigma = rng.choice((6.0, 7.0, 8.0))
        amp = rng.choice((110, 125, 140))
        for i in range(size):
            for j in range(size):
                d2 = (i - c) ** 2 + (j - c) ** 2
                img[i][j] = clamp(int(img[i][j] + amp *
                                      math.exp(-d2 / (2 * sigma ** 2))))
    return img


def image_features(img):
    """دو ویژگی سراسری: چگالی لبه و کنتراست اوج (اوج − میانه).

    چگالی لبه روی گرادیانِ تصویرِ «هموارشده» با آستانه‌ی ثابت EDGE_T
    محاسبه می‌شود تا هم نویز سرکوب شود و هم مقادیر در همه‌ی تصاویر
    قابل مقایسه باشند (اول هموار، بعد مشتق).
    """
    blurred = convolve2d(img, BOX3)
    edges = sobel_raw(blurred)
    edge_density = sum(1 for row in edges for v in row if v > EDGE_T) / \
        (len(img) * len(img[0]))
    vals = [v for row in img for v in row]
    peak_contrast = max(vals) - median(vals)
    return (edge_density, peak_contrast)


def nearest_centroid(train, test):
    """آموزش مرکز هر کلاس و برچسب‌زنی نمونه‌های آزمون (فاصله‌ی اقلیدسی 2بعدی)."""
    cents = {}
    for kind in ("round", "diffuse"):
        pts = [f for k, f in train if k == kind]
        cents[kind] = (mean([p[0] for p in pts]), mean([p[1] for p in pts]))
    preds = []
    for true_k, f in test:
        d = {k: math.hypot(f[0] - c0, f[1] - c1) for k, (c0, c1) in cents.items()}
        pred = min(d, key=d.get)
        preds.append((true_k, pred, f, d))
    return cents, preds


def part_b(scene_img, scene_comps):
    print("=" * 72)
    print("PART B | nearest-centroid classifier on synthetic images")
    print("=" * 72)
    tr = random.Random(TRAIN_SEED)
    te = random.Random(TEST_SEED)
    train = [(kind, image_features(make_sample(kind, tr)))
             for kind in ("round", "diffuse") for _ in range(N_TRAIN)]
    test = [(kind, image_features(make_sample(kind, te)))
            for kind in ("round", "diffuse") for _ in range(N_TEST)]

    cents, preds = nearest_centroid(train, test)
    print(f"train: {N_TRAIN}+{N_TRAIN} images | test: {N_TEST}+{N_TEST} images "
          f"(32x32, synthetic)")
    for kind in ("round", "diffuse"):
        c0, c1 = cents[kind]
        print(f"  centroid[{kind:>7}] = (edge_density={c0:.4f}, "
              f"peak_contrast={c1:.1f})")
    print("features = (edge_density, peak_contrast); metric = Euclidean")

    tp = sum(1 for t, p, _, _ in preds if t == "round" and p == "round")
    fp = sum(1 for t, p, _, _ in preds if t == "diffuse" and p == "round")
    fn = sum(1 for t, p, _, _ in preds if t == "round" and p == "diffuse")
    tn = sum(1 for t, p, _, _ in preds if t == "diffuse" and p == "diffuse")
    total = tp + fp + fn + tn
    acc = (tp + tn) / total
    print(f"confusion matrix (positive = 'round'): TP={tp} FP={fp} "
          f"FN={fn} TN={tn} over {total} test images")
    print(f"accuracy = {acc:.3f}")
    if fp or fn:
        print("misclassified test samples:")
        for i, (t, p, f, d) in enumerate(preds):
            if t != p:
                print(f"  test#{i}: true={t} pred={p} features=({f[0]:.4f}, "
                      f"{f[1]:.1f}) dist_round={d['round']:.3f} "
                      f"dist_diffuse={d['diffuse']:.3f}")

    # اعمال مدل روی جسمِ یافت‌شده در صحنه‌ی بخش A
    big = scene_comps[0]
    ys = [p[0] for p in big]
    xs = [p[1] for p in big]
    i0, i1 = max(0, min(ys) - 4), min(SIZE, max(ys) + 5)
    j0, j1 = max(0, min(xs) - 4), min(SIZE, max(xs) + 5)
    crop = [[scene_img[i][j] for j in range(j0, j1)] for i in range(i0, i1)]
    f = image_features(crop)
    d = {k: math.hypot(f[0] - c0, f[1] - c1) for k, (c0, c1) in cents.items()}
    pred = min(d, key=d.get)
    print()
    print("apply model to the largest object found in PART A's scene "
          "(cropped window):")
    print(f"  features=(edge_density={f[0]:.4f}, peak_contrast={f[1]:.1f}) "
          f"dist_round={d['round']:.3f} dist_diffuse={d['diffuse']:.3f} "
          f"=> predicted class '{pred}'")
    print("takeaway: two simple features + nearest centroid already separate")
    print("the synthetic classes; real medical imaging needs thousands of")
    print("annotated images and careful validation (session 27).")


def main():
    print("session 26 — medical imaging pipeline demo (all data synthetic, "
          "educational, non-diagnostic)")
    print()
    img, blurred, edges, mask, comps = part_a()
    print()
    part_b(img, comps)
    print()
    print("همه‌ی اعداد این خروجی از seedهای ثابت می‌آیند؛ اجرای دوباره همین")
    print("خروجی را تولید می‌کند. این اسکریپت هیچ ارزش تشخیصی ندارد.")


if __name__ == "__main__":
    main()
