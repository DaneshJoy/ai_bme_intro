# -*- coding: utf-8 -*-
"""کارگاه جست‌وجو — جلسه ۹

مقایسه چهار الگوریتم جست‌وجو (BFS، DFS، UCS و A*) روی «یک» گراف مشترک:
مسیریابی در یک بیمارستان از «ورودی» (S) تا «آزمایشگاه» (G).

اجرا:
    python3 code/session_09_search_workshop.py

فقط از کتابخانه استاندارد پایتون استفاده می‌شود (بدون وابستگی خارجی).
"""

from collections import deque
import heapq
import itertools
import time

# --------------------------------------------------------------- گراف مسئله
# گره‌ها بخش‌های بیمارستان‌اند و وزن هر یال، فاصله تقریبی راهرو (متر) است.
#   S: ورودی اصلی      A: پذیرش        B: رادیولوژی
#   C: داروخانه        D: آزمایش خون   E: مراقبت ویژه (ICU)
#   F: راهرو شرقی      G: آزمایشگاه    H: انبار (بن‌بست)   I: نمازخانه (بن‌بست)
GRAPH = {
    "S": {"A": 2, "B": 5},
    "A": {"S": 2, "C": 4, "D": 7, "H": 4},
    "B": {"S": 5, "D": 3, "E": 6, "I": 2},
    "C": {"A": 4, "F": 3},
    "D": {"A": 7, "B": 3, "F": 2, "G": 4},
    "E": {"B": 6, "G": 7},
    "F": {"C": 3, "D": 2, "G": 7},
    "G": {"D": 4, "E": 7, "F": 7},
    "H": {"A": 4},
    "I": {"B": 2},
}
START, GOAL = "S", "G"

# برآورد هیوریستیک (h) فاصله تا G برای A* — مجاز (Admissible) و سازگار (Consistent)
HEURISTIC = {
    "S": 9, "A": 7, "B": 6, "C": 7, "D": 4,
    "E": 7, "F": 5, "G": 0, "H": 11, "I": 8,
}


# ----------------------------------------------------------- توابع کمکی
def reconstruct(came_from, node):
    """بازسازی مسیر از دیکشنری والد‌ها."""
    path = []
    while node is not None:
        path.append(node)
        node = came_from[node]
    return path[::-1]


def path_cost(path, graph):
    """هزینه کل مسیر از روی وزن یال‌ها."""
    return sum(graph[a][b] for a, b in zip(path, path[1:]))


# ------------------------------------------------------- چهار الگوریتم
def bfs(graph, start, goal):
    """جست‌وجوی اول-سطح (Breadth-First Search) با صف؛ کم‌یال‌ترین مسیر را می‌دهد."""
    frontier = deque([start])
    came_from = {start: None}
    expanded = 0
    while frontier:
        node = frontier.popleft()
        if node == goal:
            return reconstruct(came_from, node), expanded
        expanded += 1
        for nxt in sorted(graph[node]):
            if nxt not in came_from:
                came_from[nxt] = node
                frontier.append(nxt)
    return None, expanded


def dfs(graph, start, goal):
    """جست‌وجوی اول-عمق (Depth-First Search) با پشته؛ مسیر تضمیناً بهینه نیست."""
    frontier = [start]
    came_from = {start: None}
    expanded = 0
    while frontier:
        node = frontier.pop()
        if node == goal:
            return reconstruct(came_from, node), expanded
        expanded += 1
        # معکوس push می‌کنیم تا همسایه الفبایی کوچک‌تر روی پشته و زودتر pop شود
        for nxt in sorted(graph[node], reverse=True):
            if nxt not in came_from:
                came_from[nxt] = node
                frontier.append(nxt)
    return None, expanded


def ucs(graph, start, goal):
    """جست‌وجوی یکنواخت هزینه (Uniform-Cost Search) با پشته اولویت؛ بهینه."""
    counter = itertools.count()  # برای شکستن تساوی‌ها به‌صورت قطعی
    frontier = [(0, next(counter), start)]
    best_g = {start: 0}
    came_from = {start: None}
    expanded = 0
    while frontier:
        g, _, node = heapq.heappop(frontier)
        if g > best_g.get(node, float("inf")):  # ورودی کهنه؛ نادیده بگیر
            continue
        if node == goal:
            return reconstruct(came_from, node), expanded
        expanded += 1
        for nxt, w in sorted(graph[node].items()):
            new_g = g + w
            if new_g < best_g.get(nxt, float("inf")):
                best_g[nxt] = new_g
                came_from[nxt] = node
                heapq.heappush(frontier, (new_g, next(counter), nxt))
    return None, expanded


def a_star(graph, start, goal, heuristic):
    """جست‌وجوی A*: UCS + هیوریستیک؛ با h مجاز، مسیر بهینه را با بسط کمتر می‌یابد."""
    counter = itertools.count()
    frontier = [(heuristic[start], next(counter), start)]
    best_g = {start: 0}
    came_from = {start: None}
    expanded = 0
    while frontier:
        f, _, node = heapq.heappop(frontier)
        g = best_g.get(node, float("inf"))
        if f - heuristic[node] > g:  # ورودی کهنه؛ نادیده بگیر
            continue
        if node == goal:
            return reconstruct(came_from, node), expanded
        expanded += 1
        for nxt, w in sorted(graph[node].items()):
            new_g = g + w
            if new_g < best_g.get(nxt, float("inf")):
                best_g[nxt] = new_g
                came_from[nxt] = node
                heapq.heappush(frontier, (new_g + heuristic[nxt], next(counter), nxt))
    return None, expanded


# --------------------------------------------------------------- اجرا و جدول
def main():
    algorithms = [
        ("BFS", lambda: bfs(GRAPH, START, GOAL)),
        ("DFS", lambda: dfs(GRAPH, START, GOAL)),
        ("UCS", lambda: ucs(GRAPH, START, GOAL)),
        ("A*", lambda: a_star(GRAPH, START, GOAL, HEURISTIC)),
    ]

    print("مسئله: مسیریابی از ورودی (S) تا آزمایشگاه (G) در گراف بیمارستان")
    print("هزینه = مجموع فاصله‌ها به متر؛ Expanded = تعداد گره‌های بسط‌داده‌شده")
    print()
    header = "{:<10}{:<22}{:>6}{:>6}{:>10}{:>12}".format(
        "Algorithm", "Path", "Edges", "Cost", "Expanded", "Time(ms)")
    print(header)
    print("-" * len(header))
    for name, run in algorithms:
        t0 = time.perf_counter()
        path, expanded = run()
        elapsed_ms = (time.perf_counter() - t0) * 1000
        shown = " -> ".join(path) if path else "not found"
        edges = len(path) - 1 if path else "-"
        cost = path_cost(path, GRAPH) if path else "-"
        print("{:<10}{:<22}{:>6}{:>6}{:>10}{:>12.3f}".format(
            name, shown, edges, cost, expanded, elapsed_ms))

    print()
    print("نکته‌ها:")
    print("1) BFS مسیر کم‌یال می‌دهد اما هزینه بهینه نیست (وزن یال‌ها را نمی‌بیند).")
    print("2) DFS سریع به هدف می‌رسد ولی مسیرش تضمینی بهینه نیست.")
    print("3) UCS مسیر بهینه را پیدا می‌کند اما تقریباً همه گره‌ها را بسط می‌دهد.")
    print("4) A* با هیوریستیک مجاز، همان مسیر بهینه را با بسط خیلی کمتر پیدا می‌کند.")
    print("   (زمان‌ها به سخت‌افزار بستگی دارند و برای این گراف کوچک معنادار نیستند.)")


if __name__ == "__main__":
    main()