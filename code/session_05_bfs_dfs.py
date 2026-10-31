# -*- coding: utf-8 -*-
"""جلسه ۵ — BFS و DFS روی شبکه انتقال بیمار بین بخش‌های بیمارستان.

فقط کتابخانه استاندارد پایتون (collections.deque, argparse, copy).
وزن هر یال = زمان انتقال بیمار به دقیقه (داده فرضی و صرفاً آموزشی).

اجرا:
    python3 session_05_bfs_dfs.py                 # خروجی خلاصه (مسیر، گام، هزینه، بسط‌ها)
    python3 session_05_bfs_dfs.py --trace         # جدول گام‌به‌گام: دیده‌شده‌ها + صف/پشته
    python3 session_05_bfs_dfs.py --reverse-er    # ترتیب همسایه‌های ER معکوس (مثال تکمیلی بخش ۴)
    python3 session_05_bfs_dfs.py --maze          # ماز فعالیت ۱
    python3 session_05_bfs_dfs.py --drop-or-icu   # فعالیت ۳: حذف یال OR-ICU

قراردادها (مطابق جزوه):
  * گره هنگام ورود به مرز «دیده‌شده» علامت می‌خورد (کلید came_from).
  * آزمون هدف هنگام خروج گره از مرز انجام می‌شود.
  * «گره‌های بسط‌داده‌شده» = گره‌های خارج‌شده از مرز، شامل گره هدف.
"""

import argparse
import copy
from collections import deque

# گراف شبکه انتقال بیمار (بی‌جهت، وزن‌دار)
GRAPH = {
    "ER":     [("RAD", 4), ("LAB", 2), ("PHARM", 1)],
    "PHARM":  [("ER", 1)],
    "RAD":    [("ER", 4), ("ICU", 5), ("LAB", 3)],
    "LAB":    [("ER", 2), ("RAD", 3), ("OR", 2)],
    "OR":     [("LAB", 2), ("ICU", 1)],
    "ICU":    [("RAD", 5), ("OR", 1), ("WARD_B", 2)],
    "WARD_B": [("ICU", 2)],
}

FA = {
    "ER": "اورژانس", "RAD": "تصویربرداری", "LAB": "آزمایشگاه",
    "OR": "اتاق عمل", "ICU": "مراقبت ویژه", "WARD_B": "بخش بستری B",
    "PHARM": "داروخانه",
}

# ماز فعالیت ۱ (S شروع، G هدف، X راهروی بسته)
MAZE = [
    "S.X",
    ".X.",
    "..G",
]


def build_maze_graph(maze):
    """تبدیل ماز به گراف با وزن ۱؛ ترتیب همسایه‌ها: راست، پایین، چپ، بالا."""
    graph, start, goal = {}, None, None
    rows, cols = len(maze), len(maze[0])
    for r in range(rows):
        for c in range(cols):
            if maze[r][c] == "X":
                continue
            name = f"({r + 1},{c + 1})"
            if maze[r][c] == "S":
                start = name
            if maze[r][c] == "G":
                goal = name
            nbrs = []
            for dr, dc in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                rr, cc = r + dr, c + dc
                if 0 <= rr < rows and 0 <= cc < cols and maze[rr][cc] != "X":
                    nbrs.append((f"({rr + 1},{cc + 1})", 1))
            graph[name] = nbrs
    return graph, start, goal


def reconstruct_path(came_from, goal):
    """بازسازی مسیر از دیکشنری والد‌ها."""
    node, path = goal, []
    while node is not None:
        path.append(node)
        node = came_from[node]
    path.reverse()
    return path


def path_cost(graph, path):
    """جمع وزن یال‌های مسیر (زمان انتقال)."""
    cost = 0
    for u, v in zip(path, path[1:]):
        cost += dict(graph[u])[v]
    return cost


# ---------------------------------------------------------------- ردگیری گام‌به‌گام

def _step_header(step, node, new, push_word, is_goal):
    if step == 0:
        return "گام 0 | شروع"
    head = f"گام {step} | خروج: {node}"
    if is_goal:
        return head + "  ✔ هدف"
    new_txt = ", ".join(new) if new else "—"
    return f"{head} | فرزندان جدید{push_word}: {new_txt}"


def _trace_bfs(step, node, came_from, queue, new=(), is_goal=False):
    print(_step_header(step, node, new, "", is_goal))
    print("   دیده‌شده‌ها :", ", ".join(came_from))        # افقی، به ترتیب کشف
    print("   صف (چپ = سر صف) : [" + ", ".join(queue) + "]")  # افقی


def _trace_dfs(step, node, came_from, stack, new=(), is_goal=False):
    print(_step_header(step, node, new, " (ترتیب push)", is_goal))
    print("   دیده‌شده‌ها :", ", ".join(came_from))        # افقی، به ترتیب کشف
    print("   پشته (بالا = سر پشته) :")                    # عمودی
    width = max([len(x) for x in stack] + [1])
    for i, item in enumerate(reversed(stack)):
        print("      | " + item.ljust(width) + " |" + ("  <- top" if i == 0 else ""))
    print("      +-" + "-" * width + "-+")


# ---------------------------------------------------------------- الگوریتم‌ها

def bfs(graph, start, goal, trace=False):
    """جست‌وجوی سطح‌اول: صف FIFO، کمترین تعداد گام را می‌یابد."""
    frontier = deque([start])
    came_from = {start: None}
    expansions = 0
    step, max_frontier = 0, 1
    if trace:
        print("=== BFS (صف) ===")
        _trace_bfs(0, None, came_from, frontier)
    while frontier:
        node = frontier.popleft()
        expansions += 1
        step += 1
        if node == goal:
            if trace:
                _trace_bfs(step, node, came_from, frontier, is_goal=True)
                print(f"   بیشینه اندازه مرز : {max_frontier}")
            return reconstruct_path(came_from, goal), expansions
        new = []
        for nbr, _w in graph.get(node, []):
            if nbr not in came_from:
                came_from[nbr] = node
                frontier.append(nbr)
                new.append(nbr)
        max_frontier = max(max_frontier, len(frontier))
        if trace:
            _trace_bfs(step, node, came_from, frontier, new)
    return None, expansions


def dfs(graph, start, goal, trace=False):
    """جست‌وجوی عمق‌اول: پشته LIFO، یک شاخه را تا انتها می‌رود."""
    stack = [start]
    came_from = {start: None}
    expansions = 0
    step, max_frontier = 0, 1
    if trace:
        print("=== DFS (پشته) ===")
        _trace_dfs(0, None, came_from, stack)
    while stack:
        node = stack.pop()
        expansions += 1
        step += 1
        if node == goal:
            if trace:
                _trace_dfs(step, node, came_from, stack, is_goal=True)
                print(f"   بیشینه اندازه مرز : {max_frontier}")
            return reconstruct_path(came_from, goal), expansions
        new = []
        for nbr, _w in graph.get(node, []):
            if nbr not in came_from:
                came_from[nbr] = node
                stack.append(nbr)
                new.append(nbr)
        max_frontier = max(max_frontier, len(stack))
        if trace:
            _trace_dfs(step, node, came_from, stack, new)
    return None, expansions


def describe(graph, title, path, expansions):
    if path is None:
        print(title, ": مسیری یافت نشد")
        return
    print(title, ":")
    print("  مسیر :", " -> ".join(path))
    print("  تعداد گام :", len(path) - 1)
    print("  هزینه مسیر (دقیقه) :", path_cost(graph, path))
    print("  گره‌های بسط‌داده‌شده (شامل هدف) :", expansions)


def parse_args():
    p = argparse.ArgumentParser(description="BFS و DFS — جلسه ۵")
    p.add_argument("--trace", action="store_true",
                   help="چاپ جدول گام‌به‌گام (دیده‌شده‌ها و صف/پشته)")
    p.add_argument("--maze", action="store_true", help="اجرای ماز فعالیت ۱")
    p.add_argument("--reverse-er", action="store_true",
                   help="معکوس کردن ترتیب همسایه‌های ER")
    p.add_argument("--drop-or-icu", action="store_true",
                   help="حذف یال OR-ICU (فعالیت ۳)")
    return p.parse_args()


def main():
    args = parse_args()

    if args.maze:
        graph, start, goal = build_maze_graph(MAZE)
        print("ماز فعالیت ۱: از", start, "به", goal)
    else:
        graph = copy.deepcopy(GRAPH)
        if args.reverse_er:
            graph["ER"] = graph["ER"][::-1]
        if args.drop_or_icu:
            graph["OR"] = [(n, w) for n, w in graph["OR"] if n != "ICU"]
            graph["ICU"] = [(n, w) for n, w in graph["ICU"] if n != "OR"]
        start, goal = "ER", "WARD_B"
        print("مسئله: انتقال بیمار از", FA[start], "به", FA[goal])
    print("-" * 40)

    path, exp = bfs(graph, start, goal, trace=args.trace)
    if args.trace:
        print()
    describe(graph, "BFS", path, exp)
    print("-" * 40)

    path, exp = dfs(graph, start, goal, trace=args.trace)
    if args.trace:
        print()
    describe(graph, "DFS", path, exp)
    print("-" * 40)

    print("نکته: BFS کمترین تعداد گام را می‌یابد ولی وزن‌ها را نمی‌بیند.")
    print("DFS به ترتیب همسایه‌ها وابسته است و هیچ تضمینی برای مسیر بهینه ندارد.")
    print("BFS و DFS فقط از وجود یال استفاده می‌کنند؛ وزن‌ها فقط در محاسبه هزینه مسیر به‌کار رفتند.")


if __name__ == "__main__":
    main()
