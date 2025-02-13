import pandas as pd
from flask import Flask, render_template, request

app = Flask(__name__)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

app.config['SECRET_KEY'] = 'your secret key'

# Load Dataset
train_data = pd.read_csv(r"C:\Users\USER\Downloads\crimes.csv")

# Data Cleaning
train_data["Vict Sex"] = train_data["Vict Sex"].replace({"F": 0, "M": 1})
train_data["Weapon Desc"] = pd.to_numeric(train_data["Weapon Desc"], errors='coerce').fillna(1).astype(int)
train_data["Vict Sex"] = train_data["Vict Sex"].fillna(0)
train_data.drop("Vict Descent", axis=1, inplace=True)

# Crime Area Analysis
grouped_areas = train_data['AREA NAME'].value_counts().reset_index()
grouped_areas.columns = ['AREA NAME', 'Case Count']
sorted_areas = grouped_areas.sort_values(by='Case Count', ascending=False)

def assign_rating(count):
    if count > 10000:
        return "Extreme"
    elif count > 5000:
        return "High"
    elif count > 2000:
        return "Moderate"
    else:
        return "Low"

sorted_areas['Rating'] = sorted_areas['Case Count'].apply(assign_rating)

# Create Risk Map Data
data = {
    'AREA NAME': ['Central', 'Southwest', '77th Street', 'Pacific', 'Hollywood', 'Southeast',
                  'Olympic', 'Newton', 'Van Nuys', 'N Hollywood', 'Wilshire', 'Topanga',
                  'Rampart', 'West Valley', 'West LA', 'Northeast', 'Devonshire', 'Mission',
                  'Harbor', 'Hollenbeck', 'Foothill'],
    'Case Count': [14944, 11945, 11739, 9923, 9762, 9571, 9414, 9152, 8621, 8502, 8482, 8478,
                   8346, 8102, 7911, 7628, 7411, 6990, 6618, 6193, 5983],
    'Rating': ['Extreme', 'Extreme', 'Extreme', 'High', 'High', 'High', 'High', 'High', 'High',
               'High', 'High', 'High', 'High', 'High', 'High', 'High', 'High', 'High', 'High', 
               'High', 'High']
}
risk_df = pd.DataFrame(data)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        area_name = request.form['area_name']
        
        # Find risk factors for the entered area
        area_data = risk_df[risk_df['AREA NAME'] == area_name]
        if not area_data.empty:
            risk_factors = area_data.to_dict('records')[0]
        else:
            risk_factors = None
        
        # Suggest an alternative place (basic example: the next safest area)
        current_index = risk_df[risk_df['AREA NAME'] == area_name].index.values[0]
        if current_index < len(risk_df) - 1:
            recommendation = risk_df.iloc[current_index + 1].to_dict()
        else:
            recommendation = None
            
        return render_template('index.html', area_name=area_name, risk_factors=risk_factors, recommendation=recommendation)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
