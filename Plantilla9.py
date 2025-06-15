import simpy
import random
import pandas as pd

class g: 
    machines_est1 = 2
    machines_est2 = 1
    machines_est3 = 3
    machines_est4 = 3
    machines_est5 = 4

    # A: 4, 3, 5
    # B: 5, 3, 1, 2
    # C: 1, 2, 3, 4, 5

    mean_temp_prodA = [60,48,45]
    mean_temp_prodB = [30,36,51,30]
    mean_temp_prodC = [72,15,42,54,60]

    prob_prodA = 0.5
    prob_prodB = 0.3
    prob_prodC = 0.2
    arrival_mean_time = 15

    sim_duration = 450
    num_runs = 219

class encargo:
    def __init__(self, id_encargo, tipo):
        self.id_encargo = id_encargo
        self.tipo = tipo
        self.tiempo_produccion = 0
        self.tiempo_espera = 0

class Model:
    def __init__(self, run_number):
        self.env = simpy.Environment()

        self.encargo_counter = 0

        self.est1 = simpy.Resource(self.env, capacity=g.machines_est1)
        self.est2 = simpy.Resource(self.env, capacity=g.machines_est2)
        self.est3 = simpy.Resource(self.env, capacity=g.machines_est3)
        self.est4 = simpy.Resource(self.env, capacity=g.machines_est4)
        self.est5 = simpy.Resource(self.env, capacity=g.machines_est5)

        self.results_df = pd.DataFrame()
        self.results_df['ID Encargo'] = [1]
        self.results_df['Tipo'] = ['']
        self.results_df['Tiempo Producción'] = [0.0]
        self.results_df['Tiempo Espera'] = [0.0]
        self.results_df.set_index('ID Encargo', inplace=True)

        self.run_number = run_number

        self.mean_waiting_time = 0
        self.mean_production_time = 0
    
    def generator_encargos(self):
        while True:
            #print("Encargo llega a la planta de producción a las ", self.env.now)
            self.encargo_counter += 1
            tipo_p = random.uniform(0, 1)

            if tipo_p < g.prob_prodA:
                tipo = 'A'
            elif tipo_p < g.prob_prodA + g.prob_prodB:
                tipo = 'B'
            else:
                tipo = 'C' 
            e =  encargo(self.encargo_counter, tipo)

            self.env.process(self.encargo_process(e))

            sampled_inter = random.expovariate(1 / (g.arrival_mean_time))  

            yield self.env.timeout(sampled_inter)

    def encargo_process(self, e):
        start_time = self.env.now
        self.results_df.at[e.id_encargo, 'Tipo'] = e.tipo
        #print(f"Encargo {e.id_encargo} de tipo {e.tipo} comienza a procesarse a las {start_time}")
        if e.tipo == 'A':
            with self.est4.request() as req:
                yield req

                end_q_est = self.env.now
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} espera en Estación 4 desde {start_time} hasta {end_q_est}")
                e.tiempo_espera += end_q_est - start_time

                est_time = random.expovariate(1/(g.mean_temp_prodA[0]/2))
                e.tiempo_produccion += est_time
                self.results_df.at[e.id_encargo, "Tiempo Espera"] = e.tiempo_espera
                self.results_df.at[e.id_encargo, "Tiempo Producción"] = e.tiempo_produccion
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} comienza a procesarse en Estación 4 a las {end_q_est}")
                yield self.env.timeout(est_time)
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} termina en Estación 4 a las {self.env.now}")

            start_time = self.env.now

            with self.est3.request() as req:
                yield req

                end_q_est = self.env.now
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} espera en Estación 3 desde {start_time} hasta {end_q_est}")
                e.tiempo_espera += end_q_est - start_time

                est_time = random.expovariate(1/(g.mean_temp_prodA[1]/2))

                e.tiempo_produccion += est_time

                self.results_df.at[e.id_encargo, "Tiempo Espera"] = e.tiempo_espera
                self.results_df.at[e.id_encargo, "Tiempo Producción"] = e.tiempo_produccion
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} comienza a procesarse en Estación 3 a las {end_q_est}")
                yield self.env.timeout(est_time)
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} termina en Estación 3 a las {self.env.now}")

            start_time = self.env.now
        
            with self.est5.request() as req:
                yield req

                end_q_est = self.env.now
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} espera en Estación 5 desde {start_time} hasta {end_q_est}")
                e.tiempo_espera += end_q_est - start_time

                est_time = random.expovariate(1/(g.mean_temp_prodA[2]/2))

                e.tiempo_produccion += est_time

                self.results_df.at[e.id_encargo, "Tiempo Espera"] = e.tiempo_espera
                self.results_df.at[e.id_encargo, "Tiempo Producción"] = e.tiempo_produccion
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} comienza a procesarse en Estación 5 a las {end_q_est}")
                yield self.env.timeout(est_time)
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} termina en Estación 5 a las {self.env.now}")
            
        
        elif e.tipo == 'B':

            with self.est5.request() as req:
                yield req

                end_q_est = self.env.now
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} espera en Estación 5 desde {start_time} hasta {end_q_est}")
                e.tiempo_espera += end_q_est - start_time

                est_time = random.expovariate(1/(g.mean_temp_prodB[0]/2))

                e.tiempo_produccion += est_time

                self.results_df.at[e.id_encargo, "Tiempo Espera"] = e.tiempo_espera
                self.results_df.at[e.id_encargo, "Tiempo Producción"] = e.tiempo_produccion
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} comienza a procesarse en Estación 5 a las {end_q_est}")
                yield self.env.timeout(est_time)
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} termina en Estación 5 a las {self.env.now}")

            start_time = self.env.now

            with self.est3.request() as req:
                yield req

                end_q_est = self.env.now
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} espera en Estación 3 desde {start_time} hasta {end_q_est}")
                e.tiempo_espera += end_q_est - start_time

                est_time = random.expovariate(1/(g.mean_temp_prodB[1]/2))

                e.tiempo_produccion += est_time

                self.results_df.at[e.id_encargo, "Tiempo Espera"] = e.tiempo_espera
                self.results_df.at[e.id_encargo, "Tiempo Producción"] = e.tiempo_produccion
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} comienza a procesarse en Estación 3 a las {end_q_est}")
                yield self.env.timeout(est_time)
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} termina en Estación 3 a las {self.env.now}")

            start_time = self.env.now
        
            with self.est1.request() as req:
                yield req

                end_q_est = self.env.now
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} espera en Estación 1 desde {start_time} hasta {end_q_est}")
                e.tiempo_espera += end_q_est - start_time

                est_time = random.expovariate(1/(g.mean_temp_prodB[2]/2))

                e.tiempo_produccion += est_time

                self.results_df.at[e.id_encargo, "Tiempo Espera"] = e.tiempo_espera
                self.results_df.at[e.id_encargo, "Tiempo Producción"] = e.tiempo_produccion
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} comienza a procesarse en Estación 1 a las {end_q_est}")
                yield self.env.timeout(est_time)
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} termina en Estación 1 a las {self.env.now}")

            start_time = self.env.now

            with self.est2.request() as req:
                yield req

                end_q_est = self.env.now
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} espera en Estación 2 desde {start_time} hasta {end_q_est}")
                e.tiempo_espera += end_q_est - start_time

                est_time = random.expovariate(1/(g.mean_temp_prodB[3]/2))

                e.tiempo_produccion += est_time

                self.results_df.at[e.id_encargo, "Tiempo Espera"] = e.tiempo_espera
                self.results_df.at[e.id_encargo, "Tiempo Producción"] = e.tiempo_produccion
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} comienza a procesarse en Estación 2 a las {end_q_est}")
                yield self.env.timeout(est_time)
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} termina en Estación 2 a las {self.env.now}")
        
        else:  # Tipo C

            with self.est1.request() as req:
                yield req

                end_q_est = self.env.now
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} espera en Estación 1 desde {start_time} hasta {end_q_est}")
                e.tiempo_espera += end_q_est - start_time

                est_time = random.expovariate(1/(g.mean_temp_prodC[0]/2))

                e.tiempo_produccion += est_time

                self.results_df.at[e.id_encargo, "Tiempo Espera"] = e.tiempo_espera
                self.results_df.at[e.id_encargo, "Tiempo Producción"] = e.tiempo_produccion
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} comienza a procesarse en Estación 1 a las {end_q_est}")
                yield self.env.timeout(est_time)
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} termina en Estación 1 a las {self.env.now}")

            start_time = self.env.now

            with self.est2.request() as req:
                yield req

                end_q_est = self.env.now
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} espera en Estación 2 desde {start_time} hasta {end_q_est}")
                e.tiempo_espera += end_q_est - start_time

                est_time = random.expovariate(1/(g.mean_temp_prodC[1]/2))

                self.results_df.at[e.id_encargo, "Tiempo Espera"] = e.tiempo_espera
                self.results_df.at[e.id_encargo, "Tiempo Producción"] += est_time
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} comienza a procesarse en Estación 2 a las {end_q_est}")
                yield self.env.timeout(est_time)
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} termina en Estación 2 a las {self.env.now}")

            start_time = self.env.now

            with self.est3.request() as req:
                yield req

                end_q_est = self.env.now
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} espera en Estación 3 desde {start_time} hasta {end_q_est}")
                e.tiempo_espera += end_q_est - start_time

                est_time = random.expovariate(1/(g.mean_temp_prodC[2]/2))

                self.results_df.at[e.id_encargo, "Tiempo Espera"] = e.tiempo_espera
                self.results_df.at[e.id_encargo, "Tiempo Producción"] += est_time
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} comienza a procesarse en Estación 3 a las {end_q_est}")
                yield self.env.timeout(est_time)
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} termina en Estación 3 a las {self.env.now}")

            start_time = self.env.now

            with self.est4.request() as req:
                yield req

                end_q_est = self.env.now
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} espera en Estación 4 desde {start_time} hasta {end_q_est}")
                e.tiempo_espera += end_q_est - start_time

                est_time = random.expovariate(1/(g.mean_temp_prodC[3]/2))

                self.results_df.at[e.id_encargo, "Tiempo Espera"] = e.tiempo_espera
                self.results_df.at[e.id_encargo, "Tiempo Producción"] += est_time
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} comienza a procesarse en Estación 4 a las {end_q_est}")
                yield self.env.timeout(est_time)
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} termina en Estación 4 a las {self.env.now}")

            start_time = self.env.now

            with self.est5.request() as req:
                yield req

                end_q_est = self.env.now
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} espera en Estación 5 desde {start_time} hasta {end_q_est}")
                e.tiempo_espera += end_q_est - start_time

                est_time = random.expovariate(1/(g.mean_temp_prodC[4]/2))

                self.results_df.at[e.id_encargo, "Tiempo Espera"] = e.tiempo_espera
                self.results_df.at[e.id_encargo, "Tiempo Producción"] += est_time
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} comienza a procesarse en Estación 5 a las {end_q_est}")
                yield self.env.timeout(est_time)
                #print(f"Encargo {e.id_encargo} de tipo {e.tipo} termina en Estación 5 a las {self.env.now}")

    def calculate_run_results(self):
        # Calcula los resultados de una única run. Aquí simplmente se cacula el tiempo medio pero en casos reales
        # se pueden calcular mas cosas
        self.mean_waiting_time = self.results_df['Tiempo Espera'].mean()
        self.mean_production_time = self.results_df['Tiempo Producción'].mean()

    def run(self):
        # Crea el generador de encargos
        self.env.process(self.generator_encargos())

        # Corre la simulación durante g.sim_duration minutos
        self.env.run(until=g.sim_duration)

        # Calcula los resultados de la run
        self.calculate_run_results()

        print(f"Run number: {self.run_number}")
        print(self.results_df)

class Trial:
    def __init__(self):
        self.df_trial_results = pd.DataFrame()
        self.df_trial_results['Run Number'] = [0]
        self.df_trial_results['Mean Waiting Time'] = [0.0]
        self.df_trial_results['Mean Production Time'] = [0.0]
        self.df_trial_results.set_index('Run Number', inplace=True)

    def print_trial_results(self):
        print("Trial Results:")
        print(self.df_trial_results)

    def run_trial(self):
        for run_number in range(g.num_runs):
            model = Model(run_number)
            model.run()

            # Añade los resultados de la run al df de resultados de la trial
            self.df_trial_results.at[run_number, 'Mean Waiting Time'] = model.mean_waiting_time
            self.df_trial_results.at[run_number, 'Mean Production Time'] = model.mean_production_time

        self.print_trial_results()

if __name__ == "__main__":
    # Crea una instancia de la clase Trial y corre la prueba
    trial = Trial()
    trial.run_trial()

    print("Mean Waiting time among runs:",trial.df_trial_results["Mean Waiting Time"].mean())
    print("Mean Production time among runs:",trial.df_trial_results["Mean Production Time"].mean())

    
