from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Country Info App</title>
<style>
body {
    font-family: Arial, sans-serif;
    background: linear-gradient(to bottom, #83a4d4, #b6fbff);
    color: #333;
    text-align: center;
    padding: 50px 20px;
}
form {
    margin-bottom: 30px;
}
input, button {
    padding: 10px;
    margin: 5px;
    border: none;
    border-radius: 5px;
    font-size: 16px;
}
button {
    background-color: #0077ff;
    color: white;
    cursor: pointer;
}
#countries {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
    justify-items: center;
}
.country {
    border: 1px solid #ccc;
    padding: 15px;
    border-radius: 8px;
    background: rgba(255,255,255,0.85);
    width: 100%;
    text-align: left;
    box-sizing: border-box;
}
.country img { width: 50px; vertical-align: middle; margin-right: 10px; }
</style>
</head>
<body>

<h1>🌎 Country Information</h1>

<form id="searchForm">
    <input type="text" id="searchInput" placeholder="Enter country name" required>
    <button type="submit">Search</button>
</form>

<div id="countries"></div>

<script>
let countryData = [];

const traditionalFlowers = {
  "Japan": "Cherry Blossom",
  "India": "Lotus",
  "United States": "Rose",
  "United Kingdom": "Tudor Rose",
  "France": "Lily",
  "China": "Peony",
  "South Korea": "Rose of Sharon",
  "Canada": "Maple Leaf Flower",
  "Australia": "Golden Wattle",
  "Mexico": "Dahlia"
};

// Fetch all country data
fetch('https://restcountries.com/v3.1/all?fields=name,capital,currencies,flags,population,region')
  .then(response => response.json())
  .then(data => {
    countryData = data;
    renderCountries(countryData);
  })
  .catch(err => console.error(err));

// Render countries in the grid
function renderCountries(countries) {
    const container = document.getElementById('countries');
    container.innerHTML = '';
    if(countries.length === 0){
        container.innerHTML = '<p>No countries found.</p>';
        return;
    }
    countries.forEach(country => {
        const div = document.createElement('div');
        div.className = 'country';
        const flower = traditionalFlowers[country.name.common] || 'N/A';
        div.innerHTML = `
            <img src="${country.flags.png}" alt="Flag">
            <strong>${country.name.common}</strong><br>
            Capital: ${country.capital ? country.capital[0] : 'N/A'}<br>
            Region: ${country.region} | Population: ${country.population.toLocaleString()}<br>
            Currencies: ${country.currencies ? Object.values(country.currencies).map(c => c.name + ' (' + c.symbol + ')').join(', ') : 'N/A'}<br>
            Traditional Flower: ${flower}
        `;
        container.appendChild(div);
    });
}

// Search form handler
document.getElementById('searchForm').addEventListener('submit', function(e){
    e.preventDefault();
    const term = document.getElementById('searchInput').value.toLowerCase();
    const filtered = countryData
        .filter(c => c.name.common.toLowerCase().includes(term))
        .sort((a, b) => {
            if(a.name.common.toLowerCase() === term) return -1;
            if(b.name.common.toLowerCase() === term) return 1;
            return 0;
        });
    renderCountries(filtered);
});
</script>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(debug=True)
