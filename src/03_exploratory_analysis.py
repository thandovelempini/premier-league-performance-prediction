import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

team_season = pd.read_csv("data/processed/premier_league_team_season.csv")

# EXPLORATORY ANALYSIS

# Display dataset information
print("Dataset shape:", team_season.shape)

print("\nFirst five rows:")
print(team_season.head())

# Summary statistics
print("\nSummary statistics:")
print(team_season.describe())

# Distribution of Premier League points
plt.figure(figsize=(10, 6))

plt.hist(
    team_season["Points"],
    bins=15,
    edgecolor="black"
)

plt.title("Distribution of Premier League Points")
plt.xlabel("Points")
plt.ylabel("Number of Team-Season")

plt.show()

# Average points per season
season_points = team_season.groupby("Season")["Points"].mean()

print("\nAverage points per season:")
print(season_points)

# Distribution of points by season
plt.figure(figsize=(12, 6))

sns.boxenplot(
    data=team_season,
    x="Season",
    y="Points"
)

plt.title("Distribution of Premier League Points by Season")
plt.xlabel("Season")
plt.ylabel("Points")
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()

# RELATIONSHIP BETWEEN PERFORMANCE METRICS AND POINTS

# Correlation with Points
numeric_columns = team_season.select_dtypes(
    include="number"
)

points_correlation = (
    numeric_columns.corr()["Points"]
    .sort_values(ascending=False)
)

print("\nCorrelation with Points:")
print(points_correlation)

# Performance statistics correlation with Points
performance_variables = [
    "Goals_Scored",
    "Goals_Conceded",
    "Goal_Difference",
    "Shots",
    "Shots_On_Target",
    "Fouls",
    "Corners",
    "Yellow_Cards",
    "Red_Cards"
]

performance_correlation = (
    team_season[performance_variables + ["Points"]]
    .corr()["Points"]
    .drop("Points")
    .sort_values(ascending=False)
)

print("\nPerformance statistics correlation with Points:")
print(performance_correlation)

# Visualise correlation with Points
plt.figure(figsize=(10, 6))

performance_correlation.sort_values().plot(
    kind="barh"
)
plt.title("Correlation Between Team Performance Statistics and Points")
plt.xlabel("Correlation with Points")
plt.ylabel("Performance Statistics")

plt.axvline(
    x=0,
    linewidth=1
)

plt.tight_layout()
plt.show()

# Scatter plots for the strongest relationships with Points
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

sns.regplot(
    data=team_season,
    x="Goal_Difference",
    y="Points",
    ax=axes[0, 0]
)

axes[0, 0].set_title("Goal Difference vs Points")

sns.regplot(
    data=team_season,
    x="Goals_Scored",
    y="Points",
    ax=axes[0, 1]
)

axes[0, 1].set_title("Goals Scored vs Points")

sns.regplot(
    data=team_season,
    x="Goals_Conceded",
    y="Points",
    ax=axes[1, 0]
)

axes[1, 0].set_title("Goals Conceded vs Points")

sns.regplot(
    data=team_season,
    x="Shots_On_Target",
    y="Points",
    ax=axes[1, 1]
)

axes[1, 1].set_title("Shots on Target vs Points")

plt.tight_layout()
plt.show()

# INVESTIGATE EFFICIENCY

# Create efficiency metrics
team_season["Shot_Conversion_Rate"] = (
    team_season["Goals_Scored"] / team_season["Shots"]
)

team_season["Shots_On_Target_Conversion_Rate"] = (
    team_season["Goals_Scored"] / team_season["Shots_On_Target"]
)

# Convert to percentages 
team_season["Shot_Conversion_Percentage"] = (
    team_season["Shot_Conversion_Rate"] * 100
)

team_season["Shots_On_Target_Conversion_Percentage"] = (
    team_season["Shots_On_Target_Conversion_Rate"] * 100
)

# Check correlations with Points
efficiency_variables = [
    "Shot_Conversion_Percentage",
    "Shots_On_Target_Conversion_Percentage",
    "Points"
]

print("\nEfficiency metrics correlation with Points:")
print(
    team_season[efficiency_variables]
    .corr()["Points"]
    .sort_values(ascending=False)
)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

sns.regplot(
    data=team_season,
    x="Shots",
    y="Points",
    ax=axes[0, 0]
)

axes[0, 0].set_title("Shots vs Points")

sns.regplot(
    data=team_season,
    x="Shot_Conversion_Percentage",
    y="Points",
    ax=axes[0, 1]
)

axes[0, 1].set_title("Shot Conversion Percentage vs Points")

sns.regplot(
    data=team_season,
    x="Shots_On_Target",
    y="Points",
    ax=axes[1, 0]
)

axes[1, 0].set_title("Shots on Target vs Points")

sns.regplot(
    data=team_season,
    x="Shots_On_Target_Conversion_Percentage",
    y="Points",
    ax=axes[1, 1]
)

axes[1, 1].set_title("Shots on Target Conversion Percentage vs Points")

plt.tight_layout()
plt.show()

# CEHCK RELATIONSHIP BETWEEN THE PREDICTORS

# Select independent performanc variables
model_variables = [
    "Points",
    "Shots",
    "Shots_On_Target",
    "Shot_Conversion_Percentage",
    "Shots_On_Target_Conversion_Percentage",
    "Fouls",
    "Corners",
    "Yellow_Cards",
    "Red_Cards"
]

# Calculate correlations
model_correlations = team_season[model_variables].corr()

print("\nCorrelation matrix:")
print(model_correlations)

# Visualise the correlation matrix
plt.figure(figsize=(10, 8))

sns.heatmap(
    model_correlations,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    center=0
)

plt.title("Correlation Between Team Performance Variables")
plt.tight_layout()
plt.show()

# VIF (VARIANCE INFLATION FACTOR) ANALYSIS

from statsmodels.stats.outliers_influence import variance_inflation_factor

# Select predictor variables
predictors = [
    "Shots_On_Target",
    "Shot_Conversion_Percentage",
    "Fouls",
    "Yellow_Cards",
    "Red_Cards"
]

X = team_season[predictors]

# Calculate VIF
vif_data = pd.DataFrame()
vif_data["Variable"] = X.columns
vif_data["VIF"] = [
    variance_inflation_factor(X.values, i)
    for i in range(X.shape[1])
]

print("\nVariance Inflation Factors:")
print(vif_data.sort_values("VIF", ascending=False))

# REGRESSION MODEL

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Define predictors and target
X = team_season[predictors]
y = team_season["Points"]

# Split the data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Create and train the model
model = LinearRegression()
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate model
print("\nModel Performance:")

print("R-Squared:", r2_score(y_test, y_pred))
print("Mean Absolute Error:", mean_absolute_error(y_test, y_pred))
print("Root Mean Squared Error:", mean_squared_error(y_test, y_pred) ** 0.5)

# OUT-OF-SAMPLE PREDICTED POINTS

# Create a dataframe to compare actual and predicted points
results = X_test.copy()

results["Actual_Points"] = y_test
results["Predicted_Points"] = y_pred

# Calculate overperformance 
results["Overperformance"] = (
    results["Actual_Points"] -
    results["Predicted_Points"]
)

# Add team and season information
results = results.join(
    team_season[["Season", "Team"]]
)

# Reoder columns
results = results[
    [
        "Season",
        "Team",
        "Actual_Points",
        "Predicted_Points",
        "Overperformance"
    ]
]

# Sort from biggest overperformer to biggest underperformer
results = results.sort_values(
    "Overperformance",
    ascending=False
)

print("\nBiggest Overperformers:")
print(results.head(10))

print("\nBiggest Underperformers:")
print(results.tail(10))

# CROSS-VALIDATION PREDICTIONS FRO EVERY TEAM-SEASON

from sklearn.model_selection import cross_val_predict, KFold

# Cross-validation setup
cv = KFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

# Generate out-of-fold predictions for every team-season
cv_model = LinearRegression()

team_season["Predicted_Points"] = cross_val_predict(
    cv_model,
    X,
    y,
    cv=cv
)

# Calculate performance 
team_season["Overperformance"] = (
    team_season["Points"] -
    team_season["Predicted_Points"]
)

# Create ranking dataframe
overperformance_results = team_season[
    [
        "Season",
        "Team",
        "Points",
        "Predicted_Points",
        "Overperformance"
    ]
].sort_values(
    "Overperformance",
    ascending=False
)

print("\nTop 10 Overperforming Team-Seasons:")
print(overperformance_results.head(10))

print("\nTop 10 Underperforming Team-Season:")
print(overperformance_results.tail(10))

# INVESTIGATE RESIDUALS

# Actual vs predicted points
plt.figure(figsize=(10, 7))

sns.scatterplot(
    data=team_season,
    x="Predicted_Points",
    y="Points"
)

# Perfect prediction line
plt.plot(
    [team_season["Predicted_Points"].min(),
     team_season['Predicted_Points'].max()],

     [team_season["Predicted_Points"].min(),
      team_season['Predicted_Points'].max()]
)

plt.title("Actual vs Pedicted Premier League Points")
plt.xlabel("Predicted Points")
plt.ylabel("Actual Points")

plt.tight_layout()
plt.show()

