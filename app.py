"""
CropAI - Complete AI-Powered Decision Support System
Features: Sales Forecasting | Waste-to-Value | Food Security | Vendor Rewards
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="CropAI - Food Security Decision Support",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #558B2F;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .food-security-badge {
        background-color: #1B5E20;
        color: white;
        padding: 0.5rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    .warning-card {
        background-color: #FFF3E0;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #FF6F00;
    }
    .success-card {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #2E7D32;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# DATA LOADING (Matches your Colab processing)
# ============================================
@st.cache_data
def load_crop_data():
    """Load and process crops_district_production.csv"""
    try:
        df = pd.read_csv('crops_district_production.csv')
    except:
        df = pd.read_csv('data/crops_district_production.csv')
    
    # Process exactly like Colab
    df = df[df['production'] > 0].copy()
    
    if 'crop_type' in df.columns:
        df.drop(columns=['crop_type'], inplace=True)
    
    df.rename(columns={'crop_species': 'crop_type', 'production': 'production_tonnes'}, inplace=True)
    df['crop_type'] = df['crop_type'].astype(str).str.replace('_', ' ').str.title()
    
    n_records = len(df)
    np.random.seed(42)
    
    # Generate synthetic data for missing columns
    df['harvest_area_hectares'] = df['production_tonnes'] / np.random.uniform(5, 50, n_records)
    df['season'] = np.random.choice(['Dry', 'Wet', 'Inter-monsoon'], n_records)
    df['market_price_rm_kg'] = np.random.uniform(0.5, 15, n_records)
    df['storage_days_typical'] = np.random.randint(1, 60, n_records)
    df['distance_to_market_km'] = np.random.uniform(1, 150, n_records)
    df['weather_risk_index'] = np.random.uniform(0, 10, n_records)
    df['soil_quality_index'] = np.random.uniform(0, 10, n_records)
    df['demand_trend'] = np.random.choice(['rising', 'stable', 'falling'], n_records)
    
    # Derived features
    df['perishability_score'] = df['storage_days_typical'].apply(
        lambda x: 0.9 if x < 7 else (0.5 if x < 30 else 0.1)
    )
    
    # Sales forecast (intelligent forecasting)
    df['sales_forecast_rm'] = (
        df['production_tonnes'] *
        df['market_price_rm_kg'] *
        1000 *
        (1 - df['perishability_score'] * 0.3) *
        np.random.uniform(0.8, 1.2, n_records)
    )
    
    # Food security score (based on production stability and market access)
    df['food_security_score'] = (
        (df['production_tonnes'] / df['production_tonnes'].max()) * 0.5 +
        (1 - df['perishability_score']) * 0.3 +
        (1 - df['distance_to_market_km'] / df['distance_to_market_km'].max()) * 0.2
    ) * 100
    
    return df

# ============================================
# WASTE-TO-VALUE DATABASE
# ============================================
WASTE_TO_VALUE_DB = {
    'Palm Oil': {
        'waste_materials': ['Empty Fruit Bunches', 'Palm Kernel Shells', 'Mesocarp Fiber'],
        'by_products': ['Biofuel Pellets', 'Organic Fertilizer', 'Mushroom Substrate', 'Paper Pulp'],
        'vendors': ['BioEnergy Malaysia', 'EcoFertilizer Co', 'GreenMushrooms Sdn Bhd'],
        'value_rm_tonne': [120, 80, 200, 150],
        'reward_points': [100, 50, 180, 120],
        'food_security_impact': 'Provides alternative income and renewable energy source'
    },
    'Pineapple': {
        'waste_materials': ['Skin', 'Core', 'Crown Leaves'],
        'by_products': ['Pineapple Jam', 'Fruit Vinegar', 'Animal Feed', 'Enzyme Extract', 'Fiber Fabric'],
        'vendors': ['JamFactory MY', 'Vinegar Ventures', 'EcoFeed Solutions', 'BioEnzyme Labs', 'FiberCraft'],
        'value_rm_tonne': [300, 250, 100, 500, 400],
        'reward_points': [250, 200, 80, 450, 350],
        'food_security_impact': 'Reduces post-harvest loss by up to 40%, creates preserved food products'
    },
    'Rice': {
        'waste_materials': ['Rice Husk', 'Straw', 'Broken Rice'],
        'by_products': ['Rice Bran Oil', 'Biochar', 'Animal Bedding', 'Rice Milk', 'Construction Bricks'],
        'vendors': ['RiceOil Malaysia', 'BioChar Solutions', 'EcoBricks Sdn Bhd', 'RiceMilk Co'],
        'value_rm_tonne': [400, 150, 60, 350, 200],
        'reward_points': [350, 120, 40, 300, 160],
        'food_security_impact': 'Creates value-added food products from broken grains'
    },
    'Coconut': {
        'waste_materials': ['Husk', 'Shell', 'Coir', 'Water'],
        'by_products': ['Coir Rope', 'Activated Carbon', 'Coconut Sugar', 'Coco Peat', 'Virgin Coconut Oil'],
        'vendors': ['CocoFiber Industries', 'CarbonActive MY', 'CocoSugar Co', 'PeatPro', 'VCO Malaysia'],
        'value_rm_tonne': [250, 450, 600, 180, 700],
        'reward_points': [200, 400, 550, 150, 650],
        'food_security_impact': 'Every part usable - from fuel to food to fiber'
    },
    'Banana': {
        'waste_materials': ['Peel', 'Stem', 'Leaves'],
        'by_products': ['Banana Flour', 'Biodegradable Plates', 'Animal Feed', 'Vinegar', 'Textile Fiber'],
        'vendors': ['BananaFlour MY', 'EcoTableware', 'GreenFeed Co', 'FruitVinegar Labs'],
        'value_rm_tonne': [500, 350, 80, 200, 300],
        'reward_points': [450, 300, 60, 180, 250],
        'food_security_impact': 'Green bananas can be processed into flour for long-term storage'
    }
}

# ============================================
# REWARDS SYSTEM
# ============================================
class RewardsManager:
    def __init__(self):
        if 'farmer_points' not in st.session_state:
            st.session_state.farmer_points = 0
        if 'redemption_history' not in st.session_state:
            st.session_state.redemption_history = []
    
    def add_points(self, points, reason):
        st.session_state.farmer_points += points
        st.session_state.redemption_history.append({
            'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'action': 'earned',
            'points': points,
            'reason': reason
        })
    
    def redeem_points(self, points, item):
        if st.session_state.farmer_points >= points:
            st.session_state.farmer_points -= points
            st.session_state.redemption_history.append({
                'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'action': 'redeemed',
                'points': points,
                'reason': item
            })
            return True
        return False
    
    def get_points(self):
        return st.session_state.farmer_points

# ============================================
# INTELLIGENT FORECASTING FUNCTION
# ============================================
def intelligent_forecast(crop_data, production_tonnes):
    """Generate intelligent sales forecast with confidence score"""
    
    avg_price = crop_data['market_price_rm_kg'].mean()
    avg_perishability = crop_data['perishability_score'].mean()
    
    # Base forecast
    base_revenue = production_tonnes * avg_price * 1000
    waste_adjusted = base_revenue * (1 - avg_perishability * 0.3)
    
    # Confidence score based on data availability
    confidence = min(95, 60 + (len(crop_data) / 10))
    
    # Seasonal adjustment
    if 'season' in crop_data.columns:
        season_counts = crop_data['season'].value_counts()
        if len(season_counts) > 0:
            peak_season = season_counts.index[0]
            seasonal_boost = 1.15 if peak_season == 'Dry' else 0.95
        else:
            seasonal_boost = 1.0
    else:
        seasonal_boost = 1.0
    
    final_forecast = waste_adjusted * seasonal_boost
    
    # Urgency level
    if avg_perishability > 0.7:
        urgency = "🔴 HIGH - Sell within 3 days"
        urgency_color = "red"
    elif avg_perishability > 0.4:
        urgency = "🟡 MEDIUM - Sell within 2 weeks"
        urgency_color = "orange"
    else:
        urgency = "🟢 LOW - Can store for 1+ months"
        urgency_color = "green"
    
    return {
        'forecast_rm': final_forecast,
        'confidence': confidence,
        'urgency': urgency,
        'urgency_color': urgency_color,
        'avg_price': avg_price,
        'perishability': avg_perishability
    }

# ============================================
# WASTE-TO-VALUE RECOMMENDATION
# ============================================
def get_waste_to_value_recommendations(crop_type, production_tonnes):
    """Get waste-to-value recommendations with revenue potential"""
    
    if crop_type not in WASTE_TO_VALUE_DB:
        return None
    
    crop_info = WASTE_TO_VALUE_DB[crop_type]
    waste_estimate = production_tonnes * 0.25  # Assume 25% waste
    
    recommendations = []
    for i in range(len(crop_info['by_products'])):
        recommendations.append({
            'by_product': crop_info['by_products'][i],
            'waste_material': crop_info['waste_materials'][i % len(crop_info['waste_materials'])],
            'vendor': crop_info['vendors'][i % len(crop_info['vendors'])],
            'value_rm_tonne': crop_info['value_rm_tonne'][i],
            'potential_revenue': waste_estimate * crop_info['value_rm_tonne'][i],
            'reward_points': waste_estimate * crop_info['reward_points'][i],
            'food_security_impact': crop_info['food_security_impact']
        })
    
    return sorted(recommendations, key=lambda x: x['potential_revenue'], reverse=True)[:3]

# ============================================
# MAIN APP
# ============================================
def main():
    # Header
    st.markdown('<div class="main-header">🌾 CropAI - Food Security Decision Support System</div>', unsafe_allow_html=True)
    st.markdown("*AI-powered sales forecasting | Waste-to-value conversion | Food security strengthening*")
    st.markdown("---")
    
    # Load data
    with st.spinner("Loading agricultural data..."):
        df = load_crop_data()
    
    # Initialize rewards
    rewards = RewardsManager()
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/rice-plant.png", width=80)
        st.markdown("## 📋 Farmer Input")
        
        farmer_name = st.text_input("Farmer Name", "Ahmad Abdullah")
        
        # Crop selection
        crops_list = sorted(df['crop_type'].unique())
        selected_crop = st.selectbox("Select Your Crop", crops_list)
        
        # Production input
        production_tonnes = st.number_input("Current Production (Tonnes)", 
                                           min_value=0.1, value=100.0, step=10.0)
        
        # District selection
        districts_list = sorted(df['district'].unique())
        selected_district = st.selectbox("Your District", districts_list)
        
        st.markdown("---")
        
        # Food security badge
        st.markdown('<div class="food-security-badge">🛡️ Food Security Priority</div>', unsafe_allow_html=True)
        st.caption("This system prioritizes reducing post-harvest loss and increasing farmer income to strengthen household food security.")
        
        st.markdown("---")
        
        # Rewards wallet
        st.markdown("### 🎁 Your Rewards")
        st.metric("Total Points", f"{rewards.get_points():,}")
        
        if st.button("🏆 Redeem Points", use_container_width=True):
            st.info("💡 Rewards: 500 pts = Fertilizer | 1000 pts = Equipment | 2000 pts = Cold Storage")
    
    # Filter data for selected crop
    crop_data = df[df['crop_type'] == selected_crop]
    
    # ============================================
    # MAIN DISPLAY AREA
    # ============================================
    
    # Food Security Header
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"### 🌱 Crop: {selected_crop}")
    with col2:
        avg_fs_score = crop_data['food_security_score'].mean()
        st.metric("Food Security Index", f"{avg_fs_score:.0f}/100", 
                 delta="Good" if avg_fs_score > 60 else "Needs Improvement")
    with col3:
        st.metric("Total Farmers in Database", f"{len(crop_data):,}")
    
    st.markdown("---")
    
    # ============================================
    # FEATURE 1: INTELLIGENT FORECASTING
    # ============================================
    st.markdown('<div class="sub-header">📊 1. Intelligent Sales Forecast</div>', unsafe_allow_html=True)
    
    forecast = intelligent_forecast(crop_data, production_tonnes)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Forecasted Revenue", f"RM {forecast['forecast_rm']:,.0f}")
    with col2:
        st.metric("Confidence Score", f"{forecast['confidence']:.0f}%")
    with col3:
        st.metric("Avg Market Price", f"RM {forecast['avg_price']:.2f}/kg")
    with col4:
        st.markdown(f"### {forecast['urgency']}")
    
    # Explanation of forecast
    with st.expander("📖 How this forecast helps food security"):
        st.markdown("""
        - **Prevents rushed selling** at low prices by providing optimal timing
        - **Reduces post-harvest loss** by highlighting perishability risks
        - **Enables planning** for storage or processing based on confidence score
        - **Supports loan applications** with data-driven revenue projections
        """)
    
    # ============================================
    # FEATURE 2: WASTE-TO-VALUE RECOMMENDATIONS
    # ============================================
    st.markdown('<div class="sub-header">🔄 2. Waste-to-Value Recommendations</div>', unsafe_allow_html=True)
    
    waste_recommendations = get_waste_to_value_recommendations(selected_crop, production_tonnes)
    
    if waste_recommendations:
        st.info(f"💡 Based on {production_tonnes} tonnes production, approximately {production_tonnes * 0.25:.1f} tonnes of waste can be converted into valuable products.")
        
        for idx, rec in enumerate(waste_recommendations, 1):
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1.5, 1.5, 1])
                
                with col1:
                    st.markdown(f"**{rec['by_product']}**")
                    st.caption(f"From: {rec['waste_material']}")
                
                with col2:
                    st.markdown(f"**Vendor:** {rec['vendor']}")
                    st.caption(rec['food_security_impact'][:50] + "...")
                
                with col3:
                    st.metric("Revenue Potential", f"RM {rec['potential_revenue']:,.0f}")
                
                with col4:
                    if st.button(f"🤝 Connect", key=f"vendor_{idx}"):
                        rewards.add_points(rec['reward_points'], f"Waste exchange: {rec['by_product']}")
                        st.success(f"✅ Added {rec['reward_points']:.0f} points to your wallet!")
        
        # Total waste value summary
        total_waste_value = sum(r['potential_revenue'] for r in waste_recommendations)
        total_points = sum(r['reward_points'] for r in waste_recommendations)
        
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"💰 **Total potential revenue from waste:** RM {total_waste_value:,.0f}")
        with col2:
            st.info(f"🎁 **Total reward points earned:** {total_points:.0f}")
            
    else:
        st.warning(f"Waste-to-value recommendations coming soon for {selected_crop}")
        st.markdown("Currently supported crops: Palm Oil, Pineapple, Rice, Coconut, Banana")
    
    # ============================================
    # FEATURE 3: TOP CROPS FOR FOOD SECURITY
    # ============================================
    st.markdown('<div class="sub-header">🏆 3. Top Crops for Food Security</div>', unsafe_allow_html=True)
    
    # Calculate food security ranking
    crop_fs_ranking = df.groupby('crop_type').agg({
        'food_security_score': 'mean',
        'sales_forecast_rm': 'sum',
        'production_tonnes': 'sum'
    }).reset_index().sort_values('food_security_score', ascending=False).head(5)
    
    for idx, row in crop_fs_ranking.iterrows():
        col1, col2, col3, col4 = st.columns([2, 1.5, 1.5, 2])
        
        with col1:
            st.markdown(f"**{row['crop_type']}**")
        with col2:
            st.metric("Food Security Score", f"{row['food_security_score']:.0f}/100")
        with col3:
            st.metric("Total Sales", f"RM {row['sales_forecast_rm']:,.0f}")
        with col4:
            st.progress(row['food_security_score'] / 100)
    
    # ============================================
    # FEATURE 4: FOOD SECURITY INSIGHTS
    # ============================================
    st.markdown('<div class="sub-header">📈 4. Food Security Insights</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Food security by district
        district_fs = df.groupby('district')['food_security_score'].mean().sort_values(ascending=False).head(10)
        fig1 = px.bar(x=district_fs.index, y=district_fs.values,
                      title="Top 10 Districts by Food Security Score",
                      labels={'x': 'District', 'y': 'Food Security Score'},
                      color=district_fs.values,
                      color_continuous_scale='greens')
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Perishability vs Food Security
        fig2 = px.scatter(df, x='perishability_score', y='food_security_score',
                          color='crop_type', size='production_tonnes',
                          title="Perishability vs Food Security",
                          labels={'perishability_score': 'Perishability (higher = spoils faster)',
                                 'food_security_score': 'Food Security Score'})
        st.plotly_chart(fig2, use_container_width=True)
    
    # ============================================
    # FOOD SECURITY TIPS
    # ============================================
    with st.expander("🌾 Food Security Tips for Farmers"):
        st.markdown("""
        | Strategy | Impact |
        |----------|--------|
        | **Diversify crops** | Reduces risk of total crop failure |
        | **Process waste into by-products** | Creates additional income streams |
        | **Store properly** | Extends shelf life by 30-50% |
        | **Join cooperative** | Better bargaining power and shared storage |
        | **Use forecasting tools** | Sell at optimal prices, reduce waste |
        """)
    
    # ============================================
    # REDEMPTION HISTORY (Optional)
    # ============================================
    if st.session_state.redemption_history:
        with st.expander("📜 Your Rewards History"):
            history_df = pd.DataFrame(st.session_state.redemption_history)
            st.dataframe(history_df, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("*🌾 CropAI - Strengthening Food Security Through AI | Data source: Malaysia crops_district_production*")

if __name__ == "__main__":
    main()