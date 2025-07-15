from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from io import BytesIO
import base64
from django.http import HttpResponse

import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import os
import seaborn as sns
from matplotlib import pyplot as plt

import fastf1
import fastf1.plotting
from fastf1.plotting import _Constants

_Constants['2025'] = _Constants['2023']


# Create your views here.
class CompareDriverDriverView(APIView):
    def get(self, request):
        driver1 = request.GET.get('driver1')
        driver2 = request.GET.get('driver2')
        race = request.GET.get('race')
        print(driver1, driver2, race)
        cache_path = 'cache/'
        try:
            if not os.path.exists(cache_path):
                os.makedirs(cache_path)
            fastf1.Cache.enable_cache(cache_path)  # Local cache
            session = fastf1.get_session(2025, race, 'R')
            session.load()

            lap1 = session.laps.pick_driver(driver1).pick_quicklaps().reset_index()
            lap2 = session.laps.pick_driver(driver2).pick_quicklaps().reset_index()

            tel1 = lap1.get_telemetry().add_distance()
            tel2 = lap2.get_telemetry().add_distance()

            # Interpolate
            tel2_clean = tel2.drop_duplicates(subset='Distance')
            tel2_interp = tel2_clean.set_index('Distance').reindex(tel1['Distance'], method='nearest')
            delta = (tel2_interp['Time'].reset_index(drop=True) - tel1['Time'].reset_index(
                drop=True)).dt.total_seconds()

            # Plot
            fig, ax = plt.subplots()
            ax.plot(tel1['Distance'], delta, label=f'{driver1} vs {driver2}')
            ax.set_xlabel('Distance')
            ax.set_ylabel('Cumulative Time Delta (s)')
            ax.legend()
            plt.tight_layout()

            # Encode plot as base64
            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            plt.close(fig)

            return HttpResponse(f'<img src="data:image/png;base64,{img_base64}" />', content_type='text/html')


        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CompareDriverDriverViewV2(APIView):
    from fastf1.plotting import _Constants

    _Constants['2025'] = _Constants['2023']
    def get(self, request):
        driver1 = request.GET.get('driver1')
        driver2 = request.GET.get('driver2')
        race = request.GET.get('race')
        print(driver1, driver2, race)

        cache_path = 'cache/'
        try:
            if not os.path.exists(cache_path):
                os.makedirs(cache_path)
            fastf1.Cache.enable_cache(cache_path)  # Local cache
            session = fastf1.get_session(2025, race, 'R')
            session.load()
            print('data loaded')

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
            print('starting the plot')
            for driver in drivers:
                ax = axes[count]
                driver_laps = session.laps.pick_drivers(driver).pick_quicklaps().reset_index()
                y_values = driver_laps["LapTime"].dt.total_seconds()
                sns.scatterplot(data=driver_laps,
                                x="LapNumber",
                                y=y_values,  # Convert LapTime to total seconds
                                ax=ax,
                                hue="Compound",
                                palette=fastf1.plotting.get_compound_mapping(session=session),
                                s=80,
                                linewidth=0)
                y_min = min(min(y_values), y_min)
                y_max = max(max(y_values), y_max)
                count += 1

            print('data plotting')
            # Set the same y-axis limits for both subplots
            for ax, driver in zip(axes, drivers):
                ax.set_ylim([y_min * 0.99, y_max * 1.01])
                # ax2.set_ylim([y_min, y_max])
                print('data plotting2')
                # Customize axis labels for both subplots
                ax.set_xlabel(f"Lap Number {driver}")
                ax.set_ylabel("Lap Time (min:sec)")
                print('data plotting3')
                # Use custom formatter for both y-axes to display times as minute:second
                ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_time))

                ax.set_title(f"{driver} Laptimes")
                print('data plotting4')
                # Apply gridlines for both subplots
                ax.grid(True, which='both', axis='both', color='w', linestyle='-', linewidth=0.25)

                # Remove top and right spines for a cleaner look
                sns.despine(ax=ax, left=True, bottom=True)
                print('data plotting5')

            # # Set a shared title for the whole figure
            plt.suptitle("Laptimes in the 2023 Azerbaijan Grand Prix", fontsize=16)
            # plt.suptitle(f"Laptimes in the {session.event['EventName']} {session.event['Year']} Grand Prix",
            #              fontsize=16)

            # Adjust layout and show the plots with legends
            plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust the layout to make room for the suptitle
            print('PLoted the graph from backend')
            # Encode plot as base64
            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            plt.close(fig)

            return HttpResponse(f'<img src="data:image/png;base64,{img_base64}" />', content_type='text/html')


        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

def home(request):
    return render(request, 'telemetry/compare.html')