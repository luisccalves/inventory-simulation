from geneticalgorithm import geneticalgorithm as ga
import numpy as np
import random

days = int(input('Por quantos dias quer correr a simulação: '))
demand_mean = float(input('Qual a media diaria do consumo: '))
demand_sd = float(input('Qual o desvio padrão do consumo diario: '))
lead_time_max = int(input('Qual o numero maximo de entrega do material em dias: '))
lead_time_min = int(input('Qual o numero minimo de entrega do material em dias: '))
asl = float(input('Qual o nivel de serviço pretendido (p.e. 95.0) : '))

KK = 0
if not 0 < asl < 100:  # data validation on ASL
    while KK == 0:
        print('o nivel de serviço tem de ser entre 0 e 100')
        asl = float(input('Qual o nivel de serviço pretendido (p.e. 95.0) : '))
        if not 0 < asl < 100:
            KK = 0
        else:
            KK = 1

days = days + 2*lead_time_max      # adiciona dias extra para estabilizar a simulação
days2 = days*2

# Stochastic model defined as a function called stoch_inv_sim([Order qty, Reorder point])


def stoch_inv_sim(X):
    obj = 0  # objective function for Genetic algorithm
    # Every strategy will be tested for 10 times since we are generating demand using random function,to be more exhaustive, you can increase the number to a higher value.
    for k in range(10):
        tot_demand = 0
        tot_sales = 0
        a = [max(0, np.random.normal(demand_mean, demand_sd, 1))
             for i in range(days)]  # Generating a random Demand
        stkout_count = 0
        inv = []                 # array to store daily inventory
        pip_inv = []
        in_qty = [0 for i in range(days2)]  # array indicating receipt of goods
        order_qty = X[0]
        reorder_pt = X[1]
        for i in range(days):
            if i == 0:
                beg_inv = reorder_pt  # day 0 assigning reorder point as begining inventory
                in_inv = 0
                stock_open = beg_inv + in_inv
            else:
                beg_inv = end_inv
                in_inv = in_qty[i]  # incoming inventory on i’th day
                stock_open = beg_inv + in_inv
            demand = a[i]  # calling demand of i’th day from demand array a
            # lead time of replenishment
            lead_time = random.randint(lead_time_min, lead_time_max)
            if demand < stock_open:
                end_inv = stock_open - demand  # formula to calculate ending inventory
            else:
                end_inv = 0
            # storing the average of opening stock and ending inventory as cycle inventory
            inv.append(0.5*stock_open+0.5*end_inv)
            if i == 0:
                pipeline_inv = 0
            else:
                # calculating the piepline inventory as on i’th day
                pipeline_inv = sum(in_qty[j] for j in (i+1, days2-1))
            if pipeline_inv + end_inv <= reorder_pt:
                if i+lead_time < days:
                    # ordering new stock and adding to the incoming inventory list
                    in_qty[i+lead_time] = in_qty[i+lead_time]+order_qty
            if i >= 2*lead_time_max:  # the start of simulation performance monitoring
                # total sales during the simulation length
                tot_sales = tot_sales + stock_open - end_inv
                tot_demand = tot_demand + demand  # total demand during the simulation length
        cycle_inv = 0
        for n in range(len(inv)):
            # calculating the averge cycle inventory
            cycle_inv = cycle_inv + inv[n]
        cycle_inv = cycle_inv/len(inv)
        if tot_sales*100/(tot_demand+0.000001) < asl:
            # Imposing a penatly when ASL is not met the requirement
            aa = cycle_inv+10000000*demand_mean*(tot_demand-tot_sales)
        else:
            aa = cycle_inv
        obj = obj + aa  # objective function i.e. cycle inventory calculation

    return obj/10


print()
print('Model created, Proceeding to Optimisation with GA.')
print()
print('Optimal[Order Quantity, Reorder point] & Estimated \
      Cycle Inventory level will be printed below…')
print()


# Below is the gentic Algorithm code
varbound = np.array([[0, demand_mean*lead_time_max*5]]*2)


algorithm_param = {'max_num_iteration': 1000,
                   'population_size': 30,#15
                   'mutation_probability': 0.1,
                   'elit_ratio': 0.01,
                   'crossover_probability': 0.5,
                   'parents_portion': 0.3,
                   'crossover_type': 'uniform',
                   'max_iteration_without_improv': 200}


model = ga(function=stoch_inv_sim, dimension=2, variable_type='real',
           variable_boundaries=varbound, algorithm_parameters=algorithm_param)


model.run()
