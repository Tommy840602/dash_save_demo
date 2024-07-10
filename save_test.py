#import dash 
#import dash_core_components as dcc 
#import dash_html_components as html 
#from dash import Dash, dcc, html, Input, Output, ALL,MATCH,State,ctx
#import json 
#import os 

#app = dash.Dash(__name__) 
#DATA_FILE = 'settings.json' 
 
#app.layout = html.Div([ 
#    html.Button(id='save', n_clicks=0, children='save'), 
#    html.Button(id='add', n_clicks=0, children='add'), 
#    html.Div(id='expand',children=[]),
#    html.Div(id="output")
#     ]) 


#@app.callback(
#    Output('expand', 'children'), 
#    Input('add', 'n_clicks'),
#    State('expand', 'children'),) 

#def expand(n_clicks,children): 
#    _ = html.Div([
#        dcc.Input(
#        id={"type": "input","index": n_clicks},
#        type='text'),
#        ])
#    children.append(_)
#    return children


#@app.callback(
#    Output("output","children"),
#    Input({"type":"input", "index": ALL}, "value"),
#    Input({"type":"save", "index": ALL}, "n_clicks"),
#)
#def save_data(input_value,n_clicks):
#    data = {'input_value': input_value} 
#    with open(DATA_FILE, 'w') as f: 
#        json.dump(data, f) 
#        return f"Data saved: {input_value}" 
#    return 'No data saved yet' 

   
#def load_data(): 
#    if os.path.exists(DATA_FILE): 
#        with open(DATA_FILE, 'r') as f: 
#            data = json.load(f) 
#            return data['input_value'] 
#        return '' 
    
    
#if __name__ == '__main__': 
#     initial_value = load_data()
#     print(initial_value)
#     print(app.layout.children[3])
#     app.layout.children[3].value=initial_value[0]
#     app.run_server(debug=False)

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, ALL, ctx
import sqlite3
import os

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
DB_FILE = 'settings.db'

# 初始化数据库
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            input_value TEXT,
            dropdown_value INTEGER
        )
    ''')
    conn.commit()
    conn.close()

app.layout = dbc.Container([
    dbc.Button(id='save', n_clicks=0, children='保存', color='primary', className='mr-2'),
    dbc.Button(id='add', n_clicks=0, children='新增', color='secondary', className='mr-2'),
    html.Div(id='expand', children=[]),
    html.Div(id="output"),
    dcc.Store(id='stored-data', data={})
])

@app.callback(
    Output('expand', 'children'),
    Output('stored-data', 'data'),
    Output('output', 'children'),
    [Input('add', 'n_clicks'),
    Input('save', 'n_clicks'),
    State('expand', 'children'),
    State('stored-data', 'data'),
    State({'type': 'input', 'index': ALL}, 'value'),
    State({'type': 'dropdown', 'index': ALL}, 'value')],
)
def handle_callbacks(add_clicks, save_clicks, children, stored_data, input_values, dropdown_values):
    triggered_id = ctx.triggered_id

    if triggered_id == 'add':
        if add_clicks > len(children):
            new_input = dbc.Row([
                dbc.Col([
                    dbc.Label(f'输入 {add_clicks}'),
                    dbc.Input(id={"type": "input", "index": add_clicks}, type='text', value='')
                ], width=6),
                dbc.Col([
                    dbc.Label(f'下拉菜单 {add_clicks}'),
                    dcc.Dropdown(
                        id={"type": "dropdown", "index": add_clicks},
                        options=[{'label': f'选项 {i}', 'value': i} for i in range(1, 6)],
                        value=1
                    )
                ], width=6)
            ], className='mb-2')
            children.append(new_input)
        return children, dash.no_update, dash.no_update

    elif triggered_id == 'save':
        if save_clicks > 0:
            data = {
                'inputs': {str(i): value for i, value in enumerate(input_values)},
                'dropdowns': {str(i): value for i, value in enumerate(dropdown_values)}
            }
            save_to_db(data)
            return children, data, f"数据已保存: {data}"

    if not stored_data:
        stored_data = load_from_db()
        children = [
            dbc.Row([
                dbc.Col([
                    dbc.Label(f'输入 {idx}'),
                    dbc.Input(id={"type": "input", "index": int(idx)}, type='text', value=value)
                ], width=6),
                dbc.Col([
                    dbc.Label(f'下拉菜单 {idx}'),
                    dcc.Dropdown(
                        id={"type": "dropdown", "index": int(idx)},
                        options=[{'label': f'选项 {i}', 'value': i} for i in range(1, 6)],
                        value=stored_data['dropdowns'][idx]
                    )
                ], width=6)
            ], className='mb-2') for idx, value in stored_data['inputs'].items()
        ]

    return children, stored_data, dash.no_update

def save_to_db(data):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM settings')
    for idx, value in data['inputs'].items():
        cursor.execute('''
            INSERT INTO settings (id, input_value, dropdown_value)
            VALUES (?, ?, ?)
        ''', (idx, value, data['dropdowns'][idx]))
    conn.commit()
    conn.close()

def load_from_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, input_value, dropdown_value FROM settings')
    rows = cursor.fetchall()
    data = {
        'inputs': {str(row[0]): row[1] for row in rows},
        'dropdowns': {str(row[0]): row[2] for row in rows}
    }
    conn.close()
    return data

if __name__ == '__main__':
    init_db()
    app.run_server(debug=True)