from __future__ import annotations

import html
from typing import Iterable

import streamlit as st

from modules.shared.models import CoachEvaluation, DNAProfile, MatchEvent, PenaltyResult


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --fv-bg: #05080f;
            --fv-panel: rgba(12, 18, 30, 0.92);
            --fv-panel-2: rgba(18, 27, 43, 0.94);
            --fv-line: rgba(112, 194, 255, 0.22);
            --fv-text: #f5f8ff;
            --fv-muted: #9ba8ba;
            --fv-cyan: #39d7ff;
            --fv-blue: #2374ff;
            --fv-green: #13b46b;
            --fv-gold: #d7b45a;
            --fv-silver: #cfd6e6;
        }

        .stApp {
            background:
                radial-gradient(circle at 25% 0%, rgba(35, 116, 255, 0.20), transparent 34%),
                linear-gradient(140deg, rgba(5, 8, 15, 0.96), rgba(2, 8, 8, 0.96)),
                repeating-linear-gradient(90deg, rgba(19,180,107,0.05) 0 2px, transparent 2px 80px);
            color: var(--fv-text);
        }

        .block-container {
            max-width: 1280px;
            padding-top: 1.4rem;
        }

        .fv-hero {
            position: relative;
            padding: 30px 32px;
            border: 1px solid var(--fv-line);
            background:
                linear-gradient(135deg, rgba(8, 14, 28, 0.92), rgba(5, 10, 16, 0.82)),
                repeating-linear-gradient(0deg, rgba(255,255,255,0.02) 0 1px, transparent 1px 44px);
            box-shadow: 0 24px 70px rgba(0, 0, 0, 0.32);
            margin-bottom: 20px;
            overflow: hidden;
        }

        .fv-hero::after {
            content: "";
            position: absolute;
            inset: auto -20% -35% -20%;
            height: 170px;
            background:
                linear-gradient(90deg, transparent, rgba(57, 215, 255, 0.20), transparent),
                repeating-linear-gradient(90deg, rgba(19, 180, 107, 0.32) 0 2px, transparent 2px 78px);
            opacity: 0.7;
        }

        .fv-kicker {
            color: var(--fv-cyan);
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .fv-title {
            color: var(--fv-text);
            font-size: clamp(2.2rem, 5vw, 4.4rem);
            line-height: 1.02;
            font-weight: 900;
            margin: 8px 0 8px;
            letter-spacing: 0;
        }

        .fv-subtitle {
            color: var(--fv-muted);
            max-width: 760px;
            font-size: 1.02rem;
            line-height: 1.7;
        }

        .fv-panel {
            border: 1px solid var(--fv-line);
            background: var(--fv-panel);
            padding: 20px;
            box-shadow: 0 20px 48px rgba(0, 0, 0, 0.22);
            margin-bottom: 16px;
        }

        .fv-card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: 14px;
            margin: 18px 0;
        }

        .fv-mode-card {
            min-height: 172px;
            border: 1px solid rgba(112, 194, 255, 0.24);
            background: linear-gradient(150deg, rgba(19, 27, 45, 0.96), rgba(7, 13, 22, 0.94));
            padding: 18px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .fv-mode-card h3,
        .fv-panel h3 {
            margin: 0 0 8px;
            font-size: 1rem;
            letter-spacing: 0;
            color: var(--fv-text);
        }

        .fv-mode-card p,
        .fv-panel p {
            color: var(--fv-muted);
            line-height: 1.55;
            margin: 0;
        }

        .fv-stat-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
            gap: 10px;
            margin: 14px 0;
        }

        .fv-stat {
            border: 1px solid rgba(207, 214, 230, 0.16);
            background: rgba(255,255,255,0.035);
            padding: 12px;
        }

        .fv-stat b {
            display: block;
            color: var(--fv-text);
            font-size: 1.35rem;
        }

        .fv-stat span {
            color: var(--fv-muted);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }

        .fv-dna-card,
        .fv-coach-card {
            position: relative;
            max-width: 430px;
            min-height: 560px;
            border: 1px solid rgba(215, 180, 90, 0.52);
            background:
                linear-gradient(150deg, rgba(215,180,90,0.22), transparent 24%),
                linear-gradient(160deg, #111827, #06111a 58%, #05080f);
            padding: 24px;
            box-shadow: 0 34px 80px rgba(0, 0, 0, 0.42);
            animation: fvReveal 620ms ease-out both;
            overflow: hidden;
        }

        .fv-dna-card::before,
        .fv-coach-card::before {
            content: "";
            position: absolute;
            inset: 12px;
            border: 1px solid rgba(255,255,255,0.11);
            pointer-events: none;
        }

        .fv-card-label {
            color: var(--fv-gold);
            font-weight: 800;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            font-size: 0.78rem;
        }

        .fv-card-name {
            font-size: 2.05rem;
            font-weight: 900;
            line-height: 1.05;
            margin: 10px 0 16px;
            color: var(--fv-text);
        }

        .fv-rating {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255,255,255,0.12);
            padding: 8px 0;
        }

        .fv-rating span:first-child {
            color: var(--fv-muted);
        }

        .fv-rating span:last-child {
            color: var(--fv-text);
            font-weight: 900;
            font-size: 1.15rem;
        }

        .fv-pill {
            display: inline-block;
            border: 1px solid rgba(57, 215, 255, 0.42);
            color: var(--fv-cyan);
            background: rgba(57, 215, 255, 0.08);
            padding: 7px 10px;
            margin: 6px 6px 0 0;
            font-size: 0.82rem;
            font-weight: 700;
        }

        .fv-timeline {
            border-left: 2px solid rgba(57, 215, 255, 0.35);
            padding-left: 16px;
        }

        .fv-event {
            position: relative;
            margin: 0 0 14px;
            padding: 12px 14px;
            border: 1px solid rgba(112, 194, 255, 0.18);
            background: rgba(255,255,255,0.035);
            animation: fvSlide 420ms ease-out both;
        }

        .fv-event::before {
            content: "";
            position: absolute;
            width: 9px;
            height: 9px;
            border-radius: 50%;
            background: var(--fv-cyan);
            left: -22px;
            top: 18px;
        }

        button[kind="primary"], .stButton > button {
            border-radius: 0;
            border: 1px solid rgba(57, 215, 255, 0.36);
            background: linear-gradient(135deg, #0e5dff, #18bfd6);
            color: white;
            font-weight: 800;
        }

        .stTextInput input,
        .stSelectbox div[data-baseweb="select"],
        .stTextArea textarea,
        .stNumberInput input {
            border-radius: 0;
        }

        @keyframes fvReveal {
            from { opacity: 0; transform: translateY(16px) scale(0.98); filter: blur(6px); }
            to { opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }
        }

        @keyframes fvSlide {
            from { opacity: 0; transform: translateX(-10px); }
            to { opacity: 1; transform: translateX(0); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero() -> None:
    st.markdown(
        """
        <section class="fv-hero">
            <div class="fv-kicker">AI Football Ecosystem</div>
            <div class="fv-title">FootballVerse AI</div>
            <div class="fv-subtitle">
                Discover your football identity, prove it inside a browser-based penalty arena,
                then step onto the tactics board as a coach. Built web-first for localhost demos,
                fairs, project showcases, and future production migration.
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def mode_cards() -> None:
    st.markdown(
        """
        <div class="fv-card-grid">
            <div class="fv-mode-card">
                <div>
                    <h3>Player Mode</h3>
                    <p>Football DNA, personalized challenges, gesture-mapped shots, AI keeper, and post-match report card.</p>
                </div>
                <div class="fv-pill">Discover</div>
            </div>
            <div class="fv-mode-card">
                <div>
                    <h3>Coach Mode</h3>
                    <p>Tactical crisis, formation decisions, AI evaluation, match simulation, and manager card.</p>
                </div>
                <div class="fv-pill">Coach</div>
            </div>
            <div class="fv-mode-card">
                <div>
                    <h3>Rewards</h3>
                    <p>Student check-in, ranked leaderboard, prize tiers, and fair-ready demo mode.</p>
                </div>
                <div class="fv-pill">Compete</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dna_card(profile: DNAProfile) -> None:
    ratings = "".join(
        f'<div class="fv-rating"><span>{html.escape(label)}</span><span>{value}</span></div>'
        for label, value in profile.ratings.items()
    )
    challenges = "".join(f'<span class="fv-pill">{html.escape(item)}</span>' for item in profile.challenges)
    st.markdown(
        f"""
        <div class="fv-dna-card">
            <div class="fv-card-label">Football DNA</div>
            <div class="fv-card-name">{html.escape(profile.footballer)} Type</div>
            <div class="fv-pill">{html.escape(profile.archetype)}</div>
            <div class="fv-pill">{html.escape(profile.suggested_position)}</div>
            <div style="height:18px"></div>
            {ratings}
            <div style="height:18px"></div>
            <div class="fv-card-label">Special Ability</div>
            <h3>{html.escape(profile.special_ability)}</h3>
            <p><b>Strength:</b> {html.escape(profile.strength)}<br>
            <b>Weakness:</b> {html.escape(profile.weakness)}</p>
            <div style="height:14px"></div>
            {challenges}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_coach_card(evaluation: CoachEvaluation) -> None:
    ratings = {
        "Attack": evaluation.attack,
        "Defense": evaluation.defense,
        "Creativity": evaluation.creativity,
        "Risk": evaluation.risk,
        "Possession": evaluation.possession,
    }
    rows = "".join(
        f'<div class="fv-rating"><span>{label}</span><span>{value}</span></div>' for label, value in ratings.items()
    )
    st.markdown(
        f"""
        <div class="fv-coach-card">
            <div class="fv-card-label">Coach Profile</div>
            <div class="fv-card-name">{html.escape(evaluation.rank)}</div>
            <div class="fv-pill">Score {evaluation.coach_score}</div>
            <div style="height:18px"></div>
            {rows}
            <div style="height:18px"></div>
            <p>{html.escape(evaluation.summary)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_penalty_pitch(result: PenaltyResult | None) -> None:
    if result is None:
        ball_x, ball_y = 50, 86
        keeper_x = 50
        label = "Awaiting shot"
        color = "#cfd6e6"
    else:
        target_positions = {
            "Left Corner": (25, 34),
            "Right Corner": (75, 34),
            "Top Corner": (50, 24),
            "Low Shot": (50, 58),
            "Panenka": (50, 42),
            "Power Shot": (50, 30),
            "Curve Shot": (72, 29),
        }
        ball_x, ball_y = target_positions.get(result.target, (50, 42))
        keeper_x = {"Left Corner": 28, "Right Corner": 72, "Top Corner": 50, "Low Shot": 50}.get(result.keeper_guess, 50)
        label = "GOAL" if result.success else "SAVED"
        color = "#13b46b" if result.success else "#d94e4e"

    st.markdown(
        f"""
        <svg viewBox="0 0 900 520" width="100%" role="img" aria-label="Browser penalty arena">
            <defs>
                <linearGradient id="pitch" x1="0" x2="1">
                    <stop stop-color="#08351f"/>
                    <stop offset="1" stop-color="#0c5d38"/>
                </linearGradient>
                <filter id="shadow" x="-30%" y="-30%" width="160%" height="160%">
                    <feDropShadow dx="0" dy="10" stdDeviation="10" flood-color="#000" flood-opacity="0.35"/>
                </filter>
            </defs>
            <rect x="0" y="0" width="900" height="520" fill="#05080f"/>
            <rect x="32" y="35" width="836" height="450" fill="url(#pitch)" stroke="rgba(255,255,255,.28)" stroke-width="2"/>
            <g opacity=".18">
                <path d="M32 95 H868 M32 155 H868 M32 215 H868 M32 275 H868 M32 335 H868 M32 395 H868" stroke="#fff"/>
                <path d="M110 35 V485 M190 35 V485 M270 35 V485 M350 35 V485 M430 35 V485 M510 35 V485 M590 35 V485 M670 35 V485 M750 35 V485" stroke="#fff"/>
            </g>
            <rect x="248" y="70" width="404" height="138" fill="rgba(0,0,0,.16)" stroke="#f5f8ff" stroke-width="6"/>
            <rect x="292" y="105" width="316" height="103" fill="none" stroke="rgba(255,255,255,.28)" stroke-width="2"/>
            <circle cx="{keeper_x * 9}" cy="179" r="24" fill="#39d7ff" filter="url(#shadow)">
                <animate attributeName="cx" dur=".38s" to="{keeper_x * 9}" fill="freeze" />
            </circle>
            <rect x="{keeper_x * 9 - 44}" y="205" width="88" height="16" rx="8" fill="#39d7ff" opacity=".8"/>
            <line x1="450" y1="445" x2="{ball_x * 9}" y2="{ball_y * 5.2}" stroke="#d7b45a" stroke-width="3" stroke-dasharray="8 9" opacity=".8"/>
            <circle cx="{ball_x * 9}" cy="{ball_y * 5.2}" r="17" fill="#f5f8ff" stroke="#111827" stroke-width="5" filter="url(#shadow)">
                <animate attributeName="r" from="8" to="17" dur=".42s" fill="freeze" />
            </circle>
            <text x="450" y="36" text-anchor="middle" fill="{color}" font-size="30" font-weight="900">{label}</text>
        </svg>
        """,
        unsafe_allow_html=True,
    )


def render_tactical_board(formation: str) -> None:
    layouts = {
        "4-3-3": [(50, 88), (18, 68), (38, 70), (62, 70), (82, 68), (30, 50), (50, 46), (70, 50), (22, 26), (50, 20), (78, 26)],
        "4-2-3-1": [(50, 88), (18, 68), (38, 70), (62, 70), (82, 68), (40, 52), (60, 52), (24, 34), (50, 32), (76, 34), (50, 18)],
        "3-4-3": [(50, 88), (30, 70), (50, 72), (70, 70), (18, 50), (40, 48), (60, 48), (82, 50), (24, 26), (50, 18), (76, 26)],
        "3-5-2": [(50, 88), (30, 70), (50, 72), (70, 70), (16, 52), (34, 46), (50, 42), (66, 46), (84, 52), (40, 20), (60, 20)],
        "5-3-2": [(50, 88), (12, 68), (30, 72), (50, 73), (70, 72), (88, 68), (32, 48), (50, 44), (68, 48), (40, 20), (60, 20)],
    }
    points = layouts.get(formation, layouts["4-3-3"])
    players = "".join(
        f'<circle cx="{x * 7.8}" cy="{y * 4.5}" r="16" fill="#39d7ff" stroke="#fff" stroke-width="3" />'
        f'<text x="{x * 7.8}" y="{y * 4.5 + 5}" text-anchor="middle" fill="#06111a" font-size="12" font-weight="900">{idx}</text>'
        for idx, (x, y) in enumerate(points, start=1)
    )
    st.markdown(
        f"""
        <svg viewBox="0 0 780 450" width="100%" role="img" aria-label="Tactical board">
            <rect width="780" height="450" fill="#082f1c"/>
            <rect x="28" y="22" width="724" height="406" fill="none" stroke="rgba(255,255,255,.55)" stroke-width="3"/>
            <line x1="28" y1="225" x2="752" y2="225" stroke="rgba(255,255,255,.35)" stroke-width="2"/>
            <circle cx="390" cy="225" r="54" fill="none" stroke="rgba(255,255,255,.35)" stroke-width="2"/>
            <rect x="235" y="22" width="310" height="95" fill="none" stroke="rgba(255,255,255,.35)" stroke-width="2"/>
            <rect x="235" y="333" width="310" height="95" fill="none" stroke="rgba(255,255,255,.35)" stroke-width="2"/>
            {players}
            <text x="390" y="28" text-anchor="middle" fill="#d7b45a" font-size="18" font-weight="900">{html.escape(formation)}</text>
        </svg>
        """,
        unsafe_allow_html=True,
    )


def render_timeline(events: Iterable[MatchEvent]) -> None:
    rendered = []
    for event in events:
        rendered.append(
            f"""
            <div class="fv-event">
                <b>{html.escape(event.minute)} - {html.escape(event.title)}</b>
                <p>{html.escape(event.detail)}</p>
            </div>
            """
        )
    st.markdown(f'<div class="fv-timeline">{"".join(rendered)}</div>', unsafe_allow_html=True)

