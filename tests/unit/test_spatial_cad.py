from arsenal.spatial.cad.dxf_exporter import export_dxf
from arsenal.spatial.cad.kinematic_blocks import apply_block_state


def test_dxf_exporter_and_kinematic_blocks():
    layers = {"L1": [(0.0, 0.0), (1.0, 1.0)], "L2": [(2.0, 2.0)]}
    out = export_dxf(layers)
    assert "SECTION" in out and "POINT" in out

    blocks = {"arm": {"state": "STOWED"}}
    ns = apply_block_state(blocks, {"arm": "DEPLOYED"})
    assert ns["arm"]["state"] == "DEPLOYED"
