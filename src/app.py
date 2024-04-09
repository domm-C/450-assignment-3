import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import customize

df = pd.read_csv('ProcessedTweets.csv')
#print(df.columns)
unique_months = df['Month'].unique()
#print(unique_months)
sentiment_min = df['Sentiment'].min()
sentiment_max = df['Sentiment'].max()
subjectivity_min = df['Subjectivity'].min()
subjectivity_max = df['Subjectivity'].max()


dropdown_sliders = html.Div(className="dropnslider_div", children=[
    html.P("Month "),
    dcc.Dropdown(id='month_dropdown_id',
                 options=unique_months,
                 value=None,
                 style=dict(width=100,marginLeft=2,marginRight=40)),
    html.Div(className="dropnslider_div", children=[
        html.P('Sentiment Score '),
        dcc.RangeSlider(className='slider-container',id='sentiment_slider_id',
                   min=sentiment_min,
                   max=sentiment_max,
                   marks={-1:"-1.00", 1:"1.00"},
                   value=[sentiment_min, sentiment_max])
    ]),
    html.Div(className='dropnslider_div', children=[
        html.P("Subjectivity Score "),
        dcc.RangeSlider(className='slider-container',id='subjectivity_slider_id',
                   min=subjectivity_min,
                   max=subjectivity_max,
                   marks={0:"0.00", 1:"1.00"},
                   value=[subjectivity_min, subjectivity_max])
    ])
])

fig = px.scatter(df, x="Dimension 1", y="Dimension 2", color_discrete_sequence=['rgba(128, 128, 128, 0.5)'])
fig.update_layout(customize.custom_fig, dragmode='lasso', xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))

fig.update_xaxes(showticklabels=False, title_text='')
fig.update_yaxes(showticklabels=False, title_text='')

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(className="parent_container", children=[
    html.Div(id="row1", children=[dropdown_sliders]),
    html.Div(id='row2', children=[
        html.Div(dcc.Graph(id='scatter-graph', figure=fig)),
        dash_table.DataTable(id='selected-data-table', columns=[{"name": 'RawTweet', "id": 'RawTweet'}],data=[],
                             page_current=0,
                             page_size=10,
                             style_table={'height': '350px', 'width': '100%', 'overflowY': 'auto'},
                             style_cell={'textAlign': 'center', 'whiteSpace': 'normal'})
    ])
])

@app.callback(
    Output('scatter-graph', 'figure'),
    [Input('month_dropdown_id', 'value'),
     Input('sentiment_slider_id', 'value'),
     Input('subjectivity_slider_id', 'value')]
)
def update_scatter_plot(selected_month, sentiment_range, subjectivity_range):
    filtered_df = df.copy()
    if selected_month:
        filtered_df = filtered_df[filtered_df['Month'] == selected_month]
    filtered_df = filtered_df[
        (filtered_df['Sentiment'] >= sentiment_range[0]) & (filtered_df['Sentiment'] <= sentiment_range[1]) &
        (filtered_df['Subjectivity'] >= subjectivity_range[0]) & (filtered_df['Subjectivity'] <= subjectivity_range[1])
    ]
    fig = px.scatter(filtered_df, x="Dimension 1", y="Dimension 2", color_discrete_sequence=['rgba(128, 128, 128, 0.5)'])
    fig.update_layout(customize.custom_fig, dragmode='lasso', xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
    fig.update_xaxes(showticklabels=False, title_text='')
    fig.update_yaxes(showticklabels=False, title_text='')
    return fig

@app.callback(
    Output('selected-data-table', 'data'),
    [Input('scatter-graph', 'selectedData')]
)
def update_table(selectedData):
    if selectedData is not None:
        indices = [point['pointIndex'] for point in selectedData['points']]
        selected_df = df.iloc[indices]
        return selected_df.to_dict('records')
    return []


if __name__ == '__main__':
    app.run_server(debug=True)