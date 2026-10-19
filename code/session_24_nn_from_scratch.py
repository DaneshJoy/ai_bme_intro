# -*- coding: utf-8 -*-
"""جلسه ۲۴ — شبکه‌ی عصبی از صفر (بدون NumPy): نورون، تابع فعال‌سازی، MLP و XOR

سه بخش:
1) نورون تکی: جدول σ(z) و σ′(z) و دموی «گرادیان محو» (حاصل‌ضرب مشتق‌ها در لایه‌ها).
2) یک نورون آموزش‌پذیر (sigmoid + خطای میانگین مربعات) روی داده‌ی خطی‌جداشدنی
   کوچک دو-ویژگی؛ آموزش با گرادیان کاهشی کامل (Full-batch).
3) MLP کوچک 2-4-1 روی مسئله‌ی XOR با گرادیان کاهشی و منحنی خطای متنی.

نکته تکرارپذیری: seed ثابت است و هر تابع، نمونه‌ی random خودش را محلی و با همان
seed ثابت می‌سازد (random.Random(SEED))؛ پس خروجی مستقل از ترتیب فراخوانی
توابع است و هر بار اجرا همان عددها را می‌دهد.

در Colab همین ایده‌ها با NumPy برداری‌تر و کوتاه‌تر می‌شوند؛ اینجا عمداً فقط
از کتابخانه استاندارد پایتون (math و random) استفاده شده تا آفلاین اجرا شود.
کد آموزشی است و هیچ کاربرد تشخیصی یا بالینی ندارد.

اجرا:
    python3 code/session_24_nn_from_scratch.py
"""

import math
import random

SEED = 2024          # seed ثابت برای همه‌ی بخش‌ها
LEARNING_RATE = 1.5  # نرخ یادگیری هر دو مدل


# ---------------- ابزارهای پایه ----------------

def sigmoid(z):
    """تابع فعال‌سازی سیگموید: σ(z) = 1/(1+e^{-z})."""
    return 1.0 / (1.0 + math.exp(-z))


def sigmoid_prime_from_a(a):
    """مشتق σ برحسب خروجی: σ′(z) = σ(z)·(1−σ(z))."""
    return a * (1.0 - a)


def init_weights(rng, shape):
    """وزن‌های اولیه‌ی تصادفی کوچک با نمونه‌ی local (قطعی به seed وابسته است)."""
    return [rng.uniform(-1.0, 1.0) for _ in range(shape)]


# ---------------- بخش ۱: نورون، σ و پدیده‌ی گرادیان محو ----------------

def neuron_table():
    """جدول σ(z) و σ′(z) برای چند z نمونه."""
    print("بخش ۱ — نورون تکی و تابع فعال‌سازی")
    print("  فرمول نورون: z = w1*x1 + w2*x2 + b ، a = sigma(z)")
    print("   z    |  sigma(z)  |  sigma'(z)")
    print("  ------+------------+-----------")
    for z in (-4.0, -2.0, 0.0, 2.0, 4.0):
        a = sigmoid(z)
        print("  %5.1f |   %.4f    |   %.4f" % (z, a, sigmoid_prime_from_a(a)))
    print("  بیشینه‌ی sigma' برابر 0.25 است (در z = 0).")
    print()


def vanishing_demo(layers_list=(1, 2, 3, 4, 5)):
    """حاصل‌ضرب مشتق‌ها در L لایه: چرا گرادیان در شبکه‌ی عمیق «محو» می‌شود."""
    print("دموی گرادیان محو (Vanishing Gradient):")
    print("  هر لایه‌ی sigmoid در عقب‌گرد مشتق‌ها را حداکثر در 0.25 ضرب می‌کند.")
    print("   لایه‌ها | حاصل‌ضرب با sigmoid | حاصل‌ضرب با ReLU")
    for layers in layers_list:
        prod_sigmoid = 0.25 ** layers
        prod_relu = 1.0 ** layers
        print("     %d     |       %.6f       |     %.6f" % (layers, prod_sigmoid, prod_relu))
    print("  با ReLU مشتق در ناحیه‌ی فعال دقیقاً 1 است؛ حاصل‌ضرب کوچک نمی‌شود.")
    print()
    return [0.25 ** layers for layers in layers_list]


# ---------------- بخش ۲: یک نورون آموزش‌پذیر روی داده‌ی دو-ویژگی ----------------

# داده‌ی ساختگی کوچک: 8 نمونه‌ی دو-ویژگی؛ برچسب = 1 اگر x1 + x2 >= 1.0 باشد
DATASET = [
    ((0.2, 0.3), 0),
    ((0.4, 0.6), 1),
    ((0.1, 0.8), 0),
    ((0.7, 0.2), 0),
    ((0.8, 0.8), 1),
    ((0.9, 0.5), 1),
    ((0.3, 0.4), 0),
    ((0.6, 0.9), 1),
]


def train_single_neuron(dataset, lr=2.0, epochs=6000, log_every=1500, seed=SEED):
    """آموزش یک نورون sigmoid با خطای میانگین مربعات و گرادیان کاهشی کامل.

    خروجی: (w1, w2, b، فهرست (epoch, loss, accuracy) برای نمونه‌گرفتن‌ها، loss نهایی)
    """
    rng = random.Random(seed)            # seed محلی: مستقل از ترتیب فراخوانی
    w1, w2 = init_weights(rng, 2)
    b = rng.uniform(-0.5, 0.5)
    n = len(dataset)
    snapshots = []
    samples = []                          # (x1, x2, z, a, y) برای گزارش نهایی
    for epoch in range(epochs + 1):
        # پیش‌روی و جمع گرادیان‌ها روی کل داده (Full-batch)
        g_w1 = g_w2 = g_b = loss = 0.0
        correct = 0
        for (x1, x2), y in dataset:
            a = sigmoid(w1 * x1 + w2 * x2 + b)
            err = a - y
            loss += 0.5 * err * err
            d = err * sigmoid_prime_from_a(a)   # dL/dz برای این نمونه
            g_w1 += d * x1
            g_w2 += d * x2
            g_b += d
            correct += 1 if (a >= 0.5) == (y == 1) else 0
        loss /= n
        if epoch % log_every == 0 or epoch == epochs:
            snapshots.append((epoch, loss, correct))
        # به‌روزرسانی گرادیان کاهشی
        w1 -= lr * g_w1 / n
        w2 -= lr * g_w2 / n
        b -= lr * g_b / n
    for (x1, x2), y in dataset:
        z = w1 * x1 + w2 * x2 + b
        samples.append((x1, x2, z, sigmoid(z), y))
    return w1, w2, b, snapshots, loss, samples


def single_neuron_demo():
    print("بخش ۲ — یک نورون آموزش‌پذیر روی داده‌ی خطی‌جداشدنی")
    print("  8 نمونه‌ی دو-ویژگی؛ برچسب: 1 اگر x1 + x2 >= 1.0 باشد")
    w1, w2, b, snapshots, final_loss, samples = train_single_neuron(DATASET)
    print("  epoch   loss    | دقت")
    for epoch, loss, correct in snapshots:
        print("  %5d  %.4f  | %d/8" % (epoch, loss, correct))
    print("  وزن‌های نهایی: w1 = %.4f ، w2 = %.4f ، b = %.4f" % (w1, w2, b))
    print("  مرز تصمیم یادگرفته‌شده: %+.2f*x1 %+.2f*x2 %+.2f = 0" % (w1, w2, b))
    print("  خروجی نهایی روی نمونه‌ها (z ، a = sigma(z) ، کلاس پیش‌بینی):")
    for x1, x2, z, a, y in samples:
        print("    x=(%.1f,%.1f) -> z=%+7.4f -> a=%.4f -> کلاس %d | واقعی %d %s"
              % (x1, x2, z, a, 1 if a >= 0.5 else 0, y,
                 "✓" if (a >= 0.5) == (y == 1) else "✗"))
    print("  دقت نهایی روی همان داده: %d/8" % snapshots[-1][2])
    print()
    return w1, w2, b, snapshots, final_loss, samples


# ---------------- بخش ۳: MLP کوچک روی XOR ----------------

XOR_DATA = [((0, 0), 0), ((0, 1), 1), ((1, 0), 1), ((1, 1), 0)]


class MLP:
    """شبکه‌ی 2-4-1: دو ورودی، چهار نورون پنهان sigmoid، یک خروجی sigmoid."""

    def __init__(self, hidden=4, seed=SEED):
        rng = random.Random(seed)        # seed محلی؛ خروجی مستقل از ترتیب اجراست
        self.w_hidden = [init_weights(rng, 2) for _ in range(hidden)]  # w[j][i]
        self.b_hidden = [rng.uniform(-1.0, 1.0) for _ in range(hidden)]
        self.w_out = init_weights(rng, hidden)
        self.b_out = rng.uniform(-1.0, 1.0)
        self.hidden = hidden

    def forward(self, x1, x2):
        """پیش‌روی: خروجی لایه‌ی پنهان و خروجی شبکه را برمی‌گرداند."""
        a_hidden = [sigmoid(self.w_hidden[j][0] * x1 + self.w_hidden[j][1] * x2
                            + self.b_hidden[j]) for j in range(self.hidden)]
        z_out = sum(self.w_out[j] * a_hidden[j] for j in range(self.hidden)) + self.b_out
        return a_hidden, sigmoid(z_out)

    def train_step(self, data, lr):
        """یک گام گرادیان کاهشی کامل (Full-batch) با پس‌انتشار خطا."""
        g_w_hidden = [[0.0, 0.0] for _ in range(self.hidden)]
        g_b_hidden = [0.0] * self.hidden
        g_w_out = [0.0] * self.hidden
        g_b_out = 0.0
        n = len(data)
        loss = 0.0
        for (x1, x2), y in data:
            a_hidden, a_out = self.forward(x1, x2)
            err = a_out - y
            loss += 0.5 * err * err
            delta_out = err * sigmoid_prime_from_a(a_out)          # لایه‌ی خروجی
            for j in range(self.hidden):
                delta_h = delta_out * self.w_out[j] * sigmoid_prime_from_a(a_hidden[j])
                g_w_hidden[j][0] += delta_h * x1
                g_w_hidden[j][1] += delta_h * x2
                g_b_hidden[j] += delta_h
                g_w_out[j] += delta_out * a_hidden[j]
            g_b_out += delta_out
        # میانگین‌گیری و به‌روزرسانی (پس‌انتشار کامل شد؛ حالا قدم برمی‌داریم)
        for j in range(self.hidden):
            self.w_hidden[j][0] -= lr * g_w_hidden[j][0] / n
            self.w_hidden[j][1] -= lr * g_w_hidden[j][1] / n
            self.b_hidden[j] -= lr * g_b_hidden[j] / n
            self.w_out[j] -= lr * g_w_out[j] / n
        self.b_out -= lr * g_b_out / n
        return loss / n

    def loss(self, data):
        return sum(0.5 * (self.forward(x1, x2)[1] - y) ** 2
                   for (x1, x2), y in data) / len(data)

    def predictions(self, data):
        out = []
        for (x1, x2), y in data:
            _, a = self.forward(x1, x2)
            out.append((x1, x2, a, 1 if a >= 0.5 else 0, y))
        return out


def train_xor(epochs=8000, lr=LEARNING_RATE, log_every=1000, hidden=4, seed=SEED):
    """آموزش MLP روی XOR؛ خروجی: (شبکه، تاریخچه‌ی loss، پیش‌بینی‌های نهایی)."""
    net = MLP(hidden=hidden, seed=seed)
    history = [(0, net.loss(XOR_DATA))]
    for epoch in range(1, epochs + 1):
        loss = net.train_step(XOR_DATA, lr)
        if epoch % log_every == 0:
            history.append((epoch, loss))
    return net, history, net.predictions(XOR_DATA)


def xor_demo():
    print("بخش ۳ — MLP کوچک 2-4-1 روی XOR (گرادیان کاهشی کامل)")
    net, history, preds = train_xor()
    max_loss = history[0][1]
    print("  منحنی خطا (طول میله = اندازه‌ی loss):")
    for epoch, loss in history:
        bar = "#" * max(1, int(round(loss / max_loss * 30))) if loss > 1e-12 else ""
        print("  epoch %5d | loss = %.4f | %s" % (epoch, loss, bar))
    print("  پیش‌بینی نهایی روی XOR:")
    for x1, x2, a, pred, y in preds:
        print("    x=(%d,%d) -> خروجی=%.4f -> کلاس %d | واقعی %d %s"
              % (x1, x2, a, pred, y, "✓" if pred == y else "✗"))
    correct = sum(1 for *_x, pred, y in preds if pred == y)
    print("  دقت: %d از %d" % (correct, len(preds)))
    print()
    return net, history, preds, correct


def determinism_check():
    """دو اجرای پشت‌سرهم باید دقیقاً یک نتیجه بدهند (seed محلی در هر فراخوانی)."""
    _net1, hist1, preds1 = train_xor(epochs=500)
    _net2, hist2, preds2 = train_xor(epochs=500)
    assert hist1 == hist2 and preds1 == preds2, \
        "دو اجرای با seed ثابت باید خروجی یکسان بدهند"
    print("خودآزمایی تکرارپذیری: OK — دو اجرای پشت‌سرهم XOR نتیجه‌ی یکسان داد")


# ---------------- خودآزمون‌ها با assert ----------------

def run_self_checks(neuron_res, xor_res, vanishing):
    w1, w2, b, snapshots, final_loss_neuron, samples = neuron_res
    net, history, preds, correct = xor_res

    # بخش ۱: ویژگی‌های شناخته‌شده‌ی sigmoid
    assert math.isclose(sigmoid(0.0), 0.5, abs_tol=1e-12), "sigma(0) باید 0.5 باشد"
    assert math.isclose(sigmoid_prime_from_a(0.5), 0.25, abs_tol=1e-12), \
        "بیشینه‌ی مشتق sigmoid باید 0.25 باشد"
    assert vanishing[-1] == 0.25 ** 5, "حاصل‌ضرب ۵ لایه باید 0.25^5 باشد"
    assert all(v1 > v2 for v1, v2 in zip(vanishing, vanishing[1:])), \
        "حاصل‌ضرب باید با عمق لایه‌ها کاهش یابد"
    print("خودآزمایی بخش ۱: OK — σ(0)=0.5 ، بیشینه‌ی σ′=0.25 و روند کاهشی تأیید شد")

    # بخش ۲: نورون باید داده را کامل یاد بگیرد
    assert final_loss_neuron < 0.05, "loss نهایی نورون باید کوچک باشد: %s" % final_loss_neuron
    assert snapshots[-1][2] == 8, "دقت نورون باید 8/8 باشد"
    losses = [s[1] for s in snapshots]
    assert all(l1 >= l2 for l1, l2 in zip(losses, losses[1:])), "loss باید کاهشی باشد"
    print("خودآزمایی بخش ۲: OK — loss کاهشی، دقت 8/8 و loss نهایی < 0.05")

    # بخش ۳: XOR باید همگرا شود و هر چهار نمونه درست پیش‌بینی شوند
    final_loss_xor = history[-1][1]
    assert final_loss_xor < 0.02, "loss نهایی XOR باید کوچک باشد: %s" % final_loss_xor
    assert correct == 4, "هر چهار نمونه‌ی XOR باید درست طبقه‌بندی شوند"
    assert history[0][1] > history[len(history) // 2][1] > final_loss_xor, \
        "منحنی loss باید کاهشی باشد"
    for _x1, _x2, _a, pred, y in preds:
        assert pred == y, "پیش‌بینی XOR نادرست است"
    print("خودآزمایی بخش ۳: OK — XOR همگرا شد (loss نهایی < 0.02) و دقت 4/4")

    determinism_check()


def main():
    print("=" * 62)
    print("جلسه ۲۴ — شبکه‌ی عصبی از صفر (بدون NumPy)")
    print("=" * 62)
    print()
    neuron_table()
    vanishing = vanishing_demo()
    neuron_res = single_neuron_demo()
    xor_res = xor_demo()
    print("-" * 62)
    run_self_checks(neuron_res, xor_res, vanishing)
    print()
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
