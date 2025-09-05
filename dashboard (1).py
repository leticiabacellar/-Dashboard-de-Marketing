import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

# Carregar dados
df = pd.read_csv('marketing_data.csv')
df['Data'] = pd.to_datetime(df['Data'])

# Configurar o app Dash com tema Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Cores personalizadas para o tema
colors = {
    'primary': '#2E86AB',
    'secondary': '#A23B72', 
    'success': '#F18F01',
    'info': '#C73E1D',
    'background': '#F8F9FA',
    'text': '#212529'
}

# Layout do dashboard
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("📊 Dashboard de Marketing", 
                   className="text-center mb-4",
                   style={'color': colors['primary'], 'font-weight': 'bold'}),
            html.P("Análise completa de performance de campanhas de marketing digital",
                   className="text-center text-muted mb-4")
        ])
    ]),
    
    # Filtros
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("🎯 Filtros", className="card-title"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Canal:"),
                            dcc.Dropdown(
                                id='canal-dropdown',
                                options=[{'label': 'Todos', 'value': 'all'}] + 
                                        [{'label': canal, 'value': canal} for canal in df['Canal'].unique()],
                                value='all',
                                style={'marginBottom': '10px'}
                            )
                        ], width=4),
                        dbc.Col([
                            html.Label("Campanha:"),
                            dcc.Dropdown(
                                id='campanha-dropdown',
                                options=[{'label': 'Todas', 'value': 'all'}] + 
                                        [{'label': camp, 'value': camp} for camp in df['Campanha'].unique()],
                                value='all',
                                style={'marginBottom': '10px'}
                            )
                        ], width=4),
                        dbc.Col([
                            html.Label("Período:"),
                            dcc.DatePickerRange(
                                id='date-picker-range',
                                start_date=df['Data'].min(),
                                end_date=df['Data'].max(),
                                display_format='DD/MM/YYYY'
                            )
                        ], width=4)
                    ])
                ])
            ], className="mb-4")
        ])
    ]),
    
    # KPIs Cards
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="total-receita", className="card-title text-success"),
                    html.P("💰 Receita Total", className="card-text")
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="total-custo", className="card-title text-danger"),
                    html.P("💸 Custo Total", className="card-text")
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="total-conversoes", className="card-title text-info"),
                    html.P("🎯 Conversões", className="card-text")
                ])
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="roas-medio", className="card-title text-warning"),
                    html.P("📈 ROAS Médio", className="card-text")
                ])
            ])
        ], width=3)
    ], className="mb-4"),
    
    # Gráficos principais
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("📈 Performance ao Longo do Tempo", className="card-title"),
                    dcc.Graph(id='timeline-chart')
                ])
            ])
        ], width=8),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("🎯 Performance por Canal", className="card-title"),
                    dcc.Graph(id='canal-chart')
                ])
            ])
        ], width=4)
    ], className="mb-4"),
    
    # Segunda linha de gráficos
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("💰 Análise de ROI por Campanha", className="card-title"),
                    dcc.Graph(id='roi-chart')
                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("🔄 Funil de Conversão", className="card-title"),
                    dcc.Graph(id='funnel-chart')
                ])
            ])
        ], width=6)
    ], className="mb-4"),
    
    # Insights e storytelling
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("💡 Insights Principais", className="card-title"),
                    html.Div(id="insights-content")
                ])
            ])
        ])
    ])
    
], fluid=True, style={'backgroundColor': colors['background']})

# Callbacks para interatividade
@app.callback(
    [Output('total-receita', 'children'),
     Output('total-custo', 'children'),
     Output('total-conversoes', 'children'),
     Output('roas-medio', 'children'),
     Output('timeline-chart', 'figure'),
     Output('canal-chart', 'figure'),
     Output('roi-chart', 'figure'),
     Output('funnel-chart', 'figure'),
     Output('insights-content', 'children')],
    [Input('canal-dropdown', 'value'),
     Input('campanha-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_dashboard(canal_selected, campanha_selected, start_date, end_date):
    # Filtrar dados
    filtered_df = df.copy()
    
    if canal_selected != 'all':
        filtered_df = filtered_df[filtered_df['Canal'] == canal_selected]
    if campanha_selected != 'all':
        filtered_df = filtered_df[filtered_df['Campanha'] == campanha_selected]
    if start_date and end_date:
        filtered_df = filtered_df[(filtered_df['Data'] >= start_date) & (filtered_df['Data'] <= end_date)]
    
    # Calcular KPIs
    total_receita = f"R$ {filtered_df['Receita'].sum():,.2f}"
    total_custo = f"R$ {filtered_df['Custo'].sum():,.2f}"
    total_conversoes = f"{filtered_df['Conversoes'].sum():,}"
    roas_medio = f"{filtered_df['ROAS'].mean():.1f}%"
    
    # Gráfico de timeline
    timeline_fig = px.line(
        filtered_df.groupby('Data').agg({
            'Receita': 'sum',
            'Custo': 'sum',
            'Conversoes': 'sum'
        }).reset_index(),
        x='Data',
        y=['Receita', 'Custo'],
        title="Receita vs Custo ao Longo do Tempo",
        color_discrete_map={'Receita': colors['success'], 'Custo': colors['info']}
    )
    timeline_fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=colors['text'])
    )
    
    # Gráfico por canal
    canal_data = filtered_df.groupby('Canal').agg({
        'Receita': 'sum',
        'Custo': 'sum',
        'Conversoes': 'sum'
    }).reset_index()
    canal_data['ROI'] = ((canal_data['Receita'] - canal_data['Custo']) / canal_data['Custo']) * 100
    
    canal_fig = px.bar(
        canal_data,
        x='Canal',
        y='ROI',
        title="ROI por Canal",
        color='ROI',
        color_continuous_scale='RdYlGn'
    )
    canal_fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=colors['text'])
    )
    
    # Gráfico ROI por campanha
    roi_data = filtered_df.groupby('Campanha').agg({
        'Receita': 'sum',
        'Custo': 'sum'
    }).reset_index()
    roi_data['ROI'] = ((roi_data['Receita'] - roi_data['Custo']) / roi_data['Custo']) * 100
    
    roi_fig = px.scatter(
        roi_data,
        x='Custo',
        y='Receita',
        size='ROI',
        color='Campanha',
        title="Custo vs Receita por Campanha",
        hover_data=['ROI']
    )
    roi_fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=colors['text'])
    )
    
    # Funil de conversão
    funnel_data = [
        ('Impressões', filtered_df['Impressoes'].sum()),
        ('Cliques', filtered_df['Cliques'].sum()),
        ('Conversões', filtered_df['Conversoes'].sum())
    ]
    
    funnel_fig = go.Figure(go.Funnel(
        y=[item[0] for item in funnel_data],
        x=[item[1] for item in funnel_data],
        textinfo="value+percent initial",
        marker_color=[colors['primary'], colors['secondary'], colors['success']]
    ))
    funnel_fig.update_layout(
        title="Funil de Conversão",
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=colors['text'])
    )
    
    # Insights
    melhor_canal = canal_data.loc[canal_data['ROI'].idxmax(), 'Canal']
    pior_canal = canal_data.loc[canal_data['ROI'].idxmin(), 'Canal']
    taxa_conversao = (filtered_df['Conversoes'].sum() / filtered_df['Cliques'].sum()) * 100
    
    insights = html.Div([
        html.P(f"🏆 Melhor canal: {melhor_canal} com maior ROI"),
        html.P(f"⚠️ Canal que precisa de atenção: {pior_canal}"),
        html.P(f"📊 Taxa de conversão geral: {taxa_conversao:.2f}%"),
        html.P(f"💡 Recomendação: Investir mais no canal {melhor_canal} e otimizar {pior_canal}")
    ])
    
    return (total_receita, total_custo, total_conversoes, roas_medio,
            timeline_fig, canal_fig, roi_fig, funnel_fig, insights)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)

