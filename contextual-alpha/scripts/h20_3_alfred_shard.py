"""H20.3 P1 helper: prefetch ALFRED raw vintages for a slice of the landmark calendar (write-once raw cache).

Unchanged H20.1 collector logic (h20_1_collect.alfred); output table goes to a scratch folder and is
not used: the main collector re-parses every cached raw vintage into the single alfred.parquet.

    .venv/Scripts/python "Contextual Alpha/scripts/h20_3_alfred_shard.py" <shard_calendar.json> <scratch_dir>
"""
import sys
from pathlib import Path

import h20_1_collect as c1

c1.SAMPLE, c1.OUT = Path(sys.argv[1]), Path(sys.argv[2])
c1.OUT.mkdir(parents=True, exist_ok=True)
c1.alfred()
