import pandas as pd
import argparse

# main CLI function
if __name__ == "__main__":
    # read in our country regression results for prediction
    # country (str) | slope (float) | intercept (float) | r_squared (float)
    country_regressions = pd.read_csv("country_regression_results.csv")
    # set up argument parser
    parser = argparse.ArgumentParser(
        description="Predict temperature change for a given country and year based on cumulative CO2 emissions relative to 1850.",
        epilog="""Example Usage: python cli.py -c United_States_of_America -y 2026\nYou must provide both country and year for prediction.\nNote: Use underscores (_) for spaces in country names, case sensitive.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # country argument with validation against available countries
    def validate_country(country_str):
        available_countries = country_regressions["country"].tolist()
        if country_str not in available_countries:
            raise argparse.ArgumentTypeError(f"Country '{country_str}' is not available for prediction. Use -l to list available countries.")
        return country_str

    parser.add_argument(
        "-c", "--country",
        type=validate_country,
        help="Name of country, use _ for spaces (e.g., United_States)"
    )

    # year argument with validation in [1851, 2100] time range
    def validate_year(year_str):
        year = int(year_str)
        if year < 1851 or year > 2100:
            raise argparse.ArgumentTypeError("Year must be between 1851 and 2100 inclusive")
        return year

    parser.add_argument(
        "-y", "--year",
        type=validate_year,
        help="Year for prediction (between 1851 and 2100 inclusive)"
    )

    # list argument to list available countries
    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="List all available countries for prediction"
    )

    # parse arguments
    args = parser.parse_args()

    # if list flag is set, print available countries and exit
    if args.list:
        print("Available countries for prediction:")
        for country in country_regressions["country"]:
            print(country)
        exit(0)

    # if either country or year is missing, print help and exit
    if not all([args.year, args.country]):
        parser.print_help()
        exit(0)

    # read in cumulative_CO2 for prediction
    # year (int) | cumulative_CO2 (float)
    cumulative_CO2 = pd.read_csv("../public/cumulative_co2.csv")

    # get cumulative_CO2 for the specified year
    co2_value = cumulative_CO2.loc[cumulative_CO2["year"] == args.year, "cumulative_CO2"].values[0]

    # get slope and intercept for the specified country
    country_row = country_regressions.loc[country_regressions["country"] == args.country]

    slope = country_row["slope"].values[0]
    intercept = country_row["intercept"].values[0]
    r_squared = country_row["r_squared"].values[0]
    
    # make prediction
    predicted_temp_change = slope * co2_value + intercept
    sign = "+" if predicted_temp_change >= 0 else "-"
    print(f"Predicted temperature change for {args.country} in {args.year} relative to 1850:")
    print(f"{sign}{abs(predicted_temp_change):.2f}°K/C = {sign}{abs(predicted_temp_change) * 9/5:.2f}°F with R² {r_squared:.2f}")
