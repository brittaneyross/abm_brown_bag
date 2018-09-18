
#import libraries
import fiona
import pandas as pd
import numpy as np
from os.path import dirname, join
import os

#bokeh
from bokeh.io import show, output_notebook, push_notebook, curdoc, output_file
from bokeh.plotting import figure, output_file, save
from bokeh.layouts import layout, column, row
from bokeh.models.selections import Selection
from bokeh.models import NumberFormatter,CustomJS, Panel, Spacer,HoverTool,LogColorMapper, ColumnDataSource, TapTool, BoxSelectTool, LabelSet, Label, FactorRange,NumeralTickFormatter
from bokeh.tile_providers import STAMEN_TERRAIN_RETINA,CARTODBPOSITRON_RETINA
from bokeh.core.properties import value
from bokeh.transform import factor_cmap, dodge
from bokeh.models.widgets import Div, Tabs, Paragraph, Dropdown, Button, PreText, Toggle, TableColumn, DataTable

#mapping
from shapely.geometry import Polygon, Point, MultiPoint, MultiPolygon
import geopandas as gpd

from bokeh.transform import factor_cmap
from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application
from bokeh.core.properties import value

#color
from bokeh.palettes import Spectral6

import warnings
warnings.filterwarnings('ignore')

from bokeh.io import curdoc


hh_sample= pd.read_csv(join(dirname(__file__),'data','sample_data','hh_sample.csv'))
per_sample = pd.read_csv(join(dirname(__file__),'data','sample_data','per_sample.csv'))
iTours_sample = pd.read_csv(join(dirname(__file__),'data','sample_data','itour_sample.csv'))
itrips_sample = pd.read_csv(join(dirname(__file__),'data','sample_data','itrips_sample.csv'))
abm_flow = join(dirname(__file__),'data','abm_flow_chart.png')

### plots with python call backs require the bokeh server
#plots should be inializted from bokeh application handler
column_width = 1600
margin = 150


def load_image(image, title_text):
    p = figure(x_range=(0,250), y_range=(0,410),plot_width=600, plot_height=800,
               x_axis_location=None, y_axis_location=None,tools='',title=title_text)
    p.image_url(url=[image], x=0, y=1, w=250, h=410, anchor="bottom_left")
    return p

def abm_background():
    background = Div(text = """<h1>What is the Activity Based Model</h1>""",width=column_width)

    return (row(Spacer(width = margin), column(Spacer(height=25),background)))

def overview_tab():

    #image = load_image(abm_flow,'CT-RAMP Structure and Sub-Models')
    image = Div(text="<img src='abm_pres/static/abm_flow_chart.png'>")

    overview_text = Div(text="""<h1>Activity Based Model Overview</h1>""", width = column_width)
    ctramp_text = Div(text="""<h2>Coordinated Travel - Regional Activity Modeling Platform
                        (CT-RAMP) </h2><p>ABM model implements the CT-RAMP design and software platform.
                        Features microsimulation of travel decisions for individual households and persons
                        within a household as well as intra-household interactions
                        across a range of activity and travel dimensions.</p><br>
                        <ol><li><b>Population synthesis</b> creates and distributes households and persons
                        for use in the ABM</li><br>
                        <li><b>Long-Term Location Choice</b> - Models location of usual (mandatory) destinations</li><br>
                        <li><b>Mobility</b> - Models household attributes like free parking eligibility, car ownership,
                        transit pass, or toll transponder</li><br>
                        <li><b>Coordinated Daily Activity-Travel Pattern</b> - Generates and schedules mandatory
                        and non-mandatory activities for each household member.</li><br>
                        <li><b>Tour</b> - Daily activities are organized into tours, tour mode, number,
                        and location of stops are determined.</li><br>
                        <li><b>Trips</b> - Mode, parking, and location of trips making up tour is determined.</li><br>
                        <li><b>Network Simulation</b> - List of trips for each individual and/or travel party
                        is generated and trips routes are assigned on the modeling network for auto and transit.</li>
                        </ol>""", width = int(column_width*.5))
    extra = Div(text="""<hr><ul><li>Tour: Chain of trips that start and end at home</li>
                        <li>Person Types: 8 Person Types (1=Full time worker, 2=Part time worker, 3=University student,
                        4=Adult non-worker under 65, 5=retiree, 6=driving age school child, 7=pre-driving age school child, 8=preschool child)</li>
                        <li>Activities: 10 travel purposes (work, university, school, escorting,
                        shopping, other maintenance, eating out, visiting relatives and friends,
                        other discretionary, and atwork)</li>
                        <li>Modes = 21 modes at both tour and trip level</li>
                        </ul>""", width = int(column_width*.5),
                        css_classes = ['small'])

    return (row(Spacer(width = margin), (column(Spacer(width = margin, height=25),overview_text,row(column(ctramp_text,extra),Spacer(width=100),column(image))))))


def key_features():

    kf_title = Div(text="""<h1>ABM Features</h1>""", width = column_width)

    kf_tours = Div(text="""<h2>Travel Is Organized Into Tours and Trips</h2>
                       """, width = column_width)

    kf_traveler = Div(text="""<h2>Each Traveler Can Be Identified Throughout Similuation</h2>
    <p>As individual travelers are simulated the results are listed by household, person, tour, and trip.
    Allows trip/tour results to be represented across any number of categories included in the synthetic population results.</p>
                       """, width = column_width)

    kf_attr = Div(text="""<h2>Each Traveler’s Personal Attributes Inform Unique Travel Choices</h2>
    <p>Person and household decision making units such as person type, age, work/school status, income, available vehicles
        inform travel choices.</p>
                       """, width = column_width)

    return (row(Spacer(width = margin), column(Spacer(height=25),kf_title, kf_tours,kf_traveler,kf_attr)))

def output_tab():

    hh_col = [TableColumn(field=col, title=col) for col in hh_sample.columns[:2]]+\
             [TableColumn(field='income', title='income',formatter=NumberFormatter(format="$0,0.00"))]+\
             [TableColumn(field=col, title=col) for col in hh_sample.columns[3:]]

    per_col = [TableColumn(field=col, title=col) for col in per_sample.columns]
    tour_col = [TableColumn(field=col, title=col) for col in iTours_sample.columns]
    trip_col = [TableColumn(field=col, title=col) for col in itrips_sample.columns]

    hh_src = ColumnDataSource(hh_sample.sort_values(by='hh_id'))
    per_src = ColumnDataSource(per_sample.sort_values(by='hh_id'))
    tour_src = ColumnDataSource(iTours_sample.sort_values(by='person_id'))
    trip_src = ColumnDataSource(itrips_sample.sort_values(by='person_id'))


    hh_div = Div(text="""<h2>Household Attribution Results</h2><p>Individual household attributes</p>
                        <ul><li><b>hh_id</b> : Household ID</li>
                        <li><b>maz</b> : Household Subzone</li>
                        <li><b>income</b> : Household Income</li>
                        <li><b>autos</b> : Number of Vehicles</li>
                        <li><b>size</b> : Household Size</li>
                        <li><b>workers</b> : Number of Workers in Household</li>
                        <li><b>auto_suff</b> : Auto Sufficiency</li></ul>""", width=int(column_width*.45))
    hh_tbl = DataTable(columns=hh_col, source=hh_src, height = 200, selectable = True,width=int(column_width*.45),
                             fit_columns = True, scroll_to_selection=True)

    per_div = Div(text="""<h2>Person Attribution Results</h2><p>Individual persons within a household</p>
                        <ul><li><b>hh_id</b> : Household ID</li>
                        <li><b>person_id</b> : Person ID</li>
                        <li><b>per_num</b> : Person Number in Household</li>
                        <li><b>age</b> : Age</li>
                        <li><b>gender</b> : Gender</li>
                        <li><b>type</b> : Person Type (worker, student, etc)</li></ul>""", width=int(column_width*.45))
    per_tbl = DataTable(columns=per_col, source=per_src,height = 200,selectable = True,width=int(column_width*.45),
                         fit_columns = True, scroll_to_selection=True)

    tour_div = Div(text="""<h2>Tour Results</h2><p>Tours by person and household</p>
                        <ul><li><b>hh_id</b> : Household ID</li>
                        <li><b>person_id</b> : Person ID</li>
                        <li><b>tour_id</b> : Tour ID (0=first tour, 1 second tour, ect)</li>
                        <li><b>tour_category</b> : Mandatory, Non-Mandatory</li>
                        <li><b>tour_purpose</b> : Purpose of travel</li>
                        <li><b>maz</b> : Origin and destination subzone</li>
                        <li><b>tour_mode</b> : Mode of travel</li></ul>""", width=int(column_width*.4))
    tour_tbl = DataTable(columns=tour_col, source=tour_src,height = 250,selectable = True,width=int(column_width*.45),
                         fit_columns = True, scroll_to_selection=True)

    line_div = trip_div = Div(text="""<hr>""", width = column_width)
    trip_div = Div(text="""<h2>Trip Results</h2><p>Trips by person and household</p>
                        <ul><li><b>hh_id</b> : Household ID</li>
                        <li><b>person_id</b> : Person ID</li>
                        <li><b>tour_id</b> : Tour ID (0=first tour, 1 second tour, ect)</li>
                        <li><b>purpose</b> : Origin and destination trip purpose</li>
                        <li><b>maz</b> : Origin and destination subzone</li>
                        <li><b>trip_mode</b> : Mode of travel</li>
                        <li><b>tap</b> : boarding and alighting transit id</li></ul>""", width=int(column_width*.45))
    trip_tbl = DataTable(columns=trip_col, source=trip_src,height = 250,selectable = True,width=int(column_width*.45),
                         fit_columns = True, scroll_to_selection=True)

    def hh_select():

        indices = hh_src.selected.indices
        if len(indices) == 1:
            hh_id = hh_src.data["hh_id"][indices[0]]

            new_indices = [i for i, h in enumerate(per_src.data["hh_id"]) if h == hh_id]
            per_src.selected.indices=new_indices


    #hh_src.on_change('selected',my_tap_handler)

    per_button = Button(label="Select Person Level", button_type="default")
    per_button.on_click(hh_select)


    def per_select():

        indices = per_src.selected.indices
        if len(indices) == 1:
            per_id = per_src.data["person_id"][indices[0]]

            new_indices = [i for i, p in enumerate(tour_src.data["person_id"]) if p == per_id]
            tour_src.selected.indices=new_indices


    tour_button = Button(label="Select Person Tour", button_type="default")
    tour_button.on_click(per_select)


    def trip_select():

        indices = tour_src.selected.indices
        if len(indices) == 1:
            per_id = tour_src.data["person_id"][indices[0]]
            tour_id = tour_src.data["tour_id"][indices[0]]


            new_indices = []
            i = 0
            while i < len(trip_src.data["person_id"]):
                #trip_src.data["person_id"][i] == per_id
                if trip_src.data["person_id"][i] == per_id:
                    if trip_src.data["tour_id"][i] == tour_id:
                        new_indices.append(i)
                i+=1

            trip_src.selected.indices=new_indices

    trip_button = Button(label="Select Person Trip", button_type="default")
    trip_button.on_click(trip_select)

    output_title = Div(text = """<h1>Model Output Files</h1>""",width=column_width)
    output_description = Div(text = """<p>The ABM produces output files for modeled householdes, modeled persons,
    mandatory trip locations (work, school, university), trips, tours, ect. Model data calibrated to the
    CMAP Household Travel Survey (2007-2009)<p>""",width=column_width)

    #return row(Spacer(width = margin),column(Spacer(height=25),output_title,output_description, hh_div, hh_tbl,  per_div, per_button,per_tbl,
    #             Spacer(height=10),tour_div,tour_button, tour_tbl, Spacer(height=10),trip_div,trip_button, trip_tbl))

    return (row(Spacer(width = margin), column(Spacer(height=25),output_title,output_description,
            row(column(hh_div,hh_tbl,per_button), Spacer(width = int(column_width*.1)), column(per_div,per_tbl,tour_button)),line_div,
            row(column(tour_div,tour_tbl,trip_button), Spacer(width = int(column_width*.1)), column(trip_div,trip_tbl)))))


h_1 = Div(text = """<h1><center>Intro Text</center></h1>""",width=column_width)
h_2 = Div(text = """<h1><center>Intro Text</center></h1>""")
h_4 = Div(text = """<h1><center>Intro Text</center></h1>""")

b_0 = layout(children=[abm_background()])
b_1 = layout(children=[key_features()])

l_1 = layout(children=[overview_tab()])
l_2 = layout(children=[output_tab()])
l_3 = layout(children=[h_4])

tab_0 = Panel(child=b_0, title = 'Background')
tab_1 = Panel(child=b_1, title = 'Features')

tab_2 = Panel(child=l_1, title = 'Model Overview')
tab_3 = Panel(child=l_2, title = 'Outputs')
tab_4 = Panel(child=l_3, title = 'Data Exploration')

tabs = Tabs(tabs = [tab_0, tab_1, tab_2, tab_3, tab_4], sizing_mode = "stretch_both")

curdoc().add_root(tabs)
