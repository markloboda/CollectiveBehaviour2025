from simulation import Simulation

def main():
    sim = Simulation(
        num_sheep=10,
        num_shepherds=1,
        field_size=(100, 100)
    )

    sim.run()

if __name__ == "__main__":
    main()
