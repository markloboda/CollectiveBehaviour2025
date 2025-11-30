import os
from typing import Sequence, List, Tuple, Optional
import math
import matplotlib.pyplot as plt

from simulation_state import SimulationState



# ---------- 1) Cohesion ----------

def plot_cohesion_time(states: Sequence[SimulationState], out_path: str) -> None:
    """
    Plot C(t) over time and save to out_path.
    """
    if not states:
        return

    times = [s.time for s in states]
    cohesion = [s.cohesion for s in states]

    plt.figure()
    plt.plot(times, cohesion, lw=1.5)
    plt.xlabel("Time")
    plt.ylabel("Cohesion C(t)")
    plt.title("Flock cohesion over time")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


def plot_cohesion_hist(states: Sequence[SimulationState], out_path: str, bins: int = 30) -> None:
    """
    Plot histogram of cohesion values across the whole run.
    """
    if not states:
        return

    cohesion = [s.cohesion for s in states]

    plt.figure()
    plt.hist(cohesion, bins=bins, density=True)
    plt.xlabel("Cohesion C")
    plt.ylabel("PDF")
    plt.title("Distribution of cohesion")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


# ---------- 2) Polarisation ----------

def plot_polarisation_time(states: Sequence[SimulationState], out_path: str) -> None:
    """
    Plot P(t) over time and save to out_path.
    """

    times = [s.time for s in states]
    pol = [s.polarization for s in states]

    plt.figure()
    plt.plot(times, pol, lw=1.5)
    plt.xlabel("Time")
    plt.ylabel("Polarisation P(t)")
    plt.title("Flock polarisation over time")
    plt.ylim(0.0, 1.05)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


def plot_polarisation_hist(states: Sequence[SimulationState], out_path: str, bins: int = 30) -> None:
    """
    Plot histogram of polarisation values.
    """

    pol = [s.polarization for s in states]

    plt.figure()
    plt.hist(pol, bins=bins, density=True)
    plt.xlabel("Polarisation P")
    plt.ylabel("PDF")
    plt.title("Distribution of polarisation")
    plt.xlim(0.0, 1.0)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


# ---------- 3) Elongation ----------

def plot_elongation_time(states: Sequence[SimulationState], out_path: str) -> None:
    """
    Plot E(t) over time and save to out_path.
    """

    times = [s.time for s in states]
    elong = [s.elongation for s in states]

    plt.figure()
    plt.plot(times, elong, lw=1.5)
    plt.xlabel("Time")
    plt.ylabel("Elongation E(t)")
    plt.title("Flock elongation over time")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


def plot_elongation_hist(states: Sequence[SimulationState], out_path: str, bins: int = 30) -> None:
    """
    Plot histogram of elongation values.
    """

    elong = [s.elongation for s in states]

    plt.figure()
    plt.hist(elong, bins=bins, density=True)
    plt.xlabel("Elongation E")
    plt.ylabel("PDF")
    plt.title("Distribution of elongation")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


# ---------- 4) Dog offsets (x_D, y_D) ----------

def plot_dog_offsets_time(states: Sequence[SimulationState], out_path: str) -> None:
    """
    Plot dog lateral (x_D) and longitudinal (y_D) offsets vs time.
    Uses SimulationState.dog_offsets(), which may return None.
    """

    times = []
    xD = []
    yD = []

    for s in states:
        off = s.dog_offsets
        if off is None:
            continue
        x, y = off
        times.append(s.time)
        xD.append(x)
        yD.append(y)

    if not times:
        return

    plt.figure()
    plt.plot(times, xD, label="x_D (lateral)", lw=1.5)
    plt.plot(times, yD, label="y_D (longitudinal)", lw=1.5)
    plt.xlabel("Time")
    plt.ylabel("Offset (in flock frame)")
    plt.title("Dog offsets relative to flock")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


def plot_dog_offsets_hist(states: Sequence[SimulationState], out_path: str, bins: int = 30) -> None:
    """
    Plot histograms of dog lateral and longitudinal offsets.
    """

    xD = []
    yD = []
    for s in states:
        off = s.dog_offsets
        if off is None:
            continue
        x, y = off
        xD.append(x)
        yD.append(y)

    if not xD:
        return

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    axes[0].hist(xD, bins=bins, density=True)
    axes[0].set_xlabel("x_D (lateral)")
    axes[0].set_ylabel("PDF")
    axes[0].set_title("Dog lateral offset")
    axes[0].grid(True, alpha=0.3)

    axes[1].hist(yD, bins=bins, density=True)
    axes[1].set_xlabel("y_D (longitudinal)")
    axes[1].set_ylabel("PDF")
    axes[1].set_title("Dog longitudinal offset")
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close(fig)


def plot_dog_rear_distance_time(states: Sequence[SimulationState], out_path: str) -> None:
    """
    Plot y_RD(t): distance from dog to rear-most sheep along flock direction.
    """

    times = []
    yRD = []
    for s in states:
        val = s.dog_rear_distance
        if val is None:
            continue
        times.append(s.time)
        yRD.append(val)

    if not times:
        return

    plt.figure()
    plt.plot(times, yRD, lw=1.5)
    plt.axhline(0.0, color="k", lw=0.8, ls="--")
    plt.xlabel("Time")
    plt.ylabel("y_RD")
    plt.title("Dog distance to rear-most sheep")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


def plot_dog_rear_distance_hist(states: Sequence[SimulationState], out_path: str, bins: int = 30) -> None:
    """
    Plot histogram of y_RD values.
    """

    vals = []
    for s in states:
        v = s.dog_rear_distance
        if v is None:
            continue
        vals.append(v)

    if not vals:
        return

    plt.figure()
    plt.hist(vals, bins=bins, density=True)
    plt.xlabel("y_RD")
    plt.ylabel("PDF")
    plt.title("Distribution of dog rear distance y_RD")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()



def plot_all_metrics(
    states: Sequence[SimulationState],
    results_dir: str = "results",
    prefix: str = ""
) -> None:

    os.makedirs(results_dir, exist_ok=True)

    def path(name: str) -> str:
        return os.path.join(results_dir, f"{prefix}{name}.png")

    # 1) Cohesion
    plot_cohesion_time(states, path("cohesion_time"))
    plot_cohesion_hist(states, path("cohesion_hist"))

    # 2) Polarisation
    plot_polarisation_time(states, path("polarisation_time"))
    plot_polarisation_hist(states, path("polarisation_hist"))

    # 3) Elongation
    plot_elongation_time(states, path("elongation_time"))
    plot_elongation_hist(states, path("elongation_hist"))

    # 4) Dog offsets
    plot_dog_offsets_time(states, path("dog_offsets_time"))
    plot_dog_offsets_hist(states, path("dog_offsets_hist"))

    # 5) Dog rear distance
    plot_dog_rear_distance_time(states, path("dog_rear_distance_time"))
    plot_dog_rear_distance_hist(states, path("dog_rear_distance_hist"))