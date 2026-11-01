"""Build an annotated design sheet (PNG) from the STL + OpenSCAD renders."""
import sys, numpy as np, trimesh, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Rectangle, Polygon
import matplotlib.image as mpimg

D = sys.argv[1] if len(sys.argv) > 1 else "."
for f in fm.findSystemFonts():
    if "NanumGothic" in f or "NanumSquareRound" in f:
        fm.fontManager.addfont(f)
names = {f.name for f in fm.fontManager.ttflist}
plt.rcParams["font.family"] = next((n for n in ["NanumGothic", "NanumSquareRound"] if n in names), "DejaVu Sans")

m = trimesh.load(f"{D}/window_handle_7mm.stl")
SP, GAP, OUT = 7.0, 1.0, 20.0
BLUE, GREY, FRAME = "#3f7bbf", "#8a8a8a", "#dcdcdc"

def fill_section(ax, origin, normal, to2d):
    sec = m.section(plane_origin=origin, plane_normal=normal)
    for ent in sec.discrete:
        pts = np.array([to2d(p) for p in ent])
        ax.fill(pts[:, 0], pts[:, 1], color=BLUE, alpha=0.9, lw=0)
        ax.plot(pts[:, 0], pts[:, 1], color="#1d3f66", lw=1)

def dim(ax, a, b, txt, off=(0, 0), **kw):
    ax.annotate("", a, b, arrowprops=dict(arrowstyle="<->", color="k", lw=1))
    ax.text((a[0] + b[0]) / 2 + off[0], (a[1] + b[1]) / 2 + off[1], txt, ha="center", va="center", fontsize=10,
            bbox=dict(fc="white", ec="none", pad=1), **kw)

fig = plt.figure(figsize=(16, 11), dpi=110)
fig.suptitle("7mm 네모축용 소형 창문 손잡이 (3D 프린트)", fontsize=20, weight="bold")

ax = fig.add_subplot(2, 2, 1); ax.imshow(mpimg.imread(f"{D}/images/assembly.png")[90:820, 80:1150]); ax.axis("off")
ax.set_title("① 창틀에 끼운 모습 (축 중심에서 레버 끝 80mm)", fontsize=13)

# ② side section (plane x=0): horizontal = -y (lever direction), vertical = z
ax = fig.add_subplot(2, 2, 2)
ax.add_patch(Rectangle((-30, -GAP - 8), 122, 8, color=FRAME)); ax.text(75, -GAP - 4, "창틀", ha="center", va="center", fontsize=11)
ax.add_patch(Rectangle((-SP / 2, -GAP - 12), SP, OUT + 12, color=GREY, alpha=0.85))
fill_section(ax, [0, 0, 0], [1, 0, 0], lambda p: (-p[1], p[2]))
ax.add_patch(Rectangle((-SP / 2, -GAP), SP, OUT, fill=False, ec="k", ls="--", lw=0.8))
dim(ax, (-17, -GAP), (-17, OUT - GAP), "축 20mm", off=(-3.5, 0), rotation=90)
dim(ax, (6, 0), (6, 19.5), "물림 19.5", off=(5.5, 0), rotation=90)
dim(ax, (84, 11.5), (84, 24), "12.5", off=(4, 0))
dim(ax, (0, 27), (80, 27), "80 (축 중심~끝)", off=(0, 2))
ax.annotate("M3x8 접시머리 볼트\n(머리 1.9mm 묻힘)", (-11, 9), (-44, 28), fontsize=10, arrowprops=dict(arrowstyle="->"))
ax.annotate("손가락 공간 11~12.5mm", (45, 4.5), (45, -3), fontsize=10, ha="center")
ax.annotate("끝단 4.5mm 막힘 캡", (0, 22), (12, 33), fontsize=10, arrowprops=dict(arrowstyle="->"))
ax.set_aspect("equal"); ax.set_xlim(-46, 92); ax.set_ylim(-14, 38); ax.axis("off")
ax.set_title("② 단면 (회색 = 7mm 구동축)", fontsize=13)

# ③ cross-section through hub at z = 9 (screw level)
ax = fig.add_subplot(2, 2, 3)
fill_section(ax, [0, 0, 9], [0, 0, 1], lambda p: (p[0], p[1]))
ax.add_patch(Rectangle((-SP / 2, -SP / 2), SP, SP, color=GREY))
dim(ax, (-SP / 2, -6), (SP / 2, -6), "7.25", off=(0, -1.6))
dim(ax, (SP / 2 + 0.6, 0), (13, 0), "벽 9", off=(0, 1.6))
dim(ax, (-13, 17), (13, 17), "허브 Ø26", off=(0, 1.6))
ax.annotate("모서리 릴리프\n(응력집중 방지,\n출력 뭉침 방지)", (-3.6, 3.6), (-30, 8), fontsize=10, arrowprops=dict(arrowstyle="->"))
ax.annotate("접시머리 자리 (90°, Ø7)", (2, 11.5), (13, 12), fontsize=10, arrowprops=dict(arrowstyle="->"))
ax.text(0, -18, "↓ 레버 방향 (레버는 z=10mm 위쪽에 있어 이 단면엔 안 보임)", ha="center", fontsize=10)
ax.set_aspect("equal"); ax.set_xlim(-34, 34); ax.set_ylim(-24, 22); ax.axis("off")
ax.set_title("③ 허브 단면 (z=9mm, 나사 높이)", fontsize=13)

ax = fig.add_subplot(2, 2, 4); ax.axis("off")
ax.imshow(mpimg.imread(f"{D}/images/back_socket.png")[60:900, 280:1020], extent=(0, 0.42, 0.25, 1)); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
txt = ("힘을 견디는 설계 포인트\n"
       "• 축 20mm 중 19.5mm 물림 → 접촉면적 최대\n"
       "• 축 모서리 기준 벽 두께 ≈ 8mm (허브 Ø26)\n"
       "• 사각 구멍 모서리 릴리프 → 크랙 시작점 제거\n"
       "• 허브-레버 연결부 넓은 필렛(거셋)\n"
       "• 그립: 허리 15mm → 손바닥 20mm, 모서리 R3\n"
       "• 바깥면을 베드에 두고 출력:\n"
       "   돌리는 힘이 레이어 평면 안 → 층 분리 X\n\n"
       "추천 출력 설정\n"
       "• PETG / ASA / PA-CF  (PLA 비추천)\n"
       "• 벽 6줄, 상하 6층, 인필 50%+ 자이로이드\n"
       "• 먼저 맞춤 쿠폰(7.1~7.4) 출력해 공차 선택\n\n"
       "대략 계산 (PETG, 그립 중앙 100N ≈ 10kgf → 6.5N·m)\n"
       "• 레버 뿌리 굽힘응력 ≈ 8MPa  (안전율 ≈ 5.5)\n"
       "• 소켓 면압 ≈ 21MPa  (안전율 ≈ 2.6) ← 가장 약한 곳")
ax.text(0.45, 0.98, txt, va="top", fontsize=11.5, linespacing=1.45)
ax.set_title("④ 소켓(창틀 쪽) / 설계·출력 메모", fontsize=13)

plt.tight_layout(rect=(0, 0, 1, 0.95))
plt.savefig(f"{D}/images/design_sheet.png")
