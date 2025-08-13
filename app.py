import streamlit as st
import pandas as pd
from vidigi.utils import EventPosition, create_event_position_df

st.set_page_config(layout="wide")

st.title("Streamlit Animation Builder Helper")

animation_code = ""

use_sample_dataset = st.toggle("Use sample dataset")
if use_sample_dataset:
    event_logs = "sample_event_logs.csv"
else:
    event_logs = st.file_uploader("Click to upload your event logs", ".csv")
    # print(event_logs)

animation_code += f"""
event_log_df = pd.read_csv("{event_logs}")
"""


st.info("""
        Your event logs must follow the format that vidigi expects. For help with this, you can consult the documentation.
        """)

if event_logs:
    event_logs_df = pd.read_csv(event_logs)

    col_time, col_entity_id, col_event_type, col_event = st.columns(4)

    time_col_name_options = ["time"]
    time_col_name_options.extend(event_logs_df.columns)
    time_col_name_options = list(dict.fromkeys(time_col_name_options))
    time_col_name = col_time.selectbox("Select the time column", time_col_name_options)

    entity_id_col_name_options = ["entity_id"]
    entity_id_col_name_options.extend(event_logs_df.columns)
    entity_id_col_name_options = list(dict.fromkeys(entity_id_col_name_options))
    entity_id_col_name = col_entity_id.selectbox("Select the entity identifier column", entity_id_col_name_options)

    event_type_col_name_options = ["event_type"]
    event_type_col_name_options.extend(event_logs_df.columns)
    event_type_col_name_options = list(dict.fromkeys(event_type_col_name_options))
    event_type_col_name = col_event_type.selectbox("Select the event type column", event_type_col_name_options)

    event_col_name_options = ["event"]
    event_col_name_options.extend(event_logs_df.columns)
    event_col_name_options = list(dict.fromkeys(event_col_name_options))
    event_col_name = col_event.selectbox("Select the event column", event_col_name_options)

    col_resource, col_runs = st.columns(2)

    contains_resources = col_resource.toggle("Does your model contain resources?", value=False)

    if contains_resources:
        resource_col_name_options = ["resource_id"]
        resource_col_name_options.extend(event_logs_df.columns)
        resource_col_name_options = list(dict.fromkeys(resource_col_name_options))
        resource_col_name = col_resource.selectbox("Select the resource identifier column", resource_col_name_options)

    contains_multiple_runs = col_runs.toggle("Does your event log contain data from more than one model run?", value=False)

    if contains_multiple_runs:
        run_col_name_options = ["run_number"]
        run_col_name_options.extend(event_logs_df.columns)
        run_col_name_options = list(dict.fromkeys(run_col_name_options))
        run_col_name = col_runs.selectbox("Select the run identifier column", run_col_name_options)

        chosen_run = col_runs.selectbox("Select the run you want to animate", options=event_logs_df[run_col_name].unique())

        animation_code += f"""
event_log_df = event_log_df[event_log_df[{run_col_name}] == {chosen_run}] # CHANGE THIS VALUE IF YOU WANT TO VISUALISE A RUN OTHER THAN RUN '1'
"""


    # col1, col2, col3 = st.columns(3)


    # col1.subheader("Unique Events in Your Dataset")
    # col1.markdown("".join(f"- {i}\n" for i in event_logs_df["event"].unique()))

    # col2.subheader("Event Types in Your Dataset")
    # col2.markdown("".join(f"- {i}\n" for i in event_logs_df["event_type"].unique()))

    st.subheader("Set Up Your Plot Area")

    col1, col2, col3, col4 = st.columns(4)

    plotly_plot_width = col1.number_input("Set the width (in pixels) of your plotly plot",  0, 5000, 1000)
    plotly_plot_height = col2.number_input("Set the height (in pixels) of your plotly plot", 0, 5000, 800)

    decouple_plotly_coords_from_size = st.toggle("Set separate values for the coordinates of your plotly grid")

    if decouple_plotly_coords_from_size:
        plotly_coordinates_width = col3.number_input("Set the width of the coordinate grid of your plotly plot", 0, 5000, 1000)
        plotly_coordinates_height = col4.number_input("Set the height of the coordinate grid your plotly plot", 0, 5000, 800)
    else:
        plotly_coordinates_width = plotly_plot_width
        plotly_coordinates_height = plotly_plot_width


    st.subheader("Build your initial event positioning dataframe")

    @st.fragment
    def build_event_position_df_start(event_log_df):
        event_position_df = event_log_df[["event_type", "event"]].drop_duplicates().sort_values(["event_type", "event"])
        event_position_df = event_position_df[event_position_df["event_type"].isin(["arrival_departure", "queue", "resource_use_end"])].reset_index(drop=True)
        event_position_df["x"] = 0
        event_position_df["y"] = 0
        return event_position_df

    event_position_df = build_event_position_df_start(event_logs_df)

    @st.fragment
    def build_event_position_df(event_position_df):
        event_position_df = st.data_editor(event_position_df)

        return event_position_df

    event_position_df = build_event_position_df(event_position_df)

    st.markdown("Here is your vidigi animation code! Hover over the code to bring up the copy icon in the top right so you can copy this code, then paste it into your script or notebook.")

    col_imports, col_event_position_df = st.columns(2)

    col_imports.subheader("Imports")
    col_imports.code(
"""
from vidigi.animation import animate_activity_log
from vidigi.utils import EventPosition, create_event_position_df
import pandas as pd
    """, language='python', line_numbers=True)

    col_event_position_df.subheader("Event Positioning Dataframe")
    col_event_position_df.code(
"""
print("Hello World")
"""
    )

    st.subheader("Animation Code")
    st.code(
animation_code
    )
