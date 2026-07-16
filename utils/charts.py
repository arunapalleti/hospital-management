import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Standard colors matching the theme
THEME_COLORS = ["#3b82f6", "#8b5cf6", "#10b981", "#ef4444", "#f59e0b"]

def plot_role_distribution(users):
    """
    Plots a donut chart representing the distribution of roles in the system.
    """
    if not users:
        return None
        
    df = pd.DataFrame(users)
    if "role" not in df.columns:
        return None
        
    role_counts = df["role"].value_counts().reset_index()
    role_counts.columns = ["Role", "Count"]
    
    fig = px.pie(
        role_counts, 
        values="Count", 
        names="Role", 
        hole=0.4,
        color_discrete_sequence=THEME_COLORS,
        title="Campus User Breakdown"
    )
    
    fig.update_layout(
        margin=dict(t=40, b=0, l=0, r=0),
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", size=12)
    )
    return fig

def plot_attendance_trends(attendance_records, users):
    """
    Plots historical attendance trends (daily percentages).
    """
    if not attendance_records or not users:
        # Generate some mock data for first launch dashboard
        dates = pd.date_range(end=pd.Timestamp.now(), periods=7).strftime("%Y-%m-%d").tolist()
        data = {
            "Date": dates,
            "Attendance %": [85.5, 87.2, 89.0, 84.1, 91.5, 93.0, 92.4]
        }
        df = pd.DataFrame(data)
    else:
        # Calculate actual percentages
        students = [u for u in users if u["role"] == "Student"]
        total_students = len(students)
        
        if total_students == 0:
            return None
            
        trend_data = []
        for record in attendance_records:
            date = record["date"]
            recs = record.get("records", {})
            p_count = sum(1 for status in recs.values() if status == "Present")
            pct = (p_count / total_students) * 100 if total_students > 0 else 0
            trend_data.append({"Date": date, "Attendance %": round(pct, 1)})
            
        df = pd.DataFrame(trend_data).sort_values("Date")
        if df.empty:
            return None

    fig = px.line(
        df, 
        x="Date", 
        y="Attendance %",
        markers=True,
        title="Overall Campus Attendance Trend",
        color_discrete_sequence=["#8b5cf6"]
    )
    
    fig.update_layout(
        yaxis=dict(range=[0, 105]),
        margin=dict(t=40, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", size=12)
    )
    return fig

def plot_assignment_submissions(assignments):
    """
    Bar chart showing total students vs submissions.
    """
    if not assignments:
        # Mock data for dashboard
        data = {
            "Assignment": ["Assignment 1", "Assignment 2", "Assignment 3"],
            "Submissions": [12, 8, 4]
        }
        df = pd.DataFrame(data)
    else:
        sub_data = []
        for a in assignments:
            sub_data.append({
                "Assignment": a["title"][:20] + "..." if len(a["title"]) > 20 else a["title"],
                "Submissions": len(a.get("submissions", []))
            })
        df = pd.DataFrame(sub_data)
        if df.empty:
            return None

    fig = px.bar(
        df, 
        x="Assignment", 
        y="Submissions",
        color="Submissions",
        color_continuous_scale=["#bfdbfe", "#3b82f6", "#8b5cf6"],
        title="Submissions by Assignment"
    )
    
    fig.update_layout(
        margin=dict(t=40, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", size=12)
    )
    return fig

def plot_ai_usage():
    """
    Generate interactive chart showing simulated AI Assistant queries per day.
    """
    dates = pd.date_range(end=pd.Timestamp.now(), periods=7).strftime("%Y-%m-%d").tolist()
    queries = [15, 24, 45, 32, 60, 78, 92]
    
    df = pd.DataFrame({
        "Date": dates,
        "Queries": queries
    })
    
    fig = px.area(
        df,
        x="Date",
        y="Queries",
        title="AI Assistant Activity (Last 7 Days)",
        color_discrete_sequence=["#3b82f6"]
    )
    
    fig.update_layout(
        margin=dict(t=40, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", size=12)
    )
    return fig
