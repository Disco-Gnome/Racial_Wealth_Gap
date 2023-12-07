import numpy as np
import scipy as sp
import pandas as pd
from matplotlib import pyplot
from matplotlib.animation import FuncAnimation
import matplotlib
from textwrap import wrap

#%%
matplotlib.rc("animation", html="jshtml")

##### Data #####
wealth_gap_data = pd.read_csv("White-Black wealth gap per year.csv")

#####Instantiate figure and subplot #####
fig = pyplot.figure(figsize=(16, 9))
ax = fig.add_subplot(111)
# Add Secondary X-Axis for historical events
# https://matplotlib.org/stable/gallery/subplots_axes_and_figures/secondary_axis.html
hist = ax.secondary_xaxis('top')
hist.grid()

##### Styles #####
# Fonts: https://jonathansoma.com/lede/data-studio/matplotlib/list-all-fonts-available-in-matplotlib-plus-samples/
# Colors: https://matplotlib.org/stable/gallery/color/named_colors.html

themes = {
    '1860': {
        'title_font': "Edwardian Script ITC",
        'axis_label_font': "Brush Script MT",
        'tick_label_size': 24,
        'tick_label_font': "Bradley Hand ITC",
        'tick_label_color': "#292929",
        'background_color': "#d0bfab"
    },
    '1900': {
        'title_font': 'SimSun',
        'axis_label_font': 'SimSun',
        'tick_label_size': 20,
        'tick_label_font': 'Franklin Gothic Medium',
        'tick_label_color': "#383734",
        'background_color': '#d6c7b6'
    },
    '1940': {
        'title_font': 'DejaVu Sans Mono',
        'axis_label_font': 'Consolas',
        'tick_label_size': 18,
        'tick_label_font': 'Consolas',
        'tick_label_color': '#242424',
        'background_color': '#d7d7d7'
    },
    '1980': {
        'title_font': 'Times New Roman',
        'axis_label_font': 'Microsoft Sans Serif',
        'tick_label_size': 19,
        'tick_label_font': 'Microsoft Sans Serif',
        'tick_label_color': '#000000',
        'background_color': '#ffffff'
    }
}

# Function for re-styling the graph based on current animation frame year.
def style_plot(style_year):
    # Get current style theme from `themes` dict
    if style_year >= 1980:
        current_theme = themes['1980']
    elif style_year >= 1940:
        current_theme = themes['1940']
    elif style_year >= 1900:
        current_theme = themes['1900']
    else:
        current_theme = themes['1860']

    # Secondary Axis tick labels inherit global styles, &
    # we need to ensure that styles are overwritten for all other labels.
    pyplot.rcParams.update({'font.sans-serif': current_theme['tick_label_font']})

    # Background color
    fig.patch.set_facecolor(current_theme['background_color'])

    ax.patch.set_facecolor(current_theme['background_color'])

    # Title
    pyplot.title("Black/White Wealth Gap: %s" % style_year,
                 y=1,
                 pad=140,
                 fontsize=current_theme['tick_label_size'] + 12,
                 **{'fontname': current_theme['title_font']})

    # Y-Axis labels
    pyplot.ylabel('Wealth Gap Ratio',
                  fontsize=current_theme['tick_label_size'],
                  labelpad=15,
                  color=current_theme['tick_label_color'],
                  **{'fontname': current_theme['axis_label_font']})
    pyplot.yticks(
        fontsize=current_theme['tick_label_size'] - 4,
        fontname=current_theme['tick_label_font'],
        color=current_theme['tick_label_color'])

    # X-Axis labels
    pyplot.xlabel('Year',
                  fontsize=current_theme['tick_label_size'],
                  labelpad=15,
                  color=current_theme['tick_label_color'],
                  **{'fontname': current_theme['axis_label_font']})
    pyplot.xticks(
        fontsize=current_theme['tick_label_size'] - 4,
        fontname=current_theme['tick_label_font'],
        color=current_theme['tick_label_color'])

    return current_theme

##### Axes #####
# Function to get frame X-Axis max

def get_end_year(row):
    index = max(row, 1) - 1
    return wealth_gap_data.Year[index]

# Static Y-Axis limits
maximum_ratio = wealth_gap_data.Ratio.max()
bottom_ratio = 1  # bottom of y-axis
max_ratio = np.round(maximum_ratio * 1.1)  # top of y-axis; multiply *1.1 to leave headroom

# Static X-Axis Limits
start_year = wealth_gap_data.Year[0]  # left of x-axis; first year in dataset

# List of years with historical events to label
data_with_events = wealth_gap_data[wealth_gap_data['Events'].notnull()]

# Dynamically set X-Axis values

def set_axes(current_year, current_style):
    if current_year <= 1890:
        xticks_interval = 5
    elif current_year <= 1920:
        xticks_interval = 10
    else:
        xticks_interval = 20

    # X and Y-axis lims
    pyplot.axis([start_year, current_year + 1, bottom_ratio, max_ratio])

    # X-Axis tick values and intervals
    pyplot.xticks(np.arange(start_year, current_year + 1, xticks_interval))

    # Show years with historical events on the secondary X-Axis
    # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_xticks.html
    events = ['\n'.join(wrap(event, 25)) for event in data_with_events.Events]
    hist.set_xticks(data_with_events.Year,
                    labels=events,
                    color=current_style['tick_label_color'],
                    fontsize=(current_style['tick_label_size'] - 7),
                    rotation=65.0)

##### Initialize plot #####
# Set style to first year
initial_style = style_plot(start_year)

# Intersections & labels
intersection_text_dictionary = {}
for index, event_year in enumerate(data_with_events.Year):
    pyplot.axvline(x=event_year, color="grey", linestyle="--")
    ratio = data_with_events.Ratio.iloc[index]
    transformed_x = event_year + 0.28
    transformed_y = ratio + 0.53
    #   https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.plot.html
    pyplot.plot(event_year, ratio, 'ko')
    # Initialize intersection label with empty string, so we don't see it rendering outside graph area
    # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.text.html
    text = pyplot.text(x=transformed_x, y=transformed_y, s='',
                       fontsize=8, fontweight='normal')
    # Store this for use in `update` function
    intersection_text_dictionary[event_year] = [text, str(np.round(ratio,1))]

# Create Plot; all values inside .plot() are not changed by animation
gap_plot = pyplot.plot(
    'Year',
    'Ratio',
    data=wealth_gap_data,
    linewidth=3,
    color='black'
)
# Set fixed location for X-Axis label so it doesn't jump around as the years change
ax.xaxis.set_label_coords(0.5, -0.075)
# Set fixed location for subplots
matplotlib.pyplot.subplots_adjust(top=0.73)

# Set X-Axis first interval
initial_end_year = get_end_year(row=0)
set_axes(current_year=initial_end_year, current_style=initial_style)

##### Animation #####

def update(row_num):
    new_end_year = get_end_year(row=row_num)
    style = style_plot(new_end_year)
    set_axes(current_year=new_end_year, current_style=style)

    # Check if there is a gridline intersection for this year & label it
    intersection_label = intersection_text_dictionary.get(new_end_year - 1)
    if intersection_label is not None:
        text_obj, ratio_str = intersection_label
        text_obj.set_text(ratio_str)

    return gap_plot

def draw_first_frame():
    # clear all text from plot
    for text_obj, _ratio in intersection_text_dictionary.values():
        text_obj.set_text('')

    return gap_plot

# Create the animation
anim = FuncAnimation(
    fig=pyplot.gcf(),
    func=update,
    init_func=draw_first_frame,
    frames=len(wealth_gap_data.Year),
    interval=100)

##### Run animation #####
writer = matplotlib.animation.PillowWriter(fps=8)
anim.save("animation.gif", writer=writer, dpi=150)

anim
pyplot.show()