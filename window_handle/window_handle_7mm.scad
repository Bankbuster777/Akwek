// ============================================================
//  7mm 네모축(구동축)용 소형 창문 손잡이 - 3D 프린트용
//  Compact window handle for a 7 mm square spindle
//
//  좌표계: Z축 = 구동축 방향, z=0 = 창틀 쪽 면, z=hub_h = 바깥 면
//  출력 방향: 바깥 면(z=hub_h)을 베드에 붙여 "뒤집어서" 출력 → 서포트 불필요
//            (토크/레버 힘이 모두 레이어 평면 안에서 작용 → 층간 박리 없음)
// ============================================================

/* [구동축 / Spindle] */
spindle      = 7.0;    // 축 두께 (mm)
fit_clear    = 0.25;   // 구멍 여유 (프린터에 맞게 0.15~0.35 조정, 테스트 쿠폰 참고)
spindle_out  = 20;     // 창틀에서 나와 있는 축 길이
frame_gap    = 1.0;    // 손잡이와 창틀 사이 간격
socket_depth = spindle_out - frame_gap + 0.5;   // 19.5mm 물림 (축 거의 전체)

/* [허브 / Hub] */
hub_d   = 26;          // 허브 지름 (축 모서리에서 벽두께 약 8mm)
hub_h   = socket_depth + 4.5;   // 24mm, 끝 4.5mm는 막힌 캡
edge_r  = 1.6;         // 모서리 라운드

/* [레버 / Lever] */
lever_len  = 60;       // 축 중심 ~ 레버 끝 (원래 손잡이보다 훨씬 짧음)
lever_t    = 14;       // 레버 두께 (Z)
lever_w0   = 17;       // 레버 뿌리 폭
lever_w1   = 14;       // 레버 끝 폭
lever_mid  = 28;       // 테이퍼 시작 위치

/* [고정 나사 / Set screw] */
use_setscrew = true;
screw_d      = 2.8;    // M3 나사 직접 체결(셀프탭). 인서트 사용 시 4.0
screw_z      = 9;      // 창틀 쪽 면에서의 높이

/* [출력] */
part = "handle";       // handle | coupon | assembly | section | print
$fn  = 72;

// ---------- 기본 형상 ----------
// 모서리가 둥근 원판 (두 토러스의 hull)
module puck(r, h, e = edge_r) {
    hull() for (z = [e, h - e])
        translate([0, 0, z]) rotate_extrude($fn = $fn) translate([r - e, 0]) circle(e, $fn = 24);
}

// 모서리 응력완화 구멍이 있는 사각 소켓 (2D)
module square_socket_2d(s) {
    a = s / 2;
    square(s, center = true);
    // 코너 릴리프: 프린트 시 모서리가 둥글게 뭉쳐 축이 안 들어가는 문제 방지
    // + 응력 집중 완화. 힘은 평면부에서 전달됨.
    for (x = [-1, 1], y = [-1, 1]) translate([x * (a - 0.35), y * (a - 0.35)]) circle(0.75, $fn = 20);
}

module body() {
    lz = hub_h - lever_t;
    union() {
        puck(hub_d / 2, hub_h);
        // 허브-레버 연결부: hull 로 넓은 필렛(거셋) 형성 → 뿌리 응력 분산
        translate([0, 0, lz]) hull() {
            puck(hub_d / 2, lever_t);
            translate([0, -lever_mid, 0]) puck(lever_w0 / 2, lever_t);
        }
        translate([0, 0, lz]) hull() {
            translate([0, -lever_mid, 0]) puck(lever_w0 / 2, lever_t);
            translate([0, -(lever_len - lever_w1 / 2), 0]) puck(lever_w1 / 2, lever_t);
        }
    }
}

module handle() {
    s = spindle + fit_clear;
    difference() {
        body();
        // 소켓
        translate([0, 0, -0.01]) linear_extrude(socket_depth + 0.01) square_socket_2d(s);
        // 입구 챔퍼 (끼우기 쉽게)
        translate([0, 0, -0.01]) linear_extrude(1.0, scale = s / (s + 2)) square(s + 2, center = true);
        // 고정 나사 구멍 (레버 반대쪽)
        if (use_setscrew)
            translate([0, 0, screw_z]) rotate([-90, 0, 0]) cylinder(d = screw_d, h = hub_d, $fn = 24);
        // 바깥 면 방향 표시 홈 (레버 방향 화살표)
        translate([0, -2, hub_h - 0.6]) linear_extrude(1)
            polygon([[-3, 0], [3, 0], [0, -5]]);
    }
}

// 맞춤 테스트 쿠폰: 7.10 / 7.20 / 7.30 / 7.40
module coupon() {
    clears = [0.10, 0.20, 0.30, 0.40];
    difference() {
        hull() for (x = [0, 3 * 14]) translate([x, 0, 0]) cylinder(d = 13, h = 8);
        for (i = [0 : 3]) translate([i * 14, 0, -0.01]) {
            linear_extrude(8.1) square_socket_2d(spindle + clears[i]);
            translate([0, -6.6, 7.4]) linear_extrude(1) text(str(i + 1), size = 3, halign = "center", valign = "bottom");
        }
    }
}

// 창틀 + 구동축과 함께 보기
module assembly() {
    color("Gainsboro") translate([-25, -90, -frame_gap - 8]) cube([50, 130, 8]);
    color("Silver") translate([-spindle / 2, -spindle / 2, -frame_gap - 15]) cube([spindle, spindle, spindle_out + 15]);
    color("SteelBlue") handle();
}

// 단면 보기 (축 물림 확인용)
module section() {
    module cut() { intersection() { children(); translate([0, -100, -50]) cube([100, 200, 100]); } }
    color("Gainsboro") cut() translate([-25, -90, -frame_gap - 8]) cube([50, 130, 8]);
    color("DarkGray")  cut() translate([-spindle / 2, -spindle / 2, -frame_gap - 15]) cube([spindle, spindle, spindle_out + 15]);
    color("SteelBlue") cut() handle();
}

// 출력 자세: 바깥 면이 베드 쪽
module print_pose() { translate([0, 0, hub_h]) rotate([180, 0, 0]) handle(); }

if (part == "handle") handle();
else if (part == "coupon") coupon();
else if (part == "section") section();
else if (part == "print") print_pose();
else assembly();
