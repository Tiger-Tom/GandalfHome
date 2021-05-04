#Imports
import simpleeval
import math
#Functions
##Calculate
def calculate(output, calc):
    calc = calc.replace('plus', '+').replace('minus', '-').replace('times', '*')
    calc = calc.replace('divided by', '/').replace('to the power of', '**')
    calc = calc.replace('point', '.').replace('dot', '.')
    calc = calc.replace(' ', '')
    output('Calculating '+calc)
    answer = simpleeval.simple_eval(calc)
    output(answer)
def calculateSqrt(output, x):
    try:
        x = float(x)
    except:
        output('Error: '+x+' is not a number')
        return
    output('The square root of '+str(x)+' is '+str(math.sqrt(x)))
