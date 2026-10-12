"""No framework, no model: call the OKF tools directly.

pip install astromesh-okf
"""

from pathlib import Path

from astromesh_okf import OKFTools

tools = OKFTools(Path(__file__).parent / "bundles" / "support")

if __name__ == "__main__":
    print(tools.kb_index("/"))
    print(tools.kb_find(text="refund"))
    print(tools.kb_read("policies/refunds"))
