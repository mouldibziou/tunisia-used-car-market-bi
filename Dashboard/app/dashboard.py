import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from app.data_processor import CarDataProcessor

class TunisiaCarDashboard:
    """
    Interactive Plotly Dash dashboard for Tunisia used car market analysis.
    Shows price evolution trends with interactive filters.
    """
    
    def __init__(self, merged_data: pd.DataFrame):
        """
        Initialize dashboard with pre-loaded merged data.
        
        Parameters:
        - merged_data: DataFrame containing merged car listing data
        """
        self.app = dash.Dash(__name__, 
                            meta_tags=[{"name": "viewport", 
                                    "content": "width=device-width, initial-scale=1"}])
        
        # Store merged data
        self.merged_data = merged_data
        
        # Process data for visualization
        print("🔄 Processing data for visualization...")
        self.agg_data = self._aggregate_data()
        self.market_trend = self._get_market_trend()
        self.metadata = self._get_metadata()
        print("✅ Data processing complete!")
        
        # Setup layout and callbacks
        self._create_layout()
        self._register_callbacks()

    def _aggregate_data(self) -> pd.DataFrame:
        """Aggregate data by year for trend analysis."""
        
        # Build aggregation dictionary based on available columns
        agg_dict = {
            'price': ['mean', 'median', 'count', 'std']
        }
        
        # Add optional columns if they exist
        if 'mileage' in self.merged_data.columns:
            agg_dict['mileage'] = 'mean'
        
        if 'car_age' in self.merged_data.columns:
            agg_dict['car_age'] = 'mean'
        
        # Perform aggregation
        agg_data = self.merged_data.groupby(['brand', 'model', 'year']).agg(agg_dict).reset_index()
        
        # Flatten column names
        new_columns = ['brand', 'model', 'year', 'avg_price', 
                    'median_price', 'sample_count', 'price_std']
        
        if 'mileage' in agg_dict:
            new_columns.append('avg_mileage')
        
        if 'car_age' in agg_dict:
            new_columns.append('avg_car_age')
        
        agg_data.columns = new_columns
        
        # Round values
        agg_data['avg_price'] = agg_data['avg_price'].round(0)
        agg_data['median_price'] = agg_data['median_price'].round(0)
        
        if 'avg_mileage' in agg_data.columns:
            agg_data['avg_mileage'] = agg_data['avg_mileage'].round(0)
        
        return agg_data

    def _get_market_trend(self) -> pd.DataFrame:
        """Calculate overall market average price per year."""
        market_trend = self.merged_data.groupby('year').agg({
            'price': ['mean', 'median', 'count']
        }).reset_index()
        
        market_trend.columns = ['year', 'market_avg_price', 
                            'market_median_price', 'total_listings']
        market_trend['market_avg_price'] = market_trend['market_avg_price'].round(0)
        
        return market_trend

    def _get_metadata(self) -> dict:
        """Get dataset statistics for dashboard info."""
        return {
            'total_records': len(self.merged_data),
            'brands': sorted(self.merged_data['brand'].unique()),
            'year_range': (int(self.merged_data['year'].min()), 
                        int(self.merged_data['year'].max())),
            'price_range': (int(self.merged_data['price'].min()), 
                        int(self.merged_data['price'].max())),
            'avg_market_price': int(self.merged_data['price'].mean())
        }
            
    ####################
    def _create_layout(self):
        """Create the dashboard layout with all components."""
        
        self.app.layout = html.Div([
            # Header Section
            # Header Section - REPLACE EXISTING
            html.Div([
                html.Div([
                    html.H1("🚗 Tunisia Used Car Market Analysis", 
                        className="header-title"),
                    html.P([
                        "Exploring the evolution of used car prices in Tunisia (2007–2025) | ",
                        html.Span(f"{self.metadata['total_records']:,} listings analyzed", 
                                className="highlight")
                    ], className="header-subtitle"),
                    html.P([
                        "This dashboard reveals a dramatic surge in used car prices over the past 18 years. ",
                        "Select a brand and model to explore specific trends, or toggle the market average ",
                        "to see the broader picture of price inflation in Tunisia's automotive sector."
                    ], className="header-description")
                ], className="header-content")
            ], className="header-container"),
            
            # Key Metrics Section
            # In the metrics section, replace with:
            html.Div([
                html.Div([
                    html.Div("🏢", style={'fontSize': '2rem', 'marginBottom': '0.5rem'}),
                    html.H3(f"{self.metadata['brands'].__len__()}", className="metric-value"),
                    html.P("Brands Analyzed", className="metric-label")
                ], className="metric-card"),

                html.Div([
                    html.Div("📋", style={'fontSize': '2rem', 'marginBottom': '0.5rem'}),
                    html.H3(f"{self.metadata['total_records']:,}", className="metric-value"),
                    html.P("Total Listings", className="metric-label")
                ], className="metric-card"),

                html.Div([
                    html.Div("📅", style={'fontSize': '2rem', 'marginBottom': '0.5rem'}),
                    html.H3(f"{self.metadata['year_range'][1] - self.metadata['year_range'][0]}", className="metric-value"),
                    html.P("Years Covered", className="metric-label")
                ], className="metric-card"),

                html.Div([
                    html.Div("💰", style={'fontSize': '2rem', 'marginBottom': '0.5rem'}),
                    html.H3(f"{self.metadata['avg_market_price']:,} DT", className="metric-value"),
                    html.P("Avg Market Price", className="metric-label")
                ], className="metric-card"),
            ], style={
                'display': 'flex',
                'justifyContent': 'space-around',
                'alignItems': 'center',
                'flexWrap': 'wrap',
                'marginTop': '20px'
            }),

            
            # Filters Section
            html.Div([
                html.H3("🔍 Filter Your Analysis", className="section-title"),
                html.Div([
                    # Brand Selector
                    html.Div([
                        html.Label("Select Brand", className="filter-label"),
                        dcc.Dropdown(
                            id='brand-dropdown',
                            options=[{'label': brand, 'value': brand} 
                                    for brand in self.metadata['brands']],
                            value=self.metadata['brands'][0] if self.metadata['brands'] else None,
                            clearable=False,
                            className="dropdown"
                        )
                    ], className="filter-item"),
                    
                    # Model Selector
                    html.Div([
                        html.Label("Select Model", className="filter-label"),
                        dcc.Dropdown(
                            id='model-dropdown',
                            clearable=False,
                            className="dropdown"
                        )
                    ], className="filter-item"),
                    
                    # Year Range Selector
                    html.Div([
                        html.Label("Year Range", className="filter-label"),
                        dcc.RangeSlider(
                            id='year-slider',
                            min=self.metadata['year_range'][0],
                            max=self.metadata['year_range'][1],
                            value=[self.metadata['year_range'][0], 
                                  self.metadata['year_range'][1]],
                            marks={year: str(year) for year in range(
                                self.metadata['year_range'][0], 
                                self.metadata['year_range'][1] + 1, 3)},
                            tooltip={"placement": "bottom", "always_visible": False},
                            className="slider"
                        )
                    ], className="filter-item-wide"),
                ], className="filters-grid"),
                
                # Toggle for Market Trend
                html.Div([
                    html.Label([
                        dcc.Checklist(
                            id='market-trend-toggle',
                            options=[{'label': ' Show Overall Market Trend', 'value': 'show'}],
                            value=['show'],
                            className="toggle-checkbox"
                        )
                    ], className="toggle-label")
                ], className="toggle-container")
            ], className="filters-container"),


            # Add this new section between filters-container and chart-container
            # Visual Guide Section
            html.Div([
                html.H3("📖 How to Read the Chart", className="section-title"),
                html.Div([
                    html.Div([
                        html.Div([
                            html.Div(style={
                                'width': '20px',
                                'height': '20px',
                                'borderRadius': '50%',
                                'backgroundColor': '#0066FF',
                                'marginRight': '0.75rem'
                            }),
                            html.Div([
                                html.Strong("Solid Blue Line", style={'color': '#0F172A'}),
                                html.P("Reliable data (5+ listings per year)", 
                                    style={'color': '#64748B', 'fontSize': '0.9rem', 'margin': '0'})
                            ])
                        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '1rem'}),
                        
                        html.Div([
                            html.Div("◆", style={
                                'fontSize': '20px',
                                'color': '#EF4444',
                                'marginRight': '0.75rem'
                            }),
                            html.Div([
                                html.Strong("Red Diamonds", style={'color': '#0F172A'}),
                                html.P("Limited data (<5 listings) - interpret with caution", 
                                    style={'color': '#64748B', 'fontSize': '0.9rem', 'margin': '0'})
                            ])
                        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '1rem'}),
                        
                        html.Div([
                            html.Div(style={
                                'width': '40px',
                                'height': '3px',
                                'background': 'repeating-linear-gradient(to right, #7C3AED 0, #7C3AED 5px, transparent 5px, transparent 10px)',
                                'marginRight': '0.75rem'
                            }),
                            html.Div([
                                html.Strong("Purple Dotted Line", style={'color': '#0F172A'}),
                                html.P("Overall market average (all brands/models)", 
                                    style={'color': '#64748B', 'fontSize': '0.9rem', 'margin': '0'})
                            ])
                        ], style={'display': 'flex', 'alignItems': 'center'})
                        
                    ], style={
                        'display': 'grid',
                        'gridTemplateColumns': 'repeat(auto-fit, minmax(280px, 1fr))',
                        'gap': '1.5rem'
                    })
                ], style={
                    'background': '#F8FAFC',
                    'padding': '1.5rem',
                    'borderRadius': '0.75rem',
                    'border': '1px solid #E2E8F0'
                })
            ], className="insights-container", style={'marginBottom': 'var(--space-lg)'}),
            
            # Main Chart Section
            html.Div([
                dcc.Loading(
                    id="loading-chart",
                    type="default",
                    children=[
                        dcc.Graph(id='price-evolution-chart', className="main-chart")
                    ]
                )
            ], className="chart-container"),
            
            # Data Quality Insights Section
            html.Div([
                html.H3("📊 Data Quality & Insights", className="section-title"),
                html.Div(id='data-insights', className="insights-content")
            ], className="insights-container"),
            
            # Footer
            html.Div([
                html.P([
                    "Data scraped from Tunisian online car marketplaces | ",
                    "Analysis by Mohamed Mouldi Bziou | ",
                    html.A("GitHub", href="https://github.com/yourusername", 
                          target="_blank", className="footer-link"),
                    " | ",
                    html.A("LinkedIn", href="https://www.linkedin.com/in/mohamedmouldibziou/", 
                          target="_blank", className="footer-link")
                ], className="footer-text")
            ], className="footer-container")
            
        ], className="main-container")
    
    def _register_callbacks(self):
        """Register all interactive callbacks."""
        
        # Update model dropdown based on selected brand
        @self.app.callback(
            Output('model-dropdown', 'options'),
            Output('model-dropdown', 'value'),
            Input('brand-dropdown', 'value')
        )
        def update_models(selected_brand):
            if not selected_brand:
                return [], None
            
            models = sorted(self.merged_data[
                self.merged_data['brand'] == selected_brand
            ]['model'].unique())
            
            options = [{'label': model, 'value': model} for model in models]
            value = models[0] if models else None
            
            return options, value
        
        # Update main chart and insights
        @self.app.callback(
            Output('price-evolution-chart', 'figure'),
            Output('data-insights', 'children'),
            Input('brand-dropdown', 'value'),
            Input('model-dropdown', 'value'),
            Input('year-slider', 'value'),
            Input('market-trend-toggle', 'value')
        )
        def update_chart(brand, model, year_range, show_market):
            if not brand or not model:
                return go.Figure(), html.P("Please select a brand and model.")
            
            # Filter data
            model_data = self.agg_data[
                (self.agg_data['brand'] == brand) &
                (self.agg_data['model'] == model) &
                (self.agg_data['year'] >= year_range[0]) &
                (self.agg_data['year'] <= year_range[1])
            ].sort_values('year')
            
            # Create figure
            fig = go.Figure()
            
            # Add market trend if toggled
            if 'show' in (show_market or []):
                market_filtered = self.market_trend[
                    (self.market_trend['year'] >= year_range[0]) &
                    (self.market_trend['year'] <= year_range[1])
                ]
                
                fig.add_trace(go.Scatter(
                    x=market_filtered['year'],
                    y=market_filtered['market_avg_price'],
                    mode='lines',
                    name='Overall Market Average',
                    line=dict(color='rgba(150, 150, 150, 0.5)', width=2, dash='dot'),
                    hovertemplate='<b>Market Average</b><br>Year: %{x}<br>Price: %{y:,.0f} DT<extra></extra>'
                ))
            
            # Identify sparse data points (< 5 samples)
            sparse_mask = model_data['sample_count'] < 5
            dense_data = model_data[~sparse_mask]
            sparse_data = model_data[sparse_mask]
            
            # Add main model trend line (dense data)
            # Add main model trend line (dense data) - REPLACE EXISTING
            if not dense_data.empty:
                fig.add_trace(go.Scatter(
                    x=dense_data['year'],
                    y=dense_data['avg_price'],
                    mode='lines+markers',
                    name=f'{brand} {model}',
                    line=dict(
                        color='#0066FF',
                        width=4,
                        shape='spline',  # Smooth curves
                        smoothing=0.3
                    ),
                    marker=dict(
                        size=10,
                        symbol='circle',
                        color='#0066FF',
                        line=dict(width=2, color='white')
                    ),
                    fill='tonexty',
                    fillcolor='rgba(0, 102, 255, 0.05)',
                    hovertemplate=(
                        '<b style="font-size:14px">%{fullData.name}</b><br>'
                        '<b>Year:</b> %{x}<br>'
                        '<b>Avg Price:</b> %{y:,.0f} TND<br>'
                        '<b>Samples:</b> %{customdata[0]}'
                        '<extra></extra>'
                    ),
                    customdata=dense_data[['sample_count']].values
                ))

            # Market trend - REPLACE EXISTING
            if 'show' in (show_market or []):
                market_filtered = self.market_trend[
                    (self.market_trend['year'] >= year_range[0]) &
                    (self.market_trend['year'] <= year_range[1])
                ]
                
                fig.add_trace(go.Scatter(
                    x=market_filtered['year'],
                    y=market_filtered['market_avg_price'],
                    mode='lines',
                    name='Market Average',
                    line=dict(
                        color='rgba(124, 58, 237, 0.6)',
                        width=3,
                        dash='dot'
                    ),
                    hovertemplate=(
                        '<b style="font-size:14px">Overall Market</b><br>'
                        '<b>Year:</b> %{x}<br>'
                        '<b>Avg Price:</b> %{y:,.0f} TND'
                        '<extra></extra>'
                    )
                ))

            # Sparse data points - REPLACE EXISTING
            if not sparse_data.empty:
                fig.add_trace(go.Scatter(
                    x=sparse_data['year'],
                    y=sparse_data['avg_price'],
                    mode='markers',
                    name=f'{brand} {model} (Limited Data)',
                    marker=dict(
                        size=12,
                        symbol='diamond',
                        color='#EF4444',
                        line=dict(width=2, color='white'),
                        opacity=0.8
                    ),
                    hovertemplate=(
                        '<b style="font-size:14px">%{fullData.name}</b><br>'
                        '<b>Year:</b> %{x}<br>'
                        '<b>Avg Price:</b> %{y:,.0f} TND<br>'
                        '<b>⚠️ Samples:</b> %{customdata[0]} (Low confidence)'
                        '<extra></extra>'
                    ),
                    customdata=sparse_data[['sample_count']].values
                ))
            
            # Calculate price growth if sufficient data
            # Calculate price growth if sufficient data - REPLACE EXISTING ANNOTATIONS SECTION
            annotations = []
            if len(model_data) >= 2:
                first_price = model_data.iloc[0]['avg_price']
                last_price = model_data.iloc[-1]['avg_price']
                price_growth = ((last_price - first_price) / first_price) * 100
                
                # Starting point annotation
                annotations.append(dict(
                    x=model_data.iloc[0]['year'],
                    y=first_price,
                    text=f"<b>{first_price:,.0f} TND</b><br>Starting Point",
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor="#10B981",
                    ax=40,
                    ay=-50,
                    font=dict(size=11, color="#0F172A", family="Inter"),
                    bgcolor="rgba(255, 255, 255, 0.95)",
                    bordercolor="#10B981",
                    borderwidth=2,
                    borderpad=6,
                    opacity=0.95
                ))
                
                # Ending point annotation with growth
                arrow_color = "#EF4444" if price_growth > 0 else "#10B981"
                annotations.append(dict(
                    x=model_data.iloc[-1]['year'],
                    y=last_price,
                    text=f"<b>{last_price:,.0f} TND</b><br>"
                        f"<span style='color:{arrow_color}'>{price_growth:+.1f}%</span>",
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor=arrow_color,
                    ax=-40,
                    ay=-50,
                    font=dict(size=11, color="#0F172A", family="Inter"),
                    bgcolor="rgba(255, 255, 255, 0.95)",
                    bordercolor=arrow_color,
                    borderwidth=2,
                    borderpad=6,
                    opacity=0.95
                ))
                
                # Peak price annotation if there's a significant peak
                max_price_idx = model_data['avg_price'].idxmax()
                max_price_row = model_data.loc[max_price_idx]
                if max_price_row['avg_price'] > last_price * 1.1:  # If peak is 10% higher
                    annotations.append(dict(
                        x=max_price_row['year'],
                        y=max_price_row['avg_price'],
                        text=f"<b>Peak</b><br>{max_price_row['avg_price']:,.0f} TND",
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=1,
                        arrowwidth=2,
                        arrowcolor="#F59E0B",
                        ax=0,
                        ay=-60,
                        font=dict(size=10, color="#0F172A", family="Inter"),
                        bgcolor="rgba(255, 255, 255, 0.95)",
                        bordercolor="#F59E0B",
                        borderwidth=2,
                        borderpad=4,
                        opacity=0.95
                    ))
            
            # Layout configuration
            # Inside the update_chart callback, replace the fig.update_layout() section:

# Layout configuration with premium styling
            fig.update_layout(
                title=dict(
                    text=f'<b>Price Evolution: {brand} {model}</b><br>'
                        f'<sub style="font-size:14px; color:#64748B">{year_range[0]}–{year_range[1]} • '
                        f'{len(model_data)} data points</sub>',
                    font=dict(size=26, color='#0F172A', family='Space Grotesk, Arial Black'),
                    x=0.5,
                    xanchor='center',
                    y=0.96,
                    yanchor='top'
                ),
                xaxis=dict(
                    title=dict(
                        text='<b>Year</b>',
                        font=dict(size=14, color='#475569', family='Inter')
                    ),
                    showgrid=True,
                    gridcolor='rgba(226, 232, 240, 0.5)',
                    gridwidth=1,
                    dtick=1,
                    showline=True,
                    linewidth=2,
                    linecolor='#E2E8F0',
                    tickfont=dict(size=12, color='#64748B', family='Inter'),
                    tickmode='linear'
                ),
                yaxis=dict(
                    title=dict(
                        text='<b>Average Price (TND)</b>',
                        font=dict(size=14, color='#475569', family='Inter')
                    ),
                    showgrid=True,
                    gridcolor='rgba(226, 232, 240, 0.5)',
                    gridwidth=1,
                    tickformat=',.0f',
                    showline=True,
                    linewidth=2,
                    linecolor='#E2E8F0',
                    tickfont=dict(size=12, color='#64748B', family='Inter'),
                    zeroline=False
                ),
                hovermode='x unified',
                plot_bgcolor='#FFFFFF',
                paper_bgcolor='#FFFFFF',
                font=dict(family='Inter, Arial', size=13, color='#1E293B'),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    bgcolor='rgba(255, 255, 255, 0.95)',
                    bordercolor='#E2E8F0',
                    borderwidth=1,
                    font=dict(size=12, family='Inter')
                ),
                annotations=annotations,
                height=650,
                margin=dict(t=120, b=80, l=90, r=40),
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=13,
                    font_family="Inter",
                    bordercolor='#E2E8F0'
                )
            )
            
            # Generate insights
            insights = self._generate_insights(model_data, brand, model)
            
            return fig, insights
    
    def _generate_insights(self, data, brand, model):
        """Generate data quality and trend insights with enhanced formatting."""
        if data.empty:
            return html.Div([
                html.Div([
                    html.Span("⚠️", style={'fontSize': '2rem', 'marginRight': '1rem'}),
                    html.Span("No data available for the selected filters.",
                            style={'fontSize': '1.1rem', 'color': '#EF4444'})
                ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center',
                        'padding': '2rem', 'background': 'rgba(239, 68, 68, 0.05)',
                        'borderRadius': '0.75rem', 'border': '2px dashed #EF4444'})
            ])
        
        insights_list = []
        
        # Sample size insight with icon
        total_samples = data['sample_count'].sum()
        avg_samples = data['sample_count'].mean()
        insights_list.append(
            html.Li([
                html.Span("📊", style={'fontSize': '1.5rem', 'marginRight': '0.75rem'}),
                html.Div([
                    html.Strong("Dataset Coverage: ", style={'color': '#0F172A'}),
                    html.Span(f"{int(total_samples):,} total listings | ", style={'color': '#475569'}),
                    html.Span(f"{avg_samples:.1f} avg/year", style={'color': '#475569'})
                ])
            ], style={'display': 'flex', 'alignItems': 'center'})
        )
        
        # Sparse data warning with better styling
        sparse_years = data[data['sample_count'] < 5]
        if not sparse_years.empty:
            years_str = ', '.join(map(str, sparse_years['year'].tolist()))
            insights_list.append(
                html.Li([
                    html.Span("⚠️", style={'fontSize': '1.5rem', 'marginRight': '0.75rem'}),
                    html.Div([
                        html.Strong("Limited Data Warning: ", style={'color': '#EF4444'}),
                        html.Span(f"Years with <5 samples: {years_str}",
                                style={'color': '#64748B', 'fontSize': '0.95rem'})
                    ])
                ], style={'display': 'flex', 'alignItems': 'flex-start',
                        'background': 'rgba(239, 68, 68, 0.05)',
                        'borderLeft': '4px solid #EF4444'})
            )
        
        # Price trend with visual indicator
        if len(data) >= 2:
            first_price = data.iloc[0]['avg_price']
            last_price = data.iloc[-1]['avg_price']
            price_change = last_price - first_price
            pct_change = (price_change / first_price) * 100
            
            trend_emoji = "📈" if price_change > 0 else "📉"
            trend_color = "#EF4444" if price_change > 0 else "#10B981"
            
            insights_list.append(
                html.Li([
                    html.Span(trend_emoji, style={'fontSize': '1.5rem', 'marginRight': '0.75rem'}),
                    html.Div([
                        html.Strong("Price Evolution: ", style={'color': '#0F172A'}),
                        html.Span(f"{first_price:,.0f} TND → {last_price:,.0f} TND ",
                                style={'color': '#475569'}),
                        html.Span(f"({pct_change:+.1f}%)",
                                style={'color': trend_color, 'fontWeight': '700',
                                    'background': f'{trend_color}15',
                                    'padding': '0.2rem 0.5rem',
                                    'borderRadius': '0.375rem',
                                    'fontSize': '0.95rem'})
                    ])
                ], style={'display': 'flex', 'alignItems': 'center'})
            )
        
        # Volatility insight
        if 'price_std' in data.columns and not data['price_std'].isna().all():
            avg_std = data['price_std'].mean()
            avg_price = data['avg_price'].mean()
            volatility = (avg_std / avg_price) * 100
            
            volatility_emoji = "🔴" if volatility > 20 else "🟡" if volatility > 10 else "🟢"
            volatility_label = "High" if volatility > 20 else "Moderate" if volatility > 10 else "Low"
            
            insights_list.append(
                html.Li([
                    html.Span(volatility_emoji, style={'fontSize': '1.5rem', 'marginRight': '0.75rem'}),
                    html.Div([
                        html.Strong("Price Volatility: ", style={'color': '#0F172A'}),
                        html.Span(f"{volatility_label} ({volatility:.1f}%)",
                                style={'color': '#475569'})
                    ])
                ], style={'display': 'flex', 'alignItems': 'center'})
            )
        
        return html.Ul(insights_list, style={'listStyle': 'none', 'padding': 0,
                                            'display': 'grid', 'gap': '1rem'})
    
    def run(self, debug=True, port=8050):
        """Run the Dash server."""
        self.app.run(debug=debug, port=port)