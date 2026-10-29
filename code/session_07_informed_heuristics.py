# -*- coding: utf-8 -*-
"""جلسه ۷ — جست‌وجوی آگاهانه (Informed Search) و توابع ابتکاری (Heuristics)

سناریوی آموزشی: شبکه راهروهای یک طبقه بیمارستان (شبکه ۵×۵)
- هر خانه یک تقاطع/اتاق است و حرکت به چهار همسایه هزینه ۱ دارد.
- خانه‌های «#» به‌خاطر تعمیرات بسته‌اند و از گراف حذف شده‌اند:
  راهروی ستون ۱ در ردیف‌های ۰ تا ۲ و دو اتاق (3,3) و (4,3).
- هدف: یافتن مسیر از اورژانس (0,0) تا اتاق عمل (4,4).

این اسکریپت سه کار می‌کند:
1) سه تابع ابتکاری h(n) را تعریف می‌کند (Manhattan، Euclidean، 2×Manhattan).
2) برای هر گره، h* (هزینه واقعی کمینه تا هدف) را با Dijkstra حساب می‌کند و
   «مجاز بودن» (Admissible) و «ثبات» (Consistent) هر هیوریستیک را گره‌به‌گره چاپ می‌کند.
3) جست‌وجوی حریصانه (Greedy Best-First) را با هر هیوریستیک اجرا و مقایسه می‌کند.

فقط از کتابخانه استاندارد پایتون استفاده می‌شود.
کد آموزشی است و هیچ کاربرد تشخیصی یا بالینی ندارد.
"""

import heapq

# ---------------- گراف: طبقه بیمارستان ----------------

N = 5                      # ابعاد شبکه
START = (0, 0)             # اورژانس
GOAL = (4, 4)              # اتاق عمل
BLOCKED = {(0, 1), (1, 1), (2, 1), (3, 3), (4, 3)}   # راهروهای بسته (تعمیرات)

EPS = 1e-9   # برای مقایسه اعداد اعشاری


def print_map():
    """نقشه طبقه: . = راهرو باز، # = بسته، S = شروع، G = هدف."""
    print("      c0  c1  c2  c3  c4")
    for r in range(N):
        cells = []
        for c in range(N):
            node = (r, c)
            if node == START:
                cells.append(" S ")
            elif node == GOAL:
                cells.append(" G ")
            elif node in BLOCKED:
                cells.append(" # ")
            else:
                cells.append(" . ")
        print("r%d  %s" % (r, "".join(cells)))
    print()


def neighbors(node):
    """همسایه‌های باز با هزینه یکسان ۱ (حرکت چهارجهته)."""
    r, c = node
    result = []
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nxt = (r + dr, c + dc)
        if 0 <= nxt[0] < N and 0 <= nxt[1] < N and nxt not in BLOCKED:
            result.append((nxt, 1))
    return result


def all_nodes():
    return [(r, c) for r in range(N) for c in range(N) if (r, c) not in BLOCKED]


# ---------------- توابع ابتکاری h(n) ----------------

def manhattan(a, b):
    """فاصله منهتن (Manhattan): جمع قدرمطلق اختلاف مختصات."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def euclidean(a, b):
    """فاصله اقلیدسی (Euclidean): فاصله خط مستقیم."""
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def manhattan_x2(a, b):
    """دو برابر منهتن: عمداً بیش‌برآورد می‌کند تا نقش «غیرمجاز» را نشان دهد."""
    return 2 * manhattan(a, b)


HEURISTICS = [
    ("Manhattan", manhattan),
    ("Euclidean", euclidean),
    ("2xManhattan", manhattan_x2),
]


def fmt(x):
    """نمایش خوانای اعداد (بدون اعشار اضافه)."""
    if abs(x - round(x)) < EPS:
        return "%d" % round(x)
    return "%.2f" % x


# ---------------- h*: هزینه واقعی کمینه تا هدف (Dijkstra) ----------------

def true_costs(goal):
    """هزینه واقعی کمینه h*(n) از هر گره تا هدف.

    چون یال‌ها متقارن‌اند، Dijkstra را از هدف اجرا می‌کنیم.
    """
    dist = {goal: 0}
    pq = [(0, goal)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist.get(u, float("inf")):
            continue
        for v, w in neighbors(u):
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist


# ---------------- آزمون‌های مجاز بودن و ثبات ----------------

def is_admissible(h, hstar, node):
    """مجاز بودن در یک گره: h(n) <= h*(n)."""
    return h(node, GOAL) <= hstar[node] + EPS


def is_consistent(h, node):
    """ثبات در یک گره: برای همه همسایه‌ها h(n) <= c(n,v) + h(v)."""
    hn = h(node, GOAL)
    return all(hn <= w + h(v, GOAL) + EPS for v, w in neighbors(node))


# ---------------- Greedy Best-First Search ----------------

def greedy_best_first(start, goal, h):
    """جست‌وجوی حریصانه: صف اولویت فقط با h(n) مرتب می‌شود.

    خروجی: (مسیر، هزینه مسیر، تعداد گره‌های بسط‌یافته)
    """
    counter = 0   # شکستن تساوی‌ها برای ترتیب پایدار
    frontier = [(h(start, goal), counter, start)]
    parent = {start: None}
    g_cost = {start: 0}
    closed = set()
    expanded = 0
    while frontier:
        _, _, u = heapq.heappop(frontier)
        if u in closed:
            continue
        closed.add(u)
        expanded += 1
        if u == goal:
            path = []
            while u is not None:
                path.append(u)
                u = parent[u]
            return path[::-1], g_cost[goal], expanded
        for v, w in neighbors(u):
            if v in closed or v in parent:
                continue
            parent[v] = u
            g_cost[v] = g_cost[u] + w
            counter += 1
            heapq.heappush(frontier, (h(v, goal), counter, v))
    return None, float("inf"), expanded


def path_str(path):
    return " -> ".join("(%d,%d)" % p for p in path)


def main():
    print("=" * 66)
    print("جلسه ۷ — جست‌وجوی آگاهانه: Greedy Best-First و توابع ابتکاری")
    print("=" * 66)
    print_map()

    hstar = true_costs(GOAL)

    # --- جدول ۱: h در برابر h* و آزمون مجاز بودن/ثبات برای هر گره ---
    print("جدول ۱: مقایسه h(n) با h*(n) و آزمون مجاز بودن/ثبات برای هر گره")
    print("وضعیت هر هیوریستیک به‌صورت a/c است: a = مجاز (Admissible)، c = ثابت (Consistent)؛ Y = بله، N = خیر")
    header = "%-7s %4s | %4s %4s %5s | %5s %5s %7s" % (
        "node", "h*", "hM", "hE", "h2x", "M a/c", "E a/c", "2x a/c")
    print(header)
    print("-" * len(header))
    for node in all_nodes():
        cells = [
            "(%d,%d)" % node,
            fmt(hstar[node]),
            fmt(manhattan(node, GOAL)),
            fmt(euclidean(node, GOAL)),
            fmt(manhattan_x2(node, GOAL)),
        ]
        for _, h in HEURISTICS:
            a = "Y" if is_admissible(h, hstar, node) else "N"
            c = "Y" if is_consistent(h, node) else "N"
            cells.append("%s/%s" % (a, c))
        print("%-7s %4s | %4s %4s %5s | %5s %5s %7s" % tuple(cells))
    print()

    # --- جمع‌بندی جدول ۱ ---
    print("جمع‌بندی: کدام هیوریستیک برای همه گره‌ها مجاز/ثابت است؟")
    for name, h in HEURISTICS:
        adm = all(is_admissible(h, hstar, n) for n in all_nodes())
        cons = all(is_consistent(h, n) for n in all_nodes())
        print("  %-12s مجاز: %s   ثابت: %s" % (name, "بله" if adm else "خیر", "بله" if cons else "خیر"))
    print()

    # --- جدول ۲: اجرای Greedy با هر هیوریستیک ---
    print("جدول ۲: اجرای Greedy Best-First با هر هیوریستیک")
    print("%-12s %-36s %5s %9s" % ("heuristic", "path", "cost", "expanded"))
    print("-" * 66)
    for name, h in HEURISTICS:
        path, cost, expanded = greedy_best_first(START, GOAL, h)
        print("%-12s %-36s %5s %9d" % (name, path_str(path), fmt(cost), expanded))
    print()

    print("نتیجه آموزشی:")
    print("- Greedy با Manhattan مسیر گران‌تری (12 در برابر 10) پیدا کرد: Greedy بهینه نیست،")
    print("  حتی وقتی هیوریستیک مجاز است.")
    print("- هیوریستیک 2xManhattan غیرمجاز است (h > h* در چند گره).")
    print("- در جلسه ۸ می‌بینیم A* با h مجاز، مسیر بهینه را تضمین می‌کند.")
    print()
    print("این کد فقط آموزشی است و هیچ کاربرد تشخیصی یا بالینی ندارد.")


if __name__ == "__main__":
    main()
