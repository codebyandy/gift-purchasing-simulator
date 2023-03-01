
import sys
import numpy as np
import io
import random

BUDGET = 400
PRICE_A, PRICE_B, PRICE_C = 50, 100, 250
PENALTY_A, PENALTY_B, PENALTY_C = 100, 200, 500
DAYS = 25
REWARD_DECAY = 0.98


def calculate_prices(price_a, price_b, price_c):
    price_a *= np.random.normal(1, 0.1)
    price_b *= np.random.normal(1, 0.1)
    price_c *= np.random.normal(1, 0.1)
    return round(price_a, 2), round(price_b, 2), round(price_c, 2)


def choose_action(theta, i, price_a, price_b, price_c, bought_a, bought_b, bought_c, money_left):
    action_a = False if bought_a else (True if random.random() < 0.2 and price_a < money_left else False)
    if action_a:
        money_left -= price_a

    action_b = False if bought_b else (True if random.random() < 0.2 and price_b < money_left else False)
    if action_b:
        money_left -= price_b

    action_c = False if bought_c else (True if random.random() < 0.2 and price_c < money_left else False)
    return action_a, action_b, action_c


def simulate(theta, output):
    price_a, price_b, price_c = PRICE_A, PRICE_B, PRICE_C
    bought_a, bought_b, bought_c = False, False, False
    money_left = BUDGET

    f = io.open(output, "w", newline="")
    f.write("s_date,s_price_a,s_price_b,s_price_c,s_bought_a,s_bought_b,s_bought_c,s_money_left,a,sp_date,sp_price_a,sp_price_b,sp_price_c,sp_bought_a,sp_bought_b,sp_bought_c,sp_money_left,r\n")

    for i in range(DAYS):
        f.write(",".join([str(i), str(price_a), str(price_b), str(price_c), str(bought_a), str(bought_b), str(bought_c), str(money_left)]))
        action_a, action_b, action_c = choose_action(theta, i, price_a, price_b, price_c, bought_a, bought_b, bought_c, money_left)
        f.write("," + str((action_a << 2) + (action_b << 1) + action_c) + ",")
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
        f.write("\n")
    
        if bought_a and bought_b and bought_c:
            break

    score = money_left - ((not bought_a) * PENALTY_A) - ((not bought_b) * PENALTY_B) - ((not bought_c) * PENALTY_C)
    print("Money left: ", money_left)
    print("bought_a: ", bought_a)
    print("bought_b: ", bought_b)
    print("bought_c: ", bought_c)
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
    user_simulate()
    # simulate(None, "gifts_random.csv")

if __name__ == "__main__":
    main()
