"""M10 테이퍼 스페이서 (사각뿔대 + 원뿔 교차형상) - CadQuery 파라메트릭 모델.

실행: python m10_spacer.py  ->  내경별 m10_spacer_ID*.step / .stl 생성
"""
import math
import cadquery as cq

# ---------------- 치수 (mm) ----------------
BOTTOM = 18.6          # 밑면 폭 (밑면은 지름 18.6 원형으로 마무리)
TOP = 12.0             # 윗면 사각 한 변
HEIGHT = 15.4          # 높이
HOLE_D = 10.5          # 기본 내경
HOLE_SIZES = [10.5, 10.0, 9.5, 9.0]   # 출력할 내경 목록
TOP_CORNER_D = TOP * math.sqrt(2) - 0.4   # 윗면 모서리 살짝 둥글게 (원뿔 윗지름)
HOLE_CHAMFER = 0.5     # 홀 입구 모따기

def make_spacer(hole_d=HOLE_D):
    # 1) 사각뿔대: 밑 18.6 사각 -> 위 12 사각
    frustum = (
        cq.Workplane("XY").rect(BOTTOM, BOTTOM)
        .workplane(offset=HEIGHT).rect(TOP, TOP)
        .loft(combine=True)
    )

    # 2) 원뿔: 밑 지름 18.6 -> 위 지름 ~16.6  (모서리를 깎아 너트 챔퍼 같은 곡선 경계를 만듦)
    cone = cq.Workplane("XY").add(
        cq.Solid.makeCone(BOTTOM / 2, TOP_CORNER_D / 2, HEIGHT)
    )

    body = frustum.intersect(cone)

    # 3) 관통 홀 + 위/아래 입구 모따기
    body = body.faces(">Z").workplane().hole(hole_d)
    hole_edges = [e for e in body.edges("%CIRCLE").vals()
                  if abs(e.radius() - hole_d / 2) < 1e-3]
    body = body.newObject(hole_edges).chamfer(HOLE_CHAMFER)
    return body


if __name__ == "__main__":
    for d in HOLE_SIZES:
        body = make_spacer(d)
        name = f"m10_spacer_ID{d:g}"
        cq.exporters.export(body, f"{name}.step")
        cq.exporters.export(body, f"{name}.stl", tolerance=0.01, angularTolerance=0.1)
        print(f"{name}: hole {d} mm, volume {body.val().Volume():.1f} mm^3")
