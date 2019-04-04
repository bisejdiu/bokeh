from os.path import dirname, join

import numpy as np
import pandas as pd
import pandas.io.sql as psql
import sqlite3 as sql

from bokeh.plotting import figure
from bokeh.layouts import layout, column
from bokeh.models import ColumnDataSource, Div, Range1d, CustomJS
from bokeh.models.widgets import Slider, Select, TextInput
from bokeh.io import curdoc

# TO DO LIST
# 4. Fix Radius labels/names.
# 5. Embedding Bokeh into GLI website.
# 6. Minor tweaks and optimizations.

conn = sql.connect('C:/Users/Besian/Documents/GitHub/bokeh/examples/app/gli/GPCR.db')
query = open(join(dirname(__file__), 'query.sql')).read()
dfGPCR = psql.read_sql(query, conn)

dfGPCR["color"] = np.where(dfGPCR["P1"] > 1, "red", "grey")
dfGPCR["alpha"] = np.where(dfGPCR["P1"] > 1.5, 0.9, 0.50)

axis_map = {
    "Contact Number": "P1",
    "Contact Duration": "D",
    "Residue": "ResNumber",
}

#radius_map = {
#    "7Å" : "rcutoff7A",
#    "6Å" : "rcutoff6A",
#    "5Å" : "rcutoff5A",
#}

desc = Div(text=open(join(dirname(__file__), "index.html")).read(), width=800)
# desc = Div(text=open(join(dirname(__file__), "description.html")).read(), width=800)

# Create Input controls
number = Slider(title="Number Cutoff", value=0, start=0, end=4, step=0.1)
residue = TextInput(title="Residue name (3 letter code):")

gpcr = Select(title="GPCRs", value="All",
               options=open(join(dirname(__file__), 'GPCRs.txt')).read().split())

lipid = Select(title="Lipids", value="CHOL",
               options=open(join(dirname(__file__), 'Lipids.txt')).read().split())

radius = Select(title="Radius", value="rcutoff7A",
               options=open(join(dirname(__file__), 'Radius.txt')).read().split())

x_axis = Select(title="X Axis", options=sorted(axis_map.keys()), value="Residue")
y_axis = Select(title="Y Axis", options=sorted(axis_map.keys()),
                value="Contact Number")

# Create Column Data Source that will be used by the plot
source = ColumnDataSource(data=dict(x=[], y=[], color=[], ResName=[],
                                    ResNumber=[], gpcrName=[], alpha=[],
                                    height=[]))

TOOLTIPS=[
    ("ResName", "@ResName"),
    ("ResID", "@ResNumber"),
    ("GPCR", "@gpcrName"),
]

p = figure(plot_height=800, plot_width=800, title="", toolbar_location="right", tooltips=TOOLTIPS)
p.circle(x="x", y="y", source=source, size=5, color="color", line_color=None, fill_alpha="alpha")

def select_dfGPCR():
    gpcr_val  = gpcr.value
    lipid_val = lipid.value
    radius_val = radius.value

    residue_val = residue.value.upper()
    selected = dfGPCR[
        (dfGPCR.P1 >= number.value)
    ]

    if (gpcr_val != "All"):
        selected = selected[selected.GPCRs.str.contains(gpcr_val)==True]

    if (lipid_val != "All"):
        selected = selected[selected.Lipids == lipid_val]

    if (radius_val != "All"):
        selected = selected[selected.Radius.str.contains(radius_val)==True]

    if (residue_val != ""):
        selected = selected[selected.ResName.str.contains(residue_val)==True]

    return selected


def update():
    gpcr_val = gpcr.value

    df = select_dfGPCR()

    x_name = axis_map[x_axis.value]
    y_name = axis_map[y_axis.value]

    p.xaxis.axis_label = x_axis.value
    p.yaxis.axis_label = y_axis.value
    p.title.text = "%d Data Points Selected" % len(df)

    if (gpcr_val != "All"):
        if (y_axis.value == "Contact Number"):
            del df["alpha"]
            del df["color"]
            maxN = df[df.GPCRs == gpcr_val].P1.max()
            df["alpha"] = np.where(df["P1"] > maxN * 0.6, 0.9, 0.50)
            df["color"] = np.where(df["P1"] > maxN * 0.4, "red", "grey")
        else:
            del df["alpha"]
            del df["color"]
            maxN = df[df.GPCRs == gpcr_val].D.max()
            df["alpha"] = np.where(df["D"] > maxN * 0.6, 0.9, 0.50)
            df["color"] = np.where(df["D"] > maxN * 0.4, "red", "grey")

    source.data = dict(
        x=df[x_name],
        y=df[y_name],
        color=df["color"],
        ResName=df["ResName"],
        ResNumber=df["ResNumber"],
        gpcrName=df["GPCRs"],
        alpha=df["alpha"],
    )

controls = [number, gpcr, lipid, radius, y_axis, x_axis, residue]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())

sizing_mode = 'fixed'

inputs = column(*controls, sizing_mode=sizing_mode)
l = layout([
    # [desc],
    [inputs, p],
], sizing_mode=sizing_mode)

update()

curdoc().add_root(l)
curdoc().title = "GRAPH"
