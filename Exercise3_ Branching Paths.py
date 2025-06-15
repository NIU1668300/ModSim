import simpy
import pandas as pd
import random

'''
En esta versión, hemos añadido una nueva actividad después de la consulta con la enfermera: la consulta con el doctor.
Un 60% de los pacientes pasarán por esta actividad, mientras que el 40% restante saldrá del sistema después de la consulta con la enfermera.
'''



# g-class: Acumula parametros globales para la simulación

class g:
    patient_inter = 5
    mean_receptionist_time = 2
    mean_n_consult_time = 6
    mean_d_consult_time = 20 ##NEW
    number_of_receptionists = 1
    number_of_nurses = 1
    number_of_doctors = 2 ##NEW
    prob_doctor = 0.6 ##NEW (Probabilidad de que el paciente pase por la consulta del doctor)
    sim_duration = 120
    number_of_runs = 5


# Patient class: Representa una entiidad dentro del modelo, pacientes en este caso. Contiene toda la información 
# que necesitemos sobre el paciente.
# Como si llevase un cartel con su información.
class Patient:
    def __init__(self, p_id): # Si que presenta constructor porque crearemos mas de un paciente
        self.id = p_id
        self.q_time_recep = 0 ##NEW
        self.q_time_nurse = 0


# Model class: Donde ocurre la magia. Representa el sistema que queremos simular. 
class Model:
    def __init__(self, run_number): # Prepara el enviroment, el contador de pacientes, los recursos y un data frame para almacenar los resultados (optativo)
        # Crea un ambiente de simulación donde todo se encontrará
        self.env = simpy.Environment()

        # Crea un contador de pacientes que usaremos como identificador
        self.patient_counter = 0

        # Crea un recurso que representa a las enfermeras, recepcionistas y doctores. 
        self.receptionist = simpy.Resource(self.env, capacity=g.number_of_receptionists)
        self.nurse = simpy.Resource(self.env, capacity=g.number_of_nurses)
        self.doctor = simpy.Resource(self.env, capacity=g.number_of_doctors) ##NEW

        # Guarda el run_number para poder identificar los resultados de cada simulación
        self.run_number = run_number

        # Crea un data frame para almacenar los resultados de la simulación.

        self.results_df = pd.DataFrame()
        self.results_df['Patient ID'] = [1]
        self.results_df['Q Time Receptionist'] = [0.0]
        self.results_df['Time with Receptionist'] = [0.0]
        self.results_df['Q Time Nurse'] = [0.0]
        self.results_df['Time with Nurse'] = [0.0]
        self.results_df['Q Time Doctor'] = [0.0] ##NEW
        self.results_df['Time with Doctor'] = [0.0] ##NEW
        self.results_df.set_index('Patient ID', inplace=True)

        #Crea atributo para almacenar el tiempo medio de queuing par las enfermeras a lo largo de la simulación
        self.mean_q_time_recep = 0
        self.mean_q_time_nurse = 0
        self.mean_q_time_doctor = 0 ##NEW (Tiempo medio de queuing para los doctores)

    # DES Generator: Genera pacientes a lo largo del tiempo. Cada paciente se crea con un identificador único y se le asigna un tiempo de espera en la cola de enfermeras
    # Pasos dentro de la simulación hasta que acabe la simulación:
    # 1. Incrementa el contadore de pacientes para generar una ID única
    # 2. Crea un paciente con esa ID
    # 3. Crea una instancia de la función generadora para su recorrido por el hospital y lo mete dentro
    # 4. Mide el tiempo hasta que llega el siguiente paciente
    # 5. CONGELA esta función hasta que llegue el siguiente paciente
    # 6. Devuelve 1

    def generator_patients_arrival(self): # le llama generator porque genera las ENTRADAS de pacientes al sistema.
        while True: # Bucle infinito que se detendrá cuando se acabe la simulación
            # Incrementa el contador de pacientes
            self.patient_counter += 1

            # Crea un paciente con la ID correspondiente
            p = Patient(self.patient_counter)

            # Añade el paciente a la simulación empleando el método attend_clinic, que es una función generadora que simula el
            # recorrido del paciente por el hospital (pathway)
            self.env.process(self.attend_clinic(p)) # Hay que escribirlo sabiendo como lo vas a llamar luego, porque este método no existe aun


            # Mide aleatoriamente el tiempo hasta que llega el siguiente paciente empleando una distribución exponencial 
            # con una media de g.patient_inter minutos (lambda = 1 / g.patient_inter)
            sampled_inter = random.expovariate(1 / g.patient_inter)

            # Mide el tiempo hasta que llega el siguiente paciente
            yield self.env.timeout(sampled_inter)

    # Pathway: Simula el recorrido del paciente por el hospital. Es la parte mas gorda de la clase:

    # Los pasos a seguir son:
    # 1. Miide el tiempo que el paciente empieza en la cola para la primera actividad
    # 2. Pide el recurso de la primera actividad (enfermera)
    # 3. Espera a que el recurso esté disponible (enfermera)
    # 4. Una vez el recurso está disponible, mantiene el recurso hasta que acabe la actividad. Guarda el tiempo en el que finaliza la cola y calcula
    #    el tiempo que ha estado en la cola de la enfermera.
    # 5. Mide el tiempo que estará con la enfemera (duración de la actividad)
    # 6. CONGELA la instancia de la función hasta que acabe la actividad (congelando el recurso de la enfermera para que no se pueda usar
    #  hasta que acabe la actividad) 
    # 7. Si hay otra actividad, repite el proceso. Si no, acaba la función.

    def attend_clinic(self, p):
        # Primera actividad: Recepción
        start_q_recep = self.env.now

        with self.receptionist.request() as req:
            # Espera a que el recurso esté disponible (recepcionista)
            yield req

            # Una vez el recurso está disponible, mantiene el recurso hasta que acabe la actividad. Guarda el tiempo en el que finaliza la cola y calcula
            # el tiempo que ha estado en la cola del recepcionista.
            end_q_recep = self.env.now
            p.q_time_recep = end_q_recep - start_q_recep

            # Mide el tiempo que estará con el recepcionista (duración de la actividad) empleando una distribución exponencial
            recep_time = random.expovariate(1.0 / g.mean_receptionist_time)

            # Guarda los resultados del paciente en el data frame
            self.results_df.at[p.id, "Q Time Receptionist"] = (p.q_time_recep)
            self.results_df.at[p.id, "Time with Receptionist"] = (recep_time)

            # Congela la instancia de la función hasta que acabe la actividad
            yield self.env.timeout(recep_time)


        # IMPORTANTE: Salir del With al cambiar de actividad. Si se necesita que el recurso se mantenga, se hace dentro del with.

        # Mide el tiempo que el paciente empieza en la cola para la primera actividad
        start_q_time_nurse = self.env.now

        # Segunda actividad: Enfermera
        # Pide el recurso de la SEGUNDA actividad (enfermera) y haz todo el proceso de después empleando ese recurso haciendo 
        # que de esta forma no se pueda usar por otro paciente.
        with self.nurse.request() as req:
            # Espera a que el recurso esté disponible (enfermera)
            yield req

            # Una vez el recurso está disponible, mantiene el recurso hasta que acabe la actividad. Guarda el tiempo en el que finaliza la cola y calcula
            # el tiempo que ha estado en la cola de la enfermera.
            end_q_time_nurse = self.env.now
            p.q_time_nurse = end_q_time_nurse - start_q_time_nurse

            # Mide el tiempo que estará con la enfermera (duración de la actividad) empleando otra vez una distribución exponencial
            consult_time = random.expovariate(1.0 / g.mean_n_consult_time)

            # Guarda los resultados del paciente en el data frame
            self.results_df.at[p.id, "Q Time Nurse"] = (p.q_time_nurse)
            self.results_df.at[p.id, "Time with Nurse"] = (consult_time)

            # Congela la instancia de la función hasta que acabe la actividad. Este es el tiempo que la enfermera estará ocupada con el paciente.
            yield self.env.timeout(consult_time)

            # Cuando acaba el tiempo con la enfermera la función generadora volverá aquí. Como no hay nada más que hacer la función terminará. 
            # A esto se le conoce Sink. Podríamos añadir mas actividades si quiesieramos, Que nos llevarían a otro sink. Una vez alcanzado el sink, 
            # la función generadora termina y se libera el recurso de la enfermera para que pueda ser usado por otro paciente.

        ## NEW: Tercera actividad: Doctor
        # Con una distribución uniforme, el paciente tiene un 60% de probabilidad de pasar por la consulta del doctor.
        if random.uniform(0,1) < g.prob_doctor:  # Si el paciente pasa por la consulta del doctor
            start_q_doctor = self.env.now

            with self.doctor.request() as req:
                yield req

                end_q_doctor = self.env.now

                p.q_time_doctor = end_q_doctor - start_q_doctor

                doctor_time = random.expovariate(1.0 / g.mean_d_consult_time)
                self.results_df.at[p.id, "Q Time Doctor"] = (p.q_time_doctor)
                self.results_df.at[p.id, "Time with Doctor"] = (doctor_time)

                yield self.env.timeout(doctor_time)

            

    def calculate_run_results(self): 
        # Calcula los resultados de una única run. Aquí simplmente se cacula el tiempo medio pero en casos reales
        # se pueden calcular mas cosas
        self.mean_q_time_recep = self.results_df['Q Time Receptionist'].mean()
        self.mean_q_time_nurse = self.results_df['Q Time Nurse'].mean()
        self.mean_q_time_doctor = self.results_df['Q Time Doctor'].mean() ##NEW (Tiempo medio de queuing para los doctores)


    # El metodo final y sin el que todo sería posible: RUN. 

    def run(self):

        # Crea el generador de pacientes
        self.env.process(self.generator_patients_arrival())

        # Corre la simulación durante g.sim_duration minutos
        self.env.run(until=g.sim_duration)

        # Calcula los resultados de la run
        self.calculate_run_results()

        print (f"Run number: {self.run_number}")
        print (self.results_df)

# Representa una serie de runs que realizan pruebas sobre nuestra simulación.
class Trial:
    # El constructor preara un df de pandas que guarda los resultados clave de cada run (en este caso el tiempo medio de la enfermera) usando 
    # el run number como index.
    def __init__(self):
        self.df_trial_results = pd.DataFrame()
        self.df_trial_results['Run Number'] = [0]
        self.df_trial_results['Mean Q Time Receptionist'] = [0.0]
        self.df_trial_results['Mean Q Time Nurse'] = [0.0]
        self.df_trial_results['Mean Q Time Doctor'] = [0.0] ##NEW
        self.df_trial_results.set_index('Run Number', inplace=True)

    def print_trial_results(self):
        print("Trial Results:")
        print(self.df_trial_results)

    # Metodo para ejecutar una prueba (trial)
    def run_trial(self):

        # Corre la simulación g.number_of_runs veces. Para cada run, creamos una nueva instancia de la clase Model y la corremos.
        # Al terminar la run, se guardan los resultados en el df de pandas.
        for run in range(g.number_of_runs):
            model = Model(run)
            model.run()

            self.df_trial_results.loc[run] = [model.mean_q_time_recep,
                                              model.mean_q_time_nurse.
                                              model.mean_q_time_doctor]

        self.print_trial_results()


if __name__ == "__main__":
    # Crea una instancia de la clase Trial y corre la prueba
    trial = Trial()
    trial.run_trial()

    