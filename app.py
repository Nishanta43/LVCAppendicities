from flask import Flask, render_template, request, jsonify
import pandas as pd

app = Flask(__name__)

# Constants for calculations
CT_EMISSION = 9.2  # kgCO₂e per scan
US_EMISSION = 0.5  # kgCO₂e per scan
LA_EMISSION = 27.4  # kgCO₂e per case
OA_EMISSION = 22.7  # kgCO₂e per case
USD_TO_THB = 33.61  # Exchange rate
SC_CO2_USD = 0.185  # Social cost of carbon in USD per kg
SC_CO2_THB = SC_CO2_USD * USD_TO_THB  # Social cost of carbon in THB per kg

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    # Get form data
    data = {}
    for year in ['2019', '2020', '2021']:
        data[year] = {
            'total_cases': float(request.form.get(f'total_cases_{year}', 0)),
            'peritonitis_general': float(request.form.get(f'peritonitis_general_{year}', 0)),
            'peritonitis_local': float(request.form.get(f'peritonitis_local_{year}', 0)),
            'uncomplicated': float(request.form.get(f'uncomplicated_{year}', 0)),
            'avg_cost': float(request.form.get(f'avg_cost_{year}', 0)),
            'oa_cases': float(request.form.get(f'oa_cases_{year}', 0)),
            'la_cases': float(request.form.get(f'la_cases_{year}', 0)),
            'ct_scans': float(request.form.get(f'ct_scans_{year}', 0)),
            'us_scans': float(request.form.get(f'us_scans_{year}', 0))
        }
    
    # Process calculations
    results = {}
    for year in ['2019', '2020', '2021']:
        year_data = data[year]
        
        # Calculate total cost
        total_cost = year_data['total_cases'] * year_data['avg_cost']
        
        # Calculate carbon emissions
        oa_emissions = year_data['oa_cases'] * OA_EMISSION
        la_emissions = year_data['la_cases'] * LA_EMISSION
        ct_emissions = year_data['ct_scans'] * CT_EMISSION
        us_emissions = year_data['us_scans'] * US_EMISSION
        total_emissions = oa_emissions + la_emissions + ct_emissions + us_emissions
        
        # Calculate social cost of carbon
        sc_co2 = total_emissions * SC_CO2_THB
        
        # Calculate percentages
        ct_percentage = (year_data['ct_scans'] / year_data['total_cases']) * 100 if year_data['total_cases'] > 0 else 0
        us_percentage = (year_data['us_scans'] / year_data['total_cases']) * 100 if year_data['total_cases'] > 0 else 0
        
        results[year] = {
            'total_cost': total_cost,
            'oa_emissions': oa_emissions,
            'la_emissions': la_emissions,
            'ct_emissions': ct_emissions,
            'us_emissions': us_emissions,
            'total_emissions': total_emissions,
            'sc_co2': sc_co2,
            'ct_percentage': ct_percentage,
            'us_percentage': us_percentage
        }
    
    # Calculate percentage changes
    changes = {
        '2019-2020': calculate_changes(results['2019'], results['2020']),
        '2019-2021': calculate_changes(results['2019'], results['2021'])
    }
    
    return jsonify({'results': results, 'changes': changes})

def calculate_changes(base_year, compare_year):
    changes = {}
    for key in base_year:
        if base_year[key] != 0:
            changes[key] = ((compare_year[key] - base_year[key]) / base_year[key]) * 100
        else:
            changes[key] = 0
    return changes

if __name__ == '__main__':
    app.run(debug=True)