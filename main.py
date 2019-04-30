from __future__ import with_statement
from random import *
import heapq
import sys
import numexpr as ne
import json
from consolemenu import *
from consolemenu.items import *

#global
optimization_problem = {}
current_answer = ()

def get_optimization_problem_json():
    global optimization_problem
    file = input('File with json: ')
    try:
        with open(file) as json_data:
            data = json.load(json_data)
            optimization_problem = data
            # optimization_problem['optimization'] = tuple(optimization_problem['optimization'])
            # for key, value in optimization_problem['boundaries'].items():
            #     optimization_problem['optimization'][key] = tuple(value)
    except EnvironmentError:
        print('File not found!')
        print()
        input("Press Enter to continue...")

def get_optimization_problem():
    global optimization_problem

    optimization_problem['variables'] = []
    print('Add variables:')
    while True:
        line = sys.stdin.readline().strip()
        if line:
            optimization_problem['variables'].append(line)
        else:
            break

    optimization_problem['boundaries'] = {}
    print('Variables boundaries:')
    for var in optimization_problem['variables']:
        print('Lower boundary of ' + var)
        lower = input()
        print('Upper boundary of ' + var)
        upper = input()  
        optimization_problem['boundaries'][var] = (lower, upper)
    
    optimization_problem['functions'] = []
    print('Add functions:')
    while True:
        line = sys.stdin.readline().strip()
        if line:
            optimization_problem['functions'].append(line)
        else:
            break

    print('Add optimization function:')
    function = input()
    print('min/max')
    mode = input().lower()
    optimization_problem['optimization'] = (function, mode)

def optimize():
    eps = 0.001 # stop condition
    global current_answer # current best answer (optimization_function + variables)
    current_answer = ()
    radius = () # for between two last best answers

    while True:
        points = [] # heap of best answer points
        limits = []
        if current_answer:
            for index, var in enumerate(optimization_problem['variables']):
                down_limit = current_answer[index + 1] - radius[index + 1]
                up_limit = current_answer[index + 1] + radius[index + 1]
                if down_limit < optimization_problem['boundaries'][var][0]:
                    down_limit = optimization_problem['boundaries'][var][0]
                if up_limit > optimization_problem['boundaries'][var][1]:
                    up_limit = optimization_problem['boundaries'][var][1]
                limits.append((down_limit, up_limit))
        for point in range(100000):
            answer = []
            if current_answer:
                for down_limit, up_limit in limits:
                    answer.append(uniform(down_limit, up_limit))
            else:
                for var in optimization_problem['variables']:
                    answer.append(uniform(optimization_problem['boundaries'][var][0], \
                    optimization_problem['boundaries'][var][1]))

            answer_dictionary = dict(zip(optimization_problem['variables'], answer))
            answer_optimization = ne.evaluate(optimization_problem['optimization'][0], answer_dictionary)
            answer_tuple = tuple([float(answer_optimization)] + answer)
            for function in optimization_problem['functions']:
                if not ne.evaluate(function, answer_dictionary):
                    answer_tuple = ()
            if answer_tuple: points.append(answer_tuple)

        if(len(points) <= 1):
            return ('No answer')

        top_answers_len = 50 if len(points) >= 50 else len(points)
            
        heapq.heapify(points)
        if optimization_problem['optimization'][1] == 'max':
            current_top_best_answers = heapq.nlargest(top_answers_len, points)
        else:
            current_top_best_answers = heapq.nsmallest(top_answers_len, points)

        radius = ()
        for index, answer in enumerate(current_top_best_answers[0]):
            radius = radius + tuple([abs(current_top_best_answers[0][index] - \
            current_top_best_answers[top_answers_len - 1][index])])
        
        print('Current best')
        print(current_answer)

        current_answer = current_top_best_answers[0]
        if abs(radius[0]) < eps:
            break

def prompt_optimization_problem():
    print(json.dumps(optimization_problem, indent=1, sort_keys=True))
    print()
    input("Press Enter to continue...")

def prompt_current_answer():
    if not current_answer:
        print("Nothing optimized so far")
        print()
        input("Press Enter to continue...")
        return
    print(json.dumps(dict(zip(['Optimization function'] + \
    optimization_problem['variables'], current_answer)), indent=1, sort_keys=True))
    print()
    input("Press Enter to continue...")

def prepare_menu():
    menu = ConsoleMenu("Linear Programming")
    function_item_1 = FunctionItem("Write optimization problem", get_optimization_problem)
    function_item_2 = FunctionItem("Read JSON optimization problem", get_optimization_problem_json)
    function_item_3 = FunctionItem("Prompt optimization problem", prompt_optimization_problem)
    function_item_4 = FunctionItem("Prompt current answer", prompt_current_answer)
    function_item_5 = FunctionItem("Optimize", optimize)

    menu.append_item(function_item_1)
    menu.append_item(function_item_2)
    menu.append_item(function_item_3)
    menu.append_item(function_item_4)
    menu.append_item(function_item_5)

    return menu

def main():
    menu = prepare_menu()
    menu.show()

if __name__ == "__main__":
    main()