# -*- coding: utf-8 -*-
"""جلسه ۱۵ — جست‌وجوی مقابله‌ای: Minimax و هرس آلفا–بتا روی Tic-Tac-Toe

سناریوی آموزشی: بازی ساده دوز (Tic-Tac-Toe) روی صفحه ۳×۳
- بازیکن X (ماکسی‌میزر، اول شروع می‌کند) و بازیکن O (مینی‌میزر).
- امتیاز حالت پایانی: برد X = +1 ، برد O = -1 ، مساوی = 0.
- Minimax گره‌به‌گره همه درخت بازی را بررسی می‌کند.
- Alpha-Beta با هرس کردن شاخه‌های بی‌اثر همان مقدار بهینه را با گره کمتر می‌یابد.

این اسکریپت سه کار می‌کند:
1) هر دو الگوریتم را از صفحه خالی اجرا می‌کند و مقدار بهینه بازی را حساب می‌کند.
2) تعداد گره‌های ارزیابی‌شده در هر الگوریتم را می‌شمارد و کاهش را نشان می‌دهد.
3) بهترین حرکت اول X را گزارش می‌کند (هر دو الگوریتم باید یکی باشند).

فقط از کتابخانه استاندارد پایتون استفاده می‌شود؛ خروجی قطعی (Deterministic) است.
کد آموزشی است و هیچ کاربرد تشخیصی یا بالینی ندارد.
"""

# ---------------- صفحه بازی ----------------

# خانه‌ها با اندیس ۰ تا ۸ (سطر اول از چپ):
#  0 | 1 | 2
#  ---------
#  3 | 4 | 5
#  ---------
#  6 | 7 | 8

WIN_LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),      # سطرها
    (0, 3, 6), (1, 4, 7), (2, 5, 8),      # ستون‌ها
    (0, 4, 8), (2, 4, 6),                 # قطرها
)

MAX_PLAYER = "X"     # ماکسی‌میزر (شروع‌کننده)
MIN_PLAYER = "O"     # مینی‌میزر
EMPTY = " "


def print_board(board):
    """چاپ صفحه با اندیس‌ها برای خوانایی."""
    symbols = []
    for i, cell in enumerate(board):
        symbols.append(cell if cell != EMPTY else ".")
    print("  " + symbols[0] + " | " + symbols[1] + " | " + symbols[2])
    print(" ---+---+---")
    print("  " + symbols[3] + " | " + symbols[4] + " | " + symbols[5])
    print(" ---+---+---")
    print("  " + symbols[6] + " | " + symbols[7] + " | " + symbols[8])
    print()


def winner(board):
    """برنده را برمی‌گرداند ('X' یا 'O') یا None."""
    for (a, b, c) in WIN_LINES:
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return board[a]
    return None


def is_terminal(board):
    """آیا بازی تمام شده؟ (برد یکی یا پر شدن صفحه)."""
    return winner(board) is not None or EMPTY not in board


def utility(board):
    """تابع سود حالت پایانی: +1 برد X ، -1 برد O ، 0 مساوی."""
    w = winner(board)
    if w == MAX_PLAYER:
        return 1
    if w == MIN_PLAYER:
        return -1
    return 0


def legal_moves(board):
    """لیست اندیس‌های خالی به ترتیب صعودی (قطعی)."""
    return [i for i, cell in enumerate(board) if cell == EMPTY]


# ---------------- Minimax کامل ----------------

def minimax(board, player, counter):
    """Minimax کلاسیک؛ تعداد گره‌های ارزیابی‌شده را در counter جمع می‌کند."""
    counter[0] += 1
    if is_terminal(board):
        return utility(board)
    moves = legal_moves(board)
    if player == MAX_PLAYER:
        best = -2
        for move in moves:
            board[move] = MAX_PLAYER
            value = minimax(board, MIN_PLAYER, counter)
            board[move] = EMPTY
            if value > best:
                best = value
        return best
    else:
        best = 2
        for move in moves:
            board[move] = MIN_PLAYER
            value = minimax(board, MAX_PLAYER, counter)
            board[move] = EMPTY
            if value < best:
                best = value
        return best


def minimax_best_move(board, player, counter):
    """بهترین حرکت برای player با Minimax؛ بر اساس ترتیب اندیس‌ها اولین گزینه بهینه."""
    counter[0] += 1
    moves = legal_moves(board)
    best_value = -2 if player == MAX_PLAYER else 2
    best_move = None
    for move in moves:
        board[move] = player
        if player == MAX_PLAYER:
            value = minimax(board, MIN_PLAYER, counter)
        else:
            value = minimax(board, MAX_PLAYER, counter)
        board[move] = EMPTY
        if player == MAX_PLAYER:
            if value > best_value:
                best_value, best_move = value, move
        else:
            if value < best_value:
                best_value, best_move = value, move
    return best_move, best_value


# ---------------- Alpha-Beta ----------------

def alpha_beta(board, player, alpha, beta, counter):
    """Minimax با هرس آلفا–بتا؛ alpha = بدترین حد پایین X ، beta = بدترین حد بالای O."""
    counter[0] += 1
    if is_terminal(board):
        return utility(board)
    moves = legal_moves(board)
    if player == MAX_PLAYER:
        value = -2
        for move in moves:
            board[move] = MAX_PLAYER
            child = alpha_beta(board, MIN_PLAYER, alpha, beta, counter)
            board[move] = EMPTY
            if child > value:
                value = child
            if value > alpha:
                alpha = value
            if alpha >= beta:      # هرس: حداکثرگره، حد بالای مینی‌میزر را زد
                break
        return value
    else:
        value = 2
        for move in moves:
            board[move] = MIN_PLAYER
            child = alpha_beta(board, MAX_PLAYER, alpha, beta, counter)
            board[move] = EMPTY
            if child < value:
                value = child
            if value < beta:
                beta = value
            if alpha >= beta:      # هرس: حد پایین ماکسی‌میزر را زد
                break
        return value


def alpha_beta_best_move(board, player, counter):
    """بهترین حرکت برای player با Alpha-Beta (بدون هرس در سطح حرکت اول)."""
    counter[0] += 1
    moves = legal_moves(board)
    best_value = -2 if player == MAX_PLAYER else 2
    best_move = None
    alpha, beta = -2, 2
    for move in moves:
        board[move] = player
        if player == MAX_PLAYER:
            value = alpha_beta(board, MIN_PLAYER, alpha, beta, counter)
            if value > best_value:
                best_value, best_move = value, move
            if best_value > alpha:
                alpha = best_value
        else:
            value = alpha_beta(board, MAX_PLAYER, alpha, beta, counter)
            if value < best_value:
                best_value, best_move = value, move
            if best_value < beta:
                beta = best_value
        board[move] = EMPTY
    return best_move, best_value


# ---------------- اجرا و مقایسه ----------------

def describe_move(move):
    """اندیس حرکت را به سطر/ستون خوانا تبدیل می‌کند (سطر و ستون از ۱)."""
    r, c = divmod(move, 3)
    return "سطر %d ، ستون %d (اندیس %d)" % (r + 1, c + 1, move)


def main():
    board = [EMPTY] * 9

    print("=" * 62)
    print("Minimax در برابر Alpha-Beta روی Tic-Tac-Toe (از صفحه خالی)")
    print("=" * 62)
    print("توضیح امتیاز: برد X = +1 ، برد O = -1 ، مساوی = 0")
    print_board(board)

    # --- Minimax کامل ---
    mm_counter = [0]
    mm_value = minimax(board, MAX_PLAYER, mm_counter)
    mm_move_counter = [0]
    mm_move, mm_best_value = minimax_best_move(board, MAX_PLAYER, mm_move_counter)

    # --- Alpha-Beta ---
    ab_counter = [0]
    ab_value = alpha_beta(board, MAX_PLAYER, -2, 2, ab_counter)
    ab_move_counter = [0]
    ab_move, ab_best_value = alpha_beta_best_move(board, MAX_PLAYER, ab_move_counter)

    print("---- نتایج ----")
    print("مقدار بهینه بازی (Minimax):  %+d" % mm_value)
    print("مقدار بهینه بازی (Alpha-Beta): %+d" % ab_value)
    print("بهترین حرکت اول X با Minimax:    %s" % describe_move(mm_move))
    print("بهترین حرکت اول X با Alpha-Beta: %s" % describe_move(ab_move))
    print()

    print("---- شمارش گره‌های ارزیابی‌شده ----")
    mm_total = mm_counter[0] + mm_move_counter[0]
    ab_total = ab_counter[0] + ab_move_counter[0]
    print("Minimax (ارزیابی مقدار):        %d گره" % mm_counter[0])
    print("Minimax (انتخاب حرکت اول):      %d گره" % mm_move_counter[0])
    print("جمع Minimax:                    %d گره" % mm_total)
    print("Alpha-Beta (ارزیابی مقدار):     %d گره" % ab_counter[0])
    print("Alpha-Beta (انتخاب حرکت اول):   %d گره" % ab_move_counter[0])
    print("جمع Alpha-Beta:                 %d گره" % ab_total)
    print()

    reduction = 100.0 * (1.0 - float(ab_total) / float(mm_total))
    print("کاهش گره‌های ارزیابی‌شده: %.1f%%" % reduction)
    if mm_value == ab_value == mm_best_value == ab_best_value:
        print("کنترل صحت: هر چهار مقدار ریشه برابرند (+%d)." % mm_value)
    else:
        print("کنترل صحت: هشدار — مقدارهای ریشه متفاوتند!")
    print("نتیجه: هر دو الگوریتم مقدار یکسان (+%d) و یک حرکت بهینه پیدا می‌کنند،" % mm_value)
    print("اما Alpha-Beta با هرس کردن شاخه‌های بی‌اثر این کار را با گره بسیار کمتری انجام می‌دهد.")


if __name__ == "__main__":
    main()
