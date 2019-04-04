from os.path import dirname, join

import numpy as np
import pandas as pd
import pandas.io.sql as psql
import sqlite3 as sql

from bokeh.plotting import figure
from bokeh.layouts import layout, column
from bokeh.models import ColumnDataSource, Div, Range1d
from bokeh.models.widgets import Slider, Select, TextInput
from bokeh.io import curdoc

# TO DO LIST
# 1. The y- and x-axis ranges should update automatically and not be a static property. 
# 2. Fix point colors: 
#   a. Update automatically.
#   b. Change yellow to something more beautifull.
#   c. Maybe have three different colors? 
#   d. Optimize point alpha and size. 
# 3. Fix PIP/PI lipid issue. 
# 4. Fix Radius labels/names. 
# 5. Embedding Bokeh into GLI website. 
# 6. Minor tweaks and optimizations. 

conn = sql.connect('C:/Users/Besian/Documents/GitHub/bokeh/examples/app/gli/GPCR.db')
query = open(join(dirname(__file__), 'query.sql')).read()
dfGPCR = psql.read_sql(query, conn)

dfGPCR["color"] = np.where(dfGPCR["P1"] > 1000, "orange", "grey")
dfGPCR["alpha"] = np.where(dfGPCR["P1"] > 1000, 0.9, 0.25)
dfGPCR.fillna(0, inplace=True)  # just replace missing values with zero

axis_map = {
    "Value1": "P1",
    "Value2": "P2",
    "Value3": "P3",
    "Value4": "P4",
    "Value5": "P5",
    "Value6": "D",
    "Residue": "ResNumber",
}
#radius_map = {
#    "7Å" : "rcutoff7A", 
#    "6Å" : "rcutoff6A", 
#    "5Å" : "rcutoff5A",
#}

desc = Div(text=open(join(dirname(__file__), "description.html")).read(), width=800)

# Create Input controls
number = Slider(title="Number Cutoff", value=0, start=0, end=5000, step=50)
residue = TextInput(title="Residue name (3 letter code):")
#genre = Select(title="Parameter", value="All",
#               options=open(join(dirname(__file__), 'Parameters.txt')).read().split())

gpcr = Select(title="GPCRs", value="RhodRi",
               options=open(join(dirname(__file__), 'GPCRs.txt')).read().split())

lipid = Select(title="Lipids", value="CHOL",
               options=open(join(dirname(__file__), 'Lipids.txt')).read().split())

radius = Select(title="Radius", value="rcutoff7A",
               options=open(join(dirname(__file__), 'Radius.txt')).read().split())

x_axis = Select(title="X Axis", options=sorted(axis_map.keys()), value="Residue")
y_axis = Select(title="Y Axis", options=sorted(axis_map.keys()),
                value="Value1")

# Create Column Data Source that will be used by the plot
source = ColumnDataSource(data=dict(x=[], y=[], color=[], ResName=[], ResNumber=[], alpha=[]))

TOOLTIPS=[
    ("ResName", "@ResName"),
    ("ResID", "@ResNumber"),
    # ("", "@RESIDUE"),
]

p = figure(plot_height=800, plot_width=800, title="", toolbar_location="right", tooltips=TOOLTIPS)
p.circle(x="x", y="y", source=source, size=5, color="color", line_color=None, fill_alpha="alpha")


def select_dfGPCR():
#    genre_val = genre.value
    gpcr_val  = gpcr.value
    lipid_val = lipid.value
    radius_val = radius.value

    residue_val = residue.value #.strip()
    #cast_val = cast.value.strip()
    selected = dfGPCR[
        (dfGPCR.P1 >= number.value) #& 
        #(dfGPCR.Radius == radius_val )
        # (dfGPCR.GPCRs == gpcr_val)
        #(dfGPCR.V >= number.value)
        #(dfGPCR[dfGPCR.P == "N"].V >= number.value) |
        #(dfGPCR[dfGPCR.P == "D"].V >= duration.value)
    ]

    #if (genre_val != "All"):
    #    selected = selected[selected.GPCRs.str.contains(genre_val)==True]
        #maxN = dfGPCR[dfGPCR.P != genre_val].V.max()
        #dfGPCR["alpha"] = np.where(dfGPCR["V"] > maxN * 0.5, 0.9, 0.25)
    if (gpcr_val != "All"):
        selected = selected[selected.GPCRs.str.contains(gpcr_val)==True]
    
    if (lipid_val != "All"):
        selected = selected[selected.Lipids.str.contains(lipid_val)==True]

    if (radius_val != "All"):
        selected = selected[selected.Radius.str.contains(radius_val)==True]

    if (residue_val != ""):
        selected = selected[selected.ResName.str.contains(residue_val)==True]
    #if (cast_val != ""):
    #    selected = selected[selected.Cast.str.contains(cast_val)==True]
    # print(dfGPCR.ResNumber)

    return selected

def getxMax (gpcr_val):
    if (gpcr_val == "All"):
        return 400
    M = dfGPCR[dfGPCR.GPCRs.str.contains(gpcr_val) == True]
    m1 = M["ResNumber"].tail(1).values
    m2 = M["ResNumber"].head(1).values
    return (int(m1), int(m2))

def getyMax (df, gpcr_val):
    if (gpcr_val == "All"):
        return 400
    M = df.P1.max()
    # M = dfGPCR[dfGPCR.GPCRs.str.contains(gpcr_val) == True]
    # m = M["ResNumber"].tail(1).values
    return int(M)


def update():
    #genre_val = genre.value
    gpcr_val = gpcr.value
    # lipid_val = lipid.value
    # radius_val = radius.value
    # residue_val = residue.value

    df = select_dfGPCR()
    # getxMax(gpcr_val)

    # if (gpcr_val != "All"):
    #     maxN = df[df.GPCRs == gpcr_val].P1.max()
    #     df["alpha"] = np.where(df[df.GPCRs == gpcr_val].P1 > maxN * 0.5, 0.9, 0.25)
    # else:
    #     df["alpha"] = np.where(df["P1"] > 1500, 0.9, 0.25)

    x_name = axis_map[x_axis.value]
    y_name = axis_map[y_axis.value]

    p.xaxis.axis_label = x_axis.value
    p.yaxis.axis_label = y_axis.value
    p.title.text = "%d Data Points Selected" % len(df)
    # p.x_range = Range1d(-15, getxMax(gpcr_val))
    # p.x_range.end = getxMax(gpcr_val)
    # p.x_range = Range1d(-15, 400)
    # p.y_range = Range1d(-20, 5000)

    maxN = df[df.GPCRs == gpcr_val].P1.max()
    df["alpha"] = np.where(df["P1"] > maxN * 0.5, 0.9, 0.25)

    source.data = dict(
        x=df[x_name],
        y=df[y_name],
        color=df["color"],
        ResName=df["ResName"],
        ResNumber=df["ResNumber"],
        alpha=df["alpha"],
    )
    p.x_range.start = getxMax(gpcr_val)[1] - 20
    p.x_range.end = getxMax(gpcr_val)[0] + 20
    p.y_range.end = getyMax(df, gpcr_val) + 20

#controls = [reviews, boxoffice, genre, min_year, max_year, oscars, director, cast, x_axis, y_axis]
controls = [number, gpcr, lipid, radius, y_axis, x_axis, residue]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())

sizing_mode = 'fixed'  # 'scale_width' also looks nice with this example
# sizing_mode = 'scale_width'  # 'scale_width' also looks nice with this example

inputs = column(*controls, sizing_mode=sizing_mode)
l = layout([
    [desc],
    [inputs, p],
], sizing_mode=sizing_mode)

update()  # initial load of the data

curdoc().add_root(l)
curdoc().title = "GRAPH"
