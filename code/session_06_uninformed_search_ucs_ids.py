# -*- coding: utf-8 -*-
"""جلسه ۶ — UCS و IDDFS روی شبکه انتقال بیمار، با مقایسه BFS.

فقط کتابخانه استاندارد پایتون (heapq، collections، argparse).
وزن هر یال = زمان انتقال بیمار به دقیقه (داده فرضی و صرفاً آموزشی).

اجرا:
    python3 code/session_06_uninformed_search_ucs_ids.py           # خلاصه و جدول مقایسه
    python3 code/session_06_uninformed_search_ucs_ids.py --trace   # ردگیری گام‌به‌گام UCS و IDDFS
    python3 code/session_06_uninformed_search_ucs_ids.py --demo    # مثال‌های تکمیلی جزوه

نکته برای دانشجو: ابتدا فعالیت‌های جزوه را دستی حل کنید و بعد با --trace و --demo
جواب خود را بررسی کنید.

ساختار مرز (Frontier) در هر الگوریتم:
    BFS   -> صف FIFO (collections.deque)
    IDDFS -> پشته LIFO (پشته‌ی فراخوانی‌های بازگشتی در هر تکرار DFS محدود به عمق)
    UCS   -> صف اولویت (heapq) بر اساس هزینه تجمعی g(n)
(DFS خالص در کد جلسه ۵ آمده است و اینجا تکرار نشده.)
"""

import argparse
import heapq
from collections import deque

INF = float("inf")
CUTOFF = "cutoff"  # نشانه‌ی «به حد عمق رسیدیم»؛ با «شکست» (None) فرق دارد

# همان گراف جلسه ۵ (بی‌جهت، وزن‌دار).
# ترتیب همسایه‌ها دقیقاً مطابق جدول بخش ۲ جزوه است؛ ردگیری دستی جزوه به همین ترتیب وابسته است.
GRAPH = {
    "ER":     [("RAD", 4), ("LAB", 2), ("PHARM", 1)],
    "PHARM":  [("ER", 1)],
    "RAD":    [("ER", 4), ("ICU", 5), ("LAB", 3)],
    "LAB":    [("ER", 2), ("RAD", 3), ("OR", 2)],
    "OR":     [("LAB", 2), ("ICU", 1)],
    "ICU":    [("RAD", 5), ("OR", 1), ("WARD_B", 2)],
    "WARD_B": [("ICU", 2)],
}

# گراف جهت‌دار کوچک بخش ۴-۴ جزوه: چرا آزمون هدف باید هنگام «خروج» از صف باشد؟
GRAPH_SABG = {
    "S": [("A", 1), ("B", 2)],
    "A": [("G", 100)],
    "B": [("G", 3)],
    "G": [],
}

# گراف جهت‌دار فعالیت‌های ۱ و ۲ جزوه (کلید پاسخ‌ها با این گراف تولید شده‌اند)
GRAPH_ACTIVITY = {
    "S": [("A", 1), ("B", 4)],
    "A": [("B", 2), ("C", 6)],
    "B": [("C", 1), ("G", 9)],
    "C": [("G", 3)],
    "G": [],
}

FA = {
    "ER": "اورژانس", "RAD": "تصویربرداری", "LAB": "آزمایشگاه",
    "OR": "اتاق عمل", "ICU": "مراقبت ویژه", "WARD_B": "بخش بستری B",
    "PHARM": "داروخانه",
}


# ---------------------------------------------------------------------------
# ابزارهای کمکی
# ---------------------------------------------------------------------------

def reconstruct_path(came_from, goal):
    """مسیر را از هدف به عقب (با جدول والدها) می‌سازد و سپس برعکس می‌کند."""
    node, path = goal, []
    while node is not None:
        path.append(node)
        node = came_from[node]
    path.reverse()
    return path


def path_cost(graph, path):
    """جمع وزن یال‌های مسیر (هزینه واقعی مسیر، مستقل از معیار انتخاب الگوریتم)."""
    cost = 0
    for u, v in zip(path, path[1:]):
        cost += dict(graph[u])[v]
    return cost


def validate_weights(graph):
    """UCS فقط با وزن‌های مثبت درست است (بخش ۴-۵ جزوه)؛ پیش از اجرا بررسی می‌کنیم."""
    for u, nbrs in graph.items():
        for v, w in nbrs:
            if w <= 0:
                raise ValueError(
                    f"یال {u}->{v} وزن {w} دارد؛ UCS فقط با وزن مثبت درست کار می‌کند.")


def with_weight(graph, u, v, w):
    """نسخه‌ی جدیدی از گراف می‌دهد که وزن یال u<->v (هر دو جهت) برابر w است.
    برای تکلیف ۲: وزن یال RAD<->ICU را تغییر دهید بی‌آنکه GRAPH اصلی عوض شود."""
    return {
        n: [(m, w if {n, m} == {u, v} else c) for m, c in nbrs]
        for n, nbrs in graph.items()
    }


# ---------------------------------------------------------------------------
# BFS (برای مقایسه)
# ---------------------------------------------------------------------------

def bfs(graph, start, goal):
    """جست‌وجوی سطح‌اول: صف FIFO، کمترین تعداد گام را می‌یابد.

    وزن‌ها را نمی‌بیند؛ پس مسیر کم‌گام‌ترین است، نه الزاماً ارزان‌ترین.
    """
    frontier = deque([start])   # deque: خروج از ابتدا O(1) است (list.pop(0) برابر O(n) است)
    came_from = {start: None}   # هم والدها را نگه می‌دارد و هم «دیده‌شده‌ها» را
    expansions = 0
    while frontier:
        node = frontier.popleft()   # قدیمی‌ترین گره (FIFO)
        expansions += 1
        if node == goal:
            return reconstruct_path(came_from, goal), expansions
        for nbr, _w in graph.get(node, []):   # وزن _w نادیده گرفته می‌شود
            if nbr not in came_from:
                came_from[nbr] = node
                frontier.append(nbr)
    return None, expansions


# ---------------------------------------------------------------------------
# UCS
# ---------------------------------------------------------------------------

def _frontier_view(frontier, cost_so_far, explored):
    """محتوای «واقعی» صف اولویت را برای چاپ می‌دهد (ورودی‌های کهنه حذف می‌شوند)."""
    live = sorted(
        (c, n) for c, n in frontier
        if n not in explored and c == cost_so_far[n]
    )
    return "، ".join(f"{n}:{c}" for c, n in live) or "—"


def ucs(graph, start, goal, verbose=False):
    """جست‌وجوی هزینه یکنواخت: صف اولویت با heapq، کمترین هزینه را می‌یابد.

    برگشتی: (مسیر، هزینه نهایی، تعداد بسط‌ها).
    اگر verbose=True، جدول گام‌به‌گام بخش ۴-۳ جزوه چاپ می‌شود:
        ✅ گره‌ی جدید وارد صف شد      🔄 مسیر ارزان‌تر پیدا شد و هزینه به‌روز شد
        ❌ مسیر پیدا‌شده بدتر (یا مساوی) است     ⛔ گره قبلاً بسط یافته است
    """
    validate_weights(graph)
    frontier = [(0, start)]          # عنصرها (g, گره)؛ تساوی g با نام گره (الفبایی) حل می‌شود
    came_from = {start: None}
    cost_so_far = {start: 0}         # g(n): بهترین هزینه‌ای که تا اینجا برای n می‌شناسیم
    explored = set()                 # گره‌های بسط‌یافته؛ فقط برای برچسب‌گذاری چاپ لازم است
    expansions = 0
    if verbose:
        print(f"  وضعیت اولیه: صف = [{start}:0]")
    while frontier:
        cost, node = heapq.heappop(frontier)   # ارزان‌ترین گره‌ی مرز
        if cost > cost_so_far.get(node, INF):
            continue  # ورودی کهنه: بعداً مسیر ارزان‌تری به این گره پیدا شده بود
        expansions += 1
        explored.add(node)
        if verbose:
            print(f"  گام {expansions}: خروج از صف → {node} (g={cost})")
        if node == goal:
            # آزمون هدف هنگام «خروج» از صف است، نه هنگام ورود (بخش ۴-۴ جزوه)
            if verbose:
                print("      🎯 هدف! آزمون هدف هنگام خروج از صف برقرار شد.")
            return reconstruct_path(came_from, goal), cost, expansions
        for nbr, w in graph.get(node, []):
            new_cost = cost + w
            old_cost = cost_so_far.get(nbr)
            if old_cost is None or new_cost < old_cost:
                if verbose:
                    tag = "✅ جدید" if old_cost is None else f"🔄 بهتر از {old_cost}"
                    print(f"      {nbr}: {cost}+{w}={new_cost} {tag}")
                cost_so_far[nbr] = new_cost
                came_from[nbr] = node
                # heapq عملیات «کاهش کلید» ندارد؛ ورودی جدید می‌گذاریم و ورودی کهنه
                # را هنگام خروج (شرط بالا) نادیده می‌گیریم.
                heapq.heappush(frontier, (new_cost, nbr))
            elif verbose:
                tag = "⛔ بسط‌یافته" if nbr in explored else f"❌ بدتر یا مساوی ({old_cost})"
                print(f"      {nbr}: {cost}+{w}={new_cost} {tag}")
        if verbose:
            print(f"      صف پس از گام: {_frontier_view(frontier, cost_so_far, explored)}")
    return None, INF, expansions


def ucs_wrong_goal_test(graph, start, goal):
    """⚠️ نسخه‌ی عمداً غلط فقط برای نمایش: آزمون هدف هنگام «ورود» به صف انجام می‌شود.

    در گراف S-A-B-G جزوه، هدف را با هزینه‌ی ۱۰۱ می‌پذیرد در حالی که پاسخ بهینه ۵ است.
    هرگز این‌گونه UCS را پیاده‌سازی نکنید.
    """
    if start == goal:
        return [start], 0
    frontier = [(0, start)]
    came_from = {start: None}
    cost_so_far = {start: 0}
    while frontier:
        cost, node = heapq.heappop(frontier)
        if cost > cost_so_far.get(node, INF):
            continue
        for nbr, w in graph.get(node, []):
            new_cost = cost + w
            if new_cost < cost_so_far.get(nbr, INF):
                cost_so_far[nbr] = new_cost
                came_from[nbr] = node
                if nbr == goal:            # ❌ اشتباه: گره هنوز از صف خارج نشده است
                    return reconstruct_path(came_from, goal), new_cost
                heapq.heappush(frontier, (new_cost, nbr))
    return None, INF


# ---------------------------------------------------------------------------
# IDDFS
# ---------------------------------------------------------------------------

def dls(graph, node, goal, depth, path, counter, log=None):
    """جست‌وجوی محدود به عمق (بازگشتی؛ پشته‌ی فراخوانی‌ها همان پشته LIFO است).

    depth : عمق باقی‌مانده تا حد L
    path  : نیاکان گره فعلی (گره فعلی داخل آن نیست)؛ هم برای ساختن مسیر و هم برای
            جلوگیری از چرخه روی مسیر فعلی
    counter : counter[0] تعداد «دیده‌شدن»ها؛ هر فراخوانی یک واحد (شامل گره‌های مرزِ حد عمق)
    log   : اگر لیست باشد، ترتیب دیده شدن را به شکل «گره(عمق)» ثبت می‌کند
            (⛔ = رسید به حد عمق، 🎯 = هدف)

    سه نتیجه‌ی ممکن (مثل شبه‌کد جزوه):
        لیست مسیر  -> هدف پیدا شد
        CUTOFF     -> حداقل یک‌بار به حد عمق خوردیم؛ شاید با حد بزرگ‌تر جواب پیدا شود
        None       -> «شکست»: کل درخت گشته شد و هدفی نیست
    """
    counter[0] += 1
    level = len(path)  # عمق گره فعلی نسبت به ریشه
    if node == goal:
        if log is not None:
            log.append(f"{node}({level})🎯")
        return path + [node]
    if depth == 0:
        if log is not None:
            log.append(f"{node}({level})⛔")
        return CUTOFF
    if log is not None:
        log.append(f"{node}({level})")
    cutoff_occurred = False
    for nbr, _w in graph.get(node, []):   # وزن‌ها نادیده گرفته می‌شوند
        if nbr in path:  # جلوگیری از چرخه در همان شاخه
            continue
        result = dls(graph, nbr, goal, depth - 1, path + [node], counter, log)
        if result is CUTOFF:
            cutoff_occurred = True
        elif result is not None:
            return result  # مسیر پیدا شد
    return CUTOFF if cutoff_occurred else None


def iddfs(graph, start, goal, max_depth=10, verbose=False):
    """تکثیر عمق: اجرای مکرر جست‌وجوی محدود با حد عمق ۰، ۱، ۲، ... تا max_depth.

    برگشتی: (مسیر، تعداد دیده‌شدن‌ها). اگر verbose=True، جدول تکرارهای بخش ۳-۳ چاپ می‌شود.
    اولین حد موفق = عمق کم‌عمق‌ترین هدف؛ پس مسیر کم‌گام‌ترین است (نه الزاماً ارزان‌ترین).
    """
    counter = [0]
    for limit in range(max_depth + 1):
        before = counter[0]
        log = [] if verbose else None
        result = dls(graph, start, goal, limit, [], counter, log)
        if verbose:
            print(f"  حد L={limit}: " + "، ".join(log)
                  + f"   ← {counter[0] - before} بار دیده شد")
        if result is None:          # شکست واقعی: کل درخت گشته شد، هدفی نیست
            return None, counter[0]
        if result is not CUTOFF:    # مسیر پیدا شد
            return result, counter[0]
    return None, counter[0]


# ---------------------------------------------------------------------------
# شمارش نظری گره‌ها (بخش ۳-۴ جزوه)
# ---------------------------------------------------------------------------

def bfs_node_count(b, d):
    """تعداد گره‌های درخت کامل تا عمق d: 1 + b + b^2 + ... + b^d"""
    return sum(b ** k for k in range(d + 1))


def iddfs_node_count(b, d):
    """(d+1) + b*d + b^2*(d-1) + ... + b^d: سطح k ام، (d-k+1) بار ساخته می‌شود."""
    return sum((d - k + 1) * b ** k for k in range(d + 1))


# ---------------------------------------------------------------------------
# چاپ نتایج
# ---------------------------------------------------------------------------

def section(title):
    print("=" * 56)
    print(title)
    print("=" * 56)


def compare_table(graph, start, goal):
    """BFS، IDDFS و UCS را روی یک گراف اجرا و کنار هم چاپ می‌کند (جدول مقایسه جزوه)."""
    b_path, b_exp = bfs(graph, start, goal)
    i_path, i_exp = iddfs(graph, start, goal)
    u_path, _u_cost, u_exp = ucs(graph, start, goal)
    print(f"{'روش':<6}| {'هزینه':<6}| {'گام':<4}| {'بسط':<4}| مسیر")
    for name, path, exp in (("BFS", b_path, b_exp), ("IDDFS", i_path, i_exp),
                            ("UCS", u_path, u_exp)):
        print(f"{name:<6}| {path_cost(graph, path):<6}| {len(path) - 1:<4}| {exp:<4}| "
              + " -> ".join(path))


def demo_extra():
    """مثال‌های تکمیلی جزوه: آزمون هدف، گراف فعالیت‌ها و سربار تکرار IDDFS."""
    section("۱) چرا آزمون هدف هنگام خروج از صف؟ (گراف S-A-B-G)")
    path, cost = ucs_wrong_goal_test(GRAPH_SABG, "S", "G")
    print("  آزمون هدف هنگام ورود (غلط):", " -> ".join(path), "| هزینه =", cost)
    path, cost, exp = ucs(GRAPH_SABG, "S", "G", verbose=True)
    print("  آزمون هدف هنگام خروج (درست):", " -> ".join(path), "| هزینه =", cost)

    section("۲) گراف فعالیت‌های ۱ و ۲ (کلید پاسخ)")
    print("UCS گام‌به‌گام (فعالیت ۱):")
    ucs(GRAPH_ACTIVITY, "S", "G", verbose=True)
    print("IDDFS گام‌به‌گام (فعالیت ۲)، به ترتیب همسایه‌های تعریف‌شده در گراف:")
    iddfs(GRAPH_ACTIVITY, "S", "G", verbose=True)
    print("مقایسه:")
    compare_table(GRAPH_ACTIVITY, "S", "G")

    section("۳) سربار تکرار IDDFS در درخت کامل")
    print(f"{'b':<4}{'d':<4}{'BFS':>10}{'IDDFS':>10}{'نسبت':>8}")
    for b, d in ((2, 5), (10, 5), (4, 3)):
        n_bfs, n_ids = bfs_node_count(b, d), iddfs_node_count(b, d)
        print(f"{b:<4}{d:<4}{n_bfs:>10}{n_ids:>10}{n_ids / n_bfs:>8.2f}")
    print("هرچه b بزرگ‌تر، سربار نسبی کمتر؛ ولی حافظه‌ی IDDFS همیشه O(b*d) است.")


def main():
    parser = argparse.ArgumentParser(description="UCS و IDDFS روی شبکه انتقال بیمار")
    parser.add_argument("--trace", action="store_true",
                        help="ردگیری گام‌به‌گام UCS و IDDFS روی گراف بیمارستان")
    parser.add_argument("--demo", action="store_true",
                        help="مثال‌های تکمیلی جزوه (آزمون هدف، گراف فعالیت‌ها، سربار IDDFS)")
    args = parser.parse_args()

    start, goal = "ER", "WARD_B"
    print("مسئله: انتقال بیمار از", FA[start], "به", FA[goal])
    print("-" * 40)

    path, cost, exp = ucs(GRAPH, start, goal)
    if path is None:
        print("UCS : مسیری یافت نشد")
    else:
        print("UCS :")
        print("  مسیر :", " -> ".join(path))
        print("  هزینه نهایی (دقیقه) :", cost)
        print("  گره‌های بسط‌داده‌شده :", exp)
    print("-" * 40)

    path, exp = iddfs(GRAPH, start, goal)
    if path is None:
        print("IDDFS : مسیری یافت نشد")
    else:
        print("IDDFS :")
        print("  مسیر :", " -> ".join(path))
        print("  تعداد گام :", len(path) - 1)
        print("  هزینه مسیر (دقیقه) :", path_cost(GRAPH, path))
        print("  گره‌های بسط‌داده‌شده (همه‌ی فراخوانی‌ها، شامل مرز حد عمق) :", exp)
    print("-" * 40)

    path, exp = bfs(GRAPH, start, goal)
    if path is None:
        print("BFS : مسیری یافت نشد")
    else:
        print("BFS :")
        print("  مسیر :", " -> ".join(path))
        print("  تعداد گام :", len(path) - 1)
        print("  هزینه مسیر (دقیقه) :", path_cost(GRAPH, path))
        print("  گره‌های بسط‌داده‌شده :", exp)
    print("-" * 40)

    print("جدول مقایسه (عدد بسط IDDFS با BFS و UCS هم‌معیار نیست؛ فقط مرتبه‌ی بزرگی):")
    compare_table(GRAPH, start, goal)
    print("-" * 40)

    print("نتیجه: UCS کمترین هزینه را تضمین می‌کند؛ BFS و IDDFS کمترین تعداد گام را.")
    print("IDDFS حافظه‌ی کم مصرف می‌کند ولی گره‌ها را چند بار بسط می‌دهد.")

    if args.trace:
        print()
        section("ردگیری UCS (جدول بخش ۴-۳ جزوه)")
        ucs(GRAPH, start, goal, verbose=True)
        print()
        section("ردگیری IDDFS (جدول بخش ۳-۳ جزوه)")
        iddfs(GRAPH, start, goal, verbose=True)

    if args.demo:
        print()
        demo_extra()

    # تکلیف ۲: وزن یال RAD<->ICU را از ۵ به ۱ تغییر دهید و نتیجه را پیش‌بینی و بررسی کنید.
    # دو خط زیر را از حالت کامنت خارج کنید:
    # GRAPH2 = with_weight(GRAPH, "RAD", "ICU", 1)
    # print(ucs(GRAPH2, start, goal))


if __name__ == "__main__":
    main()
