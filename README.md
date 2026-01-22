# FRED Economic Data Dashboard

A real-time dashboard for visualizing U.S. economic indicators from the Federal Reserve Economic Data (FRED) database. The dashboard displays unemployment rate, GDP, and GDP growth rate with interactive charts that update daily.

## Features

- **Interactive Visualizations**: Dynamic charts using Plotly for unemployment, GDP, and GDP growth
- **Real-time Data**: Fetches latest economic data from FRED API
- **Auto-updating**: Data refreshes automatically every 24 hours
- **Caching**: Smart caching mechanism to minimize API calls
- **Historical Data**: View trends over customizable time periods (1-30 years)
- **Data Export**: Download economic data as CSV
- **Responsive Design**: Works on desktop and mobile devices

## Dashboard Screenshots

The dashboard includes:
- Current metric cards showing latest values and changes
- Dual-axis chart comparing unemployment rate vs GDP
- Individual trend charts for each indicator
- Raw data viewer with export functionality

## Prerequisites

- Python 3.8 or higher
- FRED API key (free) - [Get one here](https://fred.stlouisfed.org/docs/api/api_key.html)

## Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd Work
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your FRED API key

1. Get a free API key from [FRED](https://fred.stlouisfed.org/docs/api/api_key.html)
2. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` and add your API key:
   ```
   FRED_API_KEY=your_actual_api_key_here
   ```

## Usage

### Running the Dashboard

Start the Streamlit dashboard:

```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

### Manual Data Update

To manually refresh the data cache:

```bash
python update_data.py
```

### Automated Daily Updates

#### Option 1: Using GitHub Actions (Recommended)

The repository includes a GitHub Actions workflow that automatically updates data daily at 9 AM UTC.

**Setup:**
1. Add your FRED API key to GitHub Secrets:
   - Go to your repository Settings → Secrets and variables → Actions
   - Add a new secret named `FRED_API_KEY` with your API key
2. The workflow will run automatically every day
3. You can also trigger it manually from the Actions tab

#### Option 2: Using Cron (Linux/Mac)

Set up a cron job to run the update script daily:

```bash
# Edit crontab
crontab -e

# Add this line to run at 9 AM daily
0 9 * * * cd /path/to/Work && /path/to/venv/bin/python update_data.py >> /path/to/logs/fred_update.log 2>&1
```

See `crontab.example` for more examples.

## Project Structure

```
Work/
├── app.py                      # Main Streamlit dashboard application
├── data_fetcher.py             # FRED API data fetching and caching
├── config.py                   # Configuration settings
├── update_data.py              # Script for manual/scheduled data updates
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (API key)
├── .env.example                # Example environment file
├── .gitignore                  # Git ignore rules
├── crontab.example             # Example cron configuration
├── .github/
│   └── workflows/
│       └── update-data.yml     # GitHub Actions workflow
└── data_cache/                 # Cached FRED data (auto-generated)
    ├── UNRATE.pkl              # Unemployment rate cache
    ├── GDP.pkl                 # GDP cache
    └── A191RL1Q225SBEA.pkl     # GDP growth rate cache
```

## Configuration

Edit `config.py` to customize:

- **FRED Series**: Add or modify economic indicators
- **Cache Settings**: Adjust cache expiration time
- **Dashboard Settings**: Modify default time ranges and titles

### Available FRED Series IDs

The dashboard currently tracks:
- `UNRATE`: Unemployment Rate
- `GDP`: Gross Domestic Product
- `A191RL1Q225SBEA`: Real GDP Growth Rate

You can add more series from the [FRED database](https://fred.stlouisfed.org/).

## API Rate Limits

The FRED API has the following limits:
- 120 requests per 60 seconds
- This dashboard uses caching to stay well below these limits
- Data refreshes only once per 24 hours by default

## Deployment

### Streamlit Cloud

1. Push your code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Deploy your app
4. Add your `FRED_API_KEY` to the Streamlit secrets

### Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t fred-dashboard .
docker run -p 8501:8501 -e FRED_API_KEY=your_key fred-dashboard
```

## Troubleshooting

### "FRED API key not found" error

- Make sure you've created a `.env` file with your API key
- Verify the key is correct and active
- Check that `python-dotenv` is installed

### Data not updating

- Run `python update_data.py` manually to test
- Check your internet connection
- Verify your FRED API key is valid
- Check the `data_cache/` directory permissions

### Charts not displaying

- Clear your browser cache
- Try running `streamlit cache clear`
- Restart the Streamlit server

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Data Source

All economic data is sourced from [FRED (Federal Reserve Economic Data)](https://fred.stlouisfed.org/), maintained by the Federal Reserve Bank of St. Louis.

## Acknowledgments

- FRED API for providing free access to economic data
- Streamlit for the excellent dashboard framework
- Plotly for interactive visualizations

## Contact

For questions or issues, please open an issue on GitHub.

---

**Note**: This dashboard is for informational purposes only and should not be used as the sole basis for investment or policy decisions.
