# Section 05: send log lines to a file instead of the screen.
# Predict first: which of the four messages end up in app.log?
import logging
from pathlib import Path

log_file = Path(__file__).parent / "out" / "app.log"
log_file.parent.mkdir(exist_ok=True)
log_file.unlink(missing_ok=True)

logging.basicConfig(filename=log_file, level=logging.INFO, encoding="utf-8",
                    format="%(levelname)-8s %(name)s: %(message)s")
log = logging.getLogger("etl")

log.debug("row 17 raw=%r", {"score": "92"})
log.info("loaded %d rows", 250)
log.warning("3 rows had no score")
try:
    1 / 0
except ZeroDivisionError:
    log.exception("average failed")

print(log_file.read_text(encoding="utf-8"))

# Then try: change level=logging.INFO to level=logging.DEBUG.
