#!/usr/bin/env python3

import os
import numpy as np
import pandas as pd
from pyulog import ULog
from pyulog.px4 import PX4ULog
from typing import TypedDict, List


class MissionData(TypedDict):
    dataset: str
    attr: str
    timestamp: np.ndarray[np.int32]
    values: np.ndarray[np.float32]


params = {
    "vehicle_attitude": ["roll", "pitch", "yaw"],
    "vehicle_attitude_setpoint": ["roll_d", "pitch_d", "yaw_d"],
    "vehicle_local_position": ["x", "y", "z"],
    "vehicle_local_position_setpoint": ["x", "y", "z"],
    "sensor_combined": [
        "accelerometer_m_s2[0]",
        "accelerometer_m_s2[1]",
        "accelerometer_m_s2[2]",
    ],
    "vehicle_magnetometer": [
        "magnetometer_ga[0]",
        "magnetometer_ga[1]",
        "magnetometer_ga[2]",
    ],
}


def extract_mission_mode(ulog) -> List[MissionData] | str:
    # find largest mission subarray
    # 3 is mission mode
    arr = ulog.get_dataset("vehicle_status").data["nav_state"] == 3
    diff = np.diff(arr.astype(int))
    start = (np.where(diff == 1)[0] + 1).tolist()
    end = (np.where(diff == -1)[0] + 1).tolist()
    if arr[0] == 1:
        start = [0] + start  # start with True
    if arr[-1] == 1:
        end = end + [len(arr)]  # ends with True
    arg = np.subtract(end, start).argmax()
    start_time = ulog.get_dataset("vehicle_status").data["timestamp"][start[arg]]
    end_time = ulog.get_dataset("vehicle_status").data["timestamp"][end[arg] - 1]

    cols = []
    for dataset, attrs in params.items():
        try:
            data = ulog.get_dataset(dataset).data
        except (KeyError, IndexError, ValueError) as error:
            return dataset
        for attr in attrs:
            values = data.get(attr)
            timestamp = data["timestamp"]
            mission_idx = np.where((timestamp > start_time) & (timestamp < end_time))[0]

            if values is None:
                raise KeyError(f"{attr} not found in {dataset}")
            cols.append(
                {
                    "dataset": dataset,
                    "attr": attr,
                    "timestamp": timestamp[mission_idx],
                    "values": values[mission_idx],
                }
            )

    return cols


def compress(col1, col2):
    # col1 should have more elements
    if len(col1["timestamp"]) < len(col2["timestamp"]):
        col1, col2 = col2, col1

    idx = np.searchsorted(col1["timestamp"], col2["timestamp"], side="right")

    start = 0
    final = np.zeros_like(col2["timestamp"], dtype=np.float32)
    for j, i in enumerate(idx):
        if i > start:
            final[j] = col1["values"][start:i].mean()
        else:
            final[j] = col1["values"][start if start < len(col1["values"]) else -1]
        start = i
    col1["timestamp"] = col2["timestamp"]
    col1["values"] = final


def expand(col1, col2):
    # col1 should have more elements
    if len(col1["timestamp"]) < len(col2["timestamp"]):
        col1, col2 = col2, col1

    idx = np.searchsorted(col2["timestamp"], col1["timestamp"], side="left")

    final = np.zeros_like(col1["timestamp"], dtype=np.float32)
    for j, i in enumerate(idx):
        final[j] = col2["values"][i if i < len(col2["values"]) else -1]
    col2["timestamp"] = col1["timestamp"]
    col2["values"] = final


def align_cols(cols: List[MissionData]) -> None:
    # vehicle_local_position.x is 10 Hz, so this should make
    # all log attributes 10 Hz
    idx = 6  # vehicle_local_position.x
    for col in cols:
        if len(col["timestamp"]) > len(cols[idx]["timestamp"]):
            compress(col, cols[idx])
        else:
            expand(cols[idx], col)


def cols_to_df(cols: List[MissionData]) -> pd.DataFrame:
    return pd.DataFrame(
        np.vstack([cols[0]["timestamp"]] + [col["values"] for col in cols]).T,
        columns=["timestamp"] + [f'{col["dataset"]}.{col["attr"]}' for col in cols],
    )


# change to current file's dir
os.chdir(os.path.dirname(os.path.abspath(__file__)))

cwd = os.path.dirname(os.path.abspath(__file__))
ulg_dir = os.path.join(cwd, "../data/ulg_files")
ulg_paths = [
    os.path.join(ulg_dir, ulg_file_name) for ulg_file_name in os.listdir(ulg_dir)
]

filter = [k for k in params.keys()] + ["vehicle_status"]

output_csv_dir = os.path.join(cwd, "../data/csv_files")

# make sure output csv dir exist
if not os.path.isdir(output_csv_dir):
    os.makedirs(output_csv_dir)

for i, ulog_path in enumerate(ulg_paths):
    csv_loc = os.path.join(output_csv_dir, os.path.basename(ulog_path)[:-4] + ".csv")

    if os.path.exists(csv_loc):
        print(f"{i+1} | File {csv_loc} already processed, skipping...")
        continue

    ulog = ULog(ulog_path, filter)
    px4ulog = PX4ULog(ulog)
    px4ulog.add_roll_pitch_yaw()

    cols = extract_mission_mode(ulog)
    if isinstance(cols, str):
        print(f"{i+1} | Skipping {ulog_path}, missing dataset {cols}")
        continue
    if min(map(lambda x: len(x["timestamp"]), cols)) < 20:
        print(f"{i+1} | Mission mode in file {csv_loc} too short, skipping...")
        continue
    align_cols(cols)
    df = cols_to_df(cols)

    # save to csv
    if df.shape[0] < 100:
        print(f"{i+1} | Mission mode in file {csv_loc} too short, skipping...")
        continue
    print(f"{i+1} | Converting {ulog_path} to csv")
    df.to_csv(csv_loc, index=False)
