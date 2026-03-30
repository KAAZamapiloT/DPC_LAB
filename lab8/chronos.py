from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List, Tuple

MOD = 9973
N = 5
DELAY_SECONDS = 0.25


def load_seed() -> dict:
    candidates = []

    if "__file__" in globals():
        candidates.append(Path(__file__).resolve().with_name("seed.json"))

    candidates.append(Path.cwd() / "seed.json")
    candidates.append(Path("seed.json"))

    for path in candidates:
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)

    raise FileNotFoundError(
        "Could not find seed.json next to the script or in the current working directory."
    )


def align_clocks(
    clocks: List[int], theta: int
) -> Tuple[List[int], int, List[int], List[int]]:
   
    trusted = [i for i, t in enumerate(clocks) if abs(t - clocks[0]) <= theta]
    if not trusted:
        raise ValueError("Trusted set is empty. Node 0 must always be trusted.")

    target = sum(clocks[i] for i in trusted) // len(trusted)

    offsets: List[int] = []
    synced: List[int] = []

    for i, t in enumerate(clocks):
        delta = target - t if i in trusted else 0
        offsets.append(delta)
        synced.append(t + delta)

    return trusted, target, offsets, synced


def can_deliver(v_local: List[int], sender: int, v_msg: List[int]) -> bool:

    if v_msg[sender] != v_local[sender] + 1:
        return False

    for k in range(N):
        if k != sender and v_msg[k] > v_local[k]:
            return False

    return True


def apply_message(v_local: List[int], v_msg: List[int]) -> None:
    
    for k in range(N):
        v_local[k] = max(v_local[k], v_msg[k])


def process_buffer(v_local: List[int], buffer: List[dict], node_id: int) -> None:
 
    changed = True
    while changed:
        changed = False
        i = 0
        while i < len(buffer):
            msg = buffer[i]
            sender = msg["sender"]
            v_msg = msg["v_msg"]

            if can_deliver(v_local, sender, v_msg):
                print(
                    f"[Node {node_id}] buffered message from {sender} is now deliverable -> processing"
                )
                time.sleep(DELAY_SECONDS)

                apply_message(v_local, v_msg)

                print(f"[Node {node_id}] vector clock updated to {v_local}")
                buffer.pop(i)
                changed = True
                i = 0  
            else:
                i += 1


def process_node(
    node_id: int, queue: List[dict], synced_clock: int
) -> Tuple[List[int], int, List[dict]]:
    v_local = [0] * N
    buffer: List[dict] = []

    print(f"\n=== Node {node_id} ===")
    print(f"[Node {node_id}] aligned clock = {synced_clock}")
    print(f"[Node {node_id}] starting vector clock = {v_local}")

    for msg in queue:
        sender = msg["sender"]
        v_msg = msg["v_msg"]

        print(f"[Node {node_id}] received message from {sender}: {v_msg}")
        time.sleep(DELAY_SECONDS)

        if can_deliver(v_local, sender, v_msg):
            apply_message(v_local, v_msg)
            print(f"[Node {node_id}] processed immediately -> {v_local}")
            process_buffer(v_local, buffer, node_id)
        else:
            buffer.append(msg)
            print(f"[Node {node_id}] buffered (causal history missing)")

    process_buffer(v_local, buffer, node_id)

    if buffer:
        print(
            f"[Node {node_id}] WARNING: {len(buffer)} message(s) could not be delivered and remain buffered."
        )
    else:
        print(f"[Node {node_id}] buffer emptied.")

    payload = (synced_clock * sum(v_local)) % MOD
    print(
        f"[Node {node_id}] final payload = ({synced_clock} * {sum(v_local)}) mod {MOD} = {payload}"
    )
    return v_local, payload, buffer


def main() -> None:
    seed = load_seed()

    theta = int(seed["theta"])
    clocks = list(seed["clocks"])
    queues = list(seed["queues"])

    if len(clocks) != N or len(queues) != N:
        raise ValueError(f"Expected exactly {N} clocks and {N} queues.")

    print("Project Chronos simulation starting...")
    print(f"Initial clocks: {clocks}")
    print(f"Theta: {theta}")

    trusted, target, offsets, synced = align_clocks(clocks, theta)

    print("\n=== Clock Alignment ===")
    print(f"Trusted nodes: {trusted}")
    print(f"Target time (floor average): {target}")
    print(f"Offsets: {offsets}")
    print(f"Synchronized clocks: {synced}")

    results = []
    for node_id in range(N):
        v_local, payload, buffer = process_node(
            node_id, queues[node_id], synced[node_id]
        )
        results.append((node_id, v_local, payload, buffer))

    print("\n=== Final Results ===")
    for node_id, v_local, payload, buffer in results:
        print(
            f"Node {node_id}: V={v_local}, payload={payload}, buffered_left={len(buffer)}"
        )


if __name__ == "__main__":
    main()
