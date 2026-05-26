import streamlit as st
import pandas as pd
import kagglehub
import plotly.express as px

st.set_page_config(
    page_title="Veridi Logistics Audit",
    layout="wide"
)

# states to regions
# norte = northe, nordeste = NE, centro-oeste = CW, sudeste = SE, sul = south
REGION_MAP = {
    'AC': 'Norte', 'AM': 'Norte', 'AP': 'Norte', 'PA': 'Norte',
    'RO': 'Norte', 'RR': 'Norte', 'TO': 'Norte',
    'AL': 'Nordeste', 'BA': 'Nordeste', 'CE': 'Nordeste', 'MA': 'Nordeste',
    'PB': 'Nordeste', 'PE': 'Nordeste', 'PI': 'Nordeste', 'RN': 'Nordeste', 'SE': 'Nordeste',
    'DF': 'Centro-Oeste', 'GO': 'Centro-Oeste', 'MS': 'Centro-Oeste', 'MT': 'Centro-Oeste',
    'ES': 'Sudeste', 'MG': 'Sudeste', 'RJ': 'Sudeste', 'SP': 'Sudeste',
    'PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul'
}

MIN_CATEGORY_ORDERS = 100
MIN_REVIEWS_FOR_TREND = 10

@st.cache_data
def load_data():
    path = kagglehub.dataset_download("olistbr/brazilian-ecommerce")

    orders = pd.read_csv(f"{path}/olist_orders_dataset.csv")
    reviews = pd.read_csv(f"{path}/olist_order_reviews_dataset.csv")
    customers = pd.read_csv(f"{path}/olist_customers_dataset.csv")
    products = pd.read_csv(f"{path}/olist_products_dataset.csv")
    translations = pd.read_csv(f"{path}/product_category_name_translation.csv")
    order_items = pd.read_csv(f"{path}/olist_order_items_dataset.csv")

    latest_reviews = (reviews.sort_values("review_answer_timestamp", ascending=False).drop_duplicates(subset="order_id", 
                                                                                                      keep="first"))

    df = orders.merge(latest_reviews, on="order_id", how="left")
    df = df.merge(customers, on="customer_id", how="left")
    date_cols = [
        "order_estimated_delivery_date",
        "order_delivered_customer_date",
        "order_purchase_timestamp"
    ]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col])
    df["days_difference"] = (df["order_delivered_customer_date"] - df["order_estimated_delivery_date"]).dt.days
    canceled_mask = df["order_status"].isin(["canceled", "unavailable"])
    undelivered_mask = df["days_difference"].isna()
    late_mask = (df["days_difference"] > 0) & (df["days_difference"] <= 5)
    super_late_mask = df["days_difference"] > 5

    df["delivery_status"] = "On Time"
    df.loc[late_mask, "delivery_status"] = "Late"
    df.loc[super_late_mask, "delivery_status"] = "Super Late"
    df.loc[undelivered_mask, "delivery_status"] = "Undelivered"
    df.loc[canceled_mask, "delivery_status"] = "Canceled/Unavailable"
    df["region"] = df["customer_state"].map(REGION_MAP)
    products = products.merge(
        translations,
        on="product_category_name",
        how="left"
    )
    # just using the first item in each order for category analysis
    first_order_items = (order_items.sort_values("order_item_id").drop_duplicates(subset="order_id", keep="first"))
    df = df.merge(first_order_items[["order_id", "product_id"]], on="order_id", how="left")
    df = df.merge(products[["product_id", "product_category_name_english"]], on="product_id", how="left")
    return df


def build_state_stats(df):
    state_stats = df.groupby("customer_state").agg(
        total_orders=("order_id", "count"),
        late_orders=("delivery_status", lambda x: x.isin(["Late", "Super Late"]).sum())
    ).reset_index()
    state_stats["pct_late"] = (state_stats["late_orders"] / state_stats["total_orders"] * 100).round(2)
    return state_stats.sort_values("pct_late", ascending=False)


with st.spinner("Loading dataset..."):
    master = load_data()

delivered = master[~master["delivery_status"].isin(["Canceled/Unavailable", "Undelivered"])]

# sidebar
st.sidebar.title("Filters")
selected_regions = st.sidebar.multiselect(
    "Region",
    options=['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul'],
    default=['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul']
)
available_states = sorted(delivered[delivered["region"].isin(selected_regions)]["customer_state"].dropna().unique())
selected_states = st.sidebar.multiselect(
    "States",
    options=available_states,
    default=available_states
)
categories = sorted(delivered["product_category_name_english"].dropna().unique())
selected_categories = st.sidebar.multiselect(
    "Product Categories",
    options=categories,
    default=categories
)
min_date = delivered["order_purchase_timestamp"].min().date()
max_date = delivered["order_purchase_timestamp"].max().date()
date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

show_on_time = st.sidebar.checkbox("On Time", value=True)
show_late = st.sidebar.checkbox("Late", value=True)
show_super_late = st.sidebar.checkbox("Super Late", value=True)

filtered = delivered[delivered["customer_state"].isin(selected_states)].copy()
filtered = filtered[filtered["product_category_name_english"].isin(selected_categories)]
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[(filtered["order_purchase_timestamp"].dt.date >= start_date)
        & (filtered["order_purchase_timestamp"].dt.date <= end_date)
    ]
statuses = []
if show_on_time: 
    statuses.append("On Time")
if show_late: 
    statuses.append("Late")
if show_super_late: 
    statuses.append("Super Late")
filtered = filtered[filtered["delivery_status"].isin(statuses)]
if len(filtered) == 0:
    st.warning("No orders match the current filters.")
    st.stop()

st.title("Veridi Logistics Audit")

total_orders = len(filtered)
late_orders = len(filtered[filtered["delivery_status"].isin(["Late", "Super Late"])])
late_rate = (late_orders / total_orders * 100) if total_orders > 0 else 0
on_time_orders = len(filtered[filtered["delivery_status"] == "On Time"])
average_review = filtered["review_score"].mean()

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total Orders", f"{total_orders:,}")
kpi2.metric(
    "On Time Rate",
    f"{(on_time_orders / total_orders * 100):.1f}%"
    if total_orders > 0 else "N/A"
)
kpi3.metric("Late Rate", f"{late_rate:.1f}%")
kpi4.metric(
    "Average Review",
    f"{average_review:.2f}/5"
    if total_orders > 0 else "N/A"
)
st.divider()


# brazil map 
st.subheader("Map of Late Delivery Rate by State")
state_stats = build_state_stats(filtered)
state_map = px.choropleth(
    state_stats,
    geojson="https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson",
    locations="customer_state",
    featureidkey="properties.sigla",
    color="pct_late",
    color_continuous_scale="Reds",
    labels={"pct_late": "% Late"}
)
state_map.update_geos(
    fitbounds="locations",
    visible=False
)
state_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=500)
st.plotly_chart(state_map, use_container_width=True)
st.divider()


l_col, r_col = st.columns(2)
with l_col:
    st.subheader("Late Delivery Rate by State")
    state_bar_chart = px.bar(
        state_stats,
        x="customer_state",
        y="pct_late",
        color="pct_late",
        color_continuous_scale="Reds"
    )
    state_bar_chart.update_layout(showlegend=False, height=400)
    st.plotly_chart(state_bar_chart, use_container_width=True)

with r_col:
    st.subheader("Review Scores")
    review_scores = (filtered.groupby("delivery_status")["review_score"].mean().reset_index())
    review_chart = px.bar(
    review_scores,
    x="delivery_status",
    y="review_score",
    color="delivery_status",
    color_discrete_map={
        "On Time": "green",
        "Late": "darkorange",
        "Super Late": "red"
    },
    category_orders={"delivery_status": ["On Time", "Late", "Super Late"]}
    )
    review_chart.update_layout(showlegend=False, height=400, yaxis_range=[1, 5])
    st.plotly_chart(review_chart, use_container_width=True)
st.divider()


st.subheader("Delivery Delay vs Review Score")
trend_source = filtered[filtered["days_difference"].notna()
    & filtered["review_score"].notna()
].copy()
review_trend = trend_source.groupby("days_difference").agg(
    avg_review=("review_score", "mean"),
    total_reviews=("review_score", "count")
).reset_index()
review_trend = review_trend[review_trend["total_reviews"] >= MIN_REVIEWS_FOR_TREND]
review_trend = review_trend.sort_values("days_difference")
trend_chart = px.line(
    review_trend,
    x="days_difference",
    y="avg_review",
    labels={
        "days_difference": "Days Early / Late",
        "avg_review": "Average Review Score"
    }
)
trend_chart.add_vline(x=0,line_dash="dash", line_color="red")
trend_chart.update_layout(
    height=500,
    yaxis_range=[1, 5]
)
st.plotly_chart(
    trend_chart,
    use_container_width=True
)
st.divider()

st.subheader("Order Volume Over Time")
filtered["year_month"] = (filtered["order_purchase_timestamp"]
    .dt.to_period("M")
    .dt.to_timestamp()
)
monthly_volume = filtered.groupby(
    ["year_month", "delivery_status"]
).size().reset_index(name="count")
volume_chart = px.line(
    monthly_volume,
    x="year_month",
    y="count",
    color="delivery_status"
)
volume_chart.update_layout(height=400)
st.plotly_chart(volume_chart, use_container_width=True)
st.divider()

st.subheader("Average Delay by Product Category")
category_delays = filtered.groupby(
    "product_category_name_english"
).agg(
    avg_delay=("days_difference", "mean"),
    total_orders=("order_id", "count")
).reset_index()
category_delays = category_delays[category_delays["total_orders"] >= MIN_CATEGORY_ORDERS]
category_delays = category_delays.sort_values("avg_delay", ascending=False)
category_chart = px.bar(
    category_delays,
    x="avg_delay",
    y="product_category_name_english",
    orientation="h",
    color="avg_delay",
    color_continuous_scale="RdYlGn_r"
)
category_chart.add_vline(x=0, line_dash="dash")
category_chart.update_layout(showlegend=False, height=900)
st.plotly_chart(category_chart, use_container_width=True)
st.caption("Category analysis only uses the first item from each order.")
st.divider()


# # for exploring the data
# st.subheader("Raw Data")
# cols = [
#     "order_id",
#     "customer_state",
#     "region",
#     "delivery_status",
#     "days_difference",
#     "review_score",
#     "product_category_name_english",
#     "order_purchase_timestamp"
# ]
# st.dataframe(filtered[cols].reset_index(drop=True), use_container_width=True)
st.caption("Dataset: Olist Brazilian E-Commerce (https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)")