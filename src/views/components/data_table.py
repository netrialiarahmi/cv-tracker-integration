"""
Data table component for displaying hiring summary.
"""

import streamlit as st
import pandas as pd
from src.models.hiring import calculate_position_progress, get_hire_type_display, format_skill_test
from src.config.settings import BASE_STAGES


def build_summary_dataframe(display_data: pd.DataFrame) -> pd.DataFrame:
    """Return a formatted summary dataframe for downstream rendering or export."""
    if len(display_data) == 0:
        return pd.DataFrame()

    progress_values = display_data.apply(
        lambda row: calculate_position_progress(row, BASE_STAGES), axis=1
    )

    return pd.DataFrame({
        "Division": display_data["Division"],
        "Job Position": display_data["Job Position"],
        "Hire Type": display_data.apply(get_hire_type_display, axis=1),
        "Status": display_data.get("Status", "Contract"),
        "PIC": display_data.get("PIC", ""),
        "Initial Int. (HR)": display_data["Initial Interview (HR)"].apply(lambda x: "✓" if x else "—"),
        "HR & User Int.": display_data["HR & User Interview (Stage 1)"].apply(lambda x: "✓" if x else "—"),
        "Skill Test": display_data.apply(format_skill_test, axis=1),
        "Final Interview": display_data["Final Interview"].apply(lambda x: "✓" if x else "—"),
        "Offering": display_data["Offering"].apply(lambda x: "✓" if x else "—"),
        "Contract Sign": display_data["Contract Sign"].apply(lambda x: "✓" if x else "—"),
        "On Boarding": display_data["On Boarding"].apply(lambda x: "✓" if x else "—"),
        "Progress (%)": progress_values,
        "Notes": display_data.get("Notes", ""),
        "Last Updated": display_data.get("Last Updated", ""),
    })


def render_data_table(display_data: pd.DataFrame) -> None:
    """
    Render formatted data table showing hiring positions summary.
    
    Args:
        display_data: DataFrame containing hiring data to display
    """
    display_df = build_summary_dataframe(display_data)
    if len(display_df) == 0:
        return

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=360,
        column_config={
            "Progress (%)": st.column_config.NumberColumn(
                "Progress (%)",
                help="Hiring stage completion rate",
                format="%d%%",
            )
        },
    )


def render_reference_table(display_data: pd.DataFrame, caption: str) -> None:
    """Provide a lightweight wrapper that frames the summary table as a reference log."""
    if len(display_data) == 0:
        return
    st.markdown('<div class="summary-table">', unsafe_allow_html=True)
    st.markdown("<h4>All position</h4>", unsafe_allow_html=True)
    if caption:
        st.markdown(f'<p class="summary-table-caption">{caption}</p>', unsafe_allow_html=True)
    render_data_table(display_data)
    st.markdown('</div>', unsafe_allow_html=True)
