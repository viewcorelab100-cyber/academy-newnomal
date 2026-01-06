# 랜딩 페이지 (Landing Page)

## 개요
애플리케이션의 첫 진입 화면으로, 사용자의 역할(관리자/학생)을 선택하는 미니멀한 퍼즐 컨셉의 페이지입니다.

## 디자인 컨셉
- **퍼즐 & 타일 (Puzzle & Tile)**: '학원 관리의 조각을 맞추다'는 메타포를 시각적으로 구현.
  - 관리자 카드: 상단 돌출 (Puzzle Tab)
  - 학생 카드: 상단 홈 (Puzzle Slot)
- **미니멀리즘 (Minimalism)**: 불필요한 네비게이션, 푸터, 기능 목록을 모두 제거하고 로그인 선택에만 집중.
- **인터랙션 (Interaction)**: 마우스 호버 시 카드가 떠오르는 듯한 효과(Lift)와 아이콘 확대 효과 적용.

## 구성 요소
1. **헤더 섹션**
   - Main Copy: "ACADEMY NEW NORMAL" (그라디언트 텍스트)
   - Sub Copy: "교육 관리의 새로운 기준을 조립하다"
   
2. **로그인 선택 카드**
   - **관리자 로그인**: `/admin/login` 으로 이동. 관리자/강사 전용.
   - **학생 로그인**: `/student/dashboard` 로 이동. 학생/학부모 전용.

## 기술 스택
- **HTML/Jinja2**: 템플릿 구조
- **Tailwind CSS**: 스타일링 (Glassmorphism, Gradients, Shadows)
- **Lucide Icons**: 아이콘 (`layout-dashboard`, `shield-check`, `graduation-cap`)
- **Vanilla JS**: 배경 Parallax 효과 (마우스 움직임 반응)

## 변경 이력
- **2025-12-26**: 기존의 복잡한 정보성 랜딩 페이지를 퍼즐 컨셉의 심플한 게이트웨이 페이지로 리디자인.



