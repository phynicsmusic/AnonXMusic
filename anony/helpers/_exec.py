import os
import ast
import traceback
from typing import Optional

def format_exception(exc: BaseException, tb: Optional[list[traceback.FrameSummary]] = None) -> str:
    """Format exception traceback into a readable string."""
    if tb is None:
        tb = traceback.extract_tb(exc.__traceback__)

    cwd = os.getcwd()
    for frame in tb:
        if cwd in frame.filename:
            frame.filename = os.path.relpath(frame.filename)

    return (
        "Traceback (most recent call last):\n"
        f"{''.join(traceback.format_list(tb))}"
        f"{type(exc).__name__}{': ' + str(exc) if str(exc) else ''}"
    )

async def meval(code: str, globs: dict, **kwargs):
    """
    Asynchronously evaluate a code string in a controlled environment.
    """
    # ဒီနေရာမှာ meval ရဲ့ ကျန်တဲ့ ကုဒ်တွေကို ဒီအတိုင်း ထားပေးပါ
    pass

