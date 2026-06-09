from __future__ import annotations

import html
import random
import re
import sqlite3

import streamlit as st

from modules.coach_mode.tactics import evaluate_plan, generate_scenario
from modules.commentary.engine import COMMENTARY_STYLES, generate_commentary
from modules.football_dna.engine import generate_dna
from modules.gestures.engine import cv_status, map_gesture_to_shot, supported_gestures
from modules.leaderboard.store import LeaderboardStore, reward_tier
from modules.player_mode.penalty import play_penalty
from modules.reports.engine import accuracy, average_reaction, best_skill, player_score, radar_chart
from modules.shared.config import APP_TAGLINE, APP_TITLE, DATABASE_PATH
from modules.shared.models import Student, TacticalPlan
from modules.shared.ui import (
    apply_theme,
    hero,
    mode_cards,
    render_coach_card,
    render_dna_card,
    render_penalty_pitch,
    render_tactical_board,
    render_timeline,
)
from modules.simulation.engine import simulate_match


st.set_page_config(
    page_title="FootballVerse AI",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()


@st.cache_resource
def store() -> LeaderboardStore:
    return LeaderboardStore(DATABASE_PATH)


def main() -> None:
    _init_session()
    with st.sidebar:
        st.markdown(f"### {APP_TITLE}")
        st.caption(APP_TAGLINE)
        page = st.radio(
            "Navigate",
            [
                "Launch",
                "Player Mode",
                "Coach Mode",
                "Reports",
                "Check-In & Rewards",
                "Demo Mode",
                "System",
            ],
        )
        student = current_student()
        if student:
            st.success(f"{student.name} | {student.student_id}")
        else:
            st.info("Check in before saving scores.")

    if page == "Launch":
        page_launch()
    elif page == "Player Mode":
        page_player_mode()
    elif page == "Coach Mode":
        page_coach_mode()
    elif page == "Reports":
        page_reports()
    elif page == "Check-In & Rewards":
        page_rewards()
    elif page == "Demo Mode":
        page_demo()
    else:
        page_system()


def _init_session() -> None:
    defaults = {
        "student": None,
        "dna_profile": None,
        "penalties": [],
        "last_penalty": None,
        "commentary": [],
        "commentary_style": "Professional",
        "coach_scenario": None,
        "coach_evaluation": None,
        "match_simulation": None,
        "last_saved_player_score": None,
        "last_saved_coach_score": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def current_student() -> Student | None:
    data = st.session_state.get("student")
    if isinstance(data, Student):
        return data
    return None


def student_check_in(compact: bool = False) -> Student | None:
    student = current_student()
    if student and compact:
        st.markdown(
            f"""
            <div class="fv-panel">
                <h3>Active Student</h3>
                <p>{student.name} | {student.student_id}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return student

    with st.form("student_check_in"):
        st.subheader("Student Check-In")
        st.caption("Scores and prize eligibility are attached to this student identity.")
        student_id = st.text_input("Student ID", value=student.student_id if student else "")
        name = st.text_input("Name", value=student.name if student else "")
        submitted = st.form_submit_button("Start Session", type="primary")
        if submitted:
            if not student_id.strip() or not name.strip():
                st.error("Enter both student ID and name before playing.")
            elif not _validate_student_id(student_id):
                st.error("Student ID must be 3-20 characters (letters, numbers, hyphens, underscores only).")
            elif len(name.strip()) > 100:
                st.error("Name must be less than 100 characters.")
            else:
                try:
                    active_student = Student(student_id=student_id.strip(), name=name.strip())
                    store().register_student(active_student)
                    st.session_state.student = active_student
                    st.success("Student registered for leaderboard and prize tracking.")
                    return active_student
                except sqlite3.IntegrityError:
                    st.error("Student ID already registered. Use the same ID or try a different one.")
                except Exception as e:
                    st.error(f"Registration failed. Please try again.")
    return student


def _validate_student_id(student_id: str) -> bool:
    """Validate student ID format: alphanumeric, hyphens, underscores, 3-20 chars."""
    return bool(re.match(r"^[A-Za-z0-9_-]{3,20}$", student_id.strip()))


def page_launch() -> None:
    """Main landing page with onboarding and mode selection."""
    hero()
    
    # Onboarding section for first-time users
    st.markdown(
        """
        <div class="fv-panel" style="background-color: rgba(33, 150, 243, 0.1); border-left: 4px solid #2196F3;">
            <h3>🎯 How to Play</h3>
            <p><b>Player Mode:</b> Answer football questions → Get your Football DNA (match a world-class footballer) → 
            Take penalty shots with increasing difficulty → Get a personalized report card</p>
            <p><b>Coach Mode:</b> Analyze a tactical match scenario → Build your formation and strategy → 
            See how well your plan would work → Get a coaching rank and score</p>
            <p><em>💡 Tip: Try Demo Mode first to see both experiences without registration!</em></p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    mode_cards()
    
    left, right = st.columns([1, 1])
    with left:
        with st.expander("📝 Student Check-In", expanded=True):
            st.caption("Register to save scores and compete on the leaderboard")
            student_check_in()
    
    with right:
        st.markdown(
            """
            <div class="fv-panel">
                <h3>⚡ Quick Start</h3>
                <ol>
                    <li><b>Check In:</b> Enter your Student ID and Name (left panel)</li>
                    <li><b>Choose a Mode:</b> Player Mode or Coach Mode (above)</li>
                    <li><b>Complete:</b> Finish the experience</li>
                    <li><b>Save:</b> Your score is saved to the leaderboard</li>
                    <li><b>Rewards:</b> Check the leaderboard for prizes</li>
                </ol>
                <hr style="margin: 1rem 0;">
                <b>🎮 First Time?</b> Try Demo Mode (in sidebar) to see both modes without registering.
            </div>
            """,
            unsafe_allow_html=True,
        )


def page_player_mode() -> None:
    st.title("Player Mode")
    student_check_in(compact=True)
    st.markdown(
        """
        <div class="fv-panel">
            <h3>🔍 Football Identity Scanner</h3>
            <p>Answer 5 quick questions about your football style → Discover which world-class footballer you match → 
            Take penalty shots → Get a detailed performance report!</p>
            <p><em>Current Version: Web UI controls | Future: Gesture recognition via camera (v2.0)</em></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.dna_profile is None:
        st.markdown("### Step 1: Generate Your Football DNA")
        st.markdown("_Answer these 5 questions about your football style:_")
        
        with st.form("dna_form"):
            col1, col2 = st.columns(2)
            with col1:
                style = st.selectbox("❓ Do you prefer passing or shooting?", ["Passing", "Shooting", "Balanced"])
                st.caption("Passing → Creative build-up | Shooting → Direct finishing")
                
                risk = st.selectbox("❓ Do you take risks?", ["Safe control", "Calculated risks", "High risk"])
                st.caption("Safe → Keep possession | High → Attack aggressively")
                
                role = st.selectbox("❓ Attack or defense?", ["Attack", "Defense", "Both"])
                
            with col2:
                teamwork = st.selectbox(
                    "❓ Teamwork or individual brilliance?",
                    ["Teamwork", "Individual brilliance", "Depends on the match"],
                )
                
                moment = st.selectbox(
                    "❓ Favorite football moment?",
                    ["Perfect assist", "Last-minute winner", "Skill move", "Counter attack", "Dominant press"],
                )
                
                expression = st.selectbox("🎥 Camera expression signal", ["focused", "confident", "creative", "intense"])
                st.caption("How you look: determined, confident, playful, or intense")
                
            submitted = st.form_submit_button("✨ Generate Football DNA", type="primary")
            if submitted:
                st.session_state.dna_profile = generate_dna(
                    {
                        "style": style,
                        "risk": risk,
                        "role": role,
                        "teamwork": teamwork,
                        "moment": moment,
                    },
                    expression_signal=expression,
                )
                st.session_state.penalties = []
                st.session_state.commentary = []
                st.session_state.last_penalty = None
                st.rerun()

    profile = st.session_state.dna_profile
    if profile is None:
        return

    card_col, arena_col = st.columns([0.9, 1.35])
    with card_col:
        render_dna_card(profile)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Reset DNA", help="Clear your Football DNA and start over"):
                st.session_state.dna_profile = None
                st.session_state.penalties = []
            st.session_state.commentary = []
            st.session_state.last_penalty = None
            st.rerun()

    with arena_col:
        st.subheader("Browser Penalty Arena")
        st.session_state.commentary_style = st.selectbox(
            "Commentator",
            COMMENTARY_STYLES,
            index=COMMENTARY_STYLES.index(st.session_state.commentary_style),
        )
        render_penalty_pitch(st.session_state.last_penalty)
        _shot_controls(profile)
        _player_scoreboard(profile)


def _shot_controls(profile) -> None:
    shots_taken = len(st.session_state.penalties)
    shots_remaining = 5 - shots_taken
    goals = sum(1 for result in st.session_state.penalties if result.success)
    
    if shots_remaining > 0:
        # Shot counter display
        st.markdown(
            f"""
            <div style="background: linear-gradient(90deg, #4CAF50 0%, #2196F3 100%); 
                        padding: 1rem; border-radius: 8px; color: white; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; font-weight: bold;">
                    <span>⚽ Goals: {goals} / {shots_taken}</span>
                    <span>📊 Shots Remaining: {shots_remaining} / 5</span>
                </div>
                <div style="margin-top: 0.5rem; font-size: 0.9rem;">
                    Success Rate: {round(100 * goals / shots_taken, 1) if shots_taken > 0 else 0}% | 
                    Difficulty: {round((shots_taken * 0.055 + 0.26), 2)}/0.82
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    if shots_remaining <= 0:
        st.success(f"✅ Five shots completed! Final Score: {goals} goals out of 5 shots")
        st.info("Save your result to the leaderboard or reset for another round.")
        return

    st.markdown(f"### Step 2: Take Your Shots ({shots_taken + 1}/5)")
    st.markdown("_Click a shot type to attempt it. Each shot gets harder as you score more goals._")
    
    gestures = supported_gestures()
    columns = st.columns(3)
    for index, gesture in enumerate(gestures):
        shot = map_gesture_to_shot(gesture)
        with columns[index % 3]:
            if st.button(f"{gesture}\n→ {shot}", key=f"shot_{gesture}", use_container_width=True):
                _take_shot(shot, profile)
                st.rerun()

    # Signature ability button (if not already in gesture list)
    if profile.special_ability not in [map_gesture_to_shot(gesture) for gesture in gestures]:
        st.markdown("### Special Ability")
        if st.button(f"⭐ {profile.special_ability}", key="signature_shot", use_container_width=True):
            st.markdown(f"_Bonus: +15% success rate and +45 points if you score_")
            _take_shot(profile.special_ability, profile)
            st.rerun()



def _take_shot(shot: str, profile) -> None:
    previous = [result.shot for result in st.session_state.penalties]
    goals = sum(1 for result in st.session_state.penalties if result.success)
    result = play_penalty(shot, profile, previous, goals)
    st.session_state.penalties.append(result)
    st.session_state.last_penalty = result
    st.session_state.commentary.append(
        generate_commentary(result.commentary_event, st.session_state.commentary_style)
    )


def _player_scoreboard(profile) -> None:
    results = st.session_state.penalties
    goals = sum(1 for result in results if result.success)
    score = player_score(results)
    acc = accuracy(results)
    reaction = average_reaction(results)
    st.markdown(
        f"""
        <div class="fv-stat-row">
            <div class="fv-stat"><b>{goals}/5</b><span>Goals</span></div>
            <div class="fv-stat"><b>{acc}%</b><span>Accuracy</span></div>
            <div class="fv-stat"><b>{reaction}s</b><span>Reaction</span></div>
            <div class="fv-stat"><b>{score}</b><span>Score</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.commentary:
        st.subheader("Commentary Chaos")
        for line in reversed(st.session_state.commentary[-4:]):
            st.write(line)

    if len(results) >= 5:
        student = current_student()
        if student is None:
            st.warning("Check in with student ID and name before saving to the prize leaderboard.")
            return
        if st.button("Save Player Result to Leaderboard", type="primary"):
            store().save_player_score(
                student,
                final_score=score,
                dna=profile.footballer,
                goals=goals,
                accuracy=acc,
            )
            st.session_state.last_saved_player_score = score
            st.success(f"Saved Player Mode score: {score}. Prize tier: {reward_tier(score)}.")


def page_coach_mode() -> None:
    st.title("Coach Mode")
    student_check_in(compact=True)
    if st.session_state.coach_scenario is None:
        st.session_state.coach_scenario = generate_scenario()

    scenario = st.session_state.coach_scenario
    st.markdown(
        f"""
        <div class="fv-panel">
            <h3>Tactical Crisis</h3>
            <p><b>{scenario.minute}'</b> | Score {scenario.current_score} | Opponent {scenario.opponent_shape}
            | Style {scenario.opponent_style} | Objective: {scenario.objective}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Generate New Scenario"):
        st.session_state.coach_scenario = generate_scenario()
        st.session_state.coach_evaluation = None
        st.session_state.match_simulation = None
        st.rerun()

    form_col, board_col = st.columns([0.9, 1.1])
    with form_col:
        with st.form("tactical_plan"):
            formation = st.selectbox("Formation", ["4-3-3", "4-2-3-1", "3-4-3", "3-5-2", "5-3-2"])
            pressing = st.slider("Pressing Intensity", 0, 100, 68)
            fullbacks = st.slider("Fullback Aggression", 0, 100, 58)
            extra_striker = st.checkbox("Add Extra Striker", value=True)
            tempo = st.slider("Tempo", 0, 100, 72)
            defensive_line = st.slider("Defensive Line", 0, 100, 64)
            risk_tolerance = st.slider("Risk Tolerance", 0, 100, 70)
            submitted = st.form_submit_button("Simulate Match", type="primary")
            if submitted:
                plan = TacticalPlan(
                    formation=formation,
                    pressing=pressing,
                    fullbacks=fullbacks,
                    extra_striker=extra_striker,
                    tempo=tempo,
                    defensive_line=defensive_line,
                    risk_tolerance=risk_tolerance,
                )
                st.session_state.coach_evaluation = evaluate_plan(scenario, plan)
                st.session_state.match_simulation = simulate_match(scenario, st.session_state.coach_evaluation)
                st.session_state.active_formation = formation
                st.rerun()

    with board_col:
        render_tactical_board(st.session_state.get("active_formation", "4-3-3"))

    evaluation = st.session_state.coach_evaluation
    simulation = st.session_state.match_simulation
    if evaluation and simulation:
        card_col, timeline_col = st.columns([0.85, 1.25])
        with card_col:
            render_coach_card(evaluation)
        with timeline_col:
            st.subheader("Match Simulation Timeline")
            render_timeline(simulation.events)
            st.markdown(
                f"""
                <div class="fv-stat-row">
                    <div class="fv-stat"><b>{simulation.final_score}</b><span>Final Score</span></div>
                    <div class="fv-stat"><b>{simulation.result_label}</b><span>Result</span></div>
                    <div class="fv-stat"><b>{simulation.points}</b><span>Leaderboard Score</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            student = current_student()
            if student is None:
                st.warning("Check in with student ID and name before saving to the prize leaderboard.")
            elif st.button("Save Coach Result to Leaderboard", type="primary"):
                store().save_coach_score(
                    student,
                    final_score=simulation.points,
                    coach_score=evaluation.coach_score,
                    coach_rank=evaluation.rank,
                )
                st.session_state.last_saved_coach_score = simulation.points
                st.success(f"Saved Coach Mode score: {simulation.points}. Prize tier: {reward_tier(simulation.points)}.")


def page_reports() -> None:
    st.title("Reports")
    profile = st.session_state.dna_profile
    penalties = st.session_state.penalties
    evaluation = st.session_state.coach_evaluation

    if profile is None and evaluation is None:
        st.info("Complete Player Mode or Coach Mode to generate report cards.")
        return

    player_col, coach_col = st.columns(2)
    with player_col:
        st.subheader("Football Report Card")
        if profile:
            goals = sum(1 for result in penalties if result.success)
            st.write(f"Football DNA: {profile.footballer} Type")
            st.write(f"Goals: {goals}/5")
            st.write(f"Accuracy: {accuracy(penalties)}%")
            st.write(f"Reaction Time: {average_reaction(penalties)}s")
            st.write(f"Best Skill: {best_skill(penalties, profile.special_ability)}")
            st.write(f"Suggested Position: {profile.suggested_position}")
            st.pyplot(radar_chart(profile, penalties), clear_figure=True)
        else:
            st.caption("No Player Mode report yet.")

    with coach_col:
        st.subheader("Coach Report Card")
        if profile and evaluation:
            st.write(f"Coach Rank: {evaluation.rank}")
            st.write(f"Coach Score: {evaluation.coach_score}")
            st.write(f"Attack: {evaluation.attack}")
            st.write(f"Defense: {evaluation.defense}")
            st.write(f"Risk: {evaluation.risk}")
            st.pyplot(radar_chart(profile, coach=evaluation), clear_figure=True)
        elif evaluation:
            st.write(f"Coach Rank: {evaluation.rank}")
            st.write(f"Coach Score: {evaluation.coach_score}")
        else:
            st.caption("No Coach Mode report yet.")


def page_rewards() -> None:
    st.title("Check-In & Rewards")
    left, right = st.columns([0.8, 1.2])
    with left:
        student_check_in()
        st.markdown(
            """
            <div class="fv-panel">
                <h3>Prize Tiers</h3>
                <p>Gold Prize: 700+ points<br>
                Silver Prize: 520+ points<br>
                Bronze Prize: 350+ points<br>
                Participation: below 350 points</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        render_leaderboards()


def render_leaderboards() -> None:
    entries = store().leaderboard(30)
    if not entries:
        st.info("No leaderboard scores yet. Play a mode or seed Demo Mode.")
        return
    st.subheader("Prize Leaderboard")
    table = [
        {
            "Rank": index,
            "Student ID": entry.student_id,
            "Name": entry.name,
            "Score": entry.final_score,
            "Mode": entry.best_mode,
            "Prize Tier": reward_tier(entry.final_score),
        }
        for index, entry in enumerate(entries, start=1)
    ]
    st.dataframe(table, use_container_width=True, hide_index=True)

    st.subheader("Leaderboard Sections")
    tab1, tab2, tab3 = st.tabs(["Best Player", "Best Coach", "Highest Accuracy"])
    with tab1:
        rows = [dict(row) for row in store().section("final_score", 100) if row["mode"] == "Player Mode"][:10]
        st.dataframe(rows, use_container_width=True, hide_index=True)
    with tab2:
        rows = [dict(row) for row in store().section("coach_score", 100) if row["mode"] == "Coach Mode"][:10]
        st.dataframe(rows, use_container_width=True, hide_index=True)
    with tab3:
        rows = [dict(row) for row in store().section("accuracy", 100) if row["mode"] == "Player Mode"][:10]
        st.dataframe(rows, use_container_width=True, hide_index=True)


def page_demo() -> None:
    st.title("Demo Mode")
    st.markdown(
        """
        <div class="fv-panel">
            <h3>Club Fair Demo</h3>
            <p>Use this mode when judges need to experience the product quickly.
            It seeds sample students, generates a ready Player Mode profile, and prepares a Coach Mode scenario.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Seed Demo Leaderboard", type="primary"):
            store().seed_demo_data()
            st.success("Demo students and scores added.")
    with col2:
        if st.button("Load Instant Judge Session", type="primary"):
            st.session_state.student = Student("JUDGE-DEMO", "Judge Demo")
            st.session_state.dna_profile = generate_dna(
                {
                    "style": "Passing",
                    "risk": "Calculated risks",
                    "role": "Attack",
                    "teamwork": "Teamwork",
                    "moment": "Perfect assist",
                },
                expression_signal="focused",
            )
            st.session_state.penalties = []
            st.session_state.last_penalty = None
            st.session_state.commentary = []
            st.session_state.coach_scenario = generate_scenario(random.Random(7))
            st.success("Judge Demo session is ready. Open Player Mode or Coach Mode.")

    render_leaderboards()


def page_system() -> None:
    st.title("System")
    st.markdown(
        """
        <div class="fv-panel">
            <h3>Architecture</h3>
            <p>Browser -> Streamlit Frontend -> Reusable Game Logic Layer -> SQLite Database.
            Core engines are independent from Streamlit for a future React + FastAPI migration.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.subheader("Computer Vision Integration Status")
    st.table(cv_status())
    st.subheader("Database")
    st.code(str(DATABASE_PATH))
    st.subheader("Cross-Platform Rules")
    st.write(
        [
            "Pathlib is used for filesystem paths.",
            "No desktop Pygame window is used.",
            "Gameplay is browser-rendered through Streamlit and SVG.",
            "Environment variables can override configuration such as FOOTBALLVERSE_DB_PATH.",
        ]
    )


if __name__ == "__main__":
    main()
