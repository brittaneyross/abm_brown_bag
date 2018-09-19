
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

image = Div(text="""<img src="/abm_pres/static/abm_flow_chart.png/">""")


# note that in my implementation, there are more elements in the column, but this is not needed for this example.
col = column(image)

# create the document
curdoc().add_root(col)
