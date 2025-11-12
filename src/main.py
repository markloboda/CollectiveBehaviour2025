from simulation import Simulation

def main():
    sim = Simulation(
        num_sheep=10,
        num_shepherds=1,
        field_size=(100, 100)
    )

    sim.run(
        steps=100,
        dt = 1.0,  # seconds
    )

if __name__ == "__main__":
    main()
