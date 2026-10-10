"""Quantum core: Qiskit circuit that picks the computer's move."""
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

MOVES = {"00": "stone", "01": "paper", "10": "scissors"}  # "11" is rejected
_sampler = StatevectorSampler()


def build_circuit() -> QuantumCircuit:
    """2 qubits, H on each -> uniform superposition over 00, 01, 10, 11."""
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.h(1)
    qc.measure([0, 1], [0, 1])
    return qc


def quantum_choice() -> str:
    """Measure once; re-measure on '11' so each move has probability 1/3."""
    qc = build_circuit()
    while True:
        counts = _sampler.run([qc], shots=1).result()[0].data.c.get_counts()
        bits = next(iter(counts))
        if bits in MOVES:
            return MOVES[bits]


def get_winner(player: str, computer: str) -> str:
    if player == computer:
        return "tie"
    beats = {"stone": "scissors", "paper": "stone", "scissors": "paper"}
    return "player" if beats[player] == computer else "computer"
