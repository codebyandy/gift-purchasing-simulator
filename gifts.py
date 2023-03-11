
import sys
import numpy as np
import io
import random

BUDGET = 400
PRICE_A, PRICE_B, PRICE_C = 50, 100, 250
PENALTY_A, PENALTY_B, PENALTY_C = 100, 200, 500
DAYS = 25
REWARD_DECAY = 0.98
GAMMA = 0.9
ALPHA = 0.00001
EPSILON = 0.2
NUM_ITERATIONS = 500

def calculate_prices(price_a, price_b, price_c):
    price_a *= np.random.normal(1, 0.1)
    price_b *= np.random.normal(1, 0.1)
    price_c *= np.random.normal(1, 0.1)
    return round(price_a, 2), round(price_b, 2), round(price_c, 2)


def choose_action_random(theta, i, price_a, price_b, price_c, bought_a, bought_b, bought_c, money_left):
    action_a = False if bought_a else (True if random.random() < 0.2 and price_a < money_left else False)
    if action_a:
        money_left -= price_a

    action_b = False if bought_b else (True if random.random() < 0.2 and price_b < money_left else False)
    if action_b:
        money_left -= price_b

    action_c = False if bought_c else (True if random.random() < 0.2 and price_c < money_left else False)
    return action_a, action_b, action_c

def get_valid_actions(price_a, price_b, price_c, bought_a, bought_b, bought_c, money_left):
    possible_actions = {(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)}

    if bought_a:
        possible_actions -= {(1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)}
    if bought_b:
        possible_actions -= {(0, 1, 0), (0, 1, 1), (1, 1, 0), (1, 1, 1)}
    if bought_c:
        possible_actions -= {(0, 0, 1), (0, 1, 1), (1, 0, 1), (1, 1, 1)}

    actions = set()
    for action in possible_actions:
        cost = 0
        if action[0]:
            cost += price_a
        if action[1]:
            cost += price_b
        if action[2]:
            cost += price_c

        if cost <= money_left:
            actions.add(action)

    return actions

def choose_action_linear(theta, date, price_a, price_b, price_c, bought_a, bought_b, bought_c, money_left):
    actions = get_valid_actions(price_a, price_b, price_c, bought_a, bought_b, bought_c, money_left)

    # Epsilon chance to explore
    if random.random() < EPSILON:
        action = random.choice(list(actions))
        return random.choice(list(actions))

    # Otherwise, greedy
    best_action = None
    best_action_score = float('-inf')
    for action in actions:
        buy_a, buy_b, buy_c = action
        score = np.dot(theta, np.array([date, price_a, price_b, price_c, bought_a, bought_b, bought_c, money_left, buy_a, buy_b, buy_c]))

        if score >= best_action_score:
            best_action = action
            best_action_score = score

    return best_action

def simulate(theta, output):
    price_a, price_b, price_c = PRICE_A, PRICE_B, PRICE_C
    bought_a, bought_b, bought_c = False, False, False
    money_left = BUDGET

    f = io.open(output, "w", newline="")
    f.write("s_date,s_price_a,s_price_b,s_price_c,s_bought_a,s_bought_b,s_bought_c,s_money_left,buy_a,buy_b,buy_c,sp_date,sp_price_a,sp_price_b,sp_price_c,sp_bought_a,sp_bought_b,sp_bought_c,sp_money_left,buy_ap,buy_bp,buy_cp,r\n")

    for i in range(DAYS):
        action_a, action_b, action_c = choose_action_linear(theta, i, price_a, price_b, price_c, bought_a, bought_b, bought_c, money_left)
        if i != 0:
            f.write("," + str(action_a) + "," + str(action_b) + "," + str(action_c))
            f.write("\n")

        f.write(",".join([str(i), str(price_a), str(price_b), str(price_c), str(bought_a), str(bought_b), str(bought_c), str(money_left)]))
        f.write("," + str(action_a) + "," + str(action_b) + "," + str(action_c) + ",")
        if action_a:
            money_left -= price_a
            bought_a = True
        if action_b:
            money_left -= price_b
            bought_b = True
        if action_c:
            money_left -= price_c
            bought_c = True

        price_a, price_b, price_c = calculate_prices(price_a, price_b, price_c)
        f.write(",".join([str(i), str(price_a), str(price_b), str(price_c), str(bought_a), str(bought_b), str(bought_c), str(money_left)]))

    
        if bought_a and bought_b and bought_c:
            break

    f.write(',NONE,NONE,NONE')      # No a' for last action
    score = money_left - ((not bought_a) * PENALTY_A) - ((not bought_b) * PENALTY_B) - ((not bought_c) * PENALTY_C)
    # print("Money left: ", money_left)
    # print("bought_a: ", bought_a)
    # print("bought_b: ", bought_b)
    # print("bought_c: ", bought_c)
    print("Score: ", score)

    with io.open(output, "r") as f:
        headers = f.readline()
        file_lines = [line.strip() for line in f.readlines()]

        for i in range(len(file_lines) - 1, -1, -1):
            file_lines[i] = file_lines[i] + "," + str(score) + "\n"
            score *= REWARD_DECAY

        file_lines = [headers] + file_lines

    with io.open(output, "w") as f:
        f.writelines(file_lines)

def readline(line):
    s_date, \
    s_price_a, s_price_b, s_price_c, \
    s_bought_a, s_bought_b, s_bought_c, \
    s_money_left, \
    buy_a, buy_b, buy_c, \
    sp_date, \
    sp_price_a, sp_price_b, sp_price_c, \
    sp_bought_a, sp_bought_b, sp_bought_c, \
    sp_money_left, \
    buy_ap, buy_bp, buy_cp, \
    r = line.split(',')

    return int(s_date), \
            float(s_price_a), float(s_price_b), float(s_price_c), \
            bool(s_bought_a), bool(s_bought_b), bool(s_bought_c), \
            float(s_money_left), \
            bool(buy_a), bool(buy_b), bool(buy_c), \
            int(sp_date), \
            float(sp_price_a), float(sp_price_b), float(sp_price_c), \
            bool(sp_bought_a), bool(sp_bought_b), bool(sp_bought_c), \
            float(sp_money_left), \
            bool(buy_ap), bool(buy_bp), bool(buy_cp), \
            float(r)

def q_approximation(theta, features):
    return np.dot(theta, features)

def learn(theta, data):
    with io.open(data, "r") as f:
        f.readline() # Skip headers
        for line in f.readlines():
            s_date, \
            s_price_a, s_price_b, s_price_c, \
            s_bought_a, s_bought_b, s_bought_c, \
            s_money_left, \
            buy_a, buy_b, buy_c, \
            sp_date, \
            sp_price_a, sp_price_b, sp_price_c, \
            sp_bought_a, sp_bought_b, sp_bought_c, \
            sp_money_left, \
            buy_ap, buy_bp, buy_cp, \
            r = readline(line)

            q_sa = q_approximation(theta, [s_date, s_price_a, s_price_b, s_price_c,
                                           s_bought_a, s_bought_b, s_bought_c,
                                           s_money_left,
                                           buy_a, buy_b, buy_c])

            q_spap = q_approximation(theta, [sp_date, sp_price_a, sp_price_b, sp_price_c,
                                             sp_bought_a, sp_bought_b, sp_bought_c,
                                             sp_money_left,
                                             buy_ap, buy_bp, buy_cp])
            q_gradient = np.array([s_date, s_price_a, s_price_b, s_price_c,
                                    s_bought_a, s_bought_b, s_bought_c,
                                    s_money_left,
                                    buy_a, buy_b, buy_c], float)

            theta += ALPHA * (r + GAMMA * q_spap - q_sa) * q_gradient

    print("New theta: " + str(theta))
    return theta

def user_simulate():
    price_a, price_b, price_c = PRICE_A, PRICE_B, PRICE_C
    bought_a, bought_b, bought_c = False, False, False
    money_left = BUDGET
    
    for i in range(DAYS):
        print("It is the December {}. Gift A costs ${:.2f}, gift B costs ${:.2f}, gift C costs ${:.2f}. You have ${:.2f} left.".format(i + 1, price_a, price_b, price_c, money_left))

        if bought_a:
            print("You've bought A already. Skip.")
        elif price_a > money_left:
            print("You can't afford A. Skip.")
        else:
            resp = input("Do you want to buy A? ")
            if resp == "y":
                bought_a = True
                money_left -= price_a
        if bought_b:
            print("You've bought B already. Skip.")
        elif price_b > money_left:
            print("You can't afford B. Skip.")
        else:
            resp = input("Do you want to buy B? ")
            if resp == "y":
                bought_b = True
                money_left -= price_b
        if bought_c:
            print("You've bought C already. Skip.")
        elif price_c > money_left:
            print("You can't afford C. Skip.")
        else:
            resp = input("Do you want to buy C? ")
            if resp == "y":
                bought_c = True
                money_left -= price_c

        if bought_a and bought_b and bought_c:
            break

        if i == DAYS - 1:
            break

        price_a, price_b, price_c = calculate_prices(price_a, price_b, price_c)
    
    score = money_left - ((not bought_a) * PENALTY_A) - ((not bought_b) * PENALTY_B) - ((not bought_c) * PENALTY_C)
    print("Money left: ", money_left)
    print("bought_a: ", bought_a)
    print("bought_b: ", bought_b)
    print("bought_c: ", bought_c)
    print("Score: ", score)
    
    
def main():
    # user_simulate()
    theta = np.zeros(11)
    for i in range(NUM_ITERATIONS):
        simulate(theta, "gifts.csv")
        theta = learn(theta, "gifts.csv")

if __name__ == "__main__":
    main()
