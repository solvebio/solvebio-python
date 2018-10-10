import dash
import dash_html_components as html
import dash_core_components as dcc
import flask

from solvebio.contrib.dash import SolveBioDash


# Initialize the Dash app with SolveBio auth.
app = SolveBioDash(
    name=__name__,
    title='Example Dash App',
    app_url='http://localhost:8050',
    client_id='zxpjuufs7k65f26zyq3vq4hqqw2dmu13x77p7qg2',
    solvebio_url='http://my.solvebio.com')


def current_user():
    if app.auth:
        user = flask.g.client.User.retrieve()
        return [
            html.Div(children='Logged-in as: {}'.format(user.full_name)),
            html.A('Log out', href='/_dash-logout')
        ]
    else:
        return [
            html.P('(SolveBio Auth not configured)')
        ]


def layout():
    return html.Div([
        html.H1('Welcome to your Dash+SolveBio app'),
        html.P(current_user()),
        dcc.Dropdown(
            id='dropdown',
            options=[{'label': i, 'value': i} for i in ['A', 'B']],
            value='A'
        ),
        dcc.Graph(id='graph')
    ], className="container")


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


#
# Your Dash app callback functions
#

@app.callback(
    dash.dependencies.Output('page-content', 'children'),
    [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    """Render the layout depending on the pathname."""
    return layout()


@app.callback(
    dash.dependencies.Output('graph', 'figure'),
    [dash.dependencies.Input('dropdown', 'value')])
def update_graph(dropdown_value):
    return {
        'layout': {
            'title': 'Graph of {}'.format(dropdown_value),
            'margin': {
                'l': 20,
                'b': 20,
                'r': 10,
                't': 60
            }
        },
        'data': [{'x': [1, 2, 3], 'y': [4, 1, 2]}]
    }


app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})

if __name__ == '__main__':
    app.run_server(debug=True)
