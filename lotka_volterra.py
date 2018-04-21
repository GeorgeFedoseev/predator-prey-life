import numpy as np
import matplotlib.pyplot as plt


def calc_Lotka_Volterra(preyN, predatorN, timeSteps, timeScale=0.001, preyBirthRate=50, preyEatenRate=0.1,
                             predatorDeathRate=20, predatorEatImprovRate=0.05, alpha=0.01):    
    
    preyValues = []
    predatorValues = []
    timeValues = []

    timeValues.append(0)
    preyValues.append(preyN)
    predatorValues.append(predatorN)

    prevPreyN = preyN
    prevPredatorN = predatorN
    

    for t in range(1, timeSteps):
        preyN = prevPreyN + timeScale * (preyBirthRate - preyEatenRate*prevPredatorN - alpha*prevPreyN)*prevPreyN

        if preyN <= 0:
            preyN = 0

        predatorN = prevPredatorN + timeScale * (predatorEatImprovRate*preyN - predatorDeathRate - alpha*prevPredatorN)*prevPredatorN        

        if predatorN <= 0:
            predatorN = 0                

        timeValues.append(t)
        preyValues.append(preyN)
        predatorValues.append(predatorN)
        

        if preyN < 1 or predatorN < 1:
            break

        prevPreyN = preyN
        prevPredatorN = predatorN

    return  timeValues, preyValues, predatorValues


if __name__ == "__main__":
    res = calc_Lotka_Volterra(200, 100, 1000)
    print res
    print len(res[0])
    
   

    plt.figure(3)        
    fig_LV_phase = plt.gcf()
    fig_LV_phase.canvas.set_window_title('LV_phase')
    plt.plot(res[1], res[2], c="b")
    fig_LV_phase.show()
    fig_LV_phase.canvas.draw()

    plt.figure(4)        
    fig_LV_t = plt.gcf()
    fig_LV_t.canvas.set_window_title('LV(t)')
    plt.plot(res[0], res[1], c="g")
    plt.plot(res[0], res[2], c="r")
    fig_LV_t.show()
    fig_LV_t.canvas.draw()

    plt.show()


    