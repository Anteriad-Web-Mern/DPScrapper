from flask import Blueprint, render_template, jsonify
import plotly.graph_objects as go
import plotly.utils
import json
from utils.db import get_data

viz_bp = Blueprint('visualize', __name__)

@viz_bp.route("/visualize")
def visualize():
    data = get_data()
    domains = [d["domain"] for d in data]
    users = [d["users"] for d in data]
    blogs = [d["blogs"] for d in data]
    thank_you = [d["thank_you"] for d in data]

    graph_data = [
        {"data": [go.Bar(x=domains, y=users, name="Users")], "layout": go.Layout(title="Users")},
        {"data": [go.Bar(x=domains, y=blogs, name="Blogs")], "layout": go.Layout(title="Blogs")},
        {"data": [go.Bar(x=domains, y=thank_you, name="Thank-You Pages")], "layout": go.Layout(title="Thank-You Pages")},
    ]
    return render_template("visualize.html", graph_data=json.dumps(graph_data, cls=plotly.utils.PlotlyJSONEncoder))
