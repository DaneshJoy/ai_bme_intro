# -*- coding: utf-8 -*-
"""Gradient Descent — جلسه ۱۱

دو آزمایش آموزشی (غیرتشخیصی) روی کالیبراسیون سنسور:

  ۱) برازش خطای بایاس سنسور دما با کمینه‌سازی مربعات خطا (Least Squares)
     مدل: y = t + θ   (قرائت سنسور = دمای مرجع + بایاس)
     خطا: J(θ) = (1/n) Σ (y_i − t_i − θ)²
     گرادیان: J'(θ) = −(2/n) Σ (y_i − t_i − θ)
     قاعده به‌روزرسانی: θ ← θ − α·J'(θ)

     اجرا با نرخ‌های یادگیری مختلف α و چاپ مسیر همگرایی + یک حالت واگرایی.

  ۲) تابع چاه-دوقلو (Double Well) برای نمایش کمینه‌های محلی:
     J(θ) = (θ² − 1)²  با دو کمینه در θ = +1 و θ = −1
     نقطه شروع، تعیین می‌کند گرادیان کاهشی به کدام کمینه می‌رود.

اجرا:
    python3 code/session_11_gradient_descent.py

فقط کتابخانه استاندارد پایتون. خروجی کاملاً قطعی است.
"""

# ------------------------------------------------ داده کالیبراسیون
TEMP = [10.0, 15.0, 20.0, 25.0, 30.0]   # دمای مرجع (دماسنج کالیبره)
READ = [12.1, 17.2, 22.0, 27.1, 32.0]   # قرائت سنسور آزمایشی


def loss(theta):
    """J(θ): میانگین مربعات خطا بین قرائت سنسور و مدل t + θ."""
    n = len(READ)
    return sum((r - t - theta) ** 2 for t, r in zip(TEMP, READ)) / n


def grad(theta):
    """J'(θ): مشتق خطا نسبت به بایاس θ."""
    n = len(READ)
    return -2.0 * sum((r - t - theta) for t, r in zip(TEMP, READ)) / n


THETA_STAR = sum(r - t for t, r in zip(TEMP, READ)) / len(READ)


def run_gd(alpha, theta0=0.0, max_steps=30, tol=0.01, stop_big=1e6):
    """اجرا گرادیان کاهشی؛ خروجی: مسیر گام‌ها، شمار گام تا همگرایی."""
    theta = theta0
    path = [(0, theta, loss(theta))]
    converged_at = None
    for step in range(1, max_steps + 1):
        theta = theta - alpha * grad(theta)
        path.append((step, theta, loss(theta)))
        if converged_at is None and abs(theta - THETA_STAR) < tol:
            converged_at = step
        if abs(theta) > stop_big:            # واگرایی؛ ادامه کار بی‌فایده است
            break
    return path, converged_at


def demo_calibration():
    print("=== آزمایش ۱: برازش بایاس سنسور با گرادیان کاهشی ===")
    print("داده (آموزشی): دمای مرجع و قرائت سنسور")
    for t, r in zip(TEMP, READ):
        print(f"  t = {t:5.1f} °C    قرائت سنسور = {r:5.2f} °C")
    print(f"بهترین بایاس (مقادیر بسته): θ* = {THETA_STAR:.4f}")
    print(f"J(θ*) = {loss(THETA_STAR):.6f} ،  J(0) = {loss(0.0):.6f}")
    print()

    for alpha in [0.1, 0.5, 0.9, 1.5]:
        path, conv = run_gd(alpha)
        print(f"--- α = {alpha} ---")
        shown = path[:7] if conv is None or conv >= 7 else path[:conv + 1]
        for step, theta, j in shown:
            print(f"  گام {step:2d}: θ = {theta:12.4f} ،  J = {j:12.4f}")
        last = path[-1]
        if conv is not None:
            print(f"  همگرایی به |θ − θ*| < 0.01 در گام {conv}")
            print(f"  مقدار نهایی: θ = {last[1]:.4f}")
        else:
            print(f"  همگرایی با tol=0.01 تا {last[0]} گام رخ نداد؛ "
                  f"θ آخر = {last[1]:.4g}")
        print()


def demo_double_well():
    print("=== آزمایش ۲: کمینه‌های محلی — تابع چاه-دوقلو ===")
    print("J(θ) = (θ² − 1)²  ،  J'(θ) = 4θ(θ² − 1)")
    print("کمینه‌های سراسری: θ = +1 و θ = −1 (هر دو J = 0) ، نقطه θ = 0 کمینه محلی نیست بلکه بیشینه است")
    print()

    def loss_dw(theta):
        return (theta ** 2 - 1) ** 2

    def grad_dw(theta):
        return 4.0 * theta * (theta ** 2 - 1)

    alpha = 0.05
    for theta0 in [-0.6, 0.0, 0.6]:
        theta = theta0
        for _ in range(60):
            theta = theta - alpha * grad_dw(theta)
        print(f"شروع از θ₀ = {theta0:+.1f} → پس از ۶۰ گام با α = {alpha}: "
              f"θ = {theta:+.4f} ، J = {loss_dw(theta):.6f}")


if __name__ == "__main__":
    demo_calibration()
    print()
    demo_double_well()
