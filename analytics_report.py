from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange, Dimension, Metric, RunReportRequest, OrderBy
)
import os
import json

# Step 1: Set service account credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service-account.json"

# Step 2: Initialize client
client = BetaAnalyticsDataClient()

# Replace with your GA4 property ID
PROPERTY_ID = "345074992"


def fetch_report(request: RunReportRequest):
    response = client.run_report(request)
    headers = [header.name for header in response.dimension_headers] + \
              [header.name for header in response.metric_headers]
    
    data = [
        dict(zip(headers, [v.value for v in list(row.dimension_values) + list(row.metric_values)]))
        for row in response.rows
    ]
    return data



# Report 1: Top Pages by Pageviews
top_pages = fetch_report(RunReportRequest(
    property=f"properties/{PROPERTY_ID}",
    dimensions=[Dimension(name="pagePath")],
    metrics=[Metric(name="screenPageViews")],
    date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
    order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"), desc=True)],
    limit=10
))

# Report 2: Daily Traffic Trend
daily_traffic = fetch_report(RunReportRequest(
    property=f"properties/{PROPERTY_ID}",
    dimensions=[Dimension(name="date")],
    metrics=[Metric(name="sessions")],
    date_ranges=[DateRange(start_date="7daysAgo", end_date="today")]
))

# Report 3: Traffic Sources
traffic_sources = fetch_report(RunReportRequest(
    property=f"properties/{PROPERTY_ID}",
    dimensions=[Dimension(name="sessionSourceMedium")],
    metrics=[Metric(name="sessions")],
    date_ranges=[DateRange(start_date="7daysAgo", end_date="today")]
))

# Report 4: Geo-location of Users
geo_location = fetch_report(RunReportRequest(
    property=f"properties/{PROPERTY_ID}",
    dimensions=[Dimension(name="country")],
    metrics=[Metric(name="activeUsers")],
    date_ranges=[DateRange(start_date="7daysAgo", end_date="today")]
))


# Report 5: Post Views (alias for Top Pages)
post_views = top_pages

# Report 6: Bounce Rate
bounce_rate = fetch_report(RunReportRequest(
    property=f"properties/{PROPERTY_ID}",
    metrics=[Metric(name="bounceRate")],
    date_ranges=[DateRange(start_date="7daysAgo", end_date="today")]
))

# Report 7: Average Time on Page
avg_time = fetch_report(RunReportRequest(
    property=f"properties/{PROPERTY_ID}",
    metrics=[Metric(name="averageSessionDuration")],
    date_ranges=[DateRange(start_date="7daysAgo", end_date="today")]
))

# Combine and Output
report = {
    "top_pages": top_pages,
    "daily_traffic": daily_traffic,
    "traffic_sources": traffic_sources,
    "geo_location": geo_location,
    "post_views": post_views,
    "bounce_rate": bounce_rate,
    "average_time_on_page": avg_time
}

print(json.dumps(report, indent=2))
