import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import os
from io import BytesIO
import base64

import seaborn as sns
from matplotlib import pyplot as plt

import fastf1
import fastf1.plotting
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

from .models import DriverComparison
from paddock.models import Driver, Race


from fastf1.plotting import _Constants
_Constants['2025'] = _Constants['2023']


# Enable Matplotlib patches for plotting timedelta values and load
# FastF1's dark color scheme
fastf1.plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=False,
                          color_scheme='fastf1')


if not os.path.exists('./cache'):
    os.makedirs('./cache')

def fetch_and_store_comparison(season, race_name, driver1_code, driver2_code, comparison_type):
    try:
        driver1 = Driver.objects.get(code=driver1_code)
        driver2 = Driver.objects.get(code=driver2_code)
    except Driver.DoesNotExist:
        raise ValueError("One or both drivers not found in the database.")


    race_obj = Race.objects.filter(season=season, name__iexact=race_name).first()

    race = fastf1.get_session(2025, race_name, 'R')
    race.load()

    fastf1.Cache.enable_cache('./cache')


    # Custom formatter to convert lap times to minute:second format
    def format_time(x, pos):
        # x is already in seconds, convert to minutes and seconds
        minutes = int(x // 60)
        seconds = x % 60
        return f'{minutes}:{seconds:05.3f}'  # MM:SS.sss format

    # Create two subplots side by side
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    # drivers = ['VER', 'RUS']
    drivers = [driver1, driver2]


    y_min = float('inf')
    y_max = float('-inf')
    count = 0
    # Plot for subplot 1: Alonso and Norris
    for driver in drivers:
        ax = axes[count]
        driver_laps = race.laps.pick_driver(driver).pick_quicklaps().reset_index()
        y_values = driver_laps["LapTime"].dt.total_seconds()
        sns.scatterplot(data=driver_laps,
                        x="LapNumber",
                        y=y_values,  # Convert LapTime to total seconds
                        ax=ax,
                        hue="Compound",
                        palette=fastf1.plotting.get_compound_mapping(session=race),
                        s=80,
                        linewidth=0)
        y_min = min(min(y_values), y_min)
        y_max = max(max(y_values), y_max)
        count += 1

    # Set the same y-axis limits for both subplots
    for ax, driver in zip(axes, drivers):
        ax.set_ylim([y_min * 0.99 , y_max * 1.01])
        # ax2.set_ylim([y_min, y_max])

        # Customize axis labels for both subplots
        ax.set_xlabel(f"Lap Number {driver}")
        ax.set_ylabel("Lap Time (min:sec)")

        # Use custom formatter for both y-axes to display times as minute:second
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_time))


        ax.set_title(f"{driver} Laptimes")

        # Apply gridlines for both subplots
        ax.grid(True, which='both', axis='both', color='w', linestyle='-', linewidth=0.25)

        # Remove top and right spines for a cleaner look
        sns.despine(ax=ax, left=True, bottom=True)

    # # Set a shared title for the whole figure
    plt.suptitle("Laptimes in the 2023 Azerbaijan Grand Prix", fontsize=16)

    # Adjust layout and show the plots with legends
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust the layout to make room for the suptitle

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)


    DriverComparison.objects.update_or_create(
        season=season,
        race=race_name,
        driver1=driver1,
        driver2=driver2,
        comparison_type=comparison_type,
        defaults={
            'race': race_obj,
            'plot_base64': img_base64,
        }
    )