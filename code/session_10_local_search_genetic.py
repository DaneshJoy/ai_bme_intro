# -*- coding: utf-8 -*-
"""جست‌وجوی محلی و الگوریتم ژنتیک — جلسه ۱۰

مسئله نمونه «چیدمان سنسور» (آموزشی و غیرتشخیصی):
روی یک مسیر ۲۰ خانه‌ای (مثلاً مسیر پیاده‌روی بیمار در کلینیک بازتوانی)
می‌خواهیم ۳ سنسور بگذاریم تا پوشش مسیر بیشینه شود؛ خانه‌های ۵ تا ۷
«ناحیه مهم» هستند و وزن دوبرابر دارند.

سه روش مقایسه می‌شوند:
  1) Hill Climbing   (صعود قله با چند شروع مجدد)
  2) Simulated Annealing (شبیه‌سازی تبرید)
  3) Genetic Algorithm   (الگوریتم ژنتیک)

برای مرجع، جست‌وجوی کامل (Brute Force) هم اجرا می‌شود تا بهینه جهانی مشخص شود.

اجرا:
    python3 code/session_10_local_search_genetic.py

فقط کتابخانه استاندارد پایتون (شامل random). هر روش تصادفی در ابتدای
اجرای خودش با seed پیش‌فرض ۴۲ مقداردهی می‌شود؛ پس نتیجه‌ی هر روش مستقل
از ترتیب و تعداد روش‌های اجراشده، تکرارپذیر است.
"""

import itertools
import math
import random

# seed پیش‌فرض همه روش‌های تصادفی؛ برای تغییر، همین مقدار یا پارامتر
# seed هر تابع را عوض کنید.
DEFAULT_SEED = 42

# ------------------------------------------------------- تعریف مسئله
CORRIDOR_LENGTH = 20      # تعداد خانه‌های مسیر: ۰ تا ۱۹
NUM_SENSORS = 3           # تعداد سنسورها
RADIUS = 2                # برد هر سنسور (خانه‌های مجاور)
CRITICAL_CELLS = {5, 6, 7}  # ناحیه مهم مسیر (وزن دوبرابر)
OVERLAP_PENALTY = 10      # جریمه هر سنسور اضافی روی یک خانه مشترک


def fitness(state):
    """برازش یک چیدمان: امتیاز پوشش منهای جریمه هم‌مکانی سنسورها."""
    total = 0
    for cell in range(CORRIDOR_LENGTH):
        best = 0
        for pos in state:
            dist = abs(cell - pos)
            if dist <= RADIUS:
                best = max(best, RADIUS - dist + 1)  # پوشش مثل نردبان ۱ تا ۳
        if best and cell in CRITICAL_CELLS:
            best *= 2
        total += best
    total -= OVERLAP_PENALTY * (NUM_SENSORS - len(set(state)))
    return total


def random_state():
    """یک چیدمان تصادفی با سنسورهای در خانه‌های متمایز."""
    return tuple(sorted(random.sample(range(CORRIDOR_LENGTH), NUM_SENSORS)))


def random_neighbor(state):
    """حرکت محلی: جابه‌جایی یک سنسور تصادفی یک خانه به چپ یا راست."""
    pos = list(state)
    i = random.randrange(NUM_SENSORS)
    pos[i] = min(CORRIDOR_LENGTH - 1, max(0, pos[i] + random.choice((-1, 1))))
    return tuple(pos)


# ------------------------------------------------- صفر: جست‌وجوی کامل (مرجع)
def brute_force():
    best_state, best_fit = None, float("-inf")
    for combo in itertools.combinations(range(CORRIDOR_LENGTH), NUM_SENSORS):
        f = fitness(combo)
        if f > best_fit:
            best_state, best_fit = combo, f
    return best_state, best_fit


# ------------------------------------------------------- ۱: Hill Climbing
def hill_climbing(restarts=5, seed=DEFAULT_SEED):
    """صعود قله‌ای با انتخاب همسایه بهتر؛ چند بار از نقطه تصادفی شروع می‌کنیم.

    seed در ابتدای تابع مقداردهی می‌شود تا نتیجه مستقل از ترتیب اجرا باشد.
    """
    random.seed(seed)
    best_state, best_fit = None, float("-inf")
    for _ in range(restarts):
        state = random_state()
        while True:
            neighbors = set()
            for i in range(NUM_SENSORS):
                for delta in (-1, 1):
                    pos = list(state)
                    pos[i] = min(CORRIDOR_LENGTH - 1, max(0, pos[i] + delta))
                    neighbors.add(tuple(pos))
            neighbors.discard(state)
            candidates = sorted(neighbors)  # ترتیب قطعی برای تکرارپذیری
            best_nb = max(candidates, key=fitness)
            if fitness(best_nb) <= fitness(state):
                break  # بهینه محلی؛ صعود بیشتر ممکن نیست
            state = best_nb
        if fitness(state) > best_fit:
            best_state, best_fit = state, fitness(state)
    return best_state, best_fit


# ------------------------------------------------ ۲: Simulated Annealing
def simulated_annealing(steps=200, t0=10.0, alpha=0.95, seed=DEFAULT_SEED):
    """تبرید: حرکت بدتر هم با احتمال exp(dF/T) پذیرفته می‌شود؛ T به‌مرور سرد می‌شود.

    seed در ابتدای تابع مقداردهی می‌شود تا نتیجه مستقل از ترتیب اجرا باشد.
    """
    random.seed(seed)
    state = random_state()
    best_state, best_fit = state, fitness(state)
    temperature = t0
    for _ in range(steps):
        candidate = random_neighbor(state)
        delta = fitness(candidate) - fitness(state)
        if delta >= 0 or random.random() < math.exp(delta / temperature):
            state = candidate
            if fitness(state) > best_fit:
                best_state, best_fit = state, fitness(state)
        temperature *= alpha
    return best_state, best_fit


# ---------------------------------------------------- ۳: Genetic Algorithm
POP_SIZE = 20        # اندازه جمعیت
GENERATIONS = 60     # تعداد نسل‌ها
TOURNAMENT_K = 3     # اندازه نمونه در گزینش مسابقه‌ای
MUTATION_RATE = 0.2  # احتمال جهش هر ژن
ELITE = 2            # تعداد نخبه‌هایی که بی‌تغییر به نسل بعد می‌روند


def tournament(population):
    """گزینش مسابقه‌ای: k عضو نمونه می‌گیریم و بهترین را برمی‌داریم."""
    contestants = random.sample(population, TOURNAMENT_K)
    return max(contestants, key=fitness)


def crossover(parent_a, parent_b):
    """تقاطع تک‌نقطه‌ای: پیشوند از والد اول، پسوند از والد دوم."""
    cut = random.randint(1, NUM_SENSORS - 1)
    return tuple(parent_a[:cut] + parent_b[cut:])


def mutate(chromosome):
    """جهش: هر ژن با احتمال MUTATION_RATE به خانه‌ای تصادفی می‌رود."""
    genes = list(chromosome)
    for i in range(NUM_SENSORS):
        if random.random() < MUTATION_RATE:
            genes[i] = random.randrange(CORRIDOR_LENGTH)
    return tuple(genes)


def genetic_algorithm(seed=DEFAULT_SEED):
    """الگوریتم ژنتیک؛ seed در ابتدای تابع مقداردهی می‌شود تا نتیجه
    مستقل از ترتیب اجرا باشد."""
    random.seed(seed)
    population = [random_state() for _ in range(POP_SIZE)]
    for _ in range(GENERATIONS):
        population.sort(key=fitness, reverse=True)
        next_population = population[:ELITE]  # نخبه‌گرایی (Elitism)
        while len(next_population) < POP_SIZE:
            child = mutate(crossover(tournament(population), tournament(population)))
            next_population.append(child)
        population = next_population
    best = max(population, key=fitness)
    return best, fitness(best)


# ------------------------------------------------------------- اجرا و جدول
def main():
    print("مسئله چیدمان ۳ سنسور روی مسیر ۲۰ خانه‌ای (ناحیه مهم: خانه‌های ۵ تا ۷)")
    print(f"seed هر روش = {DEFAULT_SEED}  →  خروجی مستقل از ترتیب اجرا تکرارپذیر است.")
    print()

    results = [
        ("Brute force (مرجع)", brute_force()),
        ("Hill Climbing", hill_climbing(seed=DEFAULT_SEED)),
        ("Simulated Annealing", simulated_annealing(seed=DEFAULT_SEED)),
        ("Genetic Algorithm", genetic_algorithm(seed=DEFAULT_SEED)),
    ]
    optimal_fit = results[0][1][1]

    header = "{:<22}{:>13}   {:<14}{:<8}".format(
        "Method", "Best fitness", "Placement", "Global opt")
    print(header)
    print("-" * len(header))
    for name, (state, fit) in results:
        is_opt = "yes" if fit == optimal_fit else "no"
        print("{:<22}{:>13}   {:<14}{:<8}".format(name, fit, str(state), is_opt))

    print()
    print("نکته‌ها:")
    print("1) Hill Climbing ساده و سریع است اما ممکن است در بهینه محلی گیر کند؛")
    print("   شروع‌های مجدد شانس رسیدن به بهینه جهانی را بالا می‌برند.")
    print("2) Simulated Annealing با پذیرفتن موقت حرکت‌های بدتر از دره می‌گذرد.")
    print("3) Genetic Algorithm با جمعیت، گزینش، تقاطع و جهش فضای جست‌وجو را پوشش می‌دهد.")
    print("4) مقایسه را با seedهای دیگر (مثلاً 7 یا 99) تکرار کنید و نتیجه را ببینید.")


if __name__ == "__main__":
    main()