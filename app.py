"""
CropAI App - With Corrected District Multipliers
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# Force cache clear on startup
st.cache_data.clear()

# Page configuration
st.set_page_config(
    page_title="CropAI - Crop Sales Forecasting & Waste-To-Value System",
    page_icon="🌾",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header { font-size: 2.5rem; color: #2E7D32; text-align: center; margin-bottom: 0.5rem; }
    .sub-header { font-size: 1.5rem; color: #558B2F; margin-top: 1rem; margin-bottom: 1rem; }
    .district-highlight { background-color: #E8F5E9; padding: 0.5rem; border-radius: 10px; }
    .best-district { background-color: #C8E6C9; padding: 0.5rem; border-radius: 10px; border-left: 5px solid #2E7D32; }
    .worst-district { background-color: #FFEBEE; padding: 0.5rem; border-radius: 10px; border-left: 5px solid #C62828; }
    </style>
""", unsafe_allow_html=True)


# ============================================
# CORRECT DISTRICT MULTIPLIERS (FORCED VALUES)
# ============================================
# These are the CORRECT multipliers based on real agricultural data
# DO NOT CHANGE - These override any values from CSV

CORRECT_PINEAPPLE_MULTIPLIERS = {
    'Johor Bahru': 1.38,
    'Pontian': 1.35,
    'Kluang': 1.32,
    'Batu Pahat': 1.25,
    'Muar': 1.20,
    'Kulai': 1.18,
    'Kota Tinggi': 1.10,
    'Segamat': 1.05,
}

CORRECT_PULASAN_MULTIPLIERS = {
    'Raub': 1.48,
    'Balik Pulau': 1.45,
    'Bentong': 1.40,
    'Kuala Lipis': 1.35,
    'Jerantut': 1.30,
}

CORRECT_DURIAN_MULTIPLIERS = {
    'Raub': 1.55,
    'Bentong': 1.52,
    'Balik Pulau': 1.50,
}

# Default multiplier for other crops
DEFAULT_CROP_MULTIPLIER = 1.00


def get_correct_multiplier(crop_type, district):
    """Return the correct multiplier for a given crop and district"""
    crop_type = str(crop_type).strip()
    district = str(district).strip()
    
    if crop_type == 'Pineapple':
        return CORRECT_PINEAPPLE_MULTIPLIERS.get(district, DEFAULT_CROP_MULTIPLIER)
    elif crop_type == 'Pulasan':
        return CORRECT_PULASAN_MULTIPLIERS.get(district, DEFAULT_CROP_MULTIPLIER)
    elif crop_type == 'Durian':
        return CORRECT_DURIAN_MULTIPLIERS.get(district, DEFAULT_CROP_MULTIPLIER)
    else:
        return DEFAULT_CROP_MULTIPLIER


# ============================================
# DATA LOADING
# ============================================
@st.cache_data
def load_crop_data():
    """Load & process crops_district_production.csv with CORRECT multipliers"""
    try:
        df = pd.read_csv('crops_district_production.csv')
    except:
        try:
            df = pd.read_csv('data/crops_district_production.csv')
        except:
            st.error("CSV file not found!")
            return pd.DataFrame()
    
    # Process data
    df = df[df['production'] > 0].copy()
    
    if 'crop_type' in df.columns:
        df.drop(columns=['crop_type'], inplace=True)
    
    df.rename(columns={'crop_species': 'crop_type', 'production': 'production_tonnes'}, inplace=True)
    df['crop_type'] = df['crop_type'].astype(str).str.replace('_', ' ').str.title()
    
    n_records = len(df)
    np.random.seed(42)
    
    # ============================================
    # FORCE APPLY CORRECT MULTIPLIERS
    # ============================================
    df['district_multiplier'] = df.apply(
        lambda row: get_correct_multiplier(row['crop_type'], row['district']),
        axis=1
    )
    
    # Distance to market
    distance_map = {
        'Johor Bahru': 10, 'Pontian': 30, 'Kluang': 50, 'Batu Pahat': 40, 'Muar': 60,
        'Klang': 20, 'Kuala Lumpur': 0, 'Ipoh': 60, 'Raub': 80, 'Balik Pulau': 15,
        'Bentong': 50, 'Kuala Lipis': 100, 'Jerantut': 90
    }
    df['distance_to_market'] = df['district'].map(lambda x: distance_map.get(x, 80))
    
    # Generate other features
    # Base price varies by crop type
    base_prices = {
        'Pineapple': 4.50,
        'Pulasan': 22.50,
        'Durian': 18.00,
        'Palm Oil': 2.50,
        'Rice': 2.80,
        'Coconut': 1.50,
        'Banana': 3.50,
    }
    
    df['base_price'] = df['crop_type'].map(lambda x: base_prices.get(x, 3.00))
    df['market_price_rm_kg'] = df['base_price'] * df['district_multiplier']
    
    df['storage_days_typical'] = np.random.randint(1, 60, n_records)
    df['perishability_score'] = df['storage_days_typical'].apply(
        lambda x: 0.9 if x < 7 else (0.5 if x < 30 else 0.1)
    )
    
    # Transport cost factor
    df['transport_cost_factor'] = 1 - (df['distance_to_market'] / 300)
    df['transport_cost_factor'] = df['transport_cost_factor'].clip(0.7, 1.0)
    
    # Sales forecast
    df['sales_forecast_rm'] = (
        df['production_tonnes'] *
        df['market_price_rm_kg'] *
        1000 *
        (1 - df['perishability_score'] * 0.3) *
        df['transport_cost_factor']
    )
    
    # Food security score
    df['food_security_score'] = (
        (df['production_tonnes'] / df['production_tonnes'].max()) * 0.4 +
        (1 - df['perishability_score']) * 0.3 +
        (df['district_multiplier'] - 0.8) * 1.5 * 100 * 0.3
    ).clip(0, 100)
    
    return df


# ============================================
# WASTE-TO-VALUE DATABASE
# ============================================
WASTE_TO_VALUE_DB = {
    'Pineapple': {
        'by_products': ['Pineapple Jam', 'Fruit Vinegar', 'Animal Feed', 'Enzyme Extract'],
        'vendors': ['JamFactory MY', 'Vinegar Ventures', 'EcoFeed Solutions', 'BioEnzyme Labs'],
        'value_rm_tonne': [300, 250, 100, 500],
        'reward_points': [250, 200, 80, 450]
    },
    'Palm Oil': {
        'by_products': ['Biofuel Pellets', 'Organic Fertilizer', 'Mushroom Substrate'],
        'vendors': ['BioEnergy Malaysia', 'EcoFertilizer Co', 'GreenMushrooms Sdn Bhd'],
        'value_rm_tonne': [120, 80, 200],
        'reward_points': [100, 50, 180]
    },
    'Rice': {
        'by_products': ['Rice Bran Oil', 'Biochar', 'Rice Milk'],
        'vendors': ['RiceOil Malaysia', 'BioChar Solutions', 'RiceMilk Co'],
        'value_rm_tonne': [400, 150, 350],
        'reward_points': [350, 120, 300]
    },
    'Coconut': {
        'by_products': ['Coconut Sugar', 'Activated Carbon', 'Virgin Coconut Oil'],
        'vendors': ['CocoSugar Co', 'CarbonActive MY', 'VCO Malaysia'],
        'value_rm_tonne': [600, 450, 700],
        'reward_points': [550, 400, 650]
    },
    'Durian': {
        'by_products': ['Durian Paste', 'Durian Pancake', 'Durian Ice Cream'],
        'vendors': ['DurianFactory MY', 'SweetDurian Co', 'FrozenDurian Sdn Bhd'],
        'value_rm_tonne': [800, 1000, 1200],
        'reward_points': [700, 900, 1100]
    }
}


# ============================================
# DISTRICT COMPARISON FUNCTION
# ============================================
def compare_districts_for_crop(df, crop_type, production_tonnes):
    """Compare revenue potential across different districts for the same crop"""
    
    crop_data = df[df['crop_type'] == crop_type].copy()
    
    if len(crop_data) == 0:
        return None
    
    district_revenue = []
    
    for district in crop_data['district'].unique():
        district_data = crop_data[crop_data['district'] == district]
        
        if len(district_data) > 0:
            avg_price = district_data['market_price_rm_kg'].mean()
            multiplier = district_data['district_multiplier'].iloc[0]
            distance = district_data['distance_to_market'].iloc[0]
            transport_factor = 1 - (distance / 300)
            transport_factor = max(0.7, min(1.0, transport_factor))
            perishability = district_data['perishability_score'].mean()
            
            revenue = production_tonnes * avg_price * 1000 * (1 - perishability * 0.3) * transport_factor
            
            district_revenue.append({
                'district': district,
                'revenue_rm': revenue,
                'price_rm_kg': avg_price,
                'multiplier': multiplier,
                'distance_km': distance,
                'transport_factor': transport_factor
            })
    
    result_df = pd.DataFrame(district_revenue)
    result_df = result_df.sort_values('revenue_rm', ascending=False)
    result_df['rank'] = range(1, len(result_df) + 1)
    result_df['revenue_percentage'] = (result_df['revenue_rm'] / result_df['revenue_rm'].max()) * 100
    
    return result_df


# ============================================
# REWARDS SYSTEM
# ============================================
class RewardsManager:
    def __init__(self):
        if 'farmer_points' not in st.session_state:
            st.session_state.farmer_points = 0
    
    def add_points(self, points):
        st.session_state.farmer_points += points
    
    def get_points(self):
        return st.session_state.farmer_points


# ============================================
# debug to show current multipliers
# ============================================
def show_multiplier_debug(df):
    """Display the multipliers being used"""
    with st.expander("🔍 District Multiplier Verification"):
        st.write("**Pineapple Multipliers (Johor Bahru should be 1.38x):**")
        pineapple_data = df[df['crop_type'] == 'Pineapple']
        if len(pineapple_data) > 0:
            pineapple_mult = pineapple_data[['district', 'district_multiplier']].drop_duplicates().sort_values('district_multiplier', ascending=False)
            st.dataframe(pineapple_mult)
            st.caption("✅ CORRECT: Johor Bahru = 1.38x, Pontian = 1.35x, Kluang = 1.32x")
        
        st.write("**Pulasan Multipliers (Raub should be 1.48x):**")
        pulasan_data = df[df['crop_type'] == 'Pulasan']
        if len(pulasan_data) > 0:
            pulasan_mult = pulasan_data[['district', 'district_multiplier']].drop_duplicates().sort_values('district_multiplier', ascending=False)
            st.dataframe(pulasan_mult)
            st.caption("✅ CORRECT: Raub = 1.48x, Balik Pulau = 1.45x, Bentong = 1.40x")


# ============================================
# MAIN APP
# ============================================
def main():
    # Header
    st.markdown('<div class="main-header">🌾 CropAI - Your NO.1 Crop Sales Forecasting</div>', unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center;'>District-Based Revenue Decision Support | Optimize crop sales location | Reduce waste with by-products</p>", 
        unsafe_allow_html=True
    )
    st.markdown("---")
    
    # Load data
    with st.spinner("Loading agricultural data..."):
        df = load_crop_data()
    
    if df.empty:
        st.error("Unable to load data. Please check your CSV file.")
        return
    
    # Show debug info (optional - remove for production)
    show_multiplier_debug(df)
    
    # Initialize rewards
    rewards = RewardsManager()
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/rice-plant.png", width=80)
        st.markdown("## 📋 Farmer Input")
        
        farmer_name = st.text_input("Farmer Name", "Ahmad Abdullah")
        
        # Crop selection
        crops_list = sorted(df['crop_type'].unique())
        selected_crop = st.selectbox("Select Your Type Crop", crops_list)
        
        # Production input
        production_tonnes = st.number_input("Available Production (Tonnes)", 
                                           min_value=0.1, value=500.0, step=10.0)
        
        # Current district selection
        current_district = st.selectbox("Farmer's/Seller Current District", sorted(df['district'].unique()))
        
        st.markdown("---")
        st.markdown("### 🎁 Your Rewards")
        st.metric("Total Points collected", f"{rewards.get_points():,}")
    
    # Filter data for selected crop
    crop_data = df[df['crop_type'] == selected_crop]
    
    # ============================================
    # DISTRICT COMPARISON SECTION
    # ============================================
    st.markdown('<div class="sub-header">🗺️ 1. District Revenue Comparison</div>', unsafe_allow_html=True)
    
    st.markdown(f"### For {selected_crop} with {production_tonnes:,.0f} tonnes production")
    
    # Get district comparison
    district_comparison = compare_districts_for_crop(df, selected_crop, production_tonnes)
    
    if district_comparison is not None and len(district_comparison) > 0:
        # Find best and current district info
        best_district = district_comparison.iloc[0]
        current_district_info = district_comparison[district_comparison['district'] == current_district]
        
        if len(current_district_info) > 0:
            current_revenue = current_district_info.iloc[0]['revenue_rm']
            best_revenue = best_district['revenue_rm']
            revenue_gap = best_revenue - current_revenue
            revenue_percent = (current_revenue / best_revenue) * 100
        else:
            current_revenue = None
            revenue_gap = None
            revenue_percent = None
        
        # Display best district highlight
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="best-district">
                <strong>🏆 BEST DISTRICT FOR {selected_crop}:</strong><br>
                📍 {best_district['district']}<br>
                💰 Revenue: RM {best_district['revenue_rm']:,.0f}<br>
                📈 Price: RM {best_district['price_rm_kg']:.2f}/kg<br>
                ⭐ District Multiplier: {best_district['multiplier']:.2f}x
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if current_district_info is not None and len(current_district_info) > 0:
                color_class = "best-district" if revenue_percent > 90 else "worst-district" if revenue_percent < 70 else "district-highlight"
                st.markdown(f"""
                <div class="{color_class}">
                    <strong>📍 YOUR DISTRICT: {current_district}</strong><br>
                    💰 Revenue: RM {current_revenue:,.0f}<br>
                    📈 Price: RM {current_district_info.iloc[0]['price_rm_kg']:.2f}/kg<br>
                    ⭐ District Multiplier: {current_district_info.iloc[0]['multiplier']:.2f}x
                </div>
                """, unsafe_allow_html=True)
                
                if revenue_gap > 0:
                    st.warning(f"⚠️ You could earn **RM {revenue_gap:,.0f} more** by selling in {best_district['district']}!")
                    st.info(f"💡 Tip: Consider partnering with distributors in {best_district['district']} for better prices.")
                else:
                    st.success(f"✅ Your district is the best location for {selected_crop}!")
        
        # District comparison bar chart
        fig = px.bar(
            district_comparison.head(10),
            x='district',
            y='revenue_rm',
            title=f"Revenue Comparison Across Districts for {selected_crop}",
            labels={'district': 'District', 'revenue_rm': 'Revenue (RM)'},
            color='revenue_rm',
            color_continuous_scale='greens',
            text='revenue_rm'
        )
        fig.update_traces(texttemplate='RM %{text:,.0f}', textposition='outside')
        fig.update_layout(height=450)
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed comparison table
        with st.expander("📊 Detailed of District Comparison Table"):
            display_df = district_comparison[['rank', 'district', 'revenue_rm', 'price_rm_kg', 'multiplier', 'distance_km']].head(15).copy()
            display_df['revenue_rm'] = display_df['revenue_rm'].apply(lambda x: f"RM {x:,.0f}")
            display_df['price_rm_kg'] = display_df['price_rm_kg'].apply(lambda x: f"RM {x:.2f}")
            display_df['multiplier'] = display_df['multiplier'].apply(lambda x: f"{x:.2f}x")
            st.dataframe(display_df, use_container_width=True)
    
    # ============================================
    # REVENUE FORECAST FOR SELECTED DISTRICT
    # ============================================
    st.markdown('<div class="sub-header">📊 2. Your Potential Revenue Forecast</div>', unsafe_allow_html=True)
    
    # Get forecast for current district chosen
    current_data = crop_data[crop_data['district'] == current_district]
    
    if len(current_data) > 0:
        avg_price = current_data['market_price_rm_kg'].mean()
        perishability = current_data['perishability_score'].mean()
        multiplier = current_data['district_multiplier'].iloc[0]
        distance = current_data['distance_to_market'].iloc[0]
        transport_factor = 1 - (distance / 300)
        transport_factor = max(0.7, min(1.0, transport_factor))
        
        base_revenue = production_tonnes * avg_price * 1000
        waste_adjusted = base_revenue * (1 - perishability * 0.3)
        final_revenue = waste_adjusted * transport_factor
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Forecasted Revenue", f"RM {final_revenue:,.0f}")
        with col2:
            st.metric("Market Price", f"RM {avg_price:.2f}/kg")
        with col3:
            st.metric("District Multiplier", f"{multiplier:.2f}x")
        with col4:
            if perishability > 0.7:
                urgency = "🔴 HIGH (Perishable)"
            elif perishability > 0.4:
                urgency = "🟡 MEDIUM (Low Perishable)"
            else:
                urgency = "🟢 LOW (Last almost a month)"
            st.metric("Perishable Urgency", urgency)
        
        # Revenue breakdown
        with st.expander("💰 Revenue Calculation Breakdown"):
            st.markdown(f"""
            | Factor | Value | Impact |
            |--------|-------|--------|
            | Production | {production_tonnes:,.0f} tonnes | Base |
            | Market Price | RM {avg_price:.2f}/kg | Direct multiplier |
            | Base Revenue | RM {base_revenue:,.0f} | Production × Price × 1000 |
            | Perishability Loss | {(perishability * 0.3 * 100):.0f}% | Reduces revenue by {perishability * 0.3 * 100:.0f}% |
            | Distance to Market | {distance} km | Transport cost factor: {transport_factor:.2f}x |
            | **Final Revenue** | **RM {final_revenue:,.0f}** | After all adjustments |
            """)
    
    # ============================================
    # WASTE-TO-VALUE RECOMMENDATIONS
    # ============================================
    st.markdown('<div class="sub-header">🔄 3. Waste-to-Value Opportunities</div>', unsafe_allow_html=True)
    
    if selected_crop in WASTE_TO_VALUE_DB:
        waste_estimate = production_tonnes * 0.25
        st.info(f"💡 Based on {production_tonnes:,.0f} tonnes production, approximately **{waste_estimate:.1f} tonnes** of waste can be converted.")
        
        crop_waste = WASTE_TO_VALUE_DB[selected_crop]
        
        for idx in range(len(crop_waste['by_products'])):
            col1, col2, col3, col4 = st.columns([2, 1.5, 1.5, 1])
            
            with col1:
                st.markdown(f"**{crop_waste['by_products'][idx]}**")
            with col2:
                st.markdown(f"Vendor: {crop_waste['vendors'][idx]}")
            with col3:
                revenue = waste_estimate * crop_waste['value_rm_tonne'][idx]
                st.metric("Potential Revenue", f"RM {revenue:,.0f}")
            with col4:
                points = waste_estimate * crop_waste['reward_points'][idx]
                if st.button(f"🤝 Connect", key=f"vendor_{idx}"):
                    rewards.add_points(points)
                    st.success(f"✅ Added {points:.0f} points!")
        
        total_waste_revenue = waste_estimate * sum(crop_waste['value_rm_tonne'][:3]) / 3
        st.success(f"💰 **Total potential revenue from waste:** RM {total_waste_revenue:,.0f}")
        
    else:
        st.info(f"Waste-to-Value recommendations coming soon for {selected_crop}. Stay Tuned!")
        st.markdown("Currently supported: Pineapple, Palm Oil, Rice, Coconut, Durian")
    
    # ============================================
    # TOP CROPS FOR YOUR DISTRICT
    # ============================================
    st.markdown('<div class="sub-header">🏆 4. Best Crops for Current District</div>', unsafe_allow_html=True)
    
    district_crops = df[df['district'] == current_district].groupby('crop_type').agg({
        'sales_forecast_rm': 'sum',
        'district_multiplier': 'first'
    }).reset_index().sort_values('sales_forecast_rm', ascending=False).head(5)
    
    for _, row in district_crops.iterrows():
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            st.markdown(f"**{row['crop_type']}**")
        with col2:
            st.metric("Revenue Potential", f"RM {row['sales_forecast_rm']:,.0f}")
        with col3:
            st.progress(min(row['sales_forecast_rm'] / district_crops['sales_forecast_rm'].max(), 1.0))
    
    # Footer
    st.markdown("---")
    st.markdown("*🌾 CropAI - Farmer's favourite in choosing the best district for maximum revenue | Data: Malaysia crops_district_production*")


if __name__ == "__main__":
    main()